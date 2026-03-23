import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message
from student_app.models import Student
from teacher_app.models import TecherRegist 
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

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

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        username = self.scope["user"].username
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chatbox_message", "message": message, "username": username},
        )

    async def chatbox_message(self, event):
        message = event["message"]
        username = event["username"]

        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )

