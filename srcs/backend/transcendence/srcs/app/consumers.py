import logging

from asgiref.sync import sync_to_async, async_to_sync

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer

from app.models import CustomUser
from app.user.relations import as_user_block_user

logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()

def chat_system_message(user, message: str):
    if (channel_layer is not None):
        async_to_sync(channel_layer.group_send)(user.username, {
            "type" : "chat.system",
            "message" : message,
        })

class UserConsumer(AsyncJsonWebsocketConsumer):

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
    

    async def receive_json(self, content):
        user : CustomUser = self.scope["user"]

        if not user.is_authenticated or user.is_anonymous:
            return await self.close()

        try:
            match content["type"]:
                case "chat.broadcast":
                    if "message" not in content:
                        print("Chat broadcast event with missing fields by user: ", self.scope["user"].username)
                        return
                    content["sender"] = user.username
                    await self.channel_layer.group_send(self.groups[1], content)

                case "chat.whisper":
                    if "receiver" not in content or "message" not in content:
                        print("Chat message event with missing fields by user: ", self.scope["user"].username)
                        return

                    if not content["receiver"] in self.channel_layer.groups:
                        await self.error_response("No such user")
                        return

                    content["sender"] = user.username
                    await self.channel_layer.group_send(content["receiver"], content)
                    if (content["receiver"] != self.groups[0]):
                        await self.channel_layer.group_send(self.groups[0], content)

                case "chat.block":
                    name_to_block = content["username"]

                    blocked: CustomUser = await CustomUser.objects.aget(username=name_to_block)
                    await sync_to_async(as_user_block_user)(self.scope["user"], blocked)
                    await self.chat_system(name_to_block + " has been blocked")

                case "chat.unblock":
                    name_to_unblock: str = content["username"]
                    user_to_unblock = await CustomUser.objects.aget(username=name_to_unblock)
                    client: CustomUser = self.scope["user"]
                    await client.blocked_users.aremove(user_to_unblock);
                    await client.asave()

                    await self.chat_system(name_to_unblock + " has been unblocked")

                case "chat.invite":
                    user_to_unblock: CustomUser = await CustomUser.objects.aget(username=name_to_unblock)

                case _:
                    print("Invalid event by user: ", self.scope["user"].username)

        except Exception as e:
            if hasattr(e, "message"):
                await self.error_response(e.message)
            else:
                await self.error_response(str(e))


    async def chat_broadcast(self, content : dict):
        receiver : CustomUser = self.scope["user"]
        sender_name : str = content["sender"]

        if await receiver.blocked_users.filter(username=sender_name).aexists():
            return

        await self.send_json(content)


    async def chat_whisper(self, content : dict):
        receiver : CustomUser = self.scope["user"]
        sender_name : str = content["sender"]

        if await receiver.blocked_users.filter(username=sender_name).aexists():
            return

        del content["receiver"]

        await self.send_json(content)

    async def chat_system(self, content : str):
        await self.send_json({
            "type" : "chat.system",
            "message" : content
        })

    async def error_response(self, content : str):
        await self.send_json({
            "type" : "chat.error",
            "message" : content,
        });
