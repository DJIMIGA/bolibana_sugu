from django.core.management.base import BaseCommand
from product.models import Product

class Command(BaseCommand):
    help = 'Vérifie les produits salam'

    def handle(self, *args, **options):
        # Vérifier le nombre total de produits
        total_products = Product.objects.count()
        self.stdout.write(f'Nombre total de produits: {total_products}')

        # Vérifier les produits salam
        salam_products = Product.objects.filter(is_salam=True)
        self.stdout.write(f'Nombre de produits salam: {salam_products.count()}')

        # Afficher les détails des produits salam
        self.stdout.write('\nDétails des produits salam:')
        for product in salam_products:
            self.stdout.write(f'- {product.title} (ID: {product.id}, Prix: {product.price})') 