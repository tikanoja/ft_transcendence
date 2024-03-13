import json

from channels.generic.websocket import AsyncWebsocketConsumer

tmp_user = ["MrSticks", "User"]
i = 0

class ClientConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.groups = [tmp_user[i], "Global"]
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()
        print(self.groups[0], " connected :O")

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data : str):
        print(text_data)
        packet = json.loads(text_data)
        await self.channel_layer.group_send(
            "Global",
            {
                "type": "chat.message",
                "message": "[" + self.groups[0] + "] " + packet["message"]
            }
        )

    async def chat_message(self, event):
        await self.send(text_data = json.dumps(event))
