from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
from utils.db import get_collection

# Access the `messages` collection from the `users` database
messages_collection = get_collection('users', 'messages')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user'].username  # The current user
        receiver = self.room_name

        # Store the message in the database (MongoDB or SQL)
        messages_collection.insert_one({
            'sender': sender,
            'receiver': receiver,
            'content': message,
            'timestamp': datetime.now()
        })

        # Send the message to the room group (broadcasting it)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'timestamp': datetime.now().isoformat(),
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket (broadcasting the message to everyone in the group)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))
