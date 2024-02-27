from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class UserConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		logger.info('New connect received')
		await self.accept()
		logger.info('New connection established')

	async def disconnect(self, close_code):
		logger.info('Connection dropped')
		pass
	
	async def receive(self, text_data):
		logger.info(f'Received text_data: {text_data}')
		text_data_json = json.loads(text_data)
		await self.send(text_data=json.dumps({
			'type': 'connection established',
			'message': 'USER CONNECTED! :)'
		}))
