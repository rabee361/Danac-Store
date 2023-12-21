from django.contrib import admin
from .models import *
from django.contrib.gis.admin import GISModelAdmin


@admin.register(Client)
class EstateAdmin(GISModelAdmin):
    list_display = ('location',)

admin.site.register(CodeVerification)
admin.site.register(CustomUser)
admin.site.register(SalesEmployee)
admin.site.register(Driver)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Order_Product)
admin.site.register(Point)
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
