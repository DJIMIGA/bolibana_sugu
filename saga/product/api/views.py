from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    CategorySerializer, PhoneSerializer, FavoriteSerializer, ReviewSerializer
)
from product.models import Product, Category, Favorite, Review
from inventory.models import ExternalCategory
from inventory.utils import get_synced_categories

class CategoryViewSet(viewsets.ModelViewSet):
    # Ne pas définir le queryset ici, le définir dans get_queryset() pour être sûr qu'il est appliqué
    queryset = Category.objects.none()  # Queryset vide par défaut, sera remplacé dans get_queryset()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    pagination_class = None  # Désactiver la pagination pour les catégories

    def get_queryset(self):
        """Filtrer pour ne retourner que les catégories B2B (comme sur le web)"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Utiliser la même fonction que le web : get_synced_categories()
        # Cette fonction retourne les catégories avec ExternalCategory
        categories = get_synced_categories()
        
        # Convertir en queryset pour compatibilité avec DRF
        if categories:
            category_ids = [cat.id for cat in categories]
            queryset = Category.objects.filter(id__in=category_ids).select_related('external_category', 'parent').prefetch_related('children')
        else:
            # Fallback : utiliser le filtre direct comme dans dropdown_categories_processor
            queryset = Category.objects.filter(
                Q(external_category__isnull=False) | Q(rayon_type__isnull=False)
            ).select_related('external_category')
        
        # Log pour debug
        queryset_count = queryset.count()
        logger.info(f"[CategoryViewSet.get_queryset] 🔍 Total catégories B2B après filtre: {queryset_count}")
        
        if queryset_count > 0:
            sample_categories = list(queryset[:5])
            for cat in sample_categories:
                has_external = hasattr(cat, 'external_category') and cat.external_category is not None
                logger.info(f"[CategoryViewSet] ✅ Catégorie B2B: {cat.name} (ID: {cat.id}, rayon_type: {cat.rayon_type}, level: {cat.level}, has_external: {has_external})")
        else:
            logger.warning(f"[CategoryViewSet] ⚠️ Aucune catégorie B2B trouvée")
            # Vérifier combien de catégories ont external_category ou rayon_type
            total_categories = Category.objects.count()
            with_external = Category.objects.filter(external_category__isnull=False).count()
            with_rayon = Category.objects.filter(rayon_type__isnull=False).count()
            logger.info(f"[CategoryViewSet] 📊 Total catégories: {total_categories}, avec external_category: {with_external}, avec rayon_type: {with_rayon}")
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list pour s'assurer que get_queryset() est appelé et appliquer le filtre"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[CategoryViewSet.list] 🚀 Début list() - Action: {self.action}")
        
        # Forcer l'utilisation de get_queryset() avec le filtre B2B
        queryset = self.get_queryset()
        queryset_count = queryset.count()
        logger.info(f"[CategoryViewSet.list] 📊 Queryset count après filtre B2B: {queryset_count}")
        
        # Log des premières catégories pour vérifier
        if queryset_count > 0:
            sample = list(queryset[:3])
            for cat in sample:
                logger.info(f"[CategoryViewSet.list] 📋 Catégorie: {cat.name} (ID: {cat.id}, rayon_type: {cat.rayon_type}, level: {cat.level})")
        else:
            logger.warning(f"[CategoryViewSet.list] ⚠️ Aucune catégorie B2B dans le queryset filtré")
        
        # Utiliser filter_queryset pour appliquer les filtres backend
        queryset = self.filter_queryset(queryset)
        
        # Sérialiser et retourner
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[CategoryViewSet.list] 📤 Retour de {len(serializer.data)} catégories")
        return Response(serializer.data)

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
        import logging
        logger = logging.getLogger(__name__)
        
        queryset = super().get_queryset()
        
        # Filtrer pour ne garder que les produits B2B
        # Inclure:
        # - catégories B2B (external_category ou rayon_type)
        # - produits synchronisés B2B même sans catégorie (external_product.is_b2b)
        queryset = queryset.filter(
            Q(category__external_category__isnull=False) |
            Q(category__rayon_type__isnull=False) |
            Q(external_product__is_b2b=True)
        ).distinct()
        
        # Log pour debug
        product_count = queryset.count()
        logger.info(f"[ProductViewSet.get_queryset] 🔍 Produits B2B après filtre (catégorie ou external): {product_count}")
        if product_count > 0:
            sample_products = list(queryset[:3])
            for p in sample_products:
                logger.info(f"[ProductViewSet] ✅ Produit B2B: {p.title} (ID: {p.id}, category: {p.category_id}, category_name: {p.category.name if p.category else 'N/A'})")
        
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

        category_ids_param = self.request.query_params.get('category_ids')
        if category_ids_param:
            raw_ids = [item.strip() for item in category_ids_param.split(',') if item.strip()]
            try:
                category_ids = [int(item) for item in raw_ids if item.isdigit()]
            except ValueError:
                category_ids = []
            if category_ids:
                queryset = queryset.filter(category_id__in=category_ids)
        
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

    def list(self, request, *args, **kwargs):
        """
        Déclenche une synchronisation B2B non bloquante avant de lister.
        Utile pour le mobile qui consomme /api/products/ (pas /inventory/...).
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            from inventory.tasks import trigger_products_sync_async
            force_sync = request.query_params.get('force_sync', 'false').lower() == 'true'
            if force_sync:
                logger.info("[ProductViewSet.list] 🔄 Synchronisation forcée demandée via ?force_sync=true")
            triggered = trigger_products_sync_async(force=force_sync)
            logger.info(f"[ProductViewSet.list] ✅ Sync auto déclenchée: {triggered}")
        except Exception as e:
            logger.warning(f"[ProductViewSet.list] ⚠️ Impossible de déclencher la sync auto: {str(e)}")

        return super().list(request, *args, **kwargs)

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

    @action(detail=True, methods=['get', 'post'], url_path='reviews')
    def reviews(self, request, slug=None):
        product = self.get_object()

        if request.method == 'GET':
            reviews = product.reviews.select_related('user').all()
            serializer = ReviewSerializer(reviews, many=True)
            avg = None
            if reviews.exists():
                avg = round(sum(r.rating for r in reviews) / reviews.count(), 1)
            return Response({
                'count': reviews.count(),
                'average_rating': avg,
                'results': serializer.data,
            })

        # POST — créer un avis
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Vérifier achat
        from cart.models import OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__is_paid=True
        ).exists()
        if not has_purchased:
            return Response(
                {'error': 'Vous devez avoir acheté ce produit pour laisser un avis.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Vérifier doublon
        if Review.objects.filter(user=request.user, product=product).exists():
            return Response(
                {'error': 'Vous avez déjà laissé un avis pour ce produit.'},
                status=status.HTTP_409_CONFLICT
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            'product', 'product__category', 'product__phone',
            'product__clothing_product', 'product__fabric_product',
            'product__cultural_product', 'product__external_product'
        ).prefetch_related('product__images')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Empêcher les doublons, retourner l'existant si déjà en favori
        product = request.data.get('product_id')
        existing = Favorite.objects.filter(user=request.user, product_id=product).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Produit introuvable'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            favorite.delete()
            return Response({'is_favorite': False}, status=status.HTTP_200_OK)
        return Response({'is_favorite': True, 'id': favorite.id}, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
