"""
Signaux Django pour la synchronisation automatique des ventes

Note: La synchronisation automatique des ventes a été désactivée
suite à la simplification de l'app inventory.
"""
import logging
from django.db import transaction
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from cart.models import Order
from product.models import Product
from inventory.models import ApiKey, ExternalProduct

logger = logging.getLogger(__name__)


def _cleanup_products_for_api_key(api_key_id: int, reason: str):
    """
    Désactive les produits liés à une clé API et marque la synchro en attente.
    """
    qs = ExternalProduct.objects.filter(api_key_id=api_key_id).select_related('product')
    count = qs.count()
    if count == 0:
        logger.info(f"[ApiKey Cleanup] Aucun produit lié à la clé {api_key_id}")
        return

    product_ids = list(qs.values_list('product_id', flat=True))
    Product.objects.filter(id__in=product_ids).update(is_available=False)
    qs.update(sync_status='pending', sync_error=reason)
    logger.warning(
        f"[ApiKey Cleanup] {count} produits désactivés (api_key_id={api_key_id}) - {reason}"
    )


@receiver(post_save, sender=Order)
def sync_order_to_inventory(sender, instance, created, **kwargs):
    """
    Signal pour synchroniser automatiquement une commande vers l'app de gestion
    
    Note: Cette fonctionnalité a été désactivée suite à la simplification.
    La synchronisation doit être faite manuellement ou via des commandes de management.
    
    Args:
        sender: Classe Order
        instance: Instance de Order
        created: True si la commande vient d'être créée
        **kwargs: Arguments supplémentaires
    """
    # Fonctionnalité désactivée - pas de synchronisation automatique
    pass


@receiver(pre_save, sender=ApiKey)
def apikey_store_previous_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_is_active = None
        return
    previous = ApiKey.objects.filter(pk=instance.pk).values_list('is_active', flat=True).first()
    instance._previous_is_active = previous


@receiver(post_save, sender=ApiKey)
def apikey_cleanup_on_disable(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_is_active', None)
    if previous is True and instance.is_active is False:
        reason = "Clé API désactivée"
        transaction.on_commit(lambda: _cleanup_products_for_api_key(instance.id, reason))


@receiver(post_delete, sender=ApiKey)
def apikey_cleanup_on_delete(sender, instance, **kwargs):
    reason = "Clé API supprimée"
    transaction.on_commit(lambda: _cleanup_products_for_api_key(instance.id, reason))
