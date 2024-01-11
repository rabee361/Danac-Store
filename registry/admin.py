from django.contrib import admin
from .models import *
from base.admin import *
# Register your models here.

admin.site.register(Deposite, DepositeAdmin)
admin.site.register(WithDraw, WithDrawAdmin)