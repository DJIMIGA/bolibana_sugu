from rest_framework import serializers
from notifications.models import PushToken


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ['token', 'device_type']


class NotificationPreferencesSerializer(serializers.Serializer):
    notifications_enabled = serializers.BooleanField()
