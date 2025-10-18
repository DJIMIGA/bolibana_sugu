#!/usr/bin/env python3
"""
Script de diagnostic pour l'erreur 500 sur l'URL de retour Orange Money
"""

import os
import sys
import django
from unittest.mock import Mock, patch

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from cart.orange_money_service import OrangeMoneyService
from cart.models import Order, Cart
from product.models import Product

User = get_user_model()

def test_orange_money_return_scenarios():
    """Test des différents scénarios de retour Orange Money"""
    print("🔍 Diagnostic Orange Money Return - Erreur 500")
    print("=" * 60)
    
    # Créer un client de test
    client = Client()
    
    # Scénario 1: Session vide
    print("\n📋 Scénario 1: Session vide")
    print("-" * 30)
    response = client.get('/cart/orange-money/return/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("❌ Erreur 500 détectée - Session vide")
    else:
        print("✅ Pas d'erreur 500")
    
    # Scénario 2: Session avec données invalides
    print("\n📋 Scénario 2: Session avec données invalides")
    print("-" * 30)
    session = client.session
    session['orange_money_order_id'] = 99999  # ID inexistant
    session['orange_money_pay_token'] = 'invalid_token'
    session.save()
    
    response = client.get('/cart/orange-money/return/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("❌ Erreur 500 détectée - Données invalides")
    else:
        print("✅ Pas d'erreur 500")
    
    # Scénario 3: Test avec utilisateur et commande valides
    print("\n📋 Scénario 3: Test avec données valides")
    print("-" * 30)
    
    try:
        # Créer un utilisateur de test
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer une commande de test
        order = Order.objects.create(
            user=user,
            subtotal=50000,
            shipping_cost=0,
            total=50000,
            payment_method=Order.MOBILE_MONEY,
            status=Order.PENDING
        )
        
        # Se connecter avec l'utilisateur
        client.force_login(user)
        
        # Configurer la session
        session = client.session
        session['orange_money_order_id'] = order.id
        session['orange_money_pay_token'] = 'test_pay_token_123'
        session.save()
        
        # Tester l'URL de retour
        response = client.get('/cart/orange-money/return/')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ Erreur 500 détectée - Données valides")
            print("Contenu de la réponse:")
            print(response.content.decode()[:500])
        else:
            print("✅ Pas d'erreur 500 avec données valides")
        
        # Nettoyer
        order.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_orange_money_service_methods():
    """Test des méthodes du service Orange Money"""
    print("\n🔧 Test des méthodes Orange Money Service")
    print("=" * 60)
    
    service = OrangeMoneyService()
    
    # Test 1: Validation des données
    print("\n📋 Test 1: Validation des données")
    print("-" * 30)
    
    test_data = {
        'order_id': 'SagaKore-TEST-001',
        'amount': 50000,
        'return_url': 'https://sagakore.com/return',
        'cancel_url': 'https://sagakore.com/cancel',
        'notif_url': 'https://sagakore.com/webhook',
        'reference': 'Test'
    }
    
    is_valid, message = service.validate_payment_data(test_data)
    print(f"Validation: {is_valid} - {message}")
    
    # Test 2: Gestion des statuts
    print("\n📋 Test 2: Gestion des statuts")
    print("-" * 30)
    
    statuts = ['SUCCESS', 'FAILED', 'PENDING', 'EXPIRED', 'INITIATED']
    for statut in statuts:
        success, message = service.handle_transaction_status(statut, 'TEST-001')
        print(f"Statut {statut}: {success} - {message}")
    
    # Test 3: Gestion des erreurs
    print("\n📋 Test 3: Gestion des erreurs")
    print("-" * 30)
    
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code
    
    for code in [400, 401, 500]:
        mock_response = MockResponse(code)
        try:
            message = service.handle_api_error(mock_response)
            print(f"Code {code}: {message}")
        except Exception as e:
            print(f"Code {code}: Erreur - {str(e)}")

def test_url_routing():
    """Test du routage des URLs"""
    print("\n🛣️ Test du routage des URLs")
    print("=" * 60)
    
    from django.urls import reverse, NoReverseMatch
    
    try:
        # Test des URLs Orange Money
        urls_to_test = [
            'cart:orange_money_payment',
            'cart:orange_money_return',
            'cart:orange_money_cancel',
            'cart:orange_money_webhook'
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name}: {url}")
            except NoReverseMatch as e:
                print(f"❌ {url_name}: Erreur - {str(e)}")
                
    except Exception as e:
        print(f"❌ Erreur lors du test des URLs: {str(e)}")

def main():
    """Fonction principale de diagnostic"""
    print("🚀 Diagnostic Orange Money Return - Erreur 500")
    print("=" * 70)
    
    try:
        test_orange_money_service_methods()
        test_url_routing()
        test_orange_money_return_scenarios()
        
        print("\n✅ Diagnostic terminé")
        print("\n📊 Recommandations:")
        print("1. Vérifier les logs Django pour plus de détails")
        print("2. S'assurer que l'utilisateur est connecté")
        print("3. Vérifier que la session contient les bonnes données")
        print("4. Tester avec des données Orange Money valides")
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
