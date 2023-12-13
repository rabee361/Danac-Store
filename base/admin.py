from django.contrib import admin
from .models import *


admin.site.register(CustomUser)
admin.site.register(Client)
admin.site.register(SalesEmployee)
admin.site.register(Driver)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Notifications)
admin.site.register(Supplier)