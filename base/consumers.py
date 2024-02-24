# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json
from .models import *
from .api.serializers import *


class CreateMessage(AsyncWebsocketConsumer):
	async def connect(self):
		self.chat_id = self.scope['url_route']['kwargs']['id']
		self.user_id = self.scope['url_route']['kwargs']['id2']
		await self.accept()

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		# user_id = text_data_json['user_id']
		# chat_id = text_data_json['chat_id']

		user = await self.get_user(self.user_id)
		chat = await self.get_chat(self.chat_id)

		try:
			await self.get_employee(user.phonenumber)
			msg = ChatMessage(sender=user,content=message, chat=chat, employee=True)
		except Employee.DoesNotExist:
			msg = ChatMessage(sender=user,content=message, chat=chat, employee=False)

		serializer = MessageSerializer(msg,many=False)
		await self.save_message(msg)

		await self.send(text_data=json.dumps({
			'sender' : serializer.data['sender'],
			'message': serializer.data['content'],
			'timestamp': serializer.data['timestamp'],
			'employee': serializer.data['employee']
		}))

	@database_sync_to_async
	def get_employee(self,phonenumber):
		return Employee.objects.get(phonenumber=phonenumber) or None

	@database_sync_to_async
	def get_user(self, user_id):
		return CustomUser.objects.get(id=user_id)

	@database_sync_to_async
	def get_chat(self, chat_id):
		return Chat.objects.get(id=chat_id)

	@database_sync_to_async
	def save_message(self, msg):
		msg.save()

	async def disconnect(self, close_code):
		pass
