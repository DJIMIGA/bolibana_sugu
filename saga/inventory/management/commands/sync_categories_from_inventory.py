"""
Commande de management pour synchroniser les catégories depuis l'app de gestion
"""
from django.core.management.base import BaseCommand
from inventory.services import ProductSyncService
from inventory.tasks import sync_categories_auto


class Command(BaseCommand):
    help = 'Synchronise les catégories depuis l\'app de gestion de stock'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Mode automatique : utilise la synchronisation automatique avec gestion du cache',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la synchronisation même si récente (utilisé avec --auto)',
        )

    def handle(self, *args, **options):
        auto_mode = options.get('auto', False)
        force = options.get('force', False)

        if auto_mode:
            self.stdout.write('Synchronisation automatique des catégories depuis B2B...')
            
            try:
                result = sync_categories_auto(force=force)
                
                if result['success']:
                    stats = result['stats']
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Synchronisation terminée: {stats["total"]} catégories traitées, '
                            f'{stats["created"]} créées, {stats["updated"]} mises à jour, '
                            f'{stats["errors"]} erreurs'
                        )
                    )
                    
                    if stats['errors'] > 0:
                        self.stdout.write(self.style.WARNING(f'Erreurs: {stats["errors_list"]}'))
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Synchronisation: {result["message"]}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erreur lors de la synchronisation: {str(e)}')
                )
        else:
            self.stdout.write('Synchronisation manuelle des catégories depuis B2B...')
            
            try:
                sync_service = ProductSyncService()
                stats = sync_service.sync_categories()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Synchronisation terminée: {stats["total"]} catégories traitées, '
                        f'{stats["created"]} créées, {stats["updated"]} mises à jour, '
                        f'{stats["errors"]} erreurs'
                    )
                )
                
                if stats['errors'] > 0:
                    self.stdout.write(self.style.WARNING(f'Erreurs: {stats["errors_list"]}'))
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erreur lors de la synchronisation: {str(e)}')
                )
