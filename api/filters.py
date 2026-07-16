import django_filters
from rest_framework import filters
from .models import Product, Order


# Create My Filter
class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0)


# Customize Filter Product
class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'price':['exact', 'lt', 'gte', 'range'],
        }


# Customize Filter Order
class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date')
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at': ['exact', 'lt', 'gt']
        }




"""
تستخدم بشكل شائع Lookup أهم 
+-------------+--------------------------+
| Lookup      | المعنى                   |
+-------------+--------------------------+
| exact       | يساوي                    |
| iexact      | يساوي بدون حساسية للأحرف |
| contains    | يحتوي                    |
| icontains   | يحتوي بدون حساسية        |
| startswith  | يبدأ بـ                  |
| istartswith | يبدأ بـ بدون حساسية      |
| endswith    | ينتهي بـ                 |
| iendswith   | ينتهي بـ بدون حساسية     |
| gt          | أكبر من                  |
| gte         | أكبر أو يساوي            |
| lt          | أصغر من                  |
| lte         | أصغر أو يساوي            |
| in          | ضمن قائمة                |
| range       | بين قيمتين               |
| isnull      | هل القيمة Null           |
| year        | السنة                    |
| month       | الشهر                    |
| day         | اليوم                    |
+-------------+--------------------------+
"""
