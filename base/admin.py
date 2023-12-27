from django.contrib import admin
from .models import *
from leaflet.admin import LeafletGeoAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
import random
from base.api.utils import Utlil
from base.api.serializers import CodeVerivecationSerializer


admin.site.site_header = "Danac"
admin.site.index_title = "Welcome to Danac Admin Panel" 


class AdminCustomUser(UserAdmin, LeafletGeoAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_filter = ['is_accepted']
    actions = ['Accept_User', 'Refusal_User']
    list_display = ['id', 'email', 'is_staff', 'is_accepted']        

    def Accept_User(self, request, queryset):
        queryset.update(is_active=True) 
        user_type = UserType.objects.get(user_type='عميل')
        queryset.update(is_accepted=True, user_type=user_type)
        user = queryset.get(is_active=True)
        rand_num = random.randint(1,10000)
        client = Client.objects.create(
            name=user.username,
            address = "syria/homs",
            phonenumber = user.phonenumber,
        )
        code_verivecation = random.randint(1000,9999)
        # email_body = 'Hi '+user.username+' Use the code below to verify your email \n'+ str(code_verivecation)
        data= {'to_email':user.email, 'email_subject':'Verify your email','username':user.username, 'code': str(code_verivecation)}
        Utlil.send_eamil(data)
        serializer = CodeVerivecationSerializer(data ={
                'user':user.id,
                'code':code_verivecation,
                'expires_at' : timezone.now() + timedelta(minutes=10)
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cart = Cart.objects.create(customer=client)
        cart.save()

    def Refusal_User(self, request, queryset):
        user = queryset.get(is_accepted=False)
        email_body = 'Hi '+user.username+' نعتذر منك لقد تم رفض حسابك لأن موقعك بعيد ولا يمكن توصيل طلباتك \n'
        data = {'email_body':email_body, 'to_email':user.email, 'email_subject':'Refusal Account'}
        Utlil.send_eamil(data)
        user.delete()

    fieldsets = (
        (None, 
                {'fields':('phonenumber','email', 'password',)}
            ),
            ('User Information',
                {'fields':('username', 'first_name', 'last_name','image','location')}
            ),
            ('Permissions', 
                {'fields':('is_verified', 'is_accepted', 'is_staff', 'is_superuser', 'is_active', 'groups','user_permissions', 'user_type')}
            ),
            ('Registration', 
                {'fields':('date_joined', 'last_login',)}
        )
    )

    add_fieldsets = (
        (None, {'classes':('wide',),
            'fields':(
                'phonenumber','email' , 'username', 'password1', 'password2', 'user_type'
            ),}
            ),
    )

    # accept_user.short_descreption = 'Accept User For complet registration'
    # accept_user.short_descreption = 'print_user'

@admin.register(Client)
class ClientAdmin(LeafletGeoAdmin):
    list_display = ('id','name','location','address','phonenumber','category','notes')
    search_fields = ['name', 'phonenumber']
    list_filter =['category']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_client_name','products_num' ,'total' , 'delivery_date', 'delivered']
    search_fields = ['client__name',]
    list_filter = ['delivered']

    def get_client_name(self, obj):
        return obj.client.name
    get_client_name.short_description = 'Client Name'


class MediumAdmin(admin.ModelAdmin):
    list_display = ['id']


class ProductMediumAdmin(admin.ModelAdmin):

    list_display = ['id', 'get_name_product']
    def get_name_product(self, obj):
        return obj.product.name
    get_name_product.short_descreption = 'product'

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'quantity', 'purchasing_price', 'category', 'num_per_item', 'item_per_carton']

    search_fields = ['name']


class CategoryAdmin(admin.ModelAdmin):
    list_display= ['id', 'name']

class CodeVerivecationAdmin(admin.ModelAdmin):
    list_display = ['get_user_name', 'code', 'is_verified','created_at', 'expires_at']

    def get_user_name(self, obj):
        return obj.user.username
    get_user_name.short_descreption = 'username'


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phonenumber', 'salary', 'address', 'birthday']
    search_fields = ['name', 'phonenumber']
    # list_filter = ['type_employee']
    list_per_page = 25


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer']


class CartProductsAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name_product', 'cart', 'quantity']

    def get_name_product(self, obj):
        return obj.products.name
    get_name_product.short_descreption = 'product'


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'phone_number', 'address']
    search_fields = ['name', 'phonenumber']



class DamagedProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name_product', 'quantity', 'total_price']
    search_fields = ['product__name']
    def get_name_product(self, obj):
        return obj.product.name
    get_name_product.short_descreption = 'product'


class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_type']


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name_product', 'order', 'quantity', 'total_price']
    search_fields = ['order__client__name']
    list_per_page = 25
    def get_name_product(self, obj):
        return obj.product.name
    get_name_product.short_descreption = 'product'


class IncomingProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'employee', 'num_item', 'total_price']
    search_fields = ['incoming__employee__name']
    def name_product(self, obj):
        return obj.product.name
    
    def employee(self, obj):
        return obj.incoming.employee.name

    name_product.short_descreption = 'product_name'
    employee.short_descreption = 'employee'


class IncomingAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'agent', 'employee', 'code_verefy', 'recive_pyement', 'Reclaimed_products', 'remaining_amount', 'date']
    search_fields = ['supplier__name', 'employee__name']
    def get_name_supplier(self, obj):
        return obj.supplier.name
    
    def get_name_employee(self, obj):
        return obj.employee.name
    
    get_name_employee.short_descreption = 'employee'
    get_name_supplier.short_descreption = 'supplier'


class ManualReceiptProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'num_manul_receipt', 'name_client', 'discount', 'num_item', 'total_price']
    search_fields = ['manualreceipt__client__name']
    def name_product(self, obj):
        return obj.product.name
    def name_client(self, obj):
        return obj.manualreceipt.client.name
    def num_manul_receipt(self, obj):
        return obj.manualreceipt.id

class ManualReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'employee', 'verify_code', 'recive_payment', 'reclaimed_products', 'previous_depts', 'remaining_amount', 'date']
    search_fields = ['client__name', 'employee__name']


class OutputsproductAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'employee', 'verify_code', 'recive_pyement', 'discount', 'Reclaimed_products', 'previous_depts', 'remaining_amount', 'date']
    search_fields = ['client__name', 'employee__name']


class OutputProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'output', 'quantity', 'total', 'discount']

    def name_product(self, obj):
        return obj.products.name
    
    def num_output(self, obj):
        return obj.output.id


class DElevaryArrivedAdmin(admin.ModelAdmin):
    list_display = ['id', 'output_receipt', 'employee']


class ReturnedGoodsClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'client', 'employee', 'quantity', 'total_price', 'reason', 'date']
    search_fields = ['client__name']
    def name_product(self, obj):
        return obj.product.name
    

class ReturnedGoodsSupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'supplier', 'employee', 'quantity', 'total_price', 'reason', 'date']
    search_fields = ['supplier__name']
    def name_product(self, obj):
        return obj.product.name


class OrderEnvoyAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'phonenumber', 'products_num', 'total_price', 'created', 'delivery_date', 'delivered']
    list_filter = ['delivered']


class ProductOrderEnvoyAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_envoy', 'name_product']
    def name_product(self, obj):
        return obj.product.name



class OverTimeAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee' , 'num_hours' , 'amount' ,'date']
    search_fields = ['employee__name']
    list_per_page = 50

class AbsenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'date', 'days', 'amount']
    search_fields = ['employee__name']
    list_per_page = 50

class BounsAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee','reason', 'amount', 'date']
    search_fields = ['employee__name']
    list_per_page = 50


class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee','reason', 'amount', 'date']
    search_fields = ['employee__name']
    list_per_page = 50

class Advance_On_salaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee','reason', 'amount', 'date']
    search_fields = ['employee__name']
    list_per_page = 50

class Extra_ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee','reason', 'amount', 'barcode', 'date']
    search_fields = ['employee__name']
    list_per_page = 50

class DepositeAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'detail_deposite', 'total', 'verify_code', 'date']
    search_fields = ['client__name']
    list_per_page = 50

class WithDrawAdmin(admin.ModelAdmin):
    list_display = ['id', 'details_withdraw', 'client', 'total', 'verify_code', 'date']
    search_fields = ['client__name']
    list_per_page = 50

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'expense_name', 'details', 'name', 'amount', 'receipt_num', 'date']
    list_per_page = 50

class Debt_SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier_name', 'amount', 'payment_method', 'bank_name', 'check_num', 'date']
    search_fields = ['supplier_name__name']
    list_per_page = 50

class Debt_ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_name', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date']
    search_fields = ['client_name__name']
    list_per_page = 50

class PointsAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'number', 'expire_date', 'date', 'is_used']
    list_filter = ['is_used']
    search_fields= ['client__name']
    list_per_page = 50


class MediumTwoAdmin(admin.ModelAdmin):
    list_display = ['id', ]

class MediumTwo_ProductsAdmin(admin.ModelAdmin):
    list_display  = ['id', 'product', 'mediumtwo', 'quantity']
    search_fields = ['porduct__name']
    list_per_page = 50


class SalarAdmin(admin.ModelAdmin):
    list_display = ['employee_name','job_position','salary','percentage','date']
    search_fields = ['employee_name']
    list_per_page = 50


class RegistryAdmin(admin.ModelAdmin):
    list_display = ['total']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','employee', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date']
    search_fields = ['employee__name']
    list_per_page = 50

class Recieved_PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','employee', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date']
    search_fields = ['employee__name']
    list_per_page = 50


#### HR ####
admin.site.register(OverTime,OverTimeAdmin)
admin.site.register(Bonus,BounsAdmin)
admin.site.register(Advance_On_salary,Advance_On_salaryAdmin)
admin.site.register(Salary,SalarAdmin)
admin.site.register(Absence,AbsenceAdmin)
admin.site.register(Extra_Expense,Extra_ExpenseAdmin)
admin.site.register(Discount,DiscountAdmin)

#### Registry ####
admin.site.register(Registry,RegistryAdmin)
admin.site.register(WithDraw,WithDrawAdmin)
admin.site.register(Deposite,DepositeAdmin)
admin.site.register(Debt_Client,Debt_ClientAdmin)
admin.site.register(Debt_Supplier,Debt_SupplierAdmin)
admin.site.register(Expense,ExpenseAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Recieved_Payment,Recieved_PaymentAdmin)

##### Goods ###
admin.site.register(ReturnedGoodsClient, ReturnedGoodsClientAdmin)
admin.site.register(ReturnedGoodsSupplier, ReturnedGoodsSupplierAdmin)
admin.site.register(DamagedProduct, DamagedProductAdmin)

#### Medium ####
admin.site.register(Medium, MediumAdmin)
admin.site.register(Products_Medium,ProductMediumAdmin)
admin.site.register(MediumTwo,MediumTwoAdmin)
admin.site.register(MediumTwo_Products,MediumTwo_ProductsAdmin)

#### Rceipts ###
admin.site.register(Incoming_Product, IncomingProductAdmin)
admin.site.register(Incoming, IncomingAdmin)
admin.site.register(ManualReceipt_Products, ManualReceiptProductAdmin)
admin.site.register(ManualReceipt, ManualReceiptAdmin)
admin.site.register(Output, OutputsproductAdmin)
admin.site.register(Output_Products, OutputProductAdmin)
admin.site.register(DelievaryArrived, DElevaryArrivedAdmin)
admin.site.register(OrderEnvoy, OrderEnvoyAdmin)
admin.site.register(Product_Order_Envoy, ProductOrderEnvoyAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Order_Product, OrderProductAdmin)

### Users ###
admin.site.register(CodeVerification,CodeVerivecationAdmin)
admin.site.register(CustomUser, AdminCustomUser)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(UserType, UserTypeAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Points,PointsAdmin)

#### Cart & Products ####
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Cart_Products, CartProductsAdmin)

