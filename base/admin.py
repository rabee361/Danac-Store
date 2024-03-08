from django.contrib import admin
from .models import *
from leaflet.admin import LeafletGeoAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
import random
from base.api.utils import Utlil
from import_export.admin import ImportExportModelAdmin
from base.resources import ProductResource
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
styles = getSampleStyleSheet()



admin.site.site_header = "Danac"
admin.site.index_title = "Welcome to Danac Admin Panel" 






def export_to_pdf_reportlab(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recipes.pdf"'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Key-value pairs
    for op in queryset:
        elements.append(Paragraph(f"date: {op.output.date}", styles['Normal']))
        elements.append(Paragraph(f"Receipt num: {op.output.id}", styles['Normal']))
        elements.append(Paragraph(f"client name: {op.output.client.name}", styles['Normal']))
        elements.append(Paragraph(f"client service: {op.output.phonenumber}", styles['Normal']))
        elements.append(Paragraph(f"client phonenumber: {op.output.client}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Table data
        data = [
        [get_display(reshape('رقم المنتج')), get_display(reshape('اسم المنتج')), get_display(reshape('عدد الوحدات')), get_display(reshape('السعر')), get_display(reshape('الكمية')), get_display(reshape('المبلغ الإجمالي'))],  # Table header reshaped and reordered
            # Add table rows here for each ingredient in the recipe
        ]
        for item in Output_Products.objects.all():
            data.append([
                item.products.id,
                item.products.name,
                item.products.num_per_item,
                item.products.sale_price,
                item.products.quantity,
                item.total_price
            ])

        # Create the table with the data
        table = Table(data, colWidths=100)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(table)
        elements.append(PageBreak())  # Add a page break after each recipe

    # Build the PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

export_to_pdf_reportlab.short_description = "Export selected objects to PDF"








class AdminCustomUser(UserAdmin, LeafletGeoAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_filter = ['is_accepted']
    actions = ['Accept_User', 'Refusal_User']
    list_display = ['id', 'phonenumber','username', 'is_staff', 'is_accepted']    
    ordering = ['-id']

    def Accept_User(self, request, queryset):
        queryset.update(is_active=True)
        user_type = UserType.objects.get(user_type='عميل')
        queryset.update(is_accepted=True, user_type=user_type)
        user = queryset.get(is_active=True)
        client,created = Client.objects.get_or_create(
            name=user.username,
            phonenumber = user.phonenumber,
            location = user.location
        )
        client.address = f'{user.state}-{user.town}-{user.address}'
        client.save()
        cart,created = Cart.objects.get_or_create(customer=client)
        chat,created = Chat.objects.get_or_create(user=user)

        # rand_num = random.randint(1,10000)
        # code_verivecation = random.randint(1000,9999)
        # email_body = 'Hi '+user.username+' Use the code below to verify your email \n'+ str(code_verivecation)
        # data= {'to_email':user.email, 'email_subject':'Verify your email','username':user.username, 'code': str(code_verivecation)}
        # Utlil.send_email(data)
        # serializer = CodeVerivecationSerializer(data ={
        #         'user':user.id,
        #         'code':code_verivecation,
        #         'expires_at' : timezone.now() + timedelta(minutes=10)
        #     })
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # cart.save()


    def Refusal_User(self, request, queryset):
        user = queryset.get(is_accepted=False)
        # email_body = 'Hi '+user.username+' نعتذر منك لقد تم رفض حسابك لأن موقعك بعيد ولا يمكن توصيل طلبات إليه \n'
        # data = {'to_email':user.email, 'email_subject':'Account Refused','username':user.username}
        # Utlil.send_email2(data)
        user.delete()

    fieldsets = (
        (None, 
                {'fields':('phonenumber','email', 'password',)}
            ),
            ('User Information',
                {'fields':('username', 'first_name', 'last_name','image','location')}
            ),
            ('Permissions', 
                {'fields':('is_verified', 'is_accepted', 'is_staff', 'is_superuser', 'is_active', 'groups','user_permissions', 'user_type','address','state','town','store_name','work_hours')}
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


@admin.register(State)
class StateAdmin(LeafletGeoAdmin):
    list_display = ['name','location']
    search_fields = ['name']
    ordering = ['-id']


@admin.register(Client)
class ClientAdmin(LeafletGeoAdmin):
    list_display = ('id','name','category','phonenumber','address','notes')
    search_fields = ['name', 'phonenumber']
    list_filter =['category']
    ordering = ['-id']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_client_name','products_num' ,'total_price','shipping_cost','total' ,'total_points', 'delivery_date', 'delivered']
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


class ProductAdmin(ImportExportModelAdmin): 
    resource_class = ProductResource
    list_display = ['id', 'name', 'quantity', 'purchasing_price', 'points','category', 'num_per_item', 'item_per_carton']
    search_fields = ['name']


class CategoryAdmin(admin.ModelAdmin):
    list_display= ['id','name','product_type']


class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


class CodeVerivecationAdmin(admin.ModelAdmin):
    list_display = ['get_user_name', 'code', 'is_verified','created_at', 'expires_at']

    def get_user_name(self, obj):
        return obj.user.username
    get_user_name.short_descreption = 'username'


class EmployeeAdmin(LeafletGeoAdmin):
    list_display = ['id', 'name', 'phonenumber', 'salary', 'address', 'birthday']
    search_fields = ['name', 'phonenumber']
    # list_filter = ['type_employee']
    list_per_page = 25


class Cart_ProductsInline(admin.TabularInline):
    model = Cart_Products
    extra = 0
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


class CartAdmin(admin.ModelAdmin):
    inlines = [Cart_ProductsInline]
    list_display = ['id', 'customer']


class CartProductsAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name_product', 'cart', 'quantity']

    def get_name_product(self, obj):
        return obj.products.name
    get_name_product.short_descreption = 'product'


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'company_name', 'phone_number', 'address']
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
    list_display = ['id', 'get_name_product', 'order', 'quantity', 'total_price' , 'total_points']
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
    list_display = ['id', 'supplier', 'employee', 'recive_pyement', 'Reclaimed_products', 'remaining_amount', 'date','freeze']
    search_fields = ['supplier__name', 'employee__name']
    readonly_fields = ['serial']

    def get_name_supplier(self, obj):
        return obj.supplier.name
    
    def get_name_employee(self, obj):
        return obj.employee.name
    
    get_name_employee.short_descreption = 'employee'
    get_name_supplier.short_descreption = 'supplier'



class FreezeIncomingAdmin(admin.ModelAdmin):
    list_display = ['receipt','reason']
    class Meta:
        app_label = 'Receipts'



class ManualReceiptProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'num_manul_receipt', 'name_client', 'num_item', 'total_price']
    search_fields = ['manualreceipt__client__name']
    def name_product(self, obj):
        return obj.product.name
    def name_client(self, obj):
        return obj.manualreceipt.client.name
    def num_manul_receipt(self, obj):
        return obj.manualreceipt.id


class ManualReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'employee', 'discount','reclaimed_products', 'previous_depts', 'remaining_amount', 'date','freeze']
    search_fields = ['client__name', 'employee__name']
    readonly_fields = ['serial']

    class Meta:
        app_label = 'Receipts'
        admin_order = 1 


class FreezeManualAdmin(admin.ModelAdmin):
    list_display = ['receipt','reason']
    class Meta:
        app_label = 'Receipts'


class OutputsproductAdmin(LeafletGeoAdmin):
    list_display = ['id', 'client', 'employee', 'recive_pyement', 'discount', 'Reclaimed_products', 'previous_depts', 'remaining_amount', 'date','freeze']
    search_fields = ['client__name', 'employee__name']
    readonly_fields = ['serial']


class FreezeOutputAdmin(admin.ModelAdmin):
    list_display = ['receipt','reason']
    class Meta:
        app_label = 'Receipts'


class OutputProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'output', 'quantity', 'total_price', 'discount']
    actions = [export_to_pdf_reportlab]

    def name_product(self, obj):
        return obj.product.name
    
    def num_output(self, obj):
        return obj.output.id


class DElevaryArrivedAdmin(admin.ModelAdmin):
    list_display = ['id', 'output_receipt', 'employee']


class ReturnedGoodsClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'quantity', 'total_price', 'reason']
    def name_product(self, obj):
        return obj.product.name
    


class ReturnedClientPackageAdmin(admin.ModelAdmin):
    list_display = ['id','employee','date','barcode']

    

class ReturnedGoodsSupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_product', 'quantity', 'total_price', 'reason']
    def name_product(self, obj):
        return obj.product.name
    

class ReturnedSupplierPackageAdmin(admin.ModelAdmin):
    list_display = ['id','supplier','employee','date','barcode']



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
    list_display = ['id', 'employee','reason', 'amount', 'date']
    search_fields = ['employee__name']
    list_per_page = 50

class DepositeAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'detail_deposite', 'total', 'registry','verify_code', 'date']
    search_fields = ['client__name']
    list_per_page = 50

class WithDrawAdmin(admin.ModelAdmin):
    list_display = ['id', 'details_withdraw', 'client', 'total','registry', 'verify_code', 'date']
    search_fields = ['client__name']
    list_per_page = 50

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'expense_name', 'details', 'name', 'amount', 'receipt_num', 'date','added_to_registry']
    list_per_page = 50

class Debt_SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier_name', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date','added_to_registry']
    search_fields = ['supplier_name__name']
    list_per_page = 50

class Debt_ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_name', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date','added_to_registry']
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


class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee_name','job_position','salary','percentage','date']
    search_fields = ['employee_name']
    list_per_page = 50


class RegistryAdmin(admin.ModelAdmin):
    list_display = ['id','total']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','employee', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date','added_to_registry']
    search_fields = ['employee__name']
    list_per_page = 50

class Recieved_PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','employee', 'amount', 'payment_method', 'bank_name', 'receipt_num', 'date','added_to_registry']
    search_fields = ['employee__name']
    list_per_page = 50


#### HR ####
admin.site.register(OverTime,OverTimeAdmin)
admin.site.register(Bonus,BounsAdmin)
admin.site.register(Advance_On_salary,Advance_On_salaryAdmin)
admin.site.register(Salary,SalaryAdmin)
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
admin.site.register(ReturnedClientPackage,ReturnedClientPackageAdmin)
admin.site.register(ReturnedGoodsClient, ReturnedGoodsClientAdmin)
admin.site.register(ReturnedSupplierPackage,ReturnedClientPackageAdmin)
admin.site.register(ReturnedGoodsSupplier, ReturnedGoodsSupplierAdmin)
admin.site.register(DamagedPackage)
admin.site.register(DamagedProduct,DamagedProductAdmin)

#### Medium ####
admin.site.register(Medium, MediumAdmin)
admin.site.register(Products_Medium,ProductMediumAdmin)
admin.site.register(MediumTwo,MediumTwoAdmin)
admin.site.register(MediumTwo_Products,MediumTwo_ProductsAdmin)

#### Rceipts ###
admin.site.register(Incoming, IncomingAdmin)
admin.site.register(FrozenIncomingReceipt , FreezeIncomingAdmin)
admin.site.register(Incoming_Product, IncomingProductAdmin)
admin.site.register(ManualReceipt, ManualReceiptAdmin)
admin.site.register(FrozenManualReceipt , FreezeManualAdmin)
admin.site.register(ManualReceipt_Products, ManualReceiptProductAdmin)
admin.site.register(Output, OutputsproductAdmin)
admin.site.register(FrozenOutputReceipt , FreezeOutputAdmin)
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
admin.site.register(Ad)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductType,ProductTypeAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Cart_Products, CartProductsAdmin)

admin.site.register(UserNotification) 

admin.site.register(Chat)
admin.site.register(ChatMessage)
