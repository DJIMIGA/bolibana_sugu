from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
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
        # Inclure les produits disponibles ET les produits B2B synchronisés
        products = Product.objects.filter(
            Q(category=category) & 
            (Q(is_available=True) | Q(external_product__sync_status='synced'))
        ).select_related(
            'category', 'supplier', 'external_product'
        ).prefetch_related('images').distinct()
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'supplier', 'phone', 'phone__color',
        'clothing_product', 'fabric_product', 'cultural_product',
        'external_product'  # Inclure la relation pour les produits B2B
    ).prefetch_related('images')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Retirer 'is_available' de filterset_fields car on le gère manuellement pour inclure les produits B2B
    filterset_fields = ['category', 'brand']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Par défaut, inclure les produits disponibles OU les produits B2B synchronisés
        # Cela permet d'inclure les produits B2B même s'ils ne sont pas explicitement marqués comme disponibles
        # Si is_available est spécifié dans les paramètres, respecter ce filtre
        is_available_param = self.request.query_params.get('is_available')
        if is_available_param is None:
            # Par défaut, inclure les produits disponibles ET les produits B2B synchronisés
            queryset = queryset.filter(
                Q(is_available=True) | 
                Q(external_product__sync_status='synced')
            ).distinct()
        elif is_available_param == 'true':
            # Si is_available=true est demandé, inclure les produits disponibles ET les produits B2B synchronisés
            queryset = queryset.filter(
                Q(is_available=True) | 
                Q(external_product__sync_status='synced')
            ).distinct()
        elif is_available_param == 'false':
            # Si is_available=false est demandé, exclure les produits disponibles
            # Mais toujours inclure les produits B2B synchronisés
            queryset = queryset.filter(
                Q(is_available=False) | 
                Q(external_product__sync_status='synced')
            ).distinct()
        
        # Filtre pour les produits en promotion
        promo = self.request.query_params.get('promo')
        if promo == 'true':
            queryset = queryset.filter(
                discount_price__isnull=False,
                discount_price__gt=0
            ).exclude(discount_price__gte=F('price'))
        
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
        # Inclure les produits disponibles ET les produits B2B synchronisés
        similar_products = Product.objects.filter(
            category=product.category
        ).filter(
            Q(is_available=True) | Q(external_product__sync_status='synced')
        ).exclude(
            id=product.id
        ).select_related('category', 'supplier', 'external_product').prefetch_related('images').distinct()[:10]  # Limiter à 10 produits
        
        serializer = ProductListSerializer(similar_products, many=True, context={'request': request})
        return Response(serializer.data)

