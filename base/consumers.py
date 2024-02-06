# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Client

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def save_message(self, message, client):
        from Clients_and_Products.models import Message
        print(type(client))
        print(message)
        client_id = Client.objects.get(id=client)
        msg = Message.objects.create(client=client_id, content=message)
        print(client)
        return msg
    

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        client = text_data_json['client']

        try:
            await self.send(text_data=json.dumps({
                'message': message,
                'client':client
            }))
            msg = await self.save_message(message, client)
        except Exception as e:
            # Handle the exception appropriately, e.g., log the error
            print(f"Failed to save Message: {e}")

