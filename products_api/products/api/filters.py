import django_filters

from products_api.products.models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    sku = django_filters.CharFilter(lookup_expr="iexact")
    description = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ["name", "description", "sku"]
