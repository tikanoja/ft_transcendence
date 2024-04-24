import logging
import json

from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from app.user import CustomUser

logger = logging.getLogger(__name__)

def _has_keys(event: dict, keys):
    for key in keys:
        if not key in event:
            return False
    return True


class UserConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        user : CustomUser = self.scope["user"]
        if not user.is_authenticated or user.is_anonymous:
            return await self.close()

        self.groups = [user.username, "Global"]
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)


    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)
    

    async def receive(self, text_data):
        try:
            event: dict = json.loads(text_data)
        except:
            print("Invalid JSON sent by user: ", self.scope["user"].username)
            return
        
        match event["type"]:
            case "chat.broadcast":
                if not _has_keys(event, ["message"]):
                    print("Chat broadcast event with missing fields by user: ", self.scope["user"].username)
                    return

                event["sender"] = self.scope["user"].username

                await self.channel_layer.group_send(self.groups[1], event)

            case "chat.whisper":
                if not _has_keys(event, ["receiver", "message"]):
                    print("Chat message event with missing fields by user: ", self.scope["user"].username)
                    return

                if not event["receiver"] in self.channel_layer.groups:
                    await self.error_response("No such user")

                event["sender"] = self.scope["user"].username

                await self.channel_layer.group_send(event["receiver"], event)
                await self.channel_layer.group_send(self.groups[0], event)

            case _:
                print("Invalid event by user: ", self.scope["user"].username)


    async def chat_broadcast(self, event : dict):
        receiver : CustomUser = self.scope["user"]
        sender_name : str = event["sender"]

        if await receiver.blocked_users.filter(username=sender_name).aexists():
            return

        await self.send(text_data = json.dumps(event))


    async def chat_whisper(self, event : dict):
        receiver : CustomUser = self.scope["user"]
        sender_name : str = event["sender"]

        if await receiver.blocked_users.filter(username=sender_name).aexists():
            return

        del event["receiver"]

        await self.send(text_data = json.dumps(event))


    async def error_response(self, message : str):
        await self.send(text_data = json.dumps({
            "type" : "chat.error",
            "message" : message
        }));
