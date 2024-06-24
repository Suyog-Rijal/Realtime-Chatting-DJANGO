from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
import uuid
from . import models
from django.views.decorators.cache import cache_control
from django.core.mail import EmailMessage
import random
from django.conf import settings


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('base')

    if request.method == 'POST':
        email, password = clean_data(request.POST['email'], request.POST['password'])
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_verified:
                login(request, user)
                return redirect('base')
            else:
                send_verification_code(request)
                return render(request, 'verify.html', {'email': email})
        else:
            return render(request, 'login.html', {'error': True})

    return render(request, 'login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('chat')
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email, password = clean_data(request.POST['email'], request.POST['password'])
        dob = request.POST['dob']
        gender = request.POST['gender']

        try:
            models.UserModel.objects.create_user(firstname=firstname, lastname=lastname, email=email, password=password, dob=dob, gender=gender)
            send_verification_code(request)
            return render(request, 'verify.html', {'email': email})
        except Exception as e:
            print(e)

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def validate_email(request):
    if request.method == 'GET':
        email = request.GET['email']
        email = email.strip().lower()
        if models.UserModel.objects.filter(email=email).exists():
            return JsonResponse({'valid': False})
        else:
            return JsonResponse({'valid': True})

    return JsonResponse({'valid': False})


def clean_data(email, password):
    email = email.strip().lower()
    password = password.strip()
    return email, password


def verify(request):
    email = ''
    code = ''
    if request.method == 'POST':
        email = request.POST['email']
        for i in range(5):
            code += request.POST[f'c{i}']

        try:
            user = models.UserModel.objects.get(email=email)
            token_obj = models.Tokens.objects.get(user=user)
            print(code, user, token_obj.token, token_obj.expiry_date)
            if token_obj.token == code and token_obj.expiry_date >= timezone.now():
                user.is_verified = True
                token_obj.delete()
                user.save()
                login(request, user)
                return redirect('base')
            else:
                return render(request, 'verify.html', {'email': email, 'error': True})
        except Exception as e:
            print(e)

    return render(request, 'verify.html', {'email': email})


def send_verification_code(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            code = random.randint(10000, 99999)
            user = models.UserModel.objects.get(email=email)

            # Send email
            subject = "Email Verification - Whisper"
            message = f"""
            <html>
            <body>
                <p>Dear User,</p>
                
                <p>Thank you for signing up for <strong>Whisper</strong>, the exciting new chatting web application! To complete your registration, please verify your email address by entering the following code:</p>
                
                <p style="font-size: 20px;"><strong>Verification Code: {code}</strong></p>
                
                <p>This code will expire in 5 minutes, so please enter it promptly to verify your account.</p>
                
                <p>If you did not request this verification, please disregard this email. Your account will not be created without your confirmation.</p>
                
                <p>Thank you for joining Whisper. We look forward to you connecting with friends and family on our platform!</p>
                
                <p>Best regards,</p>
                <p>The Whisper Team</p>
            </body>
            </html>
            """
            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
            email.content_subtype = 'html'

            try:
                obj = models.Tokens.objects.get(user=user)
                obj.token = code
                obj.expiry_date = timezone.now() + timezone.timedelta(minutes=5)
                obj.save()
            except Exception as e:
                print(e)
                models.Tokens.objects.create(user=user, token=code, expiry_date=timezone.now() + timezone.timedelta(minutes=5))

            email.send()
        except Exception as e:
            print(e)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        host = request.get_host()
        protocol = 'http' if not request.is_secure() else 'https'

        if models.UserModel.objects.filter(email=email).exists():
            user = models.UserModel.objects.get(email=email)
            token = str(uuid.uuid4())
            print(host+"/reset/"+token)
            # Send email
            subject = "Password Reset - Whisper"
            message = f"""
            <html>
            <body>
                <p>Dear User,</p>

                <p>We have received a request to reset the password for your Whisper account. To reset your password, please click the link below:</p>

                <p><a href="{protocol}://{host}/authentication/reset/password/{token}">Reset Password</a></p>

                <p>If you did not request this password reset, please disregard this email. Your account will remain secure.</p>

                <p>Thank you for using Whisper. We hope you enjoy using our platform!</p>

                <p>Best regards,</p>
                <p>The Whisper Team</p>
            </body>
            </html>
            """
            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
            email.content_subtype = 'html'

            try:
                obj = models.Tokens.objects.get(user=user)
                obj.token = token
                obj.expiry_date = timezone.now() + timezone.timedelta(days=7)
                obj.save()
            except Exception as e:
                print(e)
                models.Tokens.objects.create(user=user, token=token, expiry_date=timezone.now() + timezone.timedelta(days=7))

            email.send()
        else:
            return JsonResponse({'response': 'error'})

    return redirect('login')


def reset_password(request, slug):
    return HttpResponse('Reset Password')
