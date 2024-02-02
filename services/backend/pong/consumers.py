from channels.generic.websocket import AsyncWebsocketConsumer
import logging
import json

logger = logging.getLogger(__name__)

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('New connect received')
        await self.accept()
        logger.info('New connection established')

    async def disconnect(self, close_code):
        logger.info('Dropped connection')
        pass

    async def receive(self, text_data):
        logger.info('Received msg')
        # process user input (text_data dictionary) and update game state
        # send back the updated game state as JSON
        await self.send(text_data=json.dumps({'message': 'Your game state JSON here'}))
