import django_filters
from .models import Product ,Salary
from django_filters import rest_framework as filters
from datetime import datetime


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    barcode = django_filters.CharFilter(field_name="barcode", lookup_expr='iexact')
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta: 
        model = Product
        fields = ['category','name','barcode']



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