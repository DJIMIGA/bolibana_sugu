from rest_framework import serializers
from cart.models import Cart, CartItem
from product.api.serializers import ProductListSerializer, PhoneSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = PhoneSerializer(read_only=True)
    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity',
            'colors', 'sizes', 'unit_price', 'total_price'
        ]

    def get_colors(self, obj):
        return [color.id for color in obj.colors.all()]

    def get_sizes(self, obj):
        return [size.id for size in obj.sizes.all()]

    def get_unit_price(self, obj):
        return float(obj.get_unit_price())

    def get_total_price(self, obj):
        return float(obj.get_total_price())


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    items = serializers.SerializerMethodField()  # Alias pour compatibilité mobile
    total_price = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'cart_items', 'items',
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_items(self, obj):
        """Alias pour cart_items pour compatibilité avec le frontend mobile"""
        return CartItemSerializer(obj.cart_items.all(), many=True, context=self.context).data

    def get_total_price(self, obj):
        return float(obj.get_total_price()) 