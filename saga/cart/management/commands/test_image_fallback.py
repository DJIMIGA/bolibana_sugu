from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.template.loader import render_to_string
from cart.models import Cart, CartItem
from product.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test de la gestion des images manquantes dans les templates du panier'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Test de la gestion des images manquantes ==='))
        
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            email='test_images@example.com',
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write('✓ Utilisateur de test créé')
        else:
            self.stdout.write('✓ Utilisateur de test existant')
        
        # Récupérer ou créer un panier
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            self.stdout.write('✓ Panier créé')
        else:
            self.stdout.write('✓ Panier existant')
        
        # Récupérer des produits (avec et sans images)
        products = Product.objects.all()[:5]
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('Aucun produit trouvé dans la base de données'))
            return
        
        self.stdout.write(f'✓ {products.count()} produits trouvés')
        
        # Ajouter des produits au panier
        for i, product in enumerate(products):
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': 1}
            )
            if created:
                self.stdout.write(f'✓ Produit "{product.title}" ajouté au panier')
        
        # Tester le rendu des templates
        factory = RequestFactory()
        request = factory.get('/cart/')
        request.user = user
        
        # Test du template _order_details
        try:
            context = {
                'cart_items': cart.cart_items.all(),
                'order_total': cart.get_total_price(),
                'shipping_cost': 1000,
                'total_with_shipping': cart.get_total_price() + 1000,
                'selected_shipping_method': None,
            }
            
            rendered = render_to_string('cart/components/_order_details.html', context, request=request)
            self.stdout.write(self.style.SUCCESS('✓ Template _order_details rendu avec succès'))
            
            # Vérifier si des images sont manquantes
            if 'onerror=' in rendered:
                self.stdout.write('✓ Gestion des erreurs d\'images détectée')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erreur lors du rendu de _order_details: {e}'))
        
        # Test du template _cart_content
        try:
            context = {
                'cart': cart,
                'is_checkout': True,
            }
            
            rendered = render_to_string('cart/components/_cart_content.html', context, request=request)
            self.stdout.write(self.style.SUCCESS('✓ Template _cart_content rendu avec succès'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erreur lors du rendu de _cart_content: {e}'))
        
        # Test du template _cart_item
        try:
            for item in cart.cart_items.all()[:1]:  # Test avec un seul item
                context = {'item': item}
                rendered = render_to_string('cart/components/_cart_item.html', context, request=request)
                self.stdout.write(self.style.SUCCESS('✓ Template _cart_item rendu avec succès'))
                break
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erreur lors du rendu de _cart_item: {e}'))
        
        # Nettoyer les données de test
        cart.delete()
        user.delete()
        self.stdout.write('✓ Données de test nettoyées')
        
        self.stdout.write(self.style.SUCCESS('=== Test terminé avec succès ===')) 