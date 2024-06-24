from django.urls import path
from . import views


urlpatterns = [
    path('', views.base, name='base'),
    path('chat/', views.chat, name='chat'),
    path('ajax/laod_chat/', views.load_chat, name='load_chat'),
    path('ajax/chat_receive_image/', views.chat_receive_image, name='chat_receive_image'),
    path('ajax/chat_receive_file/', views.chat_receive_file, name='chat_receive_file'),

    path('ajax/sidebar/', views.sidebar_handler, name='sidebar'),

    path('ajax/add_friend_search/', views.add_friend_search, name='add_friend_search'),
    path('ajax/add_friend_search_add_message/', views.add_friend_search_add_message, name='add_friend_search_add_message'),
    path('ajax/add_friend_request_handler/', views.add_friend_request_handler, name='add_friend_request_handler'),
    path('ajax/sent/receiver/', views.sent_receiver, name='sent_receiver'),

    path('ajax/settings/email_check/', views.settings_email_check, name='settings_email_check'),
    path('ajax/settings/save', views.settings_save, name='settings_save'),
    path('ajax/settings/password_change', views.settings_password_change, name='settings_password_change'),
    path('ajax/settings/settings_profile_picture', views.settings_profile_picture, name='settings_profile_picture'),
    path('ajax/settings_delete_account', views.settings_delete_account, name='settings_delete_account'),
]
