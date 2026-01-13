"""
Tâches de synchronisation automatique des produits B2B
"""
import logging
import threading
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .services import ProductSyncService, InventoryAPIError
from .models import ApiKey

logger = logging.getLogger(__name__)

_PRODUCTS_LAST_SYNC_KEY = 'b2b_last_sync_time'
_CATEGORIES_LAST_SYNC_KEY = 'b2b_categories_last_sync_time'
_PRODUCTS_LOCK_KEY = 'b2b_sync_products_in_progress'
_CATEGORIES_LOCK_KEY = 'b2b_sync_categories_in_progress'
_LOCK_TTL_SECONDS = 60 * 30  # 30 min (sécurité si crash)


def _min_interval_seconds() -> int:
    """
    Intervalle minimum entre deux synchronisations.
    Réglable via settings.INVENTORY_SYNC_FREQUENCY (minutes).
    """
    try:
        minutes = int(getattr(settings, 'INVENTORY_SYNC_FREQUENCY', 60) or 60)
        return max(60, minutes * 60)  # min 1 minute
    except Exception:
        return 3600


def should_sync_products(ignore_lock: bool = False) -> bool:
    """
    Détermine si une synchronisation est nécessaire
    
    Returns:
        bool: True si une synchronisation est nécessaire
    """
    # Vérifier si une clé API est configurée
    try:
        if not ApiKey.get_active_key():
            logger.warning("Aucune clé API active - synchronisation impossible")
            return False
    except Exception as e:
        logger.error(f"Impossible de récupérer la clé API (produits) : {e}")
        return False

    # Éviter les synchronisations concurrentes
    if not ignore_lock and cache.get(_PRODUCTS_LOCK_KEY):
        logger.info("Synchronisation produits déjà en cours, ignorée")
        return False
    
    # Vérifier le cache pour éviter les synchronisations trop fréquentes
    last_sync = cache.get(_PRODUCTS_LAST_SYNC_KEY)
    if last_sync:
        # Ne pas synchroniser plus souvent que l'intervalle configuré
        time_since_sync = (timezone.now() - last_sync).total_seconds()
        min_seconds = _min_interval_seconds()
        if time_since_sync < min_seconds:
            logger.info(
                f"Synchronisation produits récente ({int(time_since_sync/60)} minutes), ignorée "
                f"(min={int(min_seconds/60)} min)"
            )
            return False
    
    return True


def should_sync_categories(ignore_lock: bool = False) -> bool:
    """
    Détermine si une synchronisation des catégories est nécessaire
    
    Returns:
        bool: True si une synchronisation est nécessaire
    """
    # Vérifier si une clé API est configurée
    try:
        if not ApiKey.get_active_key():
            logger.warning("Aucune clé API active - synchronisation des catégories impossible")
            return False
    except Exception as e:
        logger.error(f"Impossible de récupérer la clé API (catégories) : {e}")
        return False

    # Éviter les synchronisations concurrentes
    if not ignore_lock and cache.get(_CATEGORIES_LOCK_KEY):
        logger.info("Synchronisation catégories déjà en cours, ignorée")
        return False
    
    # Vérifier le cache pour éviter les synchronisations trop fréquentes
    last_sync = cache.get(_CATEGORIES_LAST_SYNC_KEY)
    if last_sync:
        # Ne pas synchroniser plus souvent que l'intervalle configuré
        time_since_sync = (timezone.now() - last_sync).total_seconds()
        min_seconds = _min_interval_seconds()
        if time_since_sync < min_seconds:
            logger.info(
                f"Synchronisation catégories récente ({int(time_since_sync/60)} minutes), ignorée "
                f"(min={int(min_seconds/60)} min)"
            )
            return False
    
    return True


def sync_products_auto(force: bool = False, _lock_acquired: bool = False):
    """
    Synchronise automatiquement les produits B2B
    
    Args:
        force: Si True, force la synchronisation même si récente
    
    Returns:
        dict: Statistiques de synchronisation
    """
    # Prendre un lock (anti-concurrence)
    if not _lock_acquired:
        if not cache.add(_PRODUCTS_LOCK_KEY, True, timeout=_LOCK_TTL_SECONDS):
            return {
                'success': False,
                'message': 'Synchronisation déjà en cours',
                'stats': None
            }

    if not force and not should_sync_products(ignore_lock=True):
        cache.delete(_PRODUCTS_LOCK_KEY)
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
        cache.set(_PRODUCTS_LAST_SYNC_KEY, timezone.now(), 7200)  # Cache pour 2 heures
        
        logger.info(
            f"[SYNC AUTO] Synchronisation automatique terminée: {stats['total']} produits, "
            f"{stats['created']} créés, {stats['updated']} mis à jour, "
            f"{stats.get('errors', 0)} erreurs, {stats.get('skipped', 0)} ignorés"
        )
        
        if stats.get('skipped_reasons'):
            logger.info(f"[SYNC AUTO] Raisons des produits ignorés: {stats['skipped_reasons']}")
        
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
    finally:
        cache.delete(_PRODUCTS_LOCK_KEY)


def sync_categories_auto(force: bool = False, _lock_acquired: bool = False):
    """
    Synchronise automatiquement les catégories B2B
    
    Args:
        force: Si True, force la synchronisation même si récente
    
    Returns:
        dict: Statistiques de synchronisation
    """
    # Prendre un lock (anti-concurrence)
    if not _lock_acquired:
        if not cache.add(_CATEGORIES_LOCK_KEY, True, timeout=_LOCK_TTL_SECONDS):
            return {
                'success': False,
                'message': 'Synchronisation catégories déjà en cours',
                'stats': None
            }

    if not force and not should_sync_categories(ignore_lock=True):
        cache.delete(_CATEGORIES_LOCK_KEY)
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
        cache.set(_CATEGORIES_LAST_SYNC_KEY, timezone.now(), 7200)  # Cache pour 2 heures
        
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
    finally:
        cache.delete(_CATEGORIES_LOCK_KEY)


def trigger_products_sync_async(force: bool = False) -> bool:
    """
    Déclenche une sync produits en arrière-plan (non bloquante).
    Retourne True si un déclenchement a été fait.
    """
    if not force and not should_sync_products():
        return False
    # Lock dès maintenant pour éviter que plusieurs requêtes lancent plusieurs threads
    if not cache.add(_PRODUCTS_LOCK_KEY, True, timeout=_LOCK_TTL_SECONDS):
        return False

    def _run():
        sync_products_auto(force=force, _lock_acquired=True)

    threading.Thread(target=_run, daemon=True).start()
    return True


def trigger_categories_sync_async(force: bool = False) -> bool:
    """
    Déclenche une sync catégories en arrière-plan (non bloquante).
    Retourne True si un déclenchement a été fait.
    """
    if not force and not should_sync_categories():
        return False
    # Lock dès maintenant pour éviter que plusieurs requêtes lancent plusieurs threads
    if not cache.add(_CATEGORIES_LOCK_KEY, True, timeout=_LOCK_TTL_SECONDS):
        return False

    def _run():
        sync_categories_auto(force=force, _lock_acquired=True)

    threading.Thread(target=_run, daemon=True).start()
    return True

