from django.db import models
from base.models import Client
# Create your models here.

class Message(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='chat_user')
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meat:
        app_label = 'Clients_and_Products'