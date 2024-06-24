import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from authentication.models import UserModel
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
        event = {
            'type': 'chat_message',
            'message': data['message'],
            'sender_id': data['sender_id'],
            'token': data['token']
        }

        await self.channel_layer.group_send(self.room_group_name, event)

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'token': event['token']
        }))

    @database_sync_to_async
    def save_message(self, data):
        pass
        # Save the message to the database
        # ChatModel.objects.create(
        #     friendship_id=self.room_name,
        #     sender_id=data['sender_id'],
        #     message=data['message'],
        #     timestamp=timezone.now(),
        #     token=data['token']
        # )




