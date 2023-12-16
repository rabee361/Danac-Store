# from django.contrib.gis.db import models
from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator


class UserType(models.Model):
    user_type = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.user_type
    

class CustomUser(AbstractUser):
    phonenumber = PhoneNumberField(region='DZ',unique=True)
    username = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/users', null=True)
    address = models.CharField(max_length=100, default='one')
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',)
    
    objects = CustomManagers()

    def __str__(self):
        return self.username
    
    # def tokens(self):
    #     refresh = RefreshToken.for_user(self)
    #     return {
    #         'refresh':str(refresh),
    #         'access':str(refresh.access_token)
    #     }

class CodeVerivecation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.IntegerField(validators=[MinValueValidator(1000,9999),])

    def __str__(self) -> str:
        return f'{self.user.username} {self.code}'


# class Client(models.Model):
#     # user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     name = models.CharField(max_length=30)
#     # location = 

class Client(models.Model):
    CHOICES = (
        ('سوبر ماركت', 'سوبر ماركت'),
        ('مقهى', 'مقهى'),
        ('محل جملة', 'محل جملة'),
        ('محل نصف جملة', 'محل نصف جملة'),
    )
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    category = models.CharField(max_length=75, choices=CHOICES, null=True)
    phomnenumber = PhoneNumberField(region='DZ')
    info = models.TextField(null=True)

    def __str__(self):
        return self.name
    
    # location


class Point(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number = models.FloatField()
    expire_date = models.DateField()
    date = models.DateField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.client.name} {self.number}'
    




class Driver(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class SalesEmployee(models.Model):
    representative = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # address = 
    # nots text
    # شاحنة
    

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    iamge = models.ImageField(upload_to='images/product')
    description = models.TextField(max_length=2000)
    quantity = models.IntegerField()
    purch_price = models.FloatField()
    sale_price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    num_per_item = models.IntegerField()
    item_per_carton = models.IntegerField()
    limit = models.IntegerField()
    info = models.TextField(max_length=1000)
    added = models.DateTimeField(auto_now_add=True)
    # barcode

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-added']

class Cart(models.Model):
    customer = models.ForeignKey(Client, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='Cart_Products')

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
        ordering = ['-products__added']

    @property
    def add_item(self):
        self.quantity += self.quantity  
        self.save()

    @property
    def sub_item(self):
        self.quantity -= self.quantity
        self.save()

    def __str__(self):
        return self.cart.customer.name





class Order(models.Model):
    clinet = models.ForeignKey(Client, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='productss')
    total = models.IntegerField()
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    deliverd = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.clinet.name}: {self.id}'
    # number order 
    # num prodect
    # full price 
    # date
    # 
    pass




class Notifications(models.Model):
    pass


class Supplier(models.Model):
    name = models.CharField(max_length=30)
    company = models.CharField(max_length=50)
    phonenubmer = PhoneNumberField(region='DZ')
    address = models.CharField(max_length=100)
    info = models.TextField(max_length=500)

    def __str__(self) -> str:
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name
    

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
    
class OverTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    num_hours = models.FloatField()
    deserved_amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name

class Absence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    num_absence = models.IntegerField()
    amoumt_deducted = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    

class Award(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason_award = models.CharField(max_length=100)
    total = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    

class Discount(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason_discount = models.CharField(max_length=100)
    total = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    

class Advance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason_advance = models.CharField(max_length=100)
    total = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    
class ExtraExpense(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason_expense = models.CharField(max_length=100)
    total = models.FloatField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.employee.name


# class Incoming(models.Model):
#     products = models.ManyToManyField(Product, through='Incoming_Products')
#     supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
#     agent = models.CharField(max_length=30)
#     num_truck = models.IntegerField(null=True)
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     code_verefy = models.IntegerField()
#     recive_pyement = models.FloatField()
#     discount = models.FloatField()
#     # Reclaimed_products = models.CharField(max_length=100)
#     previous_depts = models.FloatField()
#     # remaining_amount = models.FloatField()

#     def __str__(self):
#         return str(self.id)
    
# class Incoming_Products(models.Model):
#     products = models.ForeignKey(Product, on_delete=models.CASCADE)
#     incoming = models.ForeignKey(Incoming, on_delete=models.CASCADE)
#     # num_item = models.IntegerField()
#     # purch_price = models.FloatField()
#     quantity = models.IntegerField()

#     def __str__(self) -> str:
#         return self.incoming.supplier.name
#     @property
#     def get_items_num(self):
#         return self.products


class ManualReciept(models.Model):
    products = models.ManyToManyField(Product, through='ManualReciept_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    verify_code = models.IntegerField()
    phonenumber = PhoneNumberField(region='DZ')
    recive_pyement = models.FloatField()
    Reclaimed_products = models.FloatField()
    previous_debts = models.FloatField()
    remaining_amount = models.FloatField()

    def __str__(self) -> str:
        return self.client.name
    
class ManualReciept_Products(models.Model):
    products = models.ForeignKey(Product, on_delete= models.CASCADE)
    manualreciept = models.ForeignKey(ManualReciept, on_delete= models.CASCADE)
    quantity = models.IntegerField()
    discount = models.FloatField()

    def __str__(self) -> str:
        return str(self.id)




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
    name_user = models.CharField(max_length= 30)
    total = models.FloatField()
    verify_code = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name_user
    
class Expence(models.Model):
    detail_expence = models.CharField(max_length=50)
    name_user = models.CharField(max_length=30)
    total = models.FloatField()
    num_reciept = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name_user
    
class DeptsSuppliers(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    recive_pyement = models.FloatField()
    pyement_method = models.CharField(max_length=10)
    name_bank = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.supplier.name
    
class DeptsClients(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    recive_pyement = models.FloatField()
    pyement_method = models.CharField(max_length=10)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.client.name





