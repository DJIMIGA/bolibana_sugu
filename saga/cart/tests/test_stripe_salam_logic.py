#!/usr/bin/env python
"""
Script de test pour vérifier la logique Stripe avec les produits Salam
"""

import os
import sys
import django

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from cart.models import Cart, CartItem, Order
from product.models import Product, ShippingMethod
from accounts.models import ShippingAddress
from django.contrib.auth import get_user_model
from cart.payment_config import get_shipping_summary_for_display

User = get_user_model()

def test_stripe_salam_logic():
    """Test de la logique Stripe avec les produits Salam"""
    
    print("=== Test de la Logique Stripe avec Produits Salam ===\n")
    
    # 1. Vérifier les produits existants
    salam_products = Product.objects.filter(is_salam=True)
    classic_products = Product.objects.filter(is_salam=False)
    
    print(f"✅ Produits Salam trouvés : {salam_products.count()}")
    print(f"✅ Produits classiques trouvés : {classic_products.count()}")
    
    if not salam_products.exists() or not classic_products.exists():
        print("⚠️ Besoin de produits Salam ET classiques pour le test")
        return
    
    # 2. Vérifier les utilisateurs
    users = User.objects.all()
    if not users.exists():
        print("⚠️ Aucun utilisateur trouvé")
        return
    
    user = users.first()
    print(f"✅ Utilisateur de test : {user.email}")
    
    # 3. Créer un panier mixte pour le test
    cart, created = Cart.objects.get_or_create(user=user)
    if created:
        print("✅ Nouveau panier créé")
    else:
        print("✅ Panier existant récupéré")
    
    # Vider le panier
    cart.cart_items.all().delete()
    
    # Ajouter des produits Salam
    for product in salam_products[:2]:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
        print(f"  + Produit Salam ajouté : {product.title}")
    
    # Ajouter des produits classiques
    for product in classic_products[:2]:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
        print(f"  + Produit classique ajouté : {product.title}")
    
    print(f"\n📋 Panier créé avec {cart.cart_items.count()} articles")
    
    # 4. Test du calcul des frais de livraison sur tous les produits
    print("\n=== TEST 1: Frais de livraison sur tous les produits ===")
    try:
        shipping_summary_all = get_shipping_summary_for_display(cart)
        print(f"✅ Frais de livraison (tous produits) : {shipping_summary_all['summary']['shipping_cost']} FCFA")
        print(f"✅ Sous-total (tous produits) : {shipping_summary_all['summary']['subtotal']} FCFA")
        print(f"✅ Total (tous produits) : {shipping_summary_all['summary']['total']} FCFA")
    except Exception as e:
        print(f"❌ Erreur calcul tous produits : {str(e)}")
    
    # 5. Test du calcul des frais de livraison sur les produits Salam seulement
    print("\n=== TEST 2: Frais de livraison sur produits Salam seulement ===")
    try:
        # Créer un panier temporaire avec seulement les produits Salam
        temp_cart_items = cart.cart_items.filter(product__is_salam=True)
        
        # Créer un objet panier temporaire
        temp_cart = type('TempCart', (), {
            'cart_items': type('TempCartItems', (), {
                'all': lambda: temp_cart_items
            })()
        })()
        
        shipping_summary_salam = get_shipping_summary_for_display(temp_cart)
        print(f"✅ Frais de livraison (Salam seulement) : {shipping_summary_salam['summary']['shipping_cost']} FCFA")
        print(f"✅ Sous-total (Salam seulement) : {shipping_summary_salam['summary']['subtotal']} FCFA")
        print(f"✅ Total (Salam seulement) : {shipping_summary_salam['summary']['total']} FCFA")
    except Exception as e:
        print(f"❌ Erreur calcul Salam seulement : {str(e)}")
    
    # 6. Comparaison des résultats
    print("\n=== COMPARAISON DES RÉSULTATS ===")
    if 'shipping_summary_all' in locals() and 'shipping_summary_salam' in locals():
        diff_shipping = shipping_summary_all['summary']['shipping_cost'] - shipping_summary_salam['summary']['shipping_cost']
        diff_subtotal = shipping_summary_all['summary']['subtotal'] - shipping_summary_salam['summary']['subtotal']
        
        print(f"📊 Différence frais de livraison : {diff_shipping} FCFA")
        print(f"📊 Différence sous-total : {diff_subtotal} FCFA")
        
        if diff_shipping == 0:
            print("✅ Les frais de livraison sont identiques (normal si même zone)")
        else:
            print("⚠️ Les frais de livraison diffèrent (normal si zones différentes)")
    
    # 7. Test de la logique de création des line_items
    print("\n=== TEST 3: Création des line_items pour Stripe ===")
    
    # Simuler la création des line_items comme dans create_checkout_session
    line_items = []
    total_amount = 0
    
    # Ajouter tous les produits (comme dans le code modifié)
    for item in cart.cart_items.all():
        line_item = {
            'price_data': {
                'currency': 'xof',
                'product_data': {
                    'name': item.product.title,
                },
                'unit_amount': int(item.product.price),
            },
            'quantity': item.quantity,
        }
        line_items.append(line_item)
        total_amount += item.product.price * item.quantity
        print(f"  + Line item ajouté : {item.product.title} x{item.quantity} = {item.product.price} FCFA")
    
    print(f"✅ Total line_items créés : {len(line_items)}")
    print(f"✅ Montant total des produits : {total_amount} FCFA")
    
    # 8. Simulation du webhook
    print("\n=== TEST 4: Simulation du traitement webhook ===")
    
    # Simuler product_type = 'salam'
    product_type = 'salam'
    
    if product_type == 'salam':
        # Calculer le subtotal seulement sur les produits Salam
        salam_subtotal = sum(item.get_total_price() for item in cart.cart_items.filter(product__is_salam=True))
        salam_count = cart.cart_items.filter(product__is_salam=True).count()
        
        print(f"✅ Produits Salam à traiter : {salam_count}")
        print(f"✅ Subtotal Salam : {salam_subtotal} FCFA")
        
        # Utiliser les frais de livraison calculés sur Salam seulement
        if 'shipping_summary_salam' in locals():
            shipping_cost = shipping_summary_salam['summary']['shipping_cost']
            total_salam = salam_subtotal + shipping_cost
            
            print(f"✅ Frais de livraison appliqués : {shipping_cost} FCFA")
            print(f"✅ Total commande Salam : {total_salam} FCFA")
            
            # Vérifier la cohérence
            if total_amount >= total_salam:
                print("✅ Cohérence vérifiée : Le total Stripe couvre la commande Salam")
            else:
                print("⚠️ Attention : Le total Stripe ne couvre pas la commande Salam")
    
    # 9. Nettoyage
    print("\n=== NETTOYAGE ===")
    cart.delete()
    print("✅ Panier de test supprimé")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_stripe_salam_logic() 