import asyncio
import logging
import json

from django.contrib.auth.models import User

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        user : User = self.scope["user"]
        if not user.is_authenticated or user.is_anonymous:
            return await self.close(code = 404)

        self.groups = [user.username, "Global"]
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)
    
    async def receive(self, text_data):
        event: dict = json.loads(text_data)

        event["source"] = self.scope["user"].username

        if not event["receiver"] in self.channel_layer.groups:
            await self.error_response("Not a valid recipient")

        await self.channel_layer.group_send(event["receiver"], event)

    async def chat_message(self, event : dict):
        await self.send(text_data = json.dumps(event))

    async def error_response(self, message : str):
        print("ERRR")
        await self.send(text_data = json.dumps({
            "type" : "chat.error",
            "message" : message
        }));
