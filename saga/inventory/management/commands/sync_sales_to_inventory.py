"""
Commande de management pour synchroniser les ventes vers l'app de gestion

Note: Cette fonctionnalité a été désactivée suite à la simplification de l'app inventory.
La synchronisation des ventes doit être gérée manuellement via l'API.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Synchronise les ventes en attente vers l\'app de gestion de stock (DÉSACTIVÉ)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                '⚠️  La synchronisation automatique des ventes a été désactivée.\n'
                'Utilisez l\'API directement pour synchroniser les ventes.'
            )
        )
