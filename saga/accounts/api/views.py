from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models import Shopper, ShippingAddress
from .serializers import UserSerializer, AddressSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class AddressListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class AddressUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class AddressDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class SetDefaultAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK) 