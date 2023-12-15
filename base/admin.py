from collections import OrderedDict
from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from .models import *
import random
from base.api.serializers import CodeVerivecationSerializer


class AdminCustomUser(admin.ModelAdmin):
    actions = ['accept_user', 'print_user']

    def accept_user(self, request, queryset):
        queryset.update(is_active=True)

    def print_user(self, request, queryset):
        user = queryset.get(is_active=True)
        cline = Client.objects.create(
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
        print(code_verivecation)

        # self.opts.verbose_name='phonen'
    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     print(request.user.id)
    #     del actions['accept_user']
    #     return actions
    accept_user.short_descreption = 'Accept User For complet registration'
    print_user.short_descreption = 'print_user'


admin.site.register(CodeVerivecation)
admin.site.register(CustomUser, AdminCustomUser)
admin.site.register(Client)
admin.site.register(SalesEmployee)
admin.site.register(Driver)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Notifications)
admin.site.register(Supplier)
admin.site.register(Point)