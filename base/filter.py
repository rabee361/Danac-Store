import django_filters
from .models import *
from Inventory.models import *

class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='startswith')

    class Meta:
        model = Product
        fields = ['category']

class ProductFilterName(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="name", lookup_expr='startswith')

    class Meta:
        model = Product
        fields = ['name']

class SupplierFilter(django_filters.FilterSet):
    class Meta:
        model = Supplier
        fields = ['name']

class ClietnFilter(django_filters.FilterSet):
    class Meta:
        model = Client
        fields = ['name']

class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee
        fields = ['name']

class IncomingFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(field_name="supplier__name", lookup_expr="startswith")
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Incoming
        fields = ['supplier', 'employee']

class OutputFilter(django_filters.FilterSet):
    client = django_filters.CharFilter(field_name='client__name', lookup_expr="startswith")
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Outputs
        fields = ['client', 'employee']

class ManualReceiptFilter(django_filters.FilterSet):
    client = django_filters.CharFilter(field_name='client__name', lookup_expr='startswith')
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = ManualReceipt
        fields = ['client', 'employee']

class OrderFilter(django_filters.FilterSet):
    client = django_filters.CharFilter(field_name='client__name', lookup_expr='startswith')

    class Meta:
        model = Order
        fields = ['client']

class OverTimeFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = OverTime
        fields = ['employee']

class AbsenceFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Absence
        fields = ['employee']

class BonusFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Bonus
        fields = ['employee']

class DiscountFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Discount
        fields = ['employee']

class Advance_On_salaryFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Advance_On_salary
        fields = ['employee']

class Extra_ExpenseFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Extra_Expense
        fields = ['employee']

class ExpenseFilter(django_filters.FilterSet):
    # employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = Expense
        fields = ['expense_name']

class Debt_SupplierFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(field_name='supplier_name__name', lookup_expr='startswith')

    class Meta:
        model = Debt_Supplier
        fields = ['supplier']

class Debt_ClietnFilter(django_filters.FilterSet):
    client = django_filters.CharFilter(field_name='client_name__name', lookup_expr='startswith')

    class Meta:
        model = Debt_Client
        fields = ['client']

class DelevaryArrivedFilter(django_filters.FilterSet):
    employee = django_filters.CharFilter(field_name='employee__name', lookup_expr='startswith')

    class Meta:
        model = DelevaryArrived
        fields = ['employee']

class ReturnedGoodsSupplierFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(field_name='supplier__name', lookup_expr='startswith')

    class Meta:
        model = ReturnedGoodsSupplier
        fields = ['supplier']

class ReturnedGoodsClientFilter(django_filters.FilterSet):
    client = django_filters.CharFilter(field_name='client__name', lookup_expr='startswith')

    class Meta:
        model = ReturnedGoodsClient
        fields = ['client']

class DamagedProductFilter(django_filters.FilterSet):
    product = django_filters.CharFilter(field_name='product__name', lookup_expr='startswith')

    class Meta:
        model = DamagedProduct
        fields = ['product']