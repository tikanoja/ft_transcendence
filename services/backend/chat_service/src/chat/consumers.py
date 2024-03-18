import json
import string

from channels.generic.websocket import AsyncWebsocketConsumer

tmp_user = ["MrSticks", "User"]
i = 0

class ClientConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        global i
        self.groups = [tmp_user[i], "Global"]
        i += 1
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()
        print(self.groups[0], " connected :O")

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data : str):
        packet = json.loads(text_data)

        message : str = packet["message"].strip(string.whitespace)
        if not message or len(message) > 255 or not message.isprintable():
            return

        target : str = "Global"
        if message.startswith("/w "):
            split = message.split(None, 2)
            if len(split) < 3:
                return 
            _, target, message = split
            if not target or not message:
                return
            
        await self.channel_layer.group_send(
            target,
            {
                "type": "chat.message",
                "message": "".join(["[", self.groups[0], "] ", message])
            }
        )

    async def chat_message(self, event):
        await self.send(text_data = json.dumps(event))
