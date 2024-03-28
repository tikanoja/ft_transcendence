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

        print(self.channel_layer.groups)

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

        print("user disconnected :D")
    
    async def receive(self, text_data):
        event: dict = json.loads(text_data)
        print("user sent:", event)

        if not "type" in event:
            logger.log("no event type defined")
            return

        match event["type"]:
            case "chat.message":
                if not "receiver" in event or not "message" in event:
                    print("no receiver or message? :c")
                    return
                event["sender"] = self.groups[0]
                print("sending")
                await self.channel_layer.group_send("Global", { "type" : "chat.msg", "message" : "WHAT THE FUCK"} )

            case _:
                print("what dis")
                return

    async def chat_msg(self, event):
        print(event)
        await self.send(text_data = json.dumps(event))
        
