from rest_framework import serializers
from cart.models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from product.api.serializers import ProductDetailSerializer, PhoneSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    variant = PhoneSerializer(read_only=True)
    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    is_weighted = serializers.SerializerMethodField()
    weight_unit = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity',
            'colors', 'sizes', 'unit_price', 'total_price',
            'is_weighted', 'weight_unit'
        ]

    def get_colors(self, obj):
        return [color.id for color in obj.colors.all()]

    def get_sizes(self, obj):
        return [size.id for size in obj.sizes.all()]

    def get_unit_price(self, obj):
        return float(obj.get_unit_price())

    def get_total_price(self, obj):
        return float(obj.get_total_price())

    def _get_specs(self, obj):
        if not obj.product or not getattr(obj.product, 'specifications', None):
            return {}
        if not isinstance(obj.product.specifications, dict):
            return {}
        return obj.product.specifications

    def get_is_weighted(self, obj):
        specs = self._get_specs(obj)
        sold_by_weight = specs.get('sold_by_weight')
        is_sold_by_weight = sold_by_weight is True or (
            isinstance(sold_by_weight, str) and sold_by_weight.lower() in ['true', '1', 'yes']
        )
        unit_type = str(specs.get('unit_type') or '').lower()
        weight_unit = str(specs.get('weight_unit') or '').lower()
        unit_display = str(specs.get('unit_display') or '').lower()
        has_weight_pricing = (
            specs.get('price_per_kg') is not None
            or specs.get('discount_price_per_kg') is not None
            or specs.get('available_weight_kg') is not None
            or specs.get('available_weight_g') is not None
        )
        return bool(
            is_sold_by_weight
            or unit_type in ['weight', 'kg', 'kilogram']
            or weight_unit in ['g', 'gram', 'gramme']
            or unit_display in ['g', 'gram', 'gramme', 'kg', 'kilogram']
            or has_weight_pricing
        )

    def get_weight_unit(self, obj):
        specs = self._get_specs(obj)
        unit = specs.get('weight_unit') or specs.get('unit_display') or specs.get('unit_type')
        if unit is None:
            return 'unité'
        unit_normalized = str(unit).lower()
        if unit_normalized in ['weight', 'kg', 'kilogram']:
            return 'kg'
        if unit_normalized in ['g', 'gram', 'gramme']:
            return 'g'
        return unit_normalized


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


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id',
            'old_status',
            'new_status',
            'changed_at',
            'source',
            'note',
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'quantity',
            'price',
            'total_price',
            'colors',
            'sizes',
        ]

    def get_colors(self, obj):
        return [color.id for color in obj.colors.all()]

    def get_sizes(self, obj):
        return [size.id for size in obj.sizes.all()]

    def get_total_price(self, obj):
        return float(obj.get_total_price())


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    subtotal = serializers.FloatField()
    shipping_cost = serializers.FloatField()
    tax = serializers.FloatField()
    discount = serializers.FloatField()
    total = serializers.FloatField()

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'payment_method',
            'is_paid',
            'paid_at',
            'created_at',
            'updated_at',
            'shipping_address_id',
            'shipping_method_id',
            'tracking_number',
            'shipped_at',
            'delivered_at',
            'subtotal',
            'shipping_cost',
            'tax',
            'discount',
            'total',
            'items',
            'status_history',
            'metadata',
        ]