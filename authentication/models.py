from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class UserModel(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='static/app/profile_pictures/', default='static/app/profile_pictures/default.png')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    online_status = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def __str__(self):
        return self.email


class Tokens(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    token = models.CharField(max_length=200)
    expiry_date = models.DateTimeField()


class Friendship(models.Model):
    statusOptions = {
        'S': 'Sent',
        'B': 'Blocked',
        'A': 'Accepted',
        'D': 'Declined'
    }
    user_1 = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='user_1')
    user_2 = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='user_2')
    status = models.CharField(max_length=1, choices=statusOptions.items(), default='S')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_1.firstname + ' ---- ' + self.user_2.firstname
