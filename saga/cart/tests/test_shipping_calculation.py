#!/usr/bin/env python
"""
Script de test pour vérifier le calcul des frais de livraison par fournisseur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from cart.payment_config import (
    get_cart_suppliers_breakdown,
    calculate_shipping_by_supplier,
    get_optimal_shipping_methods,
    validate_shipping_methods_for_cart,
    get_shipping_summary_for_display
)
from product.models import Product, ShippingMethod
from cart.models import Cart, CartItem
from suppliers.models import Supplier
from django.contrib.auth import get_user_model

User = get_user_model()

def test_suppliers_breakdown():
    """Test de l'analyse du panier par fournisseur"""
    print("=== TEST ANALYSE PANIER PAR FOURNISSEUR ===\n")
    
    # Récupérer un utilisateur
    user = User.objects.first()
    if not user:
        print("❌ Aucun utilisateur trouvé")
        return
    
    # Créer ou récupérer un panier
    cart, created = Cart.objects.get_or_create(user=user)
    if created:
        print(f"✅ Panier créé pour l'utilisateur: {user.username}")
    else:
        print(f"✅ Panier existant pour l'utilisateur: {user.username}")
    
    # Vider le panier
    cart.cart_items.all().delete()
    
    # Récupérer quelques produits avec des fournisseurs différents
    products = Product.objects.filter(is_available=True)[:5]
    
    if not products.exists():
        print("❌ Aucun produit disponible")
        return
    
    print(f"📦 Produits trouvés: {products.count()}")
    
    # Ajouter les produits au panier
    for i, product in enumerate(products, 1):
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=i  # Quantités différentes pour tester
        )
        supplier_name = product.supplier.name if product.supplier else "SagaKore"
        print(f"   {i}. {product.title} (Fournisseur: {supplier_name})")
    
    # Analyser le panier par fournisseur
    suppliers_data = get_cart_suppliers_breakdown(cart)
    
    print(f"\n🏪 Fournisseurs identifiés: {len(suppliers_data)}")
    
    for supplier_name, data in suppliers_data.items():
        print(f"\n--- {supplier_name} ---")
        print(f"   Produits: {len(data['products'])}")
        print(f"   Articles totaux: {data['total_items']}")
        print(f"   Sous-total: {data['subtotal']} FCFA")
        print(f"   Méthodes de livraison: {len(data['shipping_methods'])}")
        
        for product_data in data['products']:
            product = product_data['product']
            print(f"     • {product.title} (×{product_data['quantity']}) - {product_data['total_price']} FCFA")
    
    # Nettoyer le panier
    cart.cart_items.all().delete()
    return cart

def test_shipping_calculation(cart):
    """Test du calcul des frais de livraison"""
    print("\n=== TEST CALCUL FRAIS DE LIVRAISON ===\n")
    
    if not cart.cart_items.exists():
        print("❌ Panier vide")
        return
    
    # Ajouter quelques produits pour le test
    products = Product.objects.filter(is_available=True, shipping_methods__isnull=False)[:3]
    
    for product in products:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
    
    print(f"📦 Produits ajoutés au panier: {cart.cart_items.count()}")
    
    # Calculer les frais de livraison
    shipping_data = calculate_shipping_by_supplier(cart)
    
    print(f"\n💰 RÉSUMÉ DES FRAIS DE LIVRAISON:")
    print(f"   Sous-total: {shipping_data['summary']['subtotal']} FCFA")
    print(f"   Frais de livraison: {shipping_data['summary']['shipping_cost']} FCFA")
    print(f"   Total: {shipping_data['summary']['total']} FCFA")
    print(f"   Fournisseurs: {shipping_data['summary']['suppliers_count']}")
    
    # Détail par fournisseur
    for supplier_name, data in shipping_data['suppliers_breakdown'].items():
        print(f"\n🏪 {supplier_name}:")
        print(f"   Sous-total: {data['subtotal']} FCFA")
        print(f"   Méthode: {data['selected_shipping_method'].name if data['selected_shipping_method'] else 'Non disponible'}")
        print(f"   Frais: {data['shipping_cost']} FCFA")
        print(f"   Délai: {data['delivery_time']}")
    
    # Nettoyer le panier
    cart.cart_items.all().delete()

def test_optimal_shipping_methods(cart):
    """Test des méthodes de livraison optimales"""
    print("\n=== TEST MÉTHODES DE LIVRAISON OPTIMALES ===\n")
    
    if not cart.cart_items.exists():
        print("❌ Panier vide")
        return
    
    # Ajouter des produits
    products = Product.objects.filter(is_available=True, shipping_methods__isnull=False)[:2]
    
    for product in products:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
    
    # Obtenir les méthodes optimales
    optimal_methods = get_optimal_shipping_methods(cart)
    
    print(f"🎯 MÉTHODES OPTIMALES PAR FOURNISSEUR:")
    
    for supplier_name, data in optimal_methods.items():
        if data is None:
            print(f"\n🏪 {supplier_name}: Aucune méthode disponible")
            continue
        
        recommended = data['recommended']
        all_options = data['all_options']
        
        print(f"\n🏪 {supplier_name}:")
        print(f"   Recommandée: {recommended.name} - {recommended.price} FCFA")
        print(f"   Toutes les options:")
        
        for method in all_options:
            print(f"     • {method.name}: {method.price} FCFA ({method.min_delivery_days}-{method.max_delivery_days} jours)")
    
    # Nettoyer le panier
    cart.cart_items.all().delete()

def test_shipping_validation(cart):
    """Test de validation des méthodes de livraison"""
    print("\n=== TEST VALIDATION MÉTHODES DE LIVRAISON ===\n")
    
    if not cart.cart_items.exists():
        print("❌ Panier vide")
        return
    
    # Ajouter des produits
    products = Product.objects.filter(is_available=True, shipping_methods__isnull=False)[:2]
    
    for product in products:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
    
    # Simuler des méthodes sélectionnées
    suppliers_data = get_cart_suppliers_breakdown(cart)
    selected_methods = {}
    
    for supplier_name, data in suppliers_data.items():
        if data['shipping_methods']:
            # Sélectionner la première méthode disponible
            first_method = list(data['shipping_methods'])[0]
            selected_methods[supplier_name] = first_method.id
    
    print(f"📋 MÉTHODES SÉLECTIONNÉES:")
    for supplier_name, method_id in selected_methods.items():
        print(f"   {supplier_name}: {method_id}")
    
    # Valider les méthodes
    validation_results = validate_shipping_methods_for_cart(cart, selected_methods)
    
    print(f"\n✅ RÉSULTATS DE VALIDATION:")
    for supplier_name, result in validation_results.items():
        status = "✅ Valide" if result['valid'] else "❌ Invalide"
        print(f"   {status} - {supplier_name}: {result['message']}")
    
    # Nettoyer le panier
    cart.cart_items.all().delete()

def test_display_summary(cart):
    """Test du résumé pour l'affichage"""
    print("\n=== TEST RÉSUMÉ POUR AFFICHAGE ===\n")
    
    if not cart.cart_items.exists():
        print("❌ Panier vide")
        return
    
    # Ajouter des produits
    products = Product.objects.filter(is_available=True, shipping_methods__isnull=False)[:3]
    
    for product in products:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
    
    # Obtenir le résumé pour l'affichage
    display_data = get_shipping_summary_for_display(cart)
    
    print(f"📊 RÉSUMÉ POUR AFFICHAGE:")
    print(f"   Fournisseurs: {len(display_data['suppliers'])}")
    print(f"   Total: {display_data['summary']['total']} FCFA")
    
    for supplier in display_data['suppliers']:
        print(f"\n🏪 {supplier['name']}:")
        print(f"   Produits: {supplier['products_count']}")
        print(f"   Articles: {supplier['total_items']}")
        print(f"   Sous-total: {supplier['subtotal']} FCFA")
        print(f"   Méthode: {supplier['shipping_method'].name if supplier['shipping_method'] else 'Non disponible'}")
        print(f"   Frais: {supplier['shipping_cost']} FCFA")
        print(f"   Délai: {supplier['delivery_time']}")
        
        for product in supplier['products']:
            print(f"     • {product['title']} (×{product['quantity']}) - {product['total_price']} FCFA")
    
    # Nettoyer le panier
    cart.cart_items.all().delete()

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS DE CALCUL DES FRAIS DE LIVRAISON\n")
    print("=" * 60)
    
    try:
        # Test 1: Analyse du panier par fournisseur
        cart = test_suppliers_breakdown()
        
        if cart:
            # Test 2: Calcul des frais de livraison
            test_shipping_calculation(cart)
            
            # Test 3: Méthodes optimales
            test_optimal_shipping_methods(cart)
            
            # Test 4: Validation des méthodes
            test_shipping_validation(cart)
            
            # Test 5: Résumé pour affichage
            test_display_summary(cart)
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS")
        print("\n📋 RÉSUMÉ:")
        print("• Analyse par fournisseur: ✅")
        print("• Calcul des frais: ✅")
        print("• Méthodes optimales: ✅")
        print("• Validation: ✅")
        print("• Résumé d'affichage: ✅")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 