import time
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from authentication import models
from django.db.models import Q
from django.http import JsonResponse
from chat.models import ChatModel


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def base(request):
    return render(request, 'base.html')


@login_required
def chat(request):
    try:
        friendship_obj = models.Friendship.objects.filter((Q(user_1=request.user) | Q(user_2=request.user)) & Q(status='A'))
        response = []
        for each in friendship_obj:
            message = ChatModel.objects.filter(friendship=each).last()
            file_type = 'text'
            if message and message.chat_picture:
                file_type = 'image'
            elif message and message.chat_files:
                file_type = 'file'
            if each.user_1 == request.user:
                response.append({
                    'id': each.id,
                    'firstname': each.user_2.firstname,
                    'lastname': each.user_2.lastname,
                    'address': each.user_2.address,
                    'profile_picture': each.user_2.profile_picture.url,
                    'message': message,
                    'type': file_type
                })
            else:
                response.append({
                    'id': each.id,
                    'firstname': each.user_1.firstname,
                    'lastname': each.user_1.lastname,
                    'address': each.user_1.address,
                    'profile_picture': each.user_1.profile_picture.url,
                    'message': message,
                    'type': file_type
                })

        return render(request, 'chat.html', {'response': response})

    except models.Friendship.DoesNotExist as e:
        print(e)

    return render(request, 'chat.html')


def add_friend(request):
    friends = models.Friendship.objects.filter(Q(user_1=request.user) | Q(user_2=request.user))
    response = []
    if friends:
        for each in friends:
            if each.status == 'S':
                if each.user_1 == request.user:
                    response.append({
                        'id': each.user_2.id,
                        'firstname': each.user_2.firstname,
                        'lastname': each.user_2.lastname,
                        'address': each.user_2.address,
                        'profile_picture': each.user_2.profile_picture.url,
                        'friendship_status': each.status,
                        'sender': each.user_1.id
                    })
                else:
                    response.append({
                        'id': each.user_1.id,
                        'firstname': each.user_1.firstname,
                        'lastname': each.user_1.lastname,
                        'address': each.user_1.address,
                        'profile_picture': each.user_1.profile_picture.url,
                        'friendship_status': each.status,
                        'sender': each.user_1.id
                    })
    return render(request, 'add_friend.html', {'response': response})


def settings(request):
    return render(request, 'settings.html')


def sidebar_handler(request):
    render_objects = {
        'chat': chat(request),
        'add_friend': add_friend(request),
        'settings': settings(request),
    }
    if request.method == 'GET':
        try:
            action = request.GET['action']
            return render_objects[action]
        except KeyError:
            pass

    return HttpResponse('error')


def add_friend_search(request):
    if request.method == 'GET':
        try:
            search = request.GET['search']
            search = search.strip()
            users = models.UserModel.objects.filter(Q(firstname__icontains=search) | Q(lastname__icontains=search))
            current_user = request.user
            response = []

            for user in users:
                if user == current_user:
                    continue
                friendship = models.Friendship.objects.filter(
                    (Q(user_1=current_user) & Q(user_2=user)) | (Q(user_1=user) & Q(user_2=current_user))
                ).first()
                response.append({
                    'id': user.id,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'address': user.address,
                    'profile_picture': user.profile_picture.url,
                    'friendship_status': friendship.status if friendship else None
                })

            return JsonResponse({'response': response})
        except KeyError as e:
            print(e)

    return HttpResponse('error')


def add_friend_search_add_message(request):
    if request.method == 'POST':
        action, user_id, status = request.POST['data'].split('-')
        try:
            if action == 'add' and status == 'null':
                add_obj = models.Friendship.objects.create(user_1=request.user,
                                                           user_2=models.UserModel.objects.get(id=user_id))

                return JsonResponse({'response': action+'-'+user_id+'-S'})

        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def add_friend_request_handler(request):
    if request.method == 'POST':
        friend_id, action = request.POST['data'].split('-')
        try:
            if action == 'accept':
                obj = models.Friendship.objects.filter(
                    Q(user_1=models.UserModel.objects.get(id=friend_id)) & Q(user_2=request.user)).first()
                obj.status = 'A'
                obj.save()
                return JsonResponse({'response': 'success'})
            elif action == 'decline':
                obj = models.Friendship.objects.filter((Q(user_1=models.UserModel.objects.get(id=friend_id)) & Q(user_2=request.user)) |
                                                        (Q(user_1=request.user) & Q(user_2=models.UserModel.objects.get(id=friend_id))))
                obj.delete()
                return JsonResponse({'response': 'success'})
        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def load_chat(request):
    if request.method == 'POST':
        friendship_id = request.POST['friendship_id']
        try:
            chats = ChatModel.objects.filter(friendship=models.Friendship.objects.get(id=friendship_id))
            response = []
            user = request.user
            for each in chats:
                file_type = 'text'
                if each.chat_picture:
                    file_type = 'image'
                elif each.chat_files:
                    file_type = 'file'
                response.append({
                    'sender': each.sender.id,
                    'message': each.message,
                    'timestamp': each.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'profile_picture': models.UserModel.objects.get(id=each.sender.id).profile_picture.url,
                    'type': file_type,
                    'chat_picture': each.chat_picture.url if each.chat_picture else None,
                    'chat_files': each.chat_files.url if each.chat_files else None

                })
            return JsonResponse({'response': response})
        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def settings_email_check(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            email = email.strip()
            if email.endswith('@gmail.com') is False:
                return JsonResponse({'response': 'error'})
            current_user_email = request.user.email
            if email == current_user_email:
                return JsonResponse({'response': 'success'})
            else:
                if models.UserModel.objects.filter(email=email).exists():
                    return JsonResponse({'response': 'error'})

                return JsonResponse({'response': 'success'})
        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def settings_save(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        address = request.POST['address']
        email = request.POST['email']
        gender = request.POST['gender']

        try:
            user = models.UserModel.objects.get(id=request.user.id)
            user.firstname = firstname
            user.lastname = lastname
            user.address = address
            user.email = email
            user.gender = gender
            user.save()
            return JsonResponse({'response': 'success'})
        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def settings_password_change(request):
    if request.method == 'POST':
        oldPassword = request.POST['oldPassword']
        newPassword = request.POST['newPassword']

        try:
            user = models.UserModel.objects.get(id=request.user.id)
            if user.check_password(oldPassword):
                user.set_password(newPassword)
                user.save()
                return JsonResponse({'response': 'success'})
            else:
                return JsonResponse({'response': 'error'})

        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def settings_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile-pic'):
        try:
            user = models.UserModel.objects.get(id=request.user.id)
            user.profile_picture = request.FILES['profile-pic']
            user.save()
            return JsonResponse({'response': user.profile_picture.url})
        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def sent_receiver(request):
    if request.method == 'GET':
        friends = models.Friendship.objects.filter(Q(user_1=request.user) | Q(user_2=request.user))
        response = []
        if friends:
            for each in friends:
                if each.status == 'S':
                    if each.user_1 == request.user:
                        response.append({
                            'id': each.user_2.id,
                            'firstname': each.user_2.firstname,
                            'lastname': each.user_2.lastname,
                            'address': each.user_2.address,
                            'profile_picture': each.user_2.profile_picture.url,
                            'friendship_status': each.status,
                            'sender': each.user_1.id
                        })
                    else:
                        response.append({
                            'id': each.user_1.id,
                            'firstname': each.user_1.firstname,
                            'lastname': each.user_1.lastname,
                            'address': each.user_1.address,
                            'profile_picture': each.user_1.profile_picture.url,
                            'friendship_status': each.status,
                            'sender': each.user_1.id
                        })

        return JsonResponse({'response': response})

    return JsonResponse({'response': 'error'})


def settings_delete_account(request):
    if request.method == 'POST':
        try:
            password = request.POST['password']
            user = models.UserModel.objects.get(id=request.user.id)
            if user.check_password(password):
                user.delete()
                return JsonResponse({'response': 'success'})
            else:
                return JsonResponse({'response': 'error'})

        except KeyError as e:
            print(e)

    return JsonResponse({'response': 'error'})


def chat_receive_image(request):
    if request.method == 'POST':
        try:
            image = request.FILES.get('image')
            sender_id = request.POST.get('sender_id')
            friendship_id = request.POST.get('friendship_id')
            token = request.POST.get('token')

            ChatModel.objects.create(
                friendship_id=friendship_id,
                sender_id=sender_id,
                token=token,
                chat_picture=image
            )

            return JsonResponse({'response': 'success'})
        except Exception as e:
            print(e)


def chat_receive_file(request):
    if request.method == 'POST':
        try:
            file = request.FILES.get('file')
            sender_id = request.POST.get('sender_id')
            friendship_id = request.POST.get('friendship_id')
            token = request.POST.get('token')

            ChatModel.objects.create(
                friendship_id=friendship_id,
                sender_id=sender_id,
                token=token,
                chat_files=file
            )

            return JsonResponse({'response': 'success'})
        except Exception as e:
            print(e)

