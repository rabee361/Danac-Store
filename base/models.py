# from django.contrib.gis.db import models
from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum


class UserType(models.Model):
    user_type = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.user_type
    

class CustomUser(AbstractUser):
    email = models.EmailField(max_length=50, unique=True)
    phonenumber = PhoneNumberField(region='DZ',unique=True)
    username = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/users', null=True)
    address = models.CharField(max_length=100, default='one')
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',)
    
    objects = CustomManagers()

    def __str__(self):
        return self.username
    
    @property
    def inventory_manager(self):
        return self.user_type.user_type == 'مدير مخزن'
    
    @property
    def registry_manager(self):
        return self.user_type.user_type == 'مدير صندوق'
    
    @property
    def HR_manager(self):
        return self.user_type.user_type == 'مدير موارد بشرية'
    
    @property
    def order_manager(self):
        return self.user_type.user_type == 'مدير الطلبات'
    
    @property
    def sales_employee_manager(self):
        return self.user_type.user_type == 'مدير مندوبين'
    
    @property
    def manual_sales_manager(self):
        return self.user_type.user_type == 'مدير مبيعات يدوية'
    

class CodeVerivecation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.IntegerField(validators=[MinValueValidator(1000,9999),])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=10))

    def __str__(self) -> str:
        return f'{self.user.username} {self.code}'


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
    phonenumber = PhoneNumberField(region='DZ')
    info = models.TextField(null=True)

    def __str__(self):
        return self.name
    
    # location


class Points(models.Model):
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
    image = models.ImageField(upload_to='images/product')
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
        return str(self.id)
    
    class Meta:
        ordering = ['-added']

class Cart(models.Model):
    customer = models.ForeignKey(Client, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='Cart_Products')

    def __str__(self):
        return f'{self.customer} cart'
    

class Cart_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-products__added']

    def __str__(self):
        return self.cart.customer.name


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='Order_Product')
    total = models.IntegerField(default=0)
    products_num = models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    deliverd = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.client.name}: {self.id}'
    
class Order_Product(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField(default=0)

    def __str__(self) -> str:
        return f'{self.order.clinet.name} {str(self.order.id)}'




class Notifications(models.Model):
    pass


class Supplier(models.Model):
    name = models.CharField(max_length=30)
    company = models.CharField(max_length=50)
    phonenumber = PhoneNumberField(region='DZ')
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
    birth_date = models.DateField()
    phonenumber = PhoneNumberField(region='DZ')
    type_employee = models.CharField(max_length=20) 
    number_track = models.IntegerField(null=True)
    salery = models.FloatField()
    sale_perce = models.FloatField(null=True)
    address = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
class OverTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    num_hours = models.FloatField()
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name

class Absence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    days = models.IntegerField()
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    

class Bonus(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    

class Discount(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    

class Advance_On_salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    
class Extra_Expense(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    amount = models.FloatField()
    barcode = models.CharField(max_length=200,default=" ")
    date = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.employee.name


class Incoming(models.Model):
    products = models.ManyToManyField(Product, through='Incoming_Product')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    agent = models.CharField(max_length=30)
    num_truck = models.IntegerField(null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    code_verefy = models.IntegerField()
    phonenumber = PhoneNumberField(region='DZ')
    recive_pyement = models.FloatField()
    discount = models.FloatField()
    Reclaimed_products = models.FloatField(default=0)
    previous_depts = models.FloatField()
    remaining_amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
        

class Incoming_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    incoming = models.ForeignKey(Incoming, on_delete=models.CASCADE)
    num_item = models.IntegerField()
    total_price = models.FloatField()

    def all_item(self):
        pass
    def total(self):
        pass

    def __str__(self) -> str:
        return f'{self.incoming.supplier.name}:{str(self.incoming.id)}'


class ManualReceipt(models.Model):
    products = models.ManyToManyField(Product, through='ManualReceipt_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    verify_code = models.IntegerField()
    phonenumber = PhoneNumberField(region='DZ')
    recive_payment = models.FloatField()
    discount = models.FloatField()
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
    
class Expense(models.Model):
    expense_name = models.CharField(max_length=100)
    details = models.TextField(max_length=100)
    name =  models.CharField(max_length=50)
    amount = models.IntegerField()
    receipt_num = models.IntegerField()
    date = models.DateField(default=timezone.now) ######### new

    def __str__(self):
        return self.expense_name
    
    @classmethod
    def get_total_expenses(cls):
        return cls.objects.count()

    @classmethod
    def get_total_amount(cls):
        return cls.objects.aggregate(Sum('amount'))['amount__sum'] or 0
class Debt_Supplier(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )
    supplier_name = models.ForeignKey(Supplier,on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,default='_')
    check_num = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.supplier_name.name
    
    @classmethod
    def get_total_supplier_debts(cls):
        return cls.objects.count()
    
    @classmethod
    def get_total_sum(cls):
        return cls.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
class Debt_Client(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )
    client_name = models.ForeignKey(Client,on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,default='_')
    receipt_num = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.client_name

    @classmethod
    def get_total_client_debts(cls):
        return cls.objects.count()
    
    @classmethod
    def get_total_sum(cls):
        return cls.objects.aggregate(Sum('amount'))['amount__sum'] or 0


class Outputs(models.Model):
    products = models.ManyToManyField(Product, through='Outputs_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    verify_code = models.IntegerField()
    phonenumber = models.CharField(max_length=30, default='1212231243')
    recive_pyement = models.FloatField()
    discount = models.FloatField()
    Reclaimed_products = models.FloatField()
    previous_depts = models.FloatField()
    remaining_amount = models.FloatField()
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.id)
    
class Outputs_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    output = models.ForeignKey(Outputs, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.FloatField(default=0)
    discount = models.FloatField()

    def __str__(self) -> str:
        return f'{self.products.name} {self.output.id}'

class DelevaryArrived(models.Model):
    output_receipt = models.OneToOneField(Outputs, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.employee.name} - {str(self.output_receipt.id)}'
    
# --------------------------------------CREATE MEDIUM--------------------------------------

class Medium(models.Model):
    products = models.ManyToManyField(Product, through='Products_Medium')

    def __str__(self) -> str:
        return str(self.id)

class Products_Medium(models.Model):
    medium = models.ForeignKey(Medium, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.FloatField(default=0)
    num_item = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)

    def __str__(self) -> str:
        return f'{self.product.name} : {str(self.id)}'
    
    def add_item(self):
        self.num_item += 1
        self.total_price += self.product.sale_price
        self.save()
    
    def sub_item(self):
        self.num_item -= 1
        self.total_price -= self.product.sale_price
        self.save()

    @property
    def total_price_of_item(self):
        return (self.num_item * self.product.sale_price)
    
    def add_num_item(self):
        self.num_item  +=1
        self.save()
    
    # def get

# ------------------------------------------RETURNED GOODS------------------------------------------
        
class ReturnedGoodsSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier =  models.ForeignKey(Supplier, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    reason = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.product.name}:{self.reason}'
    
class ReturnedGoodsClient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client =  models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    reason = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.product.name}:{self.reason}'
    
# ------------------------------------------DAMAGED PRODUCTS------------------------------------------

class DamagedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()

    def __str__(self) -> str:
        return self.product.name

# ----------------------------------------------ORDER ENVOY----------------------------------------------

class OrderEnvoy(models.Model):
    client = models.CharField(max_length=50)
    phonenumber = PhoneNumberField(region='DZ')
    products = models.ManyToManyField(Product, through='Product_Order_Envoy')
    products_num = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    # is_accepted = models.BooleanField(null=True, default=False)
    delivered = models.BooleanField(null=True, default=False)

    # location = 

    def __str__(self) -> str:
        return f'{self.client} - {str(self.id)}'
    

class Product_Order_Envoy(models.Model):
    order_envoy = models.ForeignKey(OrderEnvoy, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # num_item = models.IntegerField(default=0)
    # total_price = models.FloatField(default=0)

    def __str__(self):
        return f'{self.product.name} - {str(self.order_envoy.id)}'

    

class MediumTwo(models.Model):
    products = models.ManyToManyField(Product, through='MediumTwo_Products')

    def __str__(self) -> str:
        return f'medium_two - {str(self.id)}'

class MediumTwo_Products(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    mediumtwo = models.ForeignKey(MediumTwo, on_delete=models.CASCADE)
    quantity = models.IntegerField(default= 0)
    # total_price = models.FloatField()

    def add_item(self):
        self.quantity += 1
        self.save()

    def sub_item(self):
        self.quantity -= 1
        self.save()

    def __str__(self) -> str:
        return f'{self.product.name} - {str(self.mediumtwo.id)}'