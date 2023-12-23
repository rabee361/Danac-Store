import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    barcode = django_filters.CharFilter(field_name="barcode", lookup_expr='iexact')

    class Meta: 
        model = Product
        fields = ['category','name','barcode']




class PointFilter(django_filters.FilterSet):
    is_used = django_filters.BooleanFilter(field_name="is_used")

    class Meta: 
        model = Product
        fields = ['is_used']

