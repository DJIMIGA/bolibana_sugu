from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PriceSubmissionSerializer, PriceEntrySerializer, CitySerializer
from price_checker.models import PriceSubmission, PriceEntry, City


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des villes disponibles pour le price checker."""
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PriceEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Prix validés — lecture publique."""
    queryset = PriceEntry.objects.filter(is_active=True).select_related('product', 'city')
    serializer_class = PriceEntrySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'city']
    search_fields = ['product__title']


class PriceSubmissionViewSet(viewsets.ModelViewSet):
    """CRUD soumissions de prix pour les utilisateurs authentifiés."""
    serializer_class = PriceSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'city', 'product']

    def get_queryset(self):
        return PriceSubmission.objects.filter(
            user=self.request.user
        ).select_related('product', 'city')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'PENDING':
            return Response(
                {'error': 'Seules les soumissions en attente peuvent être modifiées.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'PENDING':
            return Response(
                {'error': 'Seules les soumissions en attente peuvent être supprimées.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='all', permission_classes=[permissions.IsAdminUser])
    def list_all(self, request):
        """Admin : toutes les soumissions."""
        qs = PriceSubmission.objects.select_related('product', 'city').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='approve', permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Admin : approuver une soumission."""
        submission = self.get_object()
        if submission.status != 'PENDING':
            return Response(
                {'error': 'Cette soumission a déjà été traitée.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        notes = request.data.get('notes', '')
        submission.approve(admin_user=request.user, notes=notes)
        return Response(PriceSubmissionSerializer(submission).data)

    @action(detail=True, methods=['post'], url_path='reject', permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Admin : rejeter une soumission."""
        submission = self.get_object()
        if submission.status != 'PENDING':
            return Response(
                {'error': 'Cette soumission a déjà été traitée.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        notes = request.data.get('notes', '')
        submission.reject(admin_user=request.user, notes=notes)
        return Response(PriceSubmissionSerializer(submission).data)
