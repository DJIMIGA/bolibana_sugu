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
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            logger.info(
                "[Middleware] Détection accès déclencheur auto-sync "
                f"path={request.path} ip={client_ip} ua={user_agent}"
            )
            # Déclencher en arrière-plan (non bloquant).
            # L'intervalle mini est géré par inventory.tasks (INVENTORY_SYNC_FREQUENCY).
            # NOTE: Les vues API déclenchent aussi la sync, mais le lock dans should_sync_products()
            # évite les doublons. On garde les deux pour robustesse (si middleware désactivé).
            try:
                triggered_products = trigger_products_sync_async(force=False)
                logger.info(
                    "[Middleware] Déclenchement async sync produits "
                    f"via {request.path} => {triggered_products}"
                )
            except Exception as e:
                logger.error(f"[Middleware] Erreur déclenchement async sync produits: {str(e)}")

            try:
                triggered_categories = trigger_categories_sync_async(force=False)
                logger.info(
                    "[Middleware] Déclenchement async sync catégories "
                    f"via {request.path} => {triggered_categories}"
                )
            except Exception as e:
                logger.error(f"[Middleware] Erreur déclenchement async sync catégories: {str(e)}")
        
        response = self.get_response(request)
        return response

