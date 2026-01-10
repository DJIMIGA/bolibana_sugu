"""
Tâches de synchronisation automatique des produits B2B
"""
import logging
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from .services import ProductSyncService, InventoryAPIError
from .models import ApiKey

logger = logging.getLogger(__name__)


def should_sync_products():
    """
    Détermine si une synchronisation est nécessaire
    
    Returns:
        bool: True si une synchronisation est nécessaire
    """
    # Vérifier si une clé API est configurée
    if not ApiKey.get_active_key():
        logger.warning("Aucune clé API active - synchronisation impossible")
        return False
    
    # Vérifier le cache pour éviter les synchronisations trop fréquentes
    last_sync = cache.get('b2b_last_sync_time')
    if last_sync:
        # Ne pas synchroniser plus d'une fois par heure
        time_since_sync = (timezone.now() - last_sync).total_seconds()
        if time_since_sync < 3600:  # 1 heure
            logger.info(f"Synchronisation récente ({int(time_since_sync/60)} minutes), ignorée")
            return False
    
    return True


def should_sync_categories():
    """
    Détermine si une synchronisation des catégories est nécessaire
    
    Returns:
        bool: True si une synchronisation est nécessaire
    """
    # Vérifier si une clé API est configurée
    if not ApiKey.get_active_key():
        logger.warning("Aucune clé API active - synchronisation des catégories impossible")
        return False
    
    # Vérifier le cache pour éviter les synchronisations trop fréquentes
    last_sync = cache.get('b2b_categories_last_sync_time')
    if last_sync:
        # Ne pas synchroniser plus d'une fois par heure
        time_since_sync = (timezone.now() - last_sync).total_seconds()
        if time_since_sync < 3600:  # 1 heure
            logger.info(f"Synchronisation des catégories récente ({int(time_since_sync/60)} minutes), ignorée")
            return False
    
    return True


def sync_products_auto(force=False):
    """
    Synchronise automatiquement les produits B2B
    
    Args:
        force: Si True, force la synchronisation même si récente
    
    Returns:
        dict: Statistiques de synchronisation
    """
    if not force and not should_sync_products():
        return {
            'success': False,
            'message': 'Synchronisation non nécessaire ou trop récente',
            'stats': None
        }
    
    try:
        logger.info("Démarrage de la synchronisation automatique des produits B2B")
        
        sync_service = ProductSyncService()
        stats = sync_service.sync_all_products()
        
        # Mettre à jour le cache avec l'heure de synchronisation
        cache.set('b2b_last_sync_time', timezone.now(), 7200)  # Cache pour 2 heures
        
        logger.info(
            f"Synchronisation automatique terminée: {stats['total']} produits, "
            f"{stats['created']} créés, {stats['updated']} mis à jour"
        )
        
        return {
            'success': True,
            'message': 'Synchronisation réussie',
            'stats': stats
        }
        
    except InventoryAPIError as e:
        logger.error(f"Erreur API lors de la synchronisation automatique: {str(e)}")
        return {
            'success': False,
            'message': f'Erreur API: {str(e)}',
            'stats': None
        }
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation automatique: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': f'Erreur: {str(e)}',
            'stats': None
        }


def sync_categories_auto(force=False):
    """
    Synchronise automatiquement les catégories B2B
    
    Args:
        force: Si True, force la synchronisation même si récente
    
    Returns:
        dict: Statistiques de synchronisation
    """
    if not force and not should_sync_categories():
        return {
            'success': False,
            'message': 'Synchronisation des catégories non nécessaire ou trop récente',
            'stats': None
        }
    
    try:
        logger.info("Démarrage de la synchronisation automatique des catégories B2B")
        
        sync_service = ProductSyncService()
        stats = sync_service.sync_categories()
        
        # Mettre à jour le cache avec l'heure de synchronisation
        cache.set('b2b_categories_last_sync_time', timezone.now(), 7200)  # Cache pour 2 heures
        
        logger.info(
            f"Synchronisation automatique des catégories terminée: {stats['total']} catégories, "
            f"{stats['created']} créées, {stats['updated']} mises à jour"
        )
        
        return {
            'success': True,
            'message': 'Synchronisation réussie',
            'stats': stats
        }
        
    except InventoryAPIError as e:
        logger.error(f"Erreur API lors de la synchronisation automatique des catégories: {str(e)}")
        return {
            'success': False,
            'message': f'Erreur API: {str(e)}',
            'stats': None
        }
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation automatique des catégories: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': f'Erreur: {str(e)}',
            'stats': None
        }

