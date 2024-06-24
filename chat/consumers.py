import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.files.base import ContentFile
from . models import ChatModel


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['friendship_id']
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()



    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )



    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print(data)
        await self.save_message(data)
        event = {
            'type': 'send_message',
            'message': data,
        }
        await self.channel_layer.group_send(self.room_group_name, event)



    async def send_message(self, event):
        data = event['message']
        await self.send(text_data=json.dumps({
            'message': data['message'],
            'sender_id': data['sender_id'],
            'timestamp': str(timezone.now()),
        }))

    @database_sync_to_async
    def save_message(self, data):
        try:
            existing_message = ChatModel.objects.filter(
                friendship_id=self.room_name,
                sender_id=data['sender_id'],
                message=data['message'],
                timestamp=timezone.now(),
                token=data['token']
            ).first()
            if not existing_message:
                ChatModel.objects.create(
                    friendship_id=self.room_name,
                    sender_id=data['sender_id'],
                    message=data['message'],
                    timestamp=timezone.now(),
                    token=data['token']
                )
        except Exception:
            pass


