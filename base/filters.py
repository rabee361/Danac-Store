import django_filters
from .models import Product


#----this method needs the exact genre name----#
class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')

    class Meta: 
        model = Product
        fields = ['category']


class ProductFilterName(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="name", lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['name']