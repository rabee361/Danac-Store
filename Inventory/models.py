from django.db import models
from base.models import *
# Create your models here.

class Incoming(models.Model):
    products = models.ManyToManyField(Product, through='Incoming_Product')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    # agent = models.CharField(max_length=30)
    # num_truck = models.IntegerField(null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    code_verefy = models.IntegerField(null=True, blank=True)
    phonenumber = PhoneNumberField(region='DZ')
    recive_pyement = models.FloatField(blank=True, default=0)
    discount = models.FloatField(blank=True, default=0)
    Reclaimed_products = models.FloatField(blank=True, default=0)
    previous_depts = models.FloatField(blank=True, default=True)
    remaining_amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
        

class Incoming_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    incoming = models.ForeignKey(Incoming, on_delete=models.CASCADE)
    num_item = models.IntegerField()
    total_price = models.FloatField()

    def __str__(self) -> str:
        return f'{self.incoming.supplier.name}:{str(self.incoming.id)}'


class ManualReceipt(models.Model):
    products = models.ManyToManyField(Product, through='ManualReceipt_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    verify_code = models.IntegerField()
    phonenumber = PhoneNumberField(region='DZ')
    recive_payment = models.FloatField()
    # discount = models.FloatField()
    reclaimed_products = models.FloatField()
    previous_depts = models.FloatField()
    remaining_amount = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.client.name} - {str(self.id)}'
    
    # def get_remaining_amount(self):
    #     self.remaining_amount = (self.recive_payment + self.discount + self.reclaimed_products) - self.previous_depts
    #     self.save()
    
class ManualReceipt_Products(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    manualreceipt = models.ForeignKey(ManualReceipt, on_delete= models.CASCADE)
    discount = models.FloatField()
    num_item = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)

    def __str__(self) -> str:
        return f'{self.manualreceipt.client.name} - {str(self.manualreceipt.id)}'