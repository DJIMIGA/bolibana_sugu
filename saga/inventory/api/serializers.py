"""
Serializers pour l'API de l'app inventory
"""
from rest_framework import serializers
from inventory.models import (
    ExternalProduct,
    ExternalCategory
)


class ExternalProductSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    
    class Meta:
        model = ExternalProduct
        fields = [
            'id', 'external_id', 'external_sku', 'external_category_id',
            'sync_status', 'last_synced_at', 'sync_error',
            'product_title', 'product_slug'
        ]


class ExternalCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    
    class Meta:
        model = ExternalCategory
        fields = [
            'id', 'external_id', 'external_parent_id',
            'last_synced_at', 'category_name', 'category_slug'
        ]
