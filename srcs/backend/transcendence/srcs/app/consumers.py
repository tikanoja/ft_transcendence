import logging
import builtins

from asgiref.sync import sync_to_async, async_to_sync

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer

from app.models import CustomUser
from app.user.relations import as_user_block_user

import app.play

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

        for group in [user.username, "Global"]:
            await self.channel_layer.group_add(group, self.channel_name)


    async def disconnect(self, close_code):
        user : CustomUser = self.scope["user"]

        for group in [user.username, "Global"]:
            await self.channel_layer.group_discard(group, self.channel_name)
    

    async def receive_json(self, content):
        user : CustomUser = self.scope["user"]

        if not user.is_authenticated or user.is_anonymous:
            return await self.close()

        try:
            match content["type"]:
                case "chat.broadcast":
                    content["sender"] = user.username
                    sanitized_content = {
                        "type" : content["type"],
                        "sender" : user.username,
                        "message" : content["message"]
                    }
                    await self.channel_layer.group_send("Global", sanitized_content)

                case "chat.whisper":
                    receiver = content["receiver"]
                    if not receiver in self.channel_layer.groups:
                        await self.error_response("User not reachable.")
                        return
                    content = {
                        "type" : content["type"],
                        "sender" : user.username,
                        "message" : content["message"]
                    }
                    await self.channel_layer.group_send(receiver, content)
                    if (receiver != user.username):
                        await self.channel_layer.group_send(user.username, content)

                case "chat.block":
                    name_to_block = content["username"]
                    blocked: CustomUser = await CustomUser.objects.aget(username=name_to_block)
                    await sync_to_async(as_user_block_user)(self.scope["user"], blocked)
                    await self.chat_system(name_to_block + " has been blocked.")

                case "chat.unblock":
                    user_to_unblock: CustomUser = await CustomUser.objects.aget(username=content["username"])
                    if (await user.blocked_users.filter(username=user_to_unblock).aexists()):
                        await user.blocked_users.aremove(user_to_unblock);
                        await user.asave()
                        await self.chat_system(user_to_unblock.username + " has been unblocked.")
                    else:
                        await self.chat_system(user_to_unblock.username + " isn't blocked!")

                case "chat.invite":
                    user_to_invite: CustomUser = await CustomUser.objects.aget(username=content["username"])
                    await sync_to_async(app.play.as_user_challenge_user)(user, user_to_invite, content["game"])
                    await self.chat_system(user_to_invite.username + " has been challenged.")

                case _:
                    print("Invalid event by user: ", self.scope["user"].username)

        except KeyError as e:
                await self.error_response("Content invalid.")
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
        await self.send_json(content)


    async def chat_system(self, content):
        match (content):
            case str(content):
                await self.send_json({
                    "type" : "chat.system",
                    "message" : content,
                })
            case dict(content):
                await self.send_json(content)
            case _: 
                print("Unknown dispatch type for chat.system")


    async def error_response(self, content : str):
        await self.send_json({
            "type" : "chat.error",
            "message" : content,
        });
