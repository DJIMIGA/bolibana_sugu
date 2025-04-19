from rest_framework import serializers
from accounts.models import Shopper

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopper
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}} 