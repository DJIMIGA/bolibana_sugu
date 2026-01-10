"""
Signaux Django pour la synchronisation automatique des ventes

Note: La synchronisation automatique des ventes a été désactivée
suite à la simplification de l'app inventory.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from cart.models import Order

logger = logging.getLogger(__name__)


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
