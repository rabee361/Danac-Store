# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json
from .models import *
from .api.serializers import *
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification


class CreateMessage(AsyncWebsocketConsumer):
	async def connect(self):
		self.chat_id = self.scope['url_route']['kwargs']['id']
		self.user_id = self.scope['url_route']['kwargs']['id2']
		messages = await self.get_chat_msgs(self.chat_id)
		await self.accept()

		# await self.send(text_data=json.dumps({
		# 	'message': 'hi'
		# }))

		for message in messages:
			await self.send(text_data=json.dumps(message))









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

		try:
			employee = await self.get_employee(user.phonenumber)
			# title = f'{serializer.data['sender']}'
			# body = f'{serializer.data['content']}'
			title = 'test'
			body = 'body'
			await self.send_to_client(chat,title,body)

		except:
			user_ids = await self.get_user_ids()
			devices = await self.get_devices(user_ids)
			title = 'test'
			body = 'test'
			self.send_to_all(devices)
			# for device in devices:
			# 	await device.send_message(
			# 		message=Message(
			# 			notification=Notification(
			# 				title=title,
			# 				body=body,
			# 				to=device.registration_id
			# 			),
			# 		),
			# 	)



		await self.send(text_data=json.dumps({
			'sender' : serializer.data['sender'],
			'content': serializer.data['content'],
			'timestamp': serializer.data['timestamp'],
			'employee': serializer.data['employee']
		}))



	@database_sync_to_async
	def send_to_client(self,chat,title,body):
		device = FCMDevice.objects.filter(user=chat.user)
		device.send_message(
			message=Message(
				notification=Notification(
					title=title,
					body=body
				),
			),
		)


	@database_sync_to_async
	def send_to_all(devices):
		for device in devices:
			device.send_message(
				message=Message(
					notification=Notification(
						title='title',
						body='body',
						to=device.registration_id
					),
				),
			)


	@database_sync_to_async
	def get_user_ids(self):
		return Employee.objects.values_list('id',flat=True)


	@database_sync_to_async
	def get_device(chat):
		return FCMDevice.objects.filter(user=chat.user)


	@database_sync_to_async
	def get_devices(self,user_ids):
		return FCMDevice.objects.filter(user__in=user_ids).values_list('registration_id', flat=True)



	@database_sync_to_async
	def get_chat_msgs(self,chat_id):
		messages = ChatMessage.objects.filter(chat=chat_id)
		serializer = MessageSerializer(messages,many=True)
		return serializer.data



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
