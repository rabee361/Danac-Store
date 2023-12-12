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



class Clinet(models.Model):
    clinet = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Driver(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Representative(models.Model):
    representative = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Product(models.Model):
    nameproduct = models.CharField(max_length=50)



class Category(models.Model):
    pass


class Order(models.Model):
    pass

class Cart(models.Model):
    # get Items num
    pass

class Notifications(models.Model):
    pass