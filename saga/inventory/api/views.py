"""
API REST pour l'intégration avec l'app de gestion de stock
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from inventory.models import ExternalProduct, ExternalCategory
from inventory.services import InventoryAPIClient, ProductSyncService
from inventory.utils import (
    get_synced_categories,
    get_category_tree_from_b2b,
    get_products_in_synced_category
)
from inventory.category_utils import build_category_hierarchy, get_b2b_categories_hierarchy
from product.models import Category, Product
import logging

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les catégories synchronisées depuis B2B
    """
    queryset = Category.objects.all()
    permission_classes = []  # Public read-only
    lookup_field = 'id'  # Utiliser l'ID au lieu du slug pour l'API
    
    @action(detail=False, methods=['get'], url_path='synced', url_name='synced')
    def synced(self, request):
        """Retourne les catégories synchronisées depuis B2B"""
        from django.db.models import Prefetch
        from django.core.exceptions import ValidationError
        
        logger.info(f"[CategoryViewSet] Appel de l'endpoint synced depuis {request.META.get('REMOTE_ADDR')}")
        
        try:
            categories = get_synced_categories()
            
            if not categories:
                logger.info("Aucune catégorie synchronisée trouvée")
                return Response({
                    'count': 0,
                    'results': []
                })
            
            logger.info(f"Récupération de {len(categories)} catégories synchronisées")
            
            # Annoter les catégories avec le nombre de produits disponibles
            category_ids = [cat.id for cat in categories]
            
            # Préparer le prefetch pour les enfants avec annotation
            children_prefetch = Prefetch(
                'children',
                queryset=Category.objects.annotate(
                    # Product.category a related_name='products'
                    # IMPORTANT: ne pas utiliser "product_count" car Category a une property du même nom
                    b2b_product_count=Count('products', filter=Q(products__is_available=True))
                )
            )
            
            categories_with_count = Category.objects.filter(
                id__in=category_ids
            ).annotate(
                # Product.category a related_name='products'
                # IMPORTANT: ne pas utiliser "product_count" car Category a une property du même nom
                b2b_product_count=Count('products', filter=Q(products__is_available=True))
            ).select_related('parent').prefetch_related(children_prefetch)
            
            from product.api.serializers import CategorySerializer
            
            # Sérialiser les catégories une par une pour identifier les problèmes
            results = []
            errors = []
            for cat in categories_with_count:
                try:
                    # Vérifier que la catégorie a les champs requis
                    if not cat.name:
                        logger.warning(f"Catégorie {cat.id} n'a pas de nom, ignorée")
                        continue
                    
                    # S'assurer que le slug existe ou est vide
                    if not cat.slug:
                        logger.debug(f"Catégorie {cat.id} n'a pas de slug, utilisation d'une valeur par défaut")
                    
                    cat_serializer = CategorySerializer(cat, context={'request': request})
                    results.append(cat_serializer.data)
                except ValidationError as ve:
                    error_msg = f"ValidationError pour catégorie {cat.id} ({cat.name}): {str(ve)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Erreur lors de la sérialisation de la catégorie {cat.id} ({getattr(cat, 'name', 'sans nom')}): {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
            
            response_data = {
                'count': len(results),
                'results': results
            }
            
            if errors:
                response_data['warnings'] = errors
                logger.warning(f"{len(errors)} erreurs lors de la sérialisation, {len(results)} catégories retournées")
            
            logger.info(f"[CategoryViewSet] Retour de {len(results)} catégories synchronisées")
            return Response(response_data)
            
        except Exception as e:
            error_msg = f"Erreur lors de la récupération des catégories synchronisées: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return Response({
                'error': error_msg,
                'count': 0,
                'results': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Retourne l'arbre hiérarchique des catégories synchronisées"""
        tree = get_category_tree_from_b2b()
        
        return Response({
            'categories': tree
        })
    
    @action(detail=False, methods=['get'], url_path='b2b-hierarchy', url_name='b2b-hierarchy')
    def b2b_hierarchy(self, request):
        """
        Retourne la hiérarchie des catégories B2B organisée par niveau.
        Les catégories de niveau 0 sont les principales, celles de niveau 1+ sont les sous-catégories.
        """
        try:
            hierarchy = get_b2b_categories_hierarchy()
            return Response(hierarchy)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la hiérarchie B2B: {str(e)}", exc_info=True)
            return Response({
                'error': str(e),
                'main_categories': [],
                'total_main': 0,
                'total_sub': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='sync-hierarchy', url_name='sync-hierarchy')
    def sync_hierarchy(self, request):
        """
        Synchronise la hiérarchie des catégories B2B à partir des données JSON fournies.
        Accepte un tableau de catégories avec leurs relations parent/enfant.
        """
        from inventory.category_utils import sync_b2b_categories_to_local
        
        try:
            categories_data = request.data
            if not isinstance(categories_data, list):
                return Response({
                    'error': 'Les données doivent être un tableau de catégories'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            stats = sync_b2b_categories_to_local(categories_data)
            
            return Response({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation de la hiérarchie: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Retourne les produits d'une catégorie synchronisée"""
        category = self.get_object()
        
        products = get_products_in_synced_category(category)
        
        from product.api.serializers import ProductListSerializer
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            },
            'count': products.count(),
            'products': serializer.data
        })


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les produits synchronisés depuis B2B
    """
    queryset = Product.objects.all()
    permission_classes = []  # Public read-only
    
    @action(detail=False, methods=['get'], url_path='synced', url_name='synced')
    def synced(self, request):
        """Retourne les produits synchronisés depuis B2B"""
        logger.info(f"[B2B API] Requête reçue pour /api/inventory/products/synced/")
        
        # Déclencher une synchronisation automatique si nécessaire
        # NOTE: Le middleware déclenche aussi la sync sur cet endpoint, mais le lock dans
        # should_sync_products() évite les doublons. On garde les deux pour robustesse.
        from inventory.tasks import trigger_products_sync_async
        try:
            # Non bloquant: ne ralentit pas l'API mobile
            # Le lock dans trigger_products_sync_async évite les synchronisations concurrentes
            trigger_products_sync_async(force=False)
        except Exception as e:
            logger.warning(f"Erreur lors de la synchronisation automatique: {str(e)}")
        
        try:
            # Vérifier que l'API key est configurée
            from inventory.models import ApiKey
            api_key = ApiKey.get_active_key()
            if not api_key:
                logger.warning("[B2B API] Aucune clé API active trouvée. Vérifiez /admin/inventory/apikey/")
                return Response({
                    'error': 'Aucune clé API configurée. Veuillez configurer une clé API active dans /admin/inventory/apikey/',
                    'count': 0,
                    'results': []
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Récupérer uniquement les produits B2B synchronisés
            external_products = ExternalProduct.objects.filter(
                sync_status='synced',
                is_b2b=True
            ).select_related('product')
            external_count = external_products.count()
            logger.info(f"[B2B API] Produits B2B avec sync_status='synced' et is_b2b=True: {external_count}")
            
            if external_count == 0:
                # Aucun produit synchronisé - suggérer de synchroniser
                logger.warning("[B2B API] Aucun produit synchronisé trouvé. Exécutez: python manage.py sync_products_from_inventory")
                return Response({
                    'error': 'Aucun produit synchronisé trouvé. Veuillez synchroniser les produits depuis B2B avec: python manage.py sync_products_from_inventory',
                    'count': 0,
                    'results': [],
                    'hint': 'Exécutez la commande: python manage.py sync_products_from_inventory'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Extraire les IDs des produits (via la relation OneToOneField)
            product_ids = [ep.product.id for ep in external_products if ep.product]
            if not product_ids:
                logger.warning("[B2B API] Aucun product_id valide trouvé dans ExternalProduct")
                return Response({
                    'error': 'Aucun produit valide trouvé',
                    'count': 0,
                    'results': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Filtrer uniquement les produits disponibles et trier par ID pour cohérence
            products = Product.objects.filter(
                id__in=product_ids,
                is_available=True
            ).select_related('category', 'supplier').order_by('-id')
            products_count = products.count()
            logger.info(f"[B2B API] Produits trouvés (disponibles): {products_count}")
            
            if products_count == 0:
                logger.warning(f"[B2B API] Aucun produit trouvé pour les IDs: {product_ids[:5]}...")
                return Response({
                    'error': 'Aucun produit trouvé pour les IDs synchronisés',
                    'count': 0,
                    'results': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            from product.api.serializers import ProductListSerializer
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            
            return Response({
                'count': products.count(),
                'results': serializer.data
            })
        except Exception as e:
            logger.error(f"[B2B API] Erreur dans synced: {str(e)}", exc_info=True)
            return Response({
                'error': str(e),
                'count': 0,
                'results': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue simple pour tester l'endpoint synced directement
@api_view(['GET'])
def synced_products_view(request):
    """Vue alternative pour récupérer les produits B2B synchronisés"""
    logger.info(f"[B2B API] Requête reçue via vue alternative pour /api/inventory/products/synced/")
    try:
        # Vérifier que l'API key est configurée
        from inventory.models import ApiKey
        api_key = ApiKey.get_active_key()
        if not api_key:
            logger.warning("[B2B API] Aucune clé API active trouvée. Vérifiez /admin/inventory/apikey/")
            return Response({
                'error': 'Aucune clé API configurée. Veuillez configurer une clé API active dans /admin/inventory/apikey/',
                'count': 0,
                'results': []
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Récupérer uniquement les produits B2B synchronisés
        external_products = ExternalProduct.objects.filter(
            sync_status='synced',
            is_b2b=True
        ).select_related('product')
        external_count = external_products.count()
        logger.info(f"[B2B API] Produits B2B avec sync_status='synced' et is_b2b=True: {external_count}")
        
        if external_count == 0:
            logger.warning("[B2B API] Aucun produit synchronisé trouvé. Exécutez: python manage.py sync_products_from_inventory")
            return Response({
                'error': 'Aucun produit synchronisé trouvé. Veuillez synchroniser les produits depuis B2B avec: python manage.py sync_products_from_inventory',
                'count': 0,
                'results': [],
                'hint': 'Exécutez la commande: python manage.py sync_products_from_inventory'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Extraire les IDs des produits (via la relation OneToOneField)
        product_ids = [ep.product.id for ep in external_products if ep.product]
        if not product_ids:
            logger.warning("[B2B API] Aucun product_id valide trouvé dans ExternalProduct")
            return Response({
                'error': 'Aucun produit valide trouvé',
                'count': 0,
                'results': []
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Filtrer uniquement les produits disponibles et trier par ID pour cohérence
        products = Product.objects.filter(
            id__in=product_ids,
            is_available=True
        ).select_related('category', 'supplier').order_by('-id')
        products_count = products.count()
        logger.info(f"[B2B API] Produits trouvés (disponibles): {products_count}")
        
        if products_count == 0:
            logger.warning(f"[B2B API] Aucun produit trouvé pour les IDs: {product_ids[:5]}...")
            return Response({
                'error': 'Aucun produit trouvé pour les IDs synchronisés',
                'count': 0,
                'results': []
            }, status=status.HTTP_404_NOT_FOUND)
        
        from product.api.serializers import ProductListSerializer
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        
        return Response({
            'count': products.count(),
            'results': serializer.data
        })
    except Exception as e:
        logger.error(f"[B2B API] Erreur dans synced_products_view: {str(e)}", exc_info=True)
        return Response({
            'error': str(e),
            'count': 0,
            'results': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue alternative pour l'endpoint synced des catégories (au cas où le router ne la génère pas correctement)
@api_view(['GET'])
def synced_categories_view(request):
    """Vue alternative pour récupérer les catégories B2B synchronisées"""
    logger.info(f"[synced_categories_view] Requête reçue pour /api/inventory/categories/synced/")
    from django.db.models import Prefetch
    from django.core.exceptions import ValidationError
    
    try:
        categories = get_synced_categories()
        
        if not categories:
            logger.info("Aucune catégorie synchronisée trouvée")
            return Response({
                'count': 0,
                'results': []
            })
        
        logger.info(f"Récupération de {len(categories)} catégories synchronisées")
        
        # Annoter les catégories avec le nombre de produits disponibles
        category_ids = [cat.id for cat in categories]
        
        # Préparer le prefetch pour les enfants avec annotation
        children_prefetch = Prefetch(
            'children',
            queryset=Category.objects.annotate(
                product_count=Count('product', filter=Q(product__is_available=True))
            )
        )
        
        categories_with_count = Category.objects.filter(
            id__in=category_ids
        ).annotate(
            product_count=Count('product', filter=Q(product__is_available=True))
        ).select_related('parent').prefetch_related(children_prefetch)
        
        from product.api.serializers import CategorySerializer
        
        # Sérialiser les catégories une par une pour identifier les problèmes
        results = []
        errors = []
        for cat in categories_with_count:
            try:
                # Vérifier que la catégorie a les champs requis
                if not cat.name:
                    logger.warning(f"Catégorie {cat.id} n'a pas de nom, ignorée")
                    continue
                
                cat_serializer = CategorySerializer(cat, context={'request': request})
                results.append(cat_serializer.data)
            except ValidationError as ve:
                error_msg = f"ValidationError pour catégorie {cat.id} ({cat.name}): {str(ve)}"
                logger.error(error_msg)
                errors.append(error_msg)
            except Exception as e:
                error_msg = f"Erreur lors de la sérialisation de la catégorie {cat.id} ({getattr(cat, 'name', 'sans nom')}): {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
        
        response_data = {
            'count': len(results),
            'results': results
        }
        
        if errors:
            response_data['warnings'] = errors
            logger.warning(f"{len(errors)} erreurs lors de la sérialisation, {len(results)} catégories retournées")
        
        logger.info(f"[synced_categories_view] Retour de {len(results)} catégories synchronisées")
        return Response(response_data)
        
    except Exception as e:
        error_msg = f"Erreur lors de la récupération des catégories synchronisées: {str(e)}"
        logger.error(f"[synced_categories_view] {error_msg}", exc_info=True)
        return Response({
            'error': error_msg,
            'count': 0,
            'results': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API pour tester la connexion et synchroniser
class InventoryAPIViewSet(viewsets.ViewSet):
    """
    ViewSet pour les actions API d'inventaire (test connexion, synchronisation)
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """Teste la connexion à l'API B2B"""
        try:
            api_client = InventoryAPIClient()
            if api_client.test_connection():
                from django.conf import settings
                api_url = getattr(settings, 'B2B_API_URL', 'https://www.bolibanastock.com/api/v1')
                return Response({
                    'success': True,
                    'message': 'Connexion réussie',
                    'api_url': api_url
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Connexion échouée'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def sync_products(self, request):
        """Synchronise les produits depuis B2B"""
        try:
            sync_service = ProductSyncService()
            stats = sync_service.sync_all_products()
            
            return Response({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def sync_categories(self, request):
        """Synchronise les catégories depuis B2B"""
        try:
            sync_service = ProductSyncService()
            stats = sync_service.sync_categories()
            
            return Response({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
