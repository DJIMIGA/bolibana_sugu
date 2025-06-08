from rest_framework import serializers
from ..models import Shopper, ShippingAddress

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopper
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'fidelys_number']
        read_only_fields = ['id', 'fidelys_number']
        extra_kwargs = {'password': {'write_only': True}}

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