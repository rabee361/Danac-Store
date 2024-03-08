from django.db import models, IntegrityError
from django.contrib.gis.db import models
from base.api.managers import CustomManagers
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.utils import timezone
from datetime import date
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.admin import display
import random
import string
from django.db.models import Sum, Count , Sum ,F , Q


def get_expiration_time():
    return timezone.now() + timedelta(minutes=10)

def get_expiration_date():
    return timezone.now() + timedelta(days=30)

def generate_barcode():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(8))
    return code


class UserType(models.Model):
    user_type = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.user_type


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=50, unique=True,null=True,blank=True)
    phonenumber = PhoneNumberField(region='DZ',unique=True)
    work_hours = models.CharField(max_length=100,null=True,blank=True)
    store_name = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=50 , null=True)
    town = models.CharField(max_length=100 , null=True)
    address = models.CharField(max_length=100 , null=True)
    username = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/users', null=True,default='images/account.jpg')
    location = models.PointField(default=Point(3.0589,36.7539),null=True,blank=True)
    user_type = models.ForeignKey(UserType,on_delete=models.CASCADE,null=True)
    is_accepted = models.BooleanField(default=False)

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ('username',) 

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
   
    objects = CustomManagers()

    def __str__(self):
        return self.username
    
    # @property
    # def inventory_manager(self):
    #     return self.user_type.user_type == 'مدير مخزن'
    # @property
    # def registry_manager(self):
    #     return self.user_type.user_type == 'مدير صندوق'
    
    # @property
    # def HR_manager(self):
    #     return self.user_type.user_type == 'مدير موارد بشرية'
    
    # @property
    # def order_manager(self):
    #     return self.user_type.user_type == 'مدير الطلبات'
    
    # @property
    # def sales_employee_manager(self):
    #     return self.user_type.user_type == 'مدير مندوبين'
    
    # @property
    # def manual_sales_manager(self):
    #     return self.user_type.user_type == 'مدير مبيعات يدوية'
    
    @property
    def type_client(self):
        return self.user_type.user_type == 'عميل'
    
    # # @property
    # # def type_client_or_sales_employee(self):
    # #     return self.user_type.user_type == 'عميل' or self.user_type.user_type == 'مندوب'




class State(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        return self.name




class Client(models.Model):
    CHOICES = (
        ('سوبرماركت','سوبرماركت'),
        ('مقهى','مقهى'),
        (' جملة',' جملة'),
        (' نصف جملة',' نصف جملة'),
        ('مطعم' ,'مطعم'),
        ('تجزئة' , 'تجزئة')
    )

    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100 , null=True)
    store_name = models.CharField(max_length=100 , null=True)
    phonenumber = PhoneNumberField(region='DZ')
    phonenumber2 = PhoneNumberField(region='DZ',null=True,blank=True)
    category = models.CharField(max_length=75,choices=CHOICES,default='سوبرماركت')
    notes = models.TextField(max_length=150,null=True,blank=True,default='_')
    location = models.PointField(default=Point(10,20),null=True)
    debts = models.FloatField(validators=[MinValueValidator(0.0)],default=0.0)

    class Meta:
        app_label = 'Clients_and_Products'
        ordering = ['-id']

    def __str__(self):
        return self.name
    
    def total_points(self):
        return Points.objects.filter(Q(client=self)&Q(is_used=False)&Q(expire_date__gt=timezone.now())).\
                                aggregate(total_points=models.Sum('number'))['total_points'] or 0

    def total_receipts(self):
        manuals = ManualReceipt.objects.filter(client=self).count()
        outputs = Output.objects.filter(client=self).count()
        total = manuals + outputs
        return total



class Points(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number = models.FloatField()
    expire_date = models.DateField(default=get_expiration_date)
    date = models.DateField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        app_label = 'Clients_and_Products'

    def __str__(self) -> str:
        return f'{self.client.name} {self.number}'



class UserNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.CharField(max_length=500)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return f'{self.user.username} : {self.body[:50]}'




######### delete
class CodeVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    code = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_time)

    def __str__(self):
        return f'{self.user.username} code:{self.code}'




class ProductType(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/product_types', null=True,default='images/account.jpg')

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-id']
        app_label = 'Clients_and_Products'

    def total_product_types(self):
        return ProductType.objects.count()




class Category(models.Model):
    product_type = models.ForeignKey(ProductType,on_delete=models.CASCADE)
    name = models.CharField(max_length=35)
    image = models.ImageField(upload_to='images/categories', null=True,default='images/account.jpg')

    class Meta:
        ordering = ['-id']
        app_label = 'Clients_and_Products'

    def __str__(self):
        return self.name

    def total_categories(self):
        return Category.objects.count()



class Product(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/products',null=True,blank=True,default='images/account.jpg')
    description = models.TextField(max_length=2000,null=True,blank=True)
    quantity = models.IntegerField()
    purchasing_price = models.FloatField()
    category = models.ForeignKey(Category , on_delete=models.CASCADE)
    notes = models.TextField(max_length=1000,null=True,blank=True)
    made_at = models.DateField(null=True,blank=True)
    expires_at = models.DateField(null=True,blank=True)
    limit_less = models.IntegerField()
    limit_more = models.IntegerField()
    num_per_item = models.IntegerField(blank=True,default=0)
    item_per_carton = models.IntegerField(blank=True,default=0)
    sale_price = models.IntegerField()
    added = models.DateTimeField(auto_now_add=True)
    barcode = models.CharField(max_length=200,default=generate_barcode,blank=True)
    points = models.IntegerField()

    class Meta:
        ordering = ['-added']
        app_label = 'Clients_and_Products'

    def __str__(self):
        return self.name
    


class Ad(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE ,blank=True, null=True)
    name = models.CharField(max_length=100)
    image_ad = models.ImageField(upload_to='images/ads')

    class Meta:
        app_label = 'Clients_and_Products'

    def __str__(self):
        return self.name
    
    
####################################CART HANDLING #######################################


class Cart_Products(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['products__added']
        app_label = 'Clients_and_Products'

    def add_item(self):
        self.quantity = self.quantity + 1
        self.save()

    def sub_item(self):
        self.quantity = self.quantity - 1
        self.save() 

    def total_price_of_item(self):
        return (self.quantity * self.products.sale_price)
    
    def total_points_of_item(self):
        return (self.quantity * self.products.points)

    def __str__(self):
        return f'{self.cart.customer} - {self.products.name} - {self.quantity}'




class Cart(models.Model):
    customer = models.ForeignKey(Client , on_delete=models.CASCADE)
    items = models.ManyToManyField(Product ,through='Cart_Products')
    barcode = models.CharField(max_length=200, default=generate_barcode)

    class Meta:
        app_label = 'Clients_and_Products'

    def save(self, *args, **kwargs):
        self.barcode = str(generate_barcode())
        super(Cart, self).save(*args, **kwargs)

    @property
    def get_items_num(self):
        return self.items.count()

    def total_cart_price(self):
        total = 0
        for item in self.cart_products_set.all():
            total += item.total_price_of_item()
        return total
    
    def total_cart_points(self):
        points = 0
        for item in self.cart_products_set.all():
            points += item.total_points_of_item()
        return points
    
    def create_order(self,date):
        
        order = Order.objects.create(
                client=self.customer,
                # total=0,
                # total_points=0,
                delivery_date=date,
                barcode=self.barcode
                )
        
        for item in self.cart_products_set.all():
                Order_Product.objects.create(
                product=item.products,
                order=order,
                quantity=item.quantity,
                total_price=item.total_price_of_item(),
                total_points=item.total_points_of_item()
            )
                # order.total += item.total_price_of_item()
                # order.total_points += item.total_points_of_item()
                # order.products_num += item.quantity
                order.save()
        self.items.clear()
        self.barcode = generate_barcode()
        self.save()
        return order

    def __str__(self):
        return f'{self.customer} cart'
    





class Order(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product,through='Order_Product')
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    delivered = models.BooleanField(null=True,default=False)
    barcode = models.CharField(max_length=200,null=True)
    shipping_cost = models.FloatField(default=0.0)
    client_service = models.CharField(max_length=20,default='000 208 0660')

    class Meta:
        app_label = 'Clients_and_Products'

    def total(self):
        return (self.total_price + self.shipping_cost)

    @property 
    def total_price(self):
        total_price = 0
        for item in self.order_product_set.all():
            total_price += item.total_price_of_item()
        return total_price
    
    def total_points(self):
        total_points = 0
        for item in self.order_product_set.all():
            total_points += item.total_points_of_item()
        return total_points

    def products_num(self):
        total_items =  0
        for item in self.order_product_set.all():
            total_items += item.quantity
        return total_items
    
    
    def __str__(self):
        return f'{self.client} : {self.id}'


class Order_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    total_points = models.IntegerField()

    class Meta:
        app_label = 'Clients_and_Products'
        
    def total_price_of_item(self):
        return (self.quantity * self.product.sale_price)
    
    def total_points_of_item(self):
        return (self.quantity * self.product.points)

    def __str__(self):
        return f'{self.order.client} - {self.product.name} - {self.quantity}'





##################################################################################################################


class Supplier(models.Model):
    name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=50)
    phone_number = PhoneNumberField(region='DZ')
    phone_number2 = PhoneNumberField(region='DZ',null=True,blank=True)
    address = models.CharField(max_length=100)
    info = models.TextField(max_length=500,null=True,blank=True,default='_')
    debts = models.FloatField(validators=[MinValueValidator(0.0)],default=0.0)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.name}'
    
    def total_receipts(self):
        return Incoming.objects.filter(supplier=self).count()






class Employee(models.Model):
    name = models.CharField(max_length=30)
    phonenumber = PhoneNumberField(region='DZ')
    job_position = models.CharField(max_length=20)
    truck_num = models.IntegerField(null=True,blank=True)
    location = models.PointField(default=Point(3.0589,36.7539))
    salary = models.FloatField()
    sale_percentage = models.FloatField(null=True,blank=True,default=0.0)
    address = models.CharField(max_length=100)
    notes = models.TextField(max_length=150,null=True,blank=True,default=' ')
    birthday = models.DateField()

    class Meta:
        ordering = ['-id']
        app_label = 'Human_Resources'

    def __str__(self):
        return f'{self.name}'







######################################## HR Department ##################################################################
    
class OverTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    num_hours = models.FloatField()
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'

    def __str__(self) -> str:
        return f'{self.employee.id}'

class Absence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    days = models.IntegerField()
    amount = models.FloatField()

    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'

    def __str__(self) -> str:
        return self.employee.name
    
class Bonus(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100,blank=True,null=True,default=' ')
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'

    def __str__(self) -> str:
        return self.employee.name
    

class Discount(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100,blank=True,null=True,default=' ')
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'

    def __str__(self) -> str:
        return self.employee.name
    


class Advance_On_salary(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    reason = models.CharField(max_length=100,blank=True,null=True,default=' ')
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.employee.name
    
    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'
    


class Extra_Expense(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    reason = models.TextField(max_length=100,blank=True,null=True,default=' ')
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'


class Salary(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, related_name='employee_salaries')
    employee_name = models.CharField(max_length=100)
    job_position = models.CharField(max_length=50)
    salary = models.FloatField()
    percentage = models.FloatField()
    hr = models.ForeignKey(Employee,on_delete=models.CASCADE, related_name='hr_employee_salaries')
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)
    overtime = models.FloatField(default=0.0)
    absence = models.FloatField(default=0.0)
    bonus = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    advances = models.FloatField(default=0.0)
    extra_expense = models.FloatField(default=0.0)
    total = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']
        app_label = 'Human_Resources'

    def __str__(self):
        return self.employee.name
    


################################### Register Department #######################################################

class Registry(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True)
    total = models.FloatField()

    def __str__(self):
        return f'{self.employee} Registry'
    
    class Meta:
        app_label = 'Company_Fund'



class WithDraw(models.Model):
    withdraw_name = models.CharField(max_length=50)
    details_withdraw = models.CharField(max_length=50,null=True,blank=True,default=' ')
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    total = models.FloatField()
    registry = models.ForeignKey(Registry,on_delete=models.CASCADE,null=True)
    verify_code = models.IntegerField(null=True,blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def __str__(self):
        return self.client.name
    
    def total_withdraws(self):
        return WithDraw.objects.count()
    
    def total_sum(self):
        return WithDraw.objects.aggregate(Sum('total'))['total__sum'] or 0



class Deposite(models.Model):
    deposite_name = models.CharField(max_length=50)
    detail_deposite = models.CharField(max_length=50,null=True,blank=True,default=' ')
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    total = models.FloatField()
    registry = models.ForeignKey(Registry,on_delete=models.CASCADE,null=True)
    verify_code = models.IntegerField(null=True,blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def __str__(self):
        return self.client.name
    
    def total_deposites(self):
        return Deposite.objects.count()
    
    def total_sum(self):
        return Deposite.objects.aggregate(Sum('total'))['total__sum'] or 0


    
class Debt_Client(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )   
    client_name = models.ForeignKey(Client,on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,null=True,blank=True,default='_')
    receipt_num = models.IntegerField(null=True,blank=True,unique=True)
    date = models.DateField(auto_now_add=True)
    added_to_registry = models.BooleanField(default=False)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def __str__(self):
        return self.client_name.name

    def total_client_debts(self):
        return Debt_Client.objects.count()
    
    def total_sum(self):
        return Debt_Client.objects.aggregate(Sum('amount'))['amount__sum'] or 0



class Debt_Supplier(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )
    supplier_name = models.ForeignKey(Supplier,on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,null=True,blank=True,default='_')
    receipt_num = models.IntegerField(null=True,blank=True,unique=True)
    date = models.DateField(auto_now_add=True)
    added_to_registry = models.BooleanField(default=False)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def __str__(self):
        return self.supplier_name.name
    
    def total_supplier_debts(self):
        return Supplier.objects.count()
    
    def total_sum(self):
        return Debt_Supplier.objects.aggregate(Sum('amount'))['amount__sum'] or 0



class Expense(models.Model):
    expense_name = models.CharField(max_length=100)
    details = models.TextField(max_length=100,null=True,blank=True,default=' ')
    name =  models.CharField(max_length=50)
    amount = models.IntegerField()
    receipt_num = models.IntegerField(null=True,blank=True,unique=True)
    date = models.DateField(auto_now_add=True)
    added_to_registry = models.BooleanField(default=False)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def __str__(self):
        return self.expense_name
    
    def total_expenses(self):
        return Expense.objects.count()

    def total_amount(self):
        return Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0



class Recieved_Payment(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,null=True,blank=True,default='_')
    receipt_num = models.IntegerField(null=True,blank=True,unique=True)
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)
    added_to_registry = models.BooleanField(default=False)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def total_recieved_payments(self):
        return Recieved_Payment.objects.count()

    def total_amount(self):
        return Recieved_Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0



class Payment(models.Model):
    CHOICES = (
        ('نقدا','نقدا'),
        ('بنك','بنك')
    )    
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=30,choices=CHOICES)
    bank_name = models.CharField(max_length=60,null=True,blank=True,default='_')
    receipt_num = models.IntegerField(null=True,blank=True,unique=True)
    amount = models.FloatField()
    date = models.DateField(auto_now_add=True)
    added_to_registry = models.BooleanField(default=False)

    class Meta:
        app_label = 'Company_Fund'
        ordering = ['-id']

    def total_payments(self):
        return Payment.objects.count()

    def total_amount(cls):
        return Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0








############################################-Returned & Damaged Goods-----###############################################################################
        
class ReturnedGoodsSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    reason = models.CharField(max_length=50,null=True,blank=True,default=' ')

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.product.name}:{self.reason}'
    


class ReturnedSupplierPackage(models.Model):
    supplier =  models.ForeignKey(Supplier, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    goods = models.ManyToManyField(ReturnedGoodsSupplier)
    date = models.DateField(auto_now_add=True,null=True)
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)

    def total_price(self):
        total_price = 0
        for i in self.goods.all():
            total_price += i.total_price
        return total_price

    def total_num(self):
        return self.goods.count()
    
    
    
class ReturnedGoodsClient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    reason = models.CharField(max_length=50,null=True,blank=True,default=' ')

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.product.name}:{self.reason}'



class ReturnedClientPackage(models.Model):
    client =  models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    goods = models.ManyToManyField(ReturnedGoodsClient)
    date = models.DateField(auto_now_add=True,null=True)
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)

    def total_price(self):
        total_price = 0
        for i in self.goods.all():
            total_price += i.total_price
        return total_price

    def total_num(self):
        return self.goods.count()


class DamagedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    total_price = models.FloatField()

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.product.name
    


class DamagedPackage(models.Model):
    goods = models.ManyToManyField(DamagedProduct)
    date = models.DateField(auto_now_add=True,null=True)
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)

    def total_price(self):
        total_price = 0
        for i in self.goods.all():
            total_price += i.total_price
        return total_price

    def total_num(self):
        return self.goods.count()




#########################################-------- Medium & Medium 2---------###########################################################

class Medium(models.Model):
    products = models.ManyToManyField(Product, through='Products_Medium')

    def __str__(self) -> str:
        return str(self.id)


class Products_Medium(models.Model):
    medium = models.ForeignKey(Medium, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(null=True,blank=True)
    num_item = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.product.name} : {str(self.id)}'
    
    @property
    def total_price_of_item(self):
        return (self.num_item * self.price)
    
    def add_num_item(self):
        self.num_item  +=1
        self.save()

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.product.sale_price
        super().save(*args, **kwargs)
    


class MediumTwo(models.Model):
    products = models.ManyToManyField(Product, through='MediumTwo_Products')

    def __str__(self) -> str:
        return f'medium_two - {str(self.id)}'


class MediumTwo_Products(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    mediumtwo = models.ForeignKey(MediumTwo, on_delete=models.CASCADE)
    quantity = models.IntegerField(default= 0)

    def add_item(self):
        self.quantity += 1
        self.save()

    def sub_item(self):
        self.quantity -= 1
        self.save()

    def __str__(self) -> str:
        return f'{self.product.name} - {str(self.mediumtwo.id)}'



############################################################################### INCOMING ################################################################


class Incoming(models.Model):
    serial = models.IntegerField(null=True,blank=True,editable=False)
    products = models.ManyToManyField(Product, through='Incoming_Product')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    client_service = models.CharField(max_length=20,default='000 208 0660')
    recive_pyement = models.FloatField()
    discount = models.FloatField(null=True,blank=True,default=0.0)
    Reclaimed_products = models.FloatField(null=True,blank=True,default=0.0)
    previous_depts = models.FloatField(null=True,blank=True,default=0.0)
    remaining_amount = models.FloatField(blank=True,default=0.0)
    date = models.DateTimeField(auto_now_add=True)
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)
    freeze = models.BooleanField(default=False)
    adjustment_applied = models.BooleanField(default=False) 

    class Meta:
        ordering=['-date']
        app_label = 'Receipts'

    def save(self, *args, **kwargs):
        if not self.id:
            today = timezone.now().date()
            last_instance = Incoming.objects.filter(date__date=today).order_by('-serial').first()

            if last_instance:
                if last_instance.date.date() != date.today():
                    self.serial = 1
                else:
                    self.serial = last_instance.serial + 1
            else:
                self.serial = 1
        super(Incoming, self).save(*args, **kwargs)

    def calculate_total_receipt(self):
        return self.incoming_product_set.aggregate(
            total_receipt=models.Sum('total_price')
        )['total_receipt'] or 0.0

    def __str__(self):
        return str(self.id)
        

class FrozenIncomingReceipt(models.Model):
    receipt = models.ForeignKey(Incoming,on_delete=models.CASCADE)
    reason = models.TextField()

    class Meta:
        app_label = 'Receipts'

    def __str__(self):
        return f'Manual Receipt {self.receipt.serial} reason: {self.reason}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.receipt.adjustment_applied:
            if self.receipt.freeze:
                self.adjust_product_quantities(True)
            else:
                self.adjust_product_quantities(False)
            self.receipt.adjustment_applied = True
            self.receipt.save()

    def adjust_product_quantities(self, freeze):
        for receipt_product in self.receipt.incoming_product_set.all():
            product = receipt_product.product
            if freeze:
                product.quantity += receipt_product.num_item
            else:
                product.quantity -= receipt_product.num_item
            product.save()



class Incoming_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    incoming = models.ForeignKey(Incoming, on_delete=models.CASCADE)
    num_item = models.IntegerField()
    total_price = models.FloatField()

    class Meta:
        ordering = ['-product_id']
        app_label = 'Receipts'

    # def save(self, *args, **kwargs):
    #     self.total_price = self.num_item * self.product.price
    #     super().save(*args, **kwargs)


    def __str__(self) -> str:
        return f'{self.incoming.supplier.name}:{str(self.incoming.id)}'

####################################### OUTPUT #################################################################################


class Output(models.Model):
    serial = models.IntegerField(null=True,blank=True,editable=False)
    products = models.ManyToManyField(Product, through='Output_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    client_service = models.CharField(max_length=20,default='000 208 0660')
    recive_pyement = models.FloatField()
    discount = models.FloatField(blank=True,default=0.0)
    Reclaimed_products = models.FloatField(blank=True,default=0.0)
    previous_depts = models.FloatField(blank=True,default=0.0)
    remaining_amount = models.FloatField(blank=True,default=0.0)
    date = models.DateTimeField(auto_now_add=True,null=True)
    shipping_cost = models.FloatField(default=0.0)
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)
    location = models.PointField(default=Point(3.0589,36.7539))
    delivered = models.BooleanField(default=False)
    freeze = models.BooleanField(default=False)
    adjustment_applied = models.BooleanField(default=False) 

    class Meta:
        ordering = ['-date']
        app_label = 'Receipts'

    def save(self, *args, **kwargs):
        if not self.id:
            today = timezone.now().date()
            last_instance = Output.objects.filter(date__date=today).order_by('-serial').first()

            if last_instance:
                if last_instance.date.date() != date.today():
                    self.serial = 1
                else:
                    self.serial = last_instance.serial + 1
            else:
                self.serial = 1
        super(Output, self).save(*args, **kwargs)

    def calculate_total_receipt(self):
        return self.output_products_set.aggregate(
            total_receipt=models.Sum('total_price')
        )['total_receipt'] or 0.0

    def __str__(self):
        return str(self.id)
    



class FrozenOutputReceipt(models.Model):
    receipt = models.ForeignKey(Output,on_delete=models.CASCADE)
    reason = models.TextField()

    class Meta:
        app_label = 'Receipts'

    def __str__(self):
        return f'Manual Receipt {self.receipt.serial} reason: {self.reason}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.receipt.adjustment_applied:
            if self.receipt.freeze:
                self.adjust_product_quantities(True)
            else:
                self.adjust_product_quantities(False)
            self.receipt.adjustment_applied = True
            self.receipt.save()

    def adjust_product_quantities(self, freeze):
        for receipt_product in self.receipt.output_products_set.all():
            product = receipt_product.product
            if freeze:
                product.quantity -= receipt_product.quantity
            else:
                product.quantity += receipt_product.quantity
            product.save()



class Output_Products(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    output = models.ForeignKey(Output, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    product_points = models.IntegerField()

    class Meta:
        ordering = ['-product_id']
        app_label = 'Receipts'

    def save(self, *args, **kwargs):
        self.product_points = self.quantity * self.product.points
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.product.name} {self.output.id}'



class DelievaryArrived(models.Model):
    output_receipt = models.OneToOneField(Output, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_delivered = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.employee.name} - {str(self.output_receipt.id)}'
    


####################################################### MANUAL RECEIPT #############################################################333333



class ManualReceipt(models.Model):
    serial = models.IntegerField(null=True,blank=True,editable=False)
    products = models.ManyToManyField(Product, through='ManualReceipt_Products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    client_service = models.CharField(max_length=20,default='000 208 0660')
    recive_payment = models.FloatField()
    discount = models.FloatField(null=True,blank=True,default=0.0)
    reclaimed_products = models.FloatField(null=True,blank=True,default=0.0)
    previous_depts = models.FloatField(null=True,blank=True,default=0.0)
    remaining_amount = models.FloatField(blank=True,default=0.0)
    date = models.DateTimeField(auto_now_add=True)
    barcode = models.CharField(max_length=200, default=generate_barcode, editable=False)
    freeze = models.BooleanField(default=False)
    adjustment_applied = models.BooleanField(default=False) 

    class Meta:
        ordering = ['-date']
        app_label = 'Receipts'


    def save(self, *args, **kwargs):
        if not self.id:
            today = timezone.now().date()
            last_instance = ManualReceipt.objects.filter(date__date=today).order_by('-serial').first()

            if last_instance:
                if last_instance.date.date() != date.today():
                    self.serial = 1
                else:
                    self.serial = last_instance.serial + 1
            else:
                self.serial = 1
        super(ManualReceipt, self).save(*args, **kwargs)


    def calculate_total_receipt(self):
        return self.manualreceipt_products_set.aggregate(
            total_receipt=models.Sum('total_price')
        )['total_receipt'] or 0.0

    def __str__(self) -> str:
        return f'{self.client.name} - {str(self.id)}'
    


class ManualReceipt_Products(models.Model): 
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    manualreceipt = models.ForeignKey(ManualReceipt, on_delete= models.CASCADE)
    price = models.FloatField()
    num_item = models.IntegerField()
    total_price = models.FloatField(default=0)
    product_points = models.IntegerField()

    class Meta:
        ordering = ['-product_id']
        app_label = 'Receipts'

    def save(self, *args, **kwargs):
        self.product_points = self.num_item * self.product.points
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.manualreceipt.client.name} - {str(self.manualreceipt.id)}'
    


class FrozenManualReceipt(models.Model):
    receipt = models.ForeignKey(ManualReceipt,on_delete=models.CASCADE)
    reason = models.TextField()

    class Meta:
        app_label = 'Receipts'

    def __str__(self):
        return f'Manual Receipt {self.receipt.serial} reason: {self.reason}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.receipt.adjustment_applied:
            if self.receipt.freeze:
                self.adjust_product_quantities(True)
            else:
                self.adjust_product_quantities(False)
            self.receipt.adjustment_applied = True
            self.receipt.save()

    def adjust_product_quantities(self, freeze):
        for receipt_product in self.receipt.manualreceipt_products_set.all():
            product = receipt_product.product
            if freeze:
                product.quantity -= receipt_product.num_item
            else:
                product.quantity += receipt_product.num_item
            product.save()













# ----------------------------------------------ORDER ENVOY----------------------------------------------

class OrderEnvoy(models.Model):
    client = models.CharField(max_length=50)
    address = models.CharField(max_length=100,default="address")
    phonenumber = PhoneNumberField(region='DZ')
    products = models.ManyToManyField(Product, through='Product_Order_Envoy')
    products_num = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)
    created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
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

    


    




################# Chat ##################

class Chat(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f'{self.id}'


class ChatMessage(models.Model):
    sender = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    employee = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} : "{self.content[0:20]}..."'

    class Meta:
        ordering=['-timestamp']

#########################################
    


