from collections import OrderedDict
from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http.request import HttpRequest
from .models import *
import random
from base.api.serializers import CodeVerivecationSerializer
# from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .froms import CustomUserCreationForm, CustomUserChangeForm


class AdminCustomUser(UserAdmin, admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    actions = ['accept_user', 'print_user']

    # def accept_user(self, request, queryset):
        

    def print_user(self, request, queryset):
        queryset.update(is_active=True)
        user = queryset.get(is_active=True)
        client = Client.objects.create(
            name=user.username,
            address = user.address,
            phomnenumber = user.phonenumber
        )
        code_verivecation = random.randint(1000,9999)
        serializer = CodeVerivecationSerializer(data ={
                'user':user.id,
                'code':code_verivecation
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cart = Cart.objects.create(customer=client)
        cart.save()

    fieldsets = (
        (None, 
                {'fields':('phonenumber', 'password',)}
            ),
            ('User Information',
                {'fields':('username', 'first_name', 'last_name',)}
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
                'phonenumber','username', 'password1', 'password2'
            ),}
            ),
    )

    # accept_user.short_descreption = 'Accept User For complet registration'
    print_user.short_descreption = 'print_user'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id']

class MediumAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(CodeVerivecation)
admin.site.register(CustomUser, AdminCustomUser)
admin.site.register(Client)
admin.site.register(SalesEmployee)
admin.site.register(Driver)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart)
admin.site.register(Cart_Products)
admin.site.register(Notifications)
admin.site.register(Supplier)
admin.site.register(Point)
admin.site.register(Employee)
# admin.site.register(Incoming)
admin.site.register(Incoming_Product)
admin.site.register(UserType)
admin.site.register(ManualReciept)
admin.site.register(ManualReciept_Products)
# admin.site.register(Medium, MediumAdmin)
admin.site.register(Outputs)
admin.site.register(Outputs_Products)
admin.site.register(Order_Product)
# admin.site.register(Medium_Incoming)
admin.site.register(Incoming)

# --------------------------------------CREATE MEDIUM--------------------------------------
admin.site.register(Medium)
admin.site.register(Products_Medium)
admin.site.register(DamagedProduct)
admin.site.register(ReturnedGoodsClient)
admin.site.register(ReturnedGoodsSupplier)