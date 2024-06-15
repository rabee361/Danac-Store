# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json
from .models import *
from .serializers import *
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification


class CreateEmployeeMessage(AsyncWebsocketConsumer):
	async def connect(self):
		self.chat_id = self.scope['url_route']['kwargs']['chat_id']
		self.user_id = self.scope['url_route']['kwargs']['user_id']
		self.room_group_name = str(self.chat_id)
		messages = await self.get_chat_msgs(self.chat_id)


		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		# await self.accept()
		chat_owner = await self.get_chat_owner(self.chat_id)

		if chat_owner == int(self.user_id) or await self.is_employee(self.user_id):
			await self.accept()
		else:
			raise ValueError('this is not your chat')

	

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
			title = f'{user}'
			body = f'{message}'
			await self.send_to_client(chat,title,body)

		except:
			title = f'{user}'
			body = f'{message}'
			await self.send_to_all(title,body)


		# await self.send(text_data=json.dumps({
		# 	'sender' : serializer.data['sender'],
		# 	'content': serializer.data['content'],
		# 	'timestamp': serializer.data['timestamp'],
		# 	'employee': serializer.data['employee']
		# }))


		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type':'chat_message',
				'id' : serializer.data['id'],
				'sender' : serializer.data['sender'],
				'content': serializer.data['content'],
				'timestamp': serializer.data['timestamp'],
				'employee': serializer.data['employee'],				
				'chat': serializer.data['chat']				
			}
		)

	async def chat_message(self, event):
		id = event['id']
		content = event['content']
		sender = event['sender']
		timestamp = event['timestamp']
		employee = event['employee']
		chat = event['chat']
		await self.send(text_data=json.dumps({
			'id':id,
			'sender': sender,
			'content': content,
			'timestamp': timestamp,
			'employee': employee,
			'chat': chat
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
	def send_to_all(self,title,body):
		x = Employee.objects.values_list('phonenumber',flat=True)
		y = CustomUser.objects.filter(phonenumber__in=x).values_list('id',flat=True)
		devices = FCMDevice.objects.filter(user__in=y)
		for device in devices:
			device.send_message(
				message=Message(
					notification=Notification(
						title=title,
						body=body,
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
	def is_employee(self, user_id):
		user = CustomUser.objects.get(id=user_id)
		if Employee.objects.filter(phonenumber=user.phonenumber).exists():
			return True
		else:
			return False
		


	@database_sync_to_async
	def get_chat_msgs(self,chat_id):
		messages = ChatMessage.objects.filter(chat=chat_id).order_by('timestamp')
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
	def get_chat_owner(self, chat_id):
		chat = Chat.objects.get(id=chat_id)
		return int(chat.user.id)


	@database_sync_to_async
	def save_message(self, msg):
		msg.save()

	async def disconnect(self, close_code):
		pass










class CreateDriverMessage(AsyncWebsocketConsumer):
	async def connect(self):
		self.chat_id = self.scope['url_route']['kwargs']['chat_id']
		self.user_id = self.scope['url_route']['kwargs']['user_id']
		self.room_group_name = str(self.chat_id)
		messages = await self.get_chat_msgs(self.chat_id)


		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		await self.accept()


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
			msg = ChatMessage(sender=user,content=message, chat=chat, employee=False)
		except Employee.DoesNotExist:
			msg = ChatMessage(sender=user,content=message, chat=chat, employee=True)

		serializer = MessageSerializer(msg,many=False)
		await self.save_message(msg)

		try:
			employee = await self.get_employee(user.phonenumber)
			title = f'{user}'
			body = f'{message}'
			await self.send_to_client(chat,title,body)

		except:
			title = f'{user}'
			body = f'{message}'
			await self.send_to_all(title,body)


		# await self.send(text_data=json.dumps({
		# 	'sender' : serializer.data['sender'],
		# 	'content': serializer.data['content'],
		# 	'timestamp': serializer.data['timestamp'],
		# 	'employee': serializer.data['employee']
		# }))


		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type':'chat_message',
				'id' : serializer.data['id'],
				'sender' : serializer.data['sender'],
				'content': serializer.data['content'],
				'timestamp': serializer.data['timestamp'],
				'employee': serializer.data['employee'],				
				'chat': serializer.data['chat']				
			}
		)

	async def chat_message(self, event):
		id = event['id']
		content = event['content']
		sender = event['sender']
		timestamp = event['timestamp']
		employee = event['employee']
		chat = event['chat']
		await self.send(text_data=json.dumps({
			'id':id,
			'sender': sender,
			'content': content,
			'timestamp': timestamp,
			'employee': employee,
			'chat': chat
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
	def send_to_all(self,title,body):
		x = Employee.objects.values_list('phonenumber',flat=True)
		y = CustomUser.objects.filter(phonenumber__in=x).values_list('id',flat=True)
		devices = FCMDevice.objects.filter(user__in=y)
		for device in devices:
			device.send_message(
				message=Message(
					notification=Notification(
						title=title,
						body=body,
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
		messages = ChatMessage.objects.filter(chat=chat_id).order_by('timestamp')
		serializer = MessageSerializer(messages,many=True)
		return serializer.data




	@database_sync_to_async
	def get_employee(self,phonenumber):
		return Employee.objects.filter(phonenumber=phonenumber,truck_num__gt=0).first or None

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
