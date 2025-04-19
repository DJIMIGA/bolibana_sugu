from django_filters import rest_framework as filters
from product.models import Product

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category_slug = filters.CharFilter(field_name="category__slug")
    brand_slug = filters.CharFilter(field_name="brand__slug")

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category_slug', 'brand_slug', 'is_available'] 