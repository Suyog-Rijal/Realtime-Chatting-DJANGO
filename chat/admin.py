from django.contrib import admin
from .models import ChatModel


class ChatModelAdmin(admin.ModelAdmin):
    list_display = ('friendship', 'sender', 'message', 'timestamp', 'chat_picture', 'chat_files')
    list_filter = ('timestamp',)


admin.site.register(ChatModel, ChatModelAdmin)
