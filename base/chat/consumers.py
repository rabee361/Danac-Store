# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json
from base.models import *


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         try:
#             msg = await self.save_message(message)
#             await self.send(text_data=json.dumps({
#                 'message': message
#             }))
#         except Exception as e:
#             print(f"Failed to save Message: {e}")


#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     @database_sync_to_async
#     def save_message(self, message):
#         from .models import Message
#         msg = Message.objects.create(content=message)
#         return msg
    







# class ChatHandler(AsyncWebsocketConsumer):
# 	def connect(self):
# 		self.room_uuid = self.scope['url_route']['kwargs']['uuid']
# 		self.room_group_name = f'chat_{self.room_uuid}'

# 		async_to_sync(self.channel_layer.group_add)(
# 		    self.room_group_name, self.channel_name
# 		)
# 		self.accept()

# 	def receive(self, text_data):
# 		text_data_json = json.loads(text_data)
# 		message = text_data_json['message']
# 		user_id = self.scope['user'].user_id

# 		user = User.objects.get(user_id=user_id)

# 		msg = Message(author=user,content=message)
# 		msg.save()

# 		async_to_sync(self.channel_layer.group_send)(
# 		    self.room_group_name, {'type': 'chat_message', 'message': f'{user.username}: {message}'}
# 		)

# 	def disconnect(self, close_code):
# 		async_to_sync(self.channel_layer.group_discard)(
# 		    self.room_group_name, self.channel_name
# 		)

# 	def chat_message(self, event):
# 		message = event['message']
# 		self.send(text_data=json.dumps({'message': message}))