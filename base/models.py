from django.db import models
from django.contrib.auth.models import AbstractUser
from api.managers import CustomManagers



class CustomUser(AbstractUser):
    phonenumber = models.IntegerField(unique=True)
    username = models.CharField(verbose_name="Username", max_length=200)
    is_verivecation = models.BooleanField(default=False)


    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',)
    
    objects = CustomManagers()



class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # categoru




class Driver(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class SalesEmployee(models.Model):
    representative = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # address = 
    # nots text
    # شاحنة
    



class Product(models.Model):
    name = models.CharField(max_length=50)
    iamge = models.ImageField()
    description = models.TextField(max_length=2000)
    quantity = models.IntegerField()
    purchasing_price = models.FloatField()
    # num_per_item
    # item_per_carton
    # category
    # nots text
    # limit 
    # barcode


    





class Category(models.Model):
    pass


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
    # name
    # company name
    # phone number
    # location
    # notes text
    pass
