import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        printf("yoooooooooo we here")
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # process user input (text_data dictionary) and update game state
        # send back the updated game state as JSON
        await self.send(text_data=json.dumps({'message': 'Your game state JSON here'}))
