import django_filters
from .models import *
from django_filters import rest_framework as filters
from datetime import datetime


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    barcode = django_filters.CharFilter(field_name="barcode", lookup_expr='iexact')
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta: 
        model = Product
        fields = ['category','name','barcode']


class EmployeeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='startswith')
    job_position = django_filters.CharFilter(field_name='job_position', lookup_expr='iexact')

    class Meta:
        model = Employee
        fields = ['name','job_position']


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='startswith')
    company_name = django_filters.CharFilter(field_name='company_name', lookup_expr='startswith')

    class Meta:
        model = Supplier
        fields = ['name','company_name']


class ClientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='startswith')
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')

    class Meta:
        models = Client
        fields = ['name','category']


class SalesEmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee
        fields = ['name','truck_num']

############################### Registry #################################


class WithdrawFilter(django_filters.FilterSet):
    client_name = django_filters.CharFilter(field_name='client__name', lookup_expr='startswith')
    withdraw_name = django_filters.CharFilter(field_name='withdraw_name',lookup_expr='startswith')
    class Meta: 
        model = WithDraw
        fields = ['withdraw_name','client_name']


class DepositeFilter(django_filters.FilterSet):
    client_name = django_filters.CharFilter(field_name='client__name', lookup_expr='startswith')
    deposite_name = django_filters.CharFilter(field_name='deposite_name',lookup_expr='startswith')
    class Meta: 
        model = Deposite
        fields = ['deposite_name','client_name']


class ExpenseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='startswith')
    expense_name = django_filters.CharFilter(field_name='expense_name',lookup_expr='startswith')
    class Meta: 
        model = Expense
        fields = ['expense_name','name']


class Recieved_PaymentFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name',lookup_expr='startswith')
    class Meta:
        model = Recieved_Payment
        fields = ['employee_name']


class PaymentFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name',lookup_expr='startswith')
    class Meta:
        model = Payment
        fields = ['employee_name']


class DebtClientFilter(django_filters.FilterSet):
    client_name = django_filters.CharFilter(field_name='client_name', lookup_expr='startswith')
    class Meta: 
        model = Debt_Client
        fields = ['client_name']


class DebtSupplierFilter(django_filters.FilterSet):
    supplier_name = django_filters.CharFilter(field_name='supplier_name', lookup_expr='startswith')
    class Meta: 
        model = Debt_Supplier
        fields = ['supplier_name']



################################# HR #############################################
        
class MonthFilter(filters.Filter):
    def filter(self, qs, value):
        if value:
            date = datetime.strptime(value, "%Y-%m")
            return qs.filter(date__year=date.year, date__month=date.month)
        return qs

class SalaryFilter(django_filters.FilterSet):
    date = MonthFilter(field_name="date")

    class Meta: 
        model = Salary
        fields = ['date']



class OverTimeFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')
    class Meta: 
        model = OverTime
        fields = ['employee_name']


class AbsenceFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')
    class Meta: 
        model = Debt_Supplier
        fields = ['employee_name']


class DiscountFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')
    class Meta: 
        model = Discount
        fields = ['employee_name']


class BonusFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')
    class Meta: 
        model = Bonus
        fields = ['employee_name']


class Advance_On_salaryFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')
    class Meta: 
        model = Advance_On_salary
        fields = ['employee_name']


class Extra_ExpenseFilter(django_filters.FilterSet):
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')
    class Meta: 
        model = Extra_Expense
        fields = ['employee_name']