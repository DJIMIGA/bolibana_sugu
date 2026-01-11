"""
Middleware pour la synchronisation automatique des produits et catégories B2B
"""
import logging
from .tasks import trigger_products_sync_async, trigger_categories_sync_async

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
            # Déclencher en arrière-plan (non bloquant).
            # L'intervalle mini est géré par inventory.tasks (INVENTORY_SYNC_FREQUENCY).
            try:
                if trigger_products_sync_async(force=False):
                    logger.info(f"Déclenchement async sync produits via {request.path}")
            except Exception as e:
                logger.error(f"Erreur déclenchement async sync produits: {str(e)}")

            try:
                if trigger_categories_sync_async(force=False):
                    logger.info(f"Déclenchement async sync catégories via {request.path}")
            except Exception as e:
                logger.error(f"Erreur déclenchement async sync catégories: {str(e)}")
        
        response = self.get_response(request)
        return response

