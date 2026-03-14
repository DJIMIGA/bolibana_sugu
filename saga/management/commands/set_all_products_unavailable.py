from django.core.management.base import BaseCommand
from django.db import transaction
from product.models import Product


class Command(BaseCommand):
    help = 'Met tous les produits is_available=False dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirme l\'exécution de la commande',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans effectuer les modifications',
        )

    def handle(self, *args, **options):
        # Compter les produits actuellement disponibles
        total_products = Product.objects.count()
        available_products = Product.objects.filter(is_available=True).count()
        unavailable_products = Product.objects.filter(is_available=False).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Statistiques actuelles des produits:'
            )
        )
        self.stdout.write(f'   • Total des produits: {total_products}')
        self.stdout.write(f'   • Produits disponibles: {available_products}')
        self.stdout.write(f'   • Produits non disponibles: {unavailable_products}')
        self.stdout.write('')

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    '🔍 MODE DRY-RUN - Aucune modification ne sera effectuée'
                )
            )
            self.stdout.write(
                f'   • {available_products} produits seraient mis is_available=False'
            )
            self.stdout.write(
                f'   • {unavailable_products} produits resteraient is_available=False'
            )
            return

        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    '⚠️  ATTENTION: Cette action va mettre TOUS les produits is_available=False!'
                )
            )
            self.stdout.write('')
            self.stdout.write(
                'Pour confirmer, utilisez l\'option --confirm'
            )
            self.stdout.write('')
            self.stdout.write(
                'Exemple: python manage.py set_all_products_unavailable --confirm'
            )
            return

        # Confirmation finale
        self.stdout.write(
            self.style.WARNING(
                '🚨 CONFIRMATION FINALE:'
            )
        )
        self.stdout.write(
            f'   • {available_products} produits vont être mis is_available=False'
        )
        self.stdout.write(
            '   • Cette action est IRREVERSIBLE!'
        )
        self.stdout.write('')

        # Demander une confirmation supplémentaire
        user_input = input('Tapez "CONFIRM" pour continuer: ')
        if user_input != 'CONFIRM':
            self.stdout.write(
                self.style.ERROR('❌ Opération annulée par l\'utilisateur')
            )
            return

        try:
            with transaction.atomic():
                # Mettre à jour tous les produits
                updated_count = Product.objects.filter(
                    is_available=True
                ).update(is_available=False)

                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ SUCCÈS: {updated_count} produits ont été mis is_available=False'
                    )
                )

                # Vérifier le résultat
                new_available = Product.objects.filter(is_available=True).count()
                new_unavailable = Product.objects.filter(is_available=False).count()

                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        '📊 Nouvelles statistiques:'
                    )
                )
                self.stdout.write(f'   • Produits disponibles: {new_available}')
                self.stdout.write(f'   • Produits non disponibles: {new_unavailable}')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(
                self.style.ERROR(
                    f'❌ ERREUR lors de la mise à jour: {str(e)}'
                )
            )
            raise

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                '🎉 Opération terminée avec succès!'
            )
        )
