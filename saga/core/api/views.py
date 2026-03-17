from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import StaticPage, SiteConfiguration
from .serializers import StaticPageListSerializer, StaticPageDetailSerializer, SiteConfigSerializer


class StaticPageListView(generics.ListAPIView):
    """Liste toutes les pages statiques publiées."""
    serializer_class = StaticPageListSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return StaticPage.objects.filter(is_published=True)


class StaticPageDetailView(generics.RetrieveAPIView):
    """Récupère une page statique par son slug."""
    serializer_class = StaticPageDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return StaticPage.objects.filter(is_published=True)


class SiteConfigView(APIView):
    """Retourne la configuration publique du site."""
    permission_classes = [AllowAny]

    def get(self, request):
        config = SiteConfiguration.get_config()
        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)
