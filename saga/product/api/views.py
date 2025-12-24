from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    CategorySerializer, PhoneSerializer
)
from product.models import Product, Category

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_context(self):
        """Passe le contexte de la requête au serializer pour les URLs absolues"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'supplier', 'phone', 'phone__color',
        'clothing_product', 'fabric_product', 'cultural_product'
    ).prefetch_related('images')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_available']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre pour les produits en promotion
        promo = self.request.query_params.get('promo')
        if promo == 'true':
            queryset = queryset.filter(
                discount_price__isnull=False,
                discount_price__gt=0
            ).exclude(discount_price__gte=models.F('price'))
        
        # Filtres personnalisés par type de produit (comme sur le web)
        has_phone = self.request.query_params.get('has_phone')
        if has_phone == 'true':
            queryset = queryset.filter(phone__isnull=False)
            
        has_clothing = self.request.query_params.get('has_clothing')
        if has_clothing == 'true':
            queryset = queryset.filter(clothing_product__isnull=False)
            
        has_fabric = self.request.query_params.get('has_fabric')
        if has_fabric == 'true':
            queryset = queryset.filter(fabric_product__isnull=False)
            
        has_cultural = self.request.query_params.get('has_cultural')
        if has_cultural == 'true':
            queryset = queryset.filter(cultural_product__isnull=False)

        return queryset

    def get_serializer_context(self):
        """Passe le contexte de la requête au serializer pour les URLs absolues"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        product = self.get_object()
        # Vérifier si le produit a un phone associé
        if hasattr(product, 'phone'):
            serializer = PhoneSerializer(product.phone)
            return Response(serializer.data)
        return Response({'detail': 'Ce produit n\'a pas de variantes de téléphone'}, status=404)

    @action(detail=False, methods=['get'], url_path=r'(?P<product_id>\d+)/similar_products', url_name='similar_products')
    def similar_products(self, request, product_id=None):
        """
        Retourne les produits similaires basés sur la catégorie du produit.
        Exclut le produit actuel.
        Utilise l'ID du produit directement car le ViewSet utilise lookup_field='slug'.
        """
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Produit non trouvé'}, status=404)
        
        # Récupérer les produits de la même catégorie, en excluant le produit actuel
        similar_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(
            id=product.id
        ).select_related('category', 'supplier').prefetch_related('images')[:10]  # Limiter à 10 produits
        
        serializer = ProductListSerializer(similar_products, many=True, context={'request': request})
        return Response(serializer.data)

