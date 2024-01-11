from django.db import models
from base.models import *

# Create your models here.

class Deposite(models.Model):
    detail_deposite = models.CharField(max_length=50)
    client = models.ForeignKey(Client, on_delete= models.CASCADE)
    total = models.FloatField()
    verify_code = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.client.name

class WithDraw(models.Model):
    details_withdraw = models.CharField(max_length=50)
    client = models.ForeignKey(Client,on_delete=models.CASCADE, null=True)
    total = models.FloatField()
    verify_code = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.client.name