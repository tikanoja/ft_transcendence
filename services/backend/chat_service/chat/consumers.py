import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ClientConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.roomGroupName = "Global"
        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )

    async def receive(self, text_data : str):
        packet = json.loads(text_data)
        match packet["type"]:
            case "chat.message":
                await self.send(json.dumps({"message":"Got you fam", "username":"server"}))
            case _:
                await self.send(json.dumps({"message":"What is this D:", "username":"server"}))

#    async def sendMessage(self, event):
#        message  = event["message"]
#        username = event["username"]
#        await self.send(text_data = json.dumps({"message":message, "username":username}))
