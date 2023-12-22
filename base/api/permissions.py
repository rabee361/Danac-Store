from rest_framework.permissions import BasePermission
from base.models import Employee


class IsManager(BasePermission):
    def has_permission(self, request, view):
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        return bool(request.user and request.user.user_type.user_type == employee.type_employee )
    
class IsDriver(BasePermission):
    def has_permission(self, request, view):
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        return bool(request.user and request.user.user_type == employee.type_employee)