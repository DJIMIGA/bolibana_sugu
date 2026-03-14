from rest_framework import serializers
from ..models import Shopper, ShippingAddress
from cart.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.SerializerMethodField()
    weight_unit = serializers.SerializerMethodField()
    is_weighted = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_title', 'quantity', 'price', 'weight_unit', 'is_weighted']

    def get_product_title(self, obj):
        return obj.product.title if obj.product else ''

    def get_weight_unit(self, obj):
        try:
            unit = obj.get_weight_unit()
            return unit if unit else None
        except Exception:
            return None

    def get_is_weighted(self, obj):
        try:
            return obj.get_weight_unit() in ['kg', 'g']
        except Exception:
            return False


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='items.all', read_only=True)
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_label',
            'payment_method',
            'is_paid',
            'total',
            'created_at',
            'items',
        ]
        read_only_fields = fields

    def get_status_label(self, obj):
        return obj.get_status_display()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopper
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'fidelys_number']
        read_only_fields = ['id', 'fidelys_number']
        extra_kwargs = {
            'password': {'write_only': True},
            'date_of_birth': {'allow_null': True, 'required': False},
            'phone': {'required': False},
        }

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'full_name', 'address_type', 'quarter', 'street_address', 'city', 
                 'additional_info', 'is_default']
        read_only_fields = ['id']

    def validate(self, data):
        if data.get('is_default'):
            # Si c'est une nouvelle adresse ou une mise à jour
            if not self.instance or self.instance.is_default != data['is_default']:
                # Mettre à jour toutes les autres adresses de l'utilisateur
                ShippingAddress.objects.filter(
                    user=self.context['request'].user,
                    is_default=True
                ).update(is_default=False)
        return data 