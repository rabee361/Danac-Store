from django.db import models
from django.contrib.auth.models import AbstractUser
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    phonenumber = PhoneNumberField(region='DZ', unique=True)
    username = models.CharField(max_length=200, unique=True)
    is_verivecation = models.BooleanField(default=False)


    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',)
    
    objects = CustomManagers()



class Client(models.Model):
    CHOICES = (
        ('سوبر ماركت', 'سوبر ماركت'),
        ('مقهى', 'مقهى'),
        ('محل جملة', 'محل جملة'),
        ('محل نصف جملة', 'محل نصف جملة'),
    )
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    category = models.CharField(max_length=75, choices=CHOICES)
    number = PhoneNumberField(region='DZ')
    info = models.TextField(null=True)
    # location






class Driver(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Representative(models.Model):
    representative = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # address = 
    # nots text
    # شاحنة
    

class Category(models.Model):
    name = models.CharField(max_length=20)


class Product(models.Model):
    name = models.CharField(max_length=50)
    iamge = models.ImageField()
    description = models.TextField(max_length=2000)
    quantity = models.IntegerField()
    purchasing_price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    num_per_item = models.IntegerField()
    item_per_carton = models.IntegerField()
    # num_per_item
    # item_per_carton
    # nots text
    # limit 
    # barcode



class Order(models.Model):
    # clinet 
    # number order 
    # num prodect
    # full price 
    # date
    # 
    pass



class Cart(models.Model):
    pass


class Notifications(models.Model):
    pass


class Supplier(models.Model):

    name = models.CharField(max_length=30)
    company = models.CharField(max_length=30)
    phonenumber =  PhoneNumberField(region='DZ')
    address = models.CharField(max_length=100)
    info = models.TextField()