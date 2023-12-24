from django.contrib import admin
from .models import *
from django.contrib.gis.admin import GISModelAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin



class AdminCustomUser(UserAdmin, admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    actions = ['accept_user']

    # def accept_user(self, request, queryset):
    #     queryset.update(is_active=True)
    #     user = queryset.get(is_active=True)
    #     rand_num = random.randint(1,10000)
    #     email_body = 'Hi '+user.username+' Use the code below to verify your email \n'+ str(rand_num)
    #     data = {'email_body':email_body, 'to_email':user.email, 'email_subject':'Verify your email'}
    #     Utlil.send_eamil(data)
    #     client = Client.objects.create(
    #         name=user.username,
    #         address = user.address,
    #         phonenumber = user.phonenumber
    #     )
    #     code_verivecation = random.randint(1000,9999)
    #     serializer = CodeVerivecationSerializer(data ={
    #             'user':user.id,
    #             'code':code_verivecation
    #         })
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     cart = Cart.objects.create(customer=client)
    #     cart.save()

    fieldsets = (
        (None, 
                {'fields':('phonenumber','email', 'password',)}
            ),
            ('User Information',
                {'fields':('username', 'first_name', 'last_name','location')}
            ),
            ('Permissions', 
                {'fields':('is_verified', 'is_staff', 'is_superuser', 'is_active', 'groups','user_permissions', 'user_type')}
            ),
            ('Registration', 
                {'fields':('date_joined', 'last_login',)}
        )
    )

    add_fieldsets = (
        (None, {'classes':('wide',),
            'fields':(
                'phonenumber','email','username', 'password1', 'password2'
            ),}
            ),
    )

    # # accept_user.short_descreption = 'Accept User For complet registration'
    # accept_user.short_descreption = 'print_user'


@admin.register(Client)
class EstateAdmin(GISModelAdmin):
    list_display = ('location',)

admin.site.register(UserType)
admin.site.register(CodeVerification)
admin.site.register(CustomUser,AdminCustomUser)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Order_Product)
admin.site.register(Points)
admin.site.register(Cart)
admin.site.register(Debt_Supplier)
admin.site.register(Debt_Client)
admin.site.register(Cart_Products)
admin.site.register(Notifications)
admin.site.register(Supplier)
admin.site.register(Registry)
admin.site.register(Employee)
admin.site.register(Advance_On_salary)
admin.site.register(Absence)
admin.site.register(OverTime)
admin.site.register(Discount)
admin.site.register(Bonus)
admin.site.register(Extra_Expense)
admin.site.register(WithDraw)
admin.site.register(Salary)
admin.site.register(Deposite)
admin.site.register(Medium)
admin.site.register(Products_Medium)
admin.site.register(ManualReceipt)
admin.site.register(Output)
admin.site.register(Output_Products)
admin.site.register(Incoming)
admin.site.register(Incoming_Product)
admin.site.register(ManualReceipt_Products)
admin.site.register(ReturnedGoodsSupplier)
admin.site.register(ReturnedGoodsClient)
admin.site.register(DamagedProduct)
admin.site.register(MediumTwo)
admin.site.register(MediumTwo_Products)
admin.site.register(Product_Order_Envoy)
admin.site.register(OrderEnvoy)
admin.site.register(Expense)