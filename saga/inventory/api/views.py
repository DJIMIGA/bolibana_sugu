"""
API REST pour l'intégration avec l'app de gestion de stock
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from inventory.models import ExternalProduct, ExternalCategory, ApiKey
from inventory.services import InventoryAPIClient, ProductSyncService
from inventory.utils import (
    get_synced_categories,
    get_category_tree_from_b2b,
    get_products_in_synced_category
)
from inventory.category_utils import build_category_hierarchy, get_b2b_categories_hierarchy
from product.models import Category, Product
from cart.models import Order
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

        # Déclencher une synchronisation automatique non bloquante si nécessaire
        try:
            from inventory.tasks import trigger_categories_sync_async
            force_sync = request.query_params.get('force', 'false').lower() == 'true'
            if force_sync:
                logger.info("[CategoryViewSet] 🔄 Synchronisation forcée demandée via ?force=true")
            triggered = trigger_categories_sync_async(force=force_sync)
            logger.info(f"[CategoryViewSet] ✅ Sync auto catégories déclenchée: {triggered}")
        except Exception as e:
            logger.warning(f"[CategoryViewSet] ⚠️ Impossible de déclencher la sync auto catégories: {str(e)}")
        
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
        
        # Permettre de forcer la synchronisation via paramètre ?force=true
        force_sync = request.query_params.get('force', 'false').lower() == 'true'
        
        # Déclencher une synchronisation automatique si nécessaire
        # NOTE: Le middleware déclenche aussi la sync sur cet endpoint, mais le lock dans
        # should_sync_products() évite les doublons. On garde les deux pour robustesse.
        from inventory.tasks import trigger_products_sync_async
        try:
            # Non bloquant: ne ralentit pas l'API mobile
            # Le lock dans trigger_products_sync_async évite les synchronisations concurrentes
            if force_sync:
                logger.info("[B2B API] 🔄 Synchronisation forcée demandée via paramètre ?force=true")
            triggered = trigger_products_sync_async(force=force_sync)
            logger.info(f"[B2B API] ✅ Sync auto produits déclenchée: {triggered}")
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
            
            # Produits non disponibles pour diagnostic
            unavailable_products = Product.objects.filter(
                id__in=product_ids,
                is_available=False
            ).count()
            
            logger.info(f"[B2B API] Produits synchronisés: {external_count}")
            logger.info(f"[B2B API] Produits avec Product valide: {len(product_ids)}")
            logger.info(f"[B2B API] Produits disponibles (is_available=True): {products_count}")
            logger.info(f"[B2B API] Produits non disponibles (is_available=False): {unavailable_products}")
            
            if unavailable_products > 0:
                logger.warning(
                    f"[B2B API] ⚠️  {unavailable_products} produits synchronisés ne sont pas disponibles "
                    f"(is_available=False) et ne seront pas retournés par l'API"
                )
            
            if products_count == 0:
                logger.warning(f"[B2B API] Aucun produit disponible trouvé pour les IDs: {product_ids[:5]}...")
                return Response({
                    'error': 'Aucun produit disponible trouvé pour les IDs synchronisés',
                    'count': 0,
                    'results': [],
                    'diagnostic': {
                        'synced_count': external_count,
                        'with_product_count': len(product_ids),
                        'available_count': products_count,
                        'unavailable_count': unavailable_products
                    }
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


@api_view(['GET'])
def sync_status_view(request):
    """
    Retourne l'état de la synchronisation automatique (timestamps + locks).
    """
    from inventory.tasks import get_sync_status
    status_payload = get_sync_status()
    logger.info("[SyncStatus] Consultation du statut de synchronisation auto")
    return Response(status_payload)


# Vue simple pour tester l'endpoint synced directement
@api_view(['GET'])
def synced_products_view(request):
    """Vue alternative pour récupérer les produits B2B synchronisés"""
    logger.info(f"[B2B API] Requête reçue via vue alternative pour /api/inventory/products/synced/")
    
    # Permettre de forcer la synchronisation via paramètre ?force=true
    force_sync = request.query_params.get('force', 'false').lower() == 'true'
    
    # Déclencher une synchronisation automatique si nécessaire
    from inventory.tasks import trigger_products_sync_async
    try:
        if force_sync:
            logger.info("[B2B API] 🔄 Synchronisation forcée demandée via paramètre ?force=true")
        trigger_products_sync_async(force=force_sync)
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
        
        # Produits non disponibles pour diagnostic
        unavailable_products = Product.objects.filter(
            id__in=product_ids,
            is_available=False
        ).count()
        
        logger.info(f"[B2B API] Produits synchronisés: {external_count}")
        logger.info(f"[B2B API] Produits avec Product valide: {len(product_ids)}")
        logger.info(f"[B2B API] Produits disponibles (is_available=True): {products_count}")
        logger.info(f"[B2B API] Produits non disponibles (is_available=False): {unavailable_products}")
        
        if unavailable_products > 0:
            logger.warning(
                f"[B2B API] ⚠️  {unavailable_products} produits synchronisés ne sont pas disponibles "
                f"(is_available=False) et ne seront pas retournés par l'API"
            )
        
        if products_count == 0:
            logger.warning(f"[B2B API] Aucun produit disponible trouvé pour les IDs: {product_ids[:5]}...")
            return Response({
                'error': 'Aucun produit disponible trouvé pour les IDs synchronisés',
                'count': 0,
                'results': [],
                'diagnostic': {
                    'synced_count': external_count,
                    'with_product_count': len(product_ids),
                    'available_count': products_count,
                    'unavailable_count': unavailable_products
                }
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


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def b2b_order_status_webhook(request):
    """
    Webhook pour recevoir les mises à jour de statut de commande depuis B2B
    
    Authentification: X-API-Key header (même mécanisme que pour les produits)
    Payload attendu:
    {
        "external_sale_id": int,
        "status": str,  # 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
        "order_number": str,  # Numéro de commande SagaKore
        "tracking_number": str (optionnel),
        "shipped_at": str (optionnel, ISO format),
        "delivered_at": str (optionnel, ISO format)
    }
    """
    # Vérifier la méthode HTTP
    if request.method != 'POST':
        logger.warning(
            f"[B2B Webhook] Tentative d'accès avec méthode {request.method} depuis {request.META.get('REMOTE_ADDR')}"
        )
        return Response(
            {'error': 'Method not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    # Authentification via X-API-Key
    api_key_header = request.META.get('HTTP_X_API_KEY') or request.META.get('HTTP_X-API-KEY')
    if not api_key_header:
        logger.warning(
            f"[B2B Webhook] Tentative d'accès sans clé API depuis {request.META.get('REMOTE_ADDR')}"
        )
        return Response(
            {'error': 'Missing X-API-Key header'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Vérifier que la clé API est valide (accepter toute clé active)
    active_keys = ApiKey.get_active_keys()
    active_key_values = {item.get('key') for item in active_keys if item.get('key')}
    if not active_key_values or api_key_header not in active_key_values:
        logger.warning(
            f"[B2B Webhook] Tentative d'accès avec clé API invalide depuis {request.META.get('REMOTE_ADDR')}"
        )
        return Response(
            {'error': 'Invalid API key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Log de réception du webhook avec authentification réussie
    logger.info(
        f"[B2B Webhook] ✅ Webhook reçu depuis {request.META.get('REMOTE_ADDR')} - Authentification réussie"
    )
    
    # Parser les données JSON
    try:
        data = request.data if hasattr(request, 'data') else {}
        if not data:
            import json
            data = json.loads(request.body)
        
        # Log de réception du payload
        logger.info(
            f"[B2B Webhook] ✅ Payload JSON reçu et parsé avec succès: "
            f"external_sale_id={data.get('external_sale_id')}, "
            f"status={data.get('status')}, "
            f"order_number={data.get('order_number')}"
        )
    except Exception as e:
        logger.error(f"[B2B Webhook] ❌ Erreur parsing JSON: {str(e)}")
        return Response(
            {'error': 'Invalid JSON payload'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Valider les champs requis
    external_sale_id = data.get('external_sale_id')
    status_value = data.get('status')
    order_number = data.get('order_number')
    
    if not external_sale_id or not status_value or not order_number:
        logger.warning(
            f"[B2B Webhook] Payload incomplet: external_sale_id={external_sale_id}, "
            f"status={status_value}, order_number={order_number}"
        )
        return Response(
            {'error': 'Missing required fields: external_sale_id, status, order_number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Valider le statut (alignés avec B2B)
    valid_statuses = [
        Order.DRAFT,
        Order.CONFIRMED,
        Order.SHIPPED,
        Order.DELIVERED,
        Order.CANCELLED,
    ]
    
    if status_value not in valid_statuses:
        logger.warning(
            f"[B2B Webhook] Statut invalide: {status_value} pour commande {order_number}"
        )
        return Response(
            {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Trouver la commande
    try:
        order = Order.objects.get(order_number=order_number)
        logger.info(
            f"[B2B Webhook] ✅ Commande trouvée: {order_number} (ID: {order.id}, statut actuel: {order.status})"
        )
    except Order.DoesNotExist:
        logger.warning(
            f"[B2B Webhook] ❌ Commande introuvable: {order_number}"
        )
        return Response(
            {'error': f'Order not found: {order_number}'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que l'external_sale_id correspond
    metadata = order.metadata or {}
    stored_external_id = metadata.get('b2b_sale_id')
    
    if stored_external_id and str(stored_external_id) != str(external_sale_id):
        logger.warning(
            f"[B2B Webhook] ❌ external_sale_id mismatch pour commande {order_number}: "
            f"stored={stored_external_id}, received={external_sale_id}"
        )
        return Response(
            {'error': 'external_sale_id mismatch'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Log de validation réussie
    if stored_external_id:
        logger.info(
            f"[B2B Webhook] ✅ external_sale_id validé: {external_sale_id} pour commande {order_number}"
        )
    
    # Mettre à jour la commande
    try:
        old_status = order.status

        # Empêcher un downgrade vers DRAFT après paiement/confirmation
        if status_value == Order.DRAFT and (order.is_paid or order.status in [Order.CONFIRMED, Order.SHIPPED, Order.DELIVERED]):
            logger.warning(
                "[B2B Webhook] Downgrade ignoré pour %s: %s → %s (is_paid=%s)",
                order_number,
                old_status,
                status_value,
                order.is_paid
            )
            return Response(
                {
                    'status': 'ignored',
                    'message': f'Downgrade ignoré: {old_status} → {status_value}',
                },
                status=status.HTTP_200_OK
            )

        # Mettre à jour le statut
        order.status = status_value
        
        # Mettre à jour les champs optionnels
        if 'tracking_number' in data and data['tracking_number']:
            order.tracking_number = data['tracking_number']
        
        if 'shipped_at' in data and data['shipped_at']:
            try:
                from django.utils.dateparse import parse_datetime
                shipped_at = parse_datetime(data['shipped_at'])
                if shipped_at:
                    order.shipped_at = shipped_at
            except Exception as e:
                logger.warning(f"[B2B Webhook] Erreur parsing shipped_at: {str(e)}")
        
        if 'delivered_at' in data and data['delivered_at']:
            try:
                from django.utils.dateparse import parse_datetime
                delivered_at = parse_datetime(data['delivered_at'])
                if delivered_at:
                    order.delivered_at = delivered_at
            except Exception as e:
                logger.warning(f"[B2B Webhook] Erreur parsing delivered_at: {str(e)}")
        
        # Mettre à jour les métadonnées
        metadata['b2b_last_status_update'] = timezone.now().isoformat()
        metadata['b2b_status_update_source'] = 'webhook'
        order.metadata = metadata
        
        order.save()
        
        # Log de succès détaillé
        logger.info(
            f"[B2B Webhook] ✅ Statut commande {order_number} mis à jour avec succès: "
            f"{old_status} → {status_value} (external_sale_id: {external_sale_id})"
        )
        
        # Log supplémentaire avec tous les détails de la mise à jour
        update_details = {
            'order_number': order_number,
            'order_id': order.id,
            'external_sale_id': external_sale_id,
            'old_status': old_status,
            'new_status': status_value,
            'tracking_number': order.tracking_number if order.tracking_number else None,
            'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        }
        logger.info(
            f"[B2B Webhook] ✅ Détails mise à jour commande: {update_details}"
        )
        
        return Response({
            'success': True,
            'message': f'Order status updated: {old_status} → {status_value}',
            'order_number': order_number,
            'external_sale_id': external_sale_id,
            'old_status': old_status,
            'new_status': status_value
        })
        
    except Exception as e:
        logger.error(
            f"[B2B Webhook] ❌ Erreur mise à jour commande {order_number}: {str(e)}",
            exc_info=True
        )
        return Response(
            {'error': f'Error updating order: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
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
