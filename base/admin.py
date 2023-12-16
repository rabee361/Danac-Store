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
admin.site.register(Point)
admin.site.register(Cart)
admin.site.register(Cart_Products)
admin.site.register(Notifications)
admin.site.register(Supplier)
admin.site.register(Incoming)
admin.site.register(Incoming_Products)
admin.site.register(Employee)
admin.site.register(Advance_On_salary)
admin.site.register(Absence)
admin.site.register(Discount)
admin.site.register(Bonus)

