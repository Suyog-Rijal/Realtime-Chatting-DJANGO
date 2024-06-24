from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_view, name='login'),

    path('signup/', views.signup_view, name='signup'),
    path('ajax/validate_email/', views.validate_email, name='validate_email'),

    path('verify/', views.verify, name='verify'),
    path('send_verification_code/', views.send_verification_code, name='send_verification_code'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),

    path('reset/password/<str:slug>', views.reset_password, name='reset_password'),
]
