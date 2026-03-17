from rest_framework import serializers
from price_checker.models import PriceSubmission, PriceEntry, City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'is_active']
        read_only_fields = ['id', 'slug']


class PriceSubmissionSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = PriceSubmission
        fields = [
            'id', 'product', 'product_title', 'city', 'city_name',
            'price', 'supplier_name', 'supplier_phone', 'supplier_address',
            'proof_image', 'status', 'validation_notes', 'created_at', 'validated_at',
        ]
        read_only_fields = ['id', 'status', 'validation_notes', 'created_at', 'validated_at']


class PriceEntrySerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = PriceEntry
        fields = [
            'id', 'product', 'product_title', 'city', 'city_name',
            'price', 'currency', 'supplier_name', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
