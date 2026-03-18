from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from notifications.models import PushToken
from .serializers import PushTokenSerializer, NotificationPreferencesSerializer


class RegisterPushTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        device_type = serializer.validated_data['device_type']

        # update_or_create sur le token : réassigne si l'appareil change d'utilisateur
        PushToken.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'device_type': device_type,
                'is_active': True,
            },
        )
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class UnregisterPushTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        if token:
            PushToken.objects.filter(token=token, user=request.user).update(is_active=False)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class NotificationPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'notifications_enabled': request.user.notifications_enabled,
        })

    def patch(self, request):
        serializer = NotificationPreferencesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.notifications_enabled = serializer.validated_data['notifications_enabled']
        request.user.save(update_fields=['notifications_enabled'])

        return Response({
            'notifications_enabled': request.user.notifications_enabled,
        })
