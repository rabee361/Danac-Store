from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    phonenumber = PhoneNumberField(region='DZ',unique=True)
    username = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',) 
    
    # objects = CustomManagers()

    def __str__(self):
        return self.username



class Client(models.Model):
    CHOICES = (
        ('سوبرماركت','سوبرماركت'),
        ('مقهى','مقهى'),
        ('محل جملة','محل جملة'),
        ('محل نصف جملة','محل نصف جملة')
    )
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    phonenumber = PhoneNumberField(region='DZ',default='+213876543232')
    category = models.CharField(max_length=75,choices=CHOICES,default=' ')
    location = models.PointField()

    def __str__(self):
        return self.name




class Driver(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class SalesEmployee(models.Model):
    representative = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # address = 
    # nots text
    # شاحنة
    


class Category(models.Model):
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/products')
    description = models.TextField(max_length=2000)
    quantity = models.IntegerField()
    purchasing_price = models.FloatField()
    category = models.ForeignKey(Category , on_delete=models.CASCADE)
    info = models.TextField(max_length=1000)
    limit = models.IntegerField()
    num_per_item = models.IntegerField()
    item_per_carton = models.IntegerField
    sale_price = models.IntegerField(default=50)
    added = models.DateTimeField(auto_now_add=True)
    # barcode
    class Meta:
        ordering = ['-added']


    def __str__(self):
        return self.name

    

class Cart(models.Model):
    customer = models.ForeignKey(Client , on_delete=models.CASCADE)
    items = models.ManyToManyField(Product ,through='Cart_Products')

    @property
    def get_items_num(self):
        return self.items.count()

    def __str__(self):
        return f'{self.customer} cart'



class Cart_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['products__added']





class Order(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total = models.IntegerField() 
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.client} : {self.id}'




class Notifications(models.Model):
    pass


class Supplier(models.Model):
    name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=50)
    phone_number = PhoneNumberField(region='DZ')
    address = models.CharField(max_length=100)
    info = models.TextField(max_length=500)

    def __str__(self):
        return self.name




class CodeVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])

    def __str__(self):
        return f'{self.user} code:{self.code}'



class Employee(models.Model):
    name = models.CharField(max_length=30)
    breath_date = models.DateField()
    phonenumber = PhoneNumberField(region='DZ')
    type_employee = models.CharField(max_length=20) 
    number_track = models.IntegerField()
    salery = models.FloatField()
    sale_perce = models.FloatField()
    address = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name



class Incoming(models.Model):
    product = models.ManyToManyField(Product, through='Incoming_Products')
    supplier = models.ForeignKey(Supplier,blank=True, on_delete=models.CASCADE)
    agent = models.CharField(max_length=30,blank=True)
    num_truck = models.IntegerField(null=True)
    employee = models.ForeignKey(Employee,blank=True, on_delete=models.CASCADE)
    code_verefy = models.IntegerField(null=True)
    recive_pyement = models.FloatField(null=True)
    discount = models.FloatField(null=True)
    # products_retrieved = models.CharField(max_length=100)
    previous_depts = models.FloatField(null=True)
    # remaining_amount = models.FloatField()

    def __str__(self):
        return f'incoming : {self.id}'
    
    
class Incoming_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    incoming = models.ForeignKey(Incoming, on_delete=models.CASCADE)
    # num_item = models.IntegerField()
    # purch_price = models.FloatField()

    def __str__(self) -> str:
        return f'{self.incoming.id} : {self.products.name}'
    
    @property
    def get_items_num(self):
        return self.products.count()
    