"""
Middleware pour la synchronisation automatique des produits et catégories B2B
"""
import logging
from django.utils import timezone
from django.core.cache import cache
from .tasks import sync_products_auto, sync_categories_auto

logger = logging.getLogger(__name__)


class AutoSyncB2BMiddleware:
    """
    Middleware qui synchronise automatiquement les produits et catégories B2B
    lors de l'accès à certaines pages (comme la page d'accueil)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Pages qui déclenchent une synchronisation automatique
        self.sync_trigger_paths = [
            '/',  # Page d'accueil
            '/api/inventory/products/synced/',  # API produits B2B
            '/api/inventory/categories/synced/',  # API catégories B2B
        ]
    
    def __call__(self, request):
        # Vérifier si on doit déclencher une synchronisation
        if request.path in self.sync_trigger_paths:
            # Synchroniser les produits si nécessaire
            last_sync_products = cache.get('b2b_last_sync_time')
            should_sync_products = False
            
            if not last_sync_products:
                # Jamais synchronisé
                should_sync_products = True
            else:
                # Synchroniser si la dernière sync date de plus de 2 heures
                time_since_sync = (timezone.now() - last_sync_products).total_seconds()
                if time_since_sync > 7200:  # 2 heures
                    should_sync_products = True
            
            if should_sync_products:
                # Lancer la synchronisation en arrière-plan (non bloquante)
                try:
                    logger.info(f"Déclenchement de la synchronisation automatique des produits via {request.path}")
                    result = sync_products_auto(force=False)
                    if result['success']:
                        logger.info("Synchronisation automatique des produits réussie")
                    else:
                        logger.warning(f"Synchronisation automatique des produits échouée: {result['message']}")
                except Exception as e:
                    # Ne pas bloquer la requête en cas d'erreur
                    logger.error(f"Erreur lors de la synchronisation automatique des produits: {str(e)}")
            
            # Synchroniser les catégories si nécessaire
            last_sync_categories = cache.get('b2b_categories_last_sync_time')
            should_sync_categories = False
            
            if not last_sync_categories:
                # Jamais synchronisé
                should_sync_categories = True
            else:
                # Synchroniser si la dernière sync date de plus de 2 heures
                time_since_sync = (timezone.now() - last_sync_categories).total_seconds()
                if time_since_sync > 7200:  # 2 heures
                    should_sync_categories = True
            
            if should_sync_categories:
                # Lancer la synchronisation en arrière-plan (non bloquante)
                try:
                    logger.info(f"Déclenchement de la synchronisation automatique des catégories via {request.path}")
                    result = sync_categories_auto(force=False)
                    if result['success']:
                        logger.info("Synchronisation automatique des catégories réussie")
                    else:
                        logger.warning(f"Synchronisation automatique des catégories échouée: {result['message']}")
                except Exception as e:
                    # Ne pas bloquer la requête en cas d'erreur
                    logger.error(f"Erreur lors de la synchronisation automatique des catégories: {str(e)}")
        
        response = self.get_response(request)
        return response

