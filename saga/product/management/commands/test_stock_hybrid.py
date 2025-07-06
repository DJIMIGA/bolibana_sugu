from django.core.management.base import BaseCommand
from product.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test du système de stock simplifié (Salam OU Classique)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Test du système de stock simplifié ==='))
        
        # Récupérer quelques produits pour les tests
        products = Product.objects.all()[:5]
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('Aucun produit trouvé dans la base de données'))
            return
        
        self.stdout.write(f'✓ {products.count()} produits trouvés pour les tests')
        
        for i, product in enumerate(products, 1):
            self.stdout.write(f'\n--- Produit {i}: {product.title} ---')
            
            # Afficher les informations de stock actuelles
            self.stdout.write(f'Type: {"Salam" if product.is_salam else "Classique"}')
            self.stdout.write(f'Stock classique: {product.stock}')
            self.stdout.write(f'Délai Salam: {product.salam_delivery_days} jours')
            
            # Tester les méthodes de statut
            status = product.get_stock_status()
            self.stdout.write(f'Statut: {status["status"]}')
            self.stdout.write(f'Message: {status["message"]}')
            self.stdout.write(f'Disponible: {status["available"]}')
            self.stdout.write(f'Type de stock: {status["stock_type"]}')
            
            # Tester les méthodes de vérification
            self.stdout.write(f'Peut commander: {product.can_order()}')
            self.stdout.write(f'A du stock: {product.has_stock()}')
            self.stdout.write(f'Délai estimé: {product.get_delivery_estimate()} jours')
            
            # Tester l'affichage
            self.stdout.write(f'Affichage: {product.get_stock_display()}')
        
        # Test de simulation de commande
        self.stdout.write('\n=== Test de simulation de commande ===')
        test_product = products.first()
        if test_product:
            self.stdout.write(f'Produit test: {test_product.title}')
            
            # Simuler une commande
            if test_product.can_order():
                if test_product.is_salam:
                    self.stdout.write(f'Commande Salam possible: ✓')
                    self.stdout.write(f'Délai de livraison: {test_product.salam_delivery_days} jours')
                else:
                    old_stock = test_product.stock
                    success = test_product.reserve_stock(1)
                    self.stdout.write(f'Réservation classique: {"✓" if success else "✗"}')
                    if success:
                        self.stdout.write(f'Stock avant: {old_stock}, après: {test_product.stock}')
            else:
                self.stdout.write('Commande impossible: ✗')
        
        self.stdout.write(self.style.SUCCESS('\n=== Test terminé avec succès ===')) 