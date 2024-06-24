from django.db import models
from django.utils import timezone

from authentication.models import UserModel, Friendship


class ChatModel(models.Model):
    friendship = models.ForeignKey('authentication.Friendship', on_delete=models.CASCADE)
    sender = models.ForeignKey('authentication.UserModel', on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)
    token = models.CharField(max_length=255, blank=True, null=True)
    chat_picture = models.ImageField(upload_to='static/app/chat_pictures/', blank=True, null=True)
    chat_files = models.FileField(upload_to='static/app/chat_files/', blank=True, null=True)

    def __str__(self):
        if self.message:
            return self.message
        if self.chat_picture:
            return self.chat_picture.url
        if self.chat_files:
            return self.chat_files.name
        return "No message or file"

    class Meta:
        ordering = ('timestamp',)


class ActiveConnections(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255)

    def __str__(self):
        return self.user.firstname
