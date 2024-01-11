from django.contrib import admin
from .models import *
from base.admin import *

# Register your models here.

admin.site.register(Incoming_Product, IncomingProductAdmin)
admin.site.register(Incoming, IncomingAdmin)
admin.site.register(ManualReceipt_Products, ManualReceiptProductAdmin)
admin.site.register(ManualReceipt, ManualReceiptAdmin)