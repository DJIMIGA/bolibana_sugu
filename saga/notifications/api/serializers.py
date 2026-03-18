from rest_framework import serializers
from notifications.models import PushToken, Notification


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ['token', 'device_type']


class NotificationPreferencesSerializer(serializers.Serializer):
    notifications_enabled = serializers.BooleanField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'data', 'is_read', 'created_at']
        read_only_fields = ['id', 'title', 'body', 'data', 'created_at']
