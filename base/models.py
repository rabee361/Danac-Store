from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
import uuid
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

class UserType(models.Model):
    user_type = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.user_type


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=50, unique=True)
    phonenumber = PhoneNumberField(region='DZ',unique=True)
    username = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/users', null=True)
    location = models.PointField(default=Point(0,0))
    user_type = models.ForeignKey(UserType,on_delete=models.CASCADE,null=True)

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',) 
    
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
    notes = models.TextField(max_length=150,default='note')
    location = models.PointField(null=True)

    def __str__(self):
        return f'{self.name}'




class CodeVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    code = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=10))

    def __str__(self):
        return f'{self.user.username} code:{self.code}'



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
    notes = models.TextField(max_length=1000)
    limit_less = models.IntegerField(default=0)
    limit_more = models.IntegerField(default=0)
    num_per_item = models.IntegerField()
    item_per_carton = models.IntegerField()
    sale_price = models.IntegerField(default=50)
    added = models.DateTimeField(auto_now_add=True)
    barcode = models.CharField(max_length=200,default=' ')
    class Meta:
        ordering = ['-added']

    def __str__(self):
        return self.name
    

    
    
##############################################CART HANDLING ###########################################################################################################


class Order(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product,through='Order_Product')
    total = models.IntegerField()
    products_num = models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    delivered = models.BooleanField(null=True,default=False)


    def __str__(self):
        return f'{self.client} : {self.id}'


class Order_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()

    def __str__(self):
        return f'{self.order.client} - {self.product.name} - {self.quantity}'



class Cart_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['products__added']

    def add_item(self):
        self.quantity = self.quantity + 1
        self.save()

    def sub_item(self):
        self.quantity = self.quantity - 1
        self.save() 

    def total_price_of_item(self):
        return (self.quantity * self.products.sale_price)

    def __str__(self):
        return f'{self.cart.customer} - {self.products.name} - {self.quantity}'




class Cart(models.Model):
    customer = models.ForeignKey(Client , on_delete=models.CASCADE)
    items = models.ManyToManyField(Product ,through='Cart_Products')

    @property
    def get_items_num(self):
        return self.items.count()

    def total_cart_price(self):
        total = 0
        for item in self.cart_products_set.all():
            total += item.total_price_of_item()
        return total
    
    def create_order(self,date):
        order = Order.objects.create(client=self.customer,total=0,delivery_date=date)
        for item in self.cart_products_set.all():
                Order_Product.objects.create(
                product=item.products,
                order=order,
                quantity=item.quantity,
                total_price=item.total_price_of_item()
            )
                order.total += item.total_price_of_item()
                order.products_num += item.quantity
                order.save()

        self.items.clear()
        return order

    def __str__(self):
        return f'{self.customer} cart'
    

    
##################################################################################################################



class Notifications(models.Model):
    pass


class Supplier(models.Model):
    name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=50)
    phone_number = PhoneNumberField(region='DZ')
    address = models.CharField(max_length=100)
    info = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.name}'






class Employee(models.Model):
    name = models.CharField(max_length=30)
    phonenumber = PhoneNumberField(region='DZ')
    job_position = models.CharField(max_length=20)
    truck_num = models.IntegerField(null=True)
    location = models.PointField(default=Point(0,0))
    salary = models.FloatField()
    sale_percentage = models.FloatField(null=True)
    address = models.CharField(max_length=100)
    notes = models.TextField(max_length=150,default=' ')
    birthday = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'




class Points(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number = models.FloatField()
    expire_date = models.DateField()
    date = models.DateField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.client.name} {self.number}'








######################################## HR Department ##################################################################
    
class OverTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE) #### drop down menu ?
    num_hours = models.FloatField() #### drop down menu ?
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.employee.id}'

class Absence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    days = models.IntegerField()
    amount = models.FloatField()

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
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    


class Extra_Expense(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    reason = models.TextField(max_length=100)
    amount = models.FloatField()
    barcode = models.CharField(max_length=200,default=" ")
    date = models.DateField(auto_now_add=True)


class Salary(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, related_name='employee_salaries')
    employee_name = models.CharField(max_length=100)
    job_position = models.CharField(max_length=50)
    salary = models.FloatField()
    percentage = models.FloatField()
    hr = models.ForeignKey(Employee,on_delete=models.CASCADE, related_name='hr_employee_salaries')
    barcode = models.CharField(max_length=200, default=uuid.uuid4, editable=False)
    overtime = models.FloatField(default=0.0)
    absence = models.FloatField(default=0.0)
    bonus = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    advances = models.FloatField(default=0.0)
    extra_expense = models.FloatField(default=0.0)
    total = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.employee.name
    


################################### Register Department #######################################################

class Registry(models.Model):
    total = models.FloatField()

    def __str__(self):
        return f'{self.total}'
    
    

class WithDraw(models.Model):
    details_withdraw = models.CharField(max_length=50)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    total = models.FloatField()
    verify_code = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.client.name
    
    @classmethod
    def get_total_withdraws(cls):
        return cls.objects.count()
    
    @classmethod
    def get_total_sum(cls):
        return cls.objects.aggregate(Sum('total'))['total__sum'] or 0



class Deposite(models.Model):
    detail_deposite = models.CharField(max_length=50)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    total = models.FloatField()
    verify_code = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.client.name
    
    @classmethod
    def get_total_deposites(cls):
        return cls.objects.count()
    
    @classmethod
    def get_total_sum(cls):
        return cls.objects.aggregate(Sum('total'))['total__sum'] or 0

    

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



class Recieved_Payment(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE)
    name = models.CharField(max_length=50)####### ???
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,default='_')
    receipt_num = models.IntegerField()
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)


class Payment(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )    
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE)
    name = models.CharField(max_length=50)####### ???
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,default='_')
    receipt_num = models.IntegerField()
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)






############################################-RETURNED GOODS-----###############################################################################
        
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

class DamagedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product.name
    






#########################################--------CREATE MEDIUM---------###########################################################

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
    






############################################################################### INCOMING ################################################################


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
    barcode = models.CharField(max_length=200, default=uuid.uuid4, editable=False)

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

####################################### OUTPUT #################################################################################


class Output(models.Model):
    products = models.ManyToManyField(Product, through='Output_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    verify_code = models.IntegerField()
    phonenumber = PhoneNumberField(region='DZ' ,default='+213672007698')
    recive_pyement = models.FloatField()
    discount = models.FloatField()
    Reclaimed_products = models.FloatField()
    previous_depts = models.FloatField()
    remaining_amount = models.FloatField()
    date = models.DateField(auto_now_add=True, null=True)
    barcode = models.CharField(max_length=200, default=uuid.uuid4, editable=False)
    location = models.PointField(default=Point(0.0,0.0))

    def __str__(self):
        return str(self.id)
    
class Output_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    output = models.ForeignKey(Output, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.FloatField(default=0)
    discount = models.FloatField()

    def __str__(self) -> str:
        return f'{self.products.name} {self.output.id}'

class DelievaryArrived(models.Model):
    output_receipt = models.OneToOneField(Output, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.employee.name} - {str(self.output_receipt.id)}'
    


####################################################### MANUAL RECEIPT #############################################################333333



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
    barcode = models.CharField(max_length=200, default=uuid.uuid4, editable=False)


    def __str__(self) -> str:
        return f'{self.client.name} - {str(self.id)}'
    

class ManualReceipt_Products(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    manualreceipt = models.ForeignKey(ManualReceipt, on_delete= models.CASCADE)
    discount = models.FloatField()
    num_item = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)

    def __str__(self) -> str:
        return f'{self.manualreceipt.client.name} - {str(self.manualreceipt.id)}'











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