from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField



class CustomUser(AbstractUser):
    phonenumber = PhoneNumberField(region='DZ',unique=True)
    username = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',) 
    
    objects = CustomManagers()

    def __str__(self):
        return self.username



class Client(models.Model):
    # user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    # location = 

    def __str__(self):
        return self.name




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
