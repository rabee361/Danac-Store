from rest_framework.permissions import BasePermission
from base.models import Employee


class InventoryManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.inventory_manager)

    
class RegistryManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.registry_manager)
    
class HRManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.HR_manager)
    
class OrderManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.order_manager)
    
class SalesEmployeeManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.sales_employee_manager)
    
class ManualSalesManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.manual_sales_manager)
    
class Is_Client(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.type_client)
    
# class Is_Client_Or_Is_SalesEmployee(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.type_client_or_sales_employee)