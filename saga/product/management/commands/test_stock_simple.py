from django.core.management.base import BaseCommand
from product.models import Product, Category

class Command(BaseCommand):
    help = 'Test simple du système de stock (Salam OU Classique)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Test simple du système de stock ==='))
        
        # Récupérer un produit Salam existant
        salam_product = Product.objects.filter(is_salam=True).first()
        if salam_product:
            self.stdout.write(f'\n--- Produit Salam: {salam_product.title} ---')
            status = salam_product.get_stock_status()
            self.stdout.write(f'Type: Salam')
            self.stdout.write(f'Statut: {status["status"]}')
            self.stdout.write(f'Message: {status["message"]}')
            self.stdout.write(f'Disponible: {status["available"]}')
            self.stdout.write(f'Délai: {status["delivery_days"]} jours')
        
        # Créer un produit classique de test
        try:
            cat = Category.objects.get(slug='tous-les-produits')
            classic_product = Product.objects.create(
                title='Test Produit Classique',
                price=50000,
                stock=3,
                is_salam=False,
                salam_delivery_days=14,
                category=cat
            )
            
            self.stdout.write(f'\n--- Produit Classique créé: {classic_product.title} ---')
            status = classic_product.get_stock_status()
            self.stdout.write(f'Type: Classique')
            self.stdout.write(f'Stock: {classic_product.stock}')
            self.stdout.write(f'Statut: {status["status"]}')
            self.stdout.write(f'Message: {status["message"]}')
            self.stdout.write(f'Disponible: {status["available"]}')
            self.stdout.write(f'Délai: {status["delivery_days"]} jours')
            
            # Test de réservation
            old_stock = classic_product.stock
            success = classic_product.reserve_stock(1)
            self.stdout.write(f'Réservation: {"✓" if success else "✗"}')
            if success:
                self.stdout.write(f'Stock avant: {old_stock}, après: {classic_product.stock}')
            
            # Nettoyer le produit de test
            classic_product.delete()
            self.stdout.write('Produit de test supprimé')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Test terminé ===')) 