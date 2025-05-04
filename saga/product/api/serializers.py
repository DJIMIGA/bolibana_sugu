from rest_framework import serializers
from product.models import Product, Category, ImageProduct, Phone



class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduct
        fields = ['id', 'image', 'alt_text', 'is_feature']



class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    feature_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'category', 'brand', 'feature_image',
            'is_available', 'created_at'
        ]

    def get_feature_image(self, obj):
        feature_image = obj.images.filter(is_feature=True).first()
        if feature_image:
            return ProductImageSerializer(feature_image).data
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'category', 'brand',
            'images', 'variants', 'stock',
            'is_available', 'created_at', 'updated_at',
            'specifications', 'weight', 'dimensions'
        ]

class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['id', 'color', 'storage', 'price', 'stock', 'sku'] 