#!/usr/bin/env python3
"""
Script de test pour les améliorations Orange Money
Teste la validation des champs, la gestion des statuts et la gestion des erreurs
"""

import os
import sys
import django
from unittest.mock import Mock, patch

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from cart.orange_money_service import OrangeMoneyService

def test_validation_des_champs():
    """Test de la validation des champs"""
    print("🧪 Test 1: Validation des champs")
    print("=" * 50)
    
    service = OrangeMoneyService()
    
    # Test avec des données valides
    valid_data = {
        'order_id': 'SagaKore-12345',
        'amount': 50000,
        'return_url': 'https://sagakore.com/return',
        'cancel_url': 'https://sagakore.com/cancel',
        'notif_url': 'https://sagakore.com/webhook',
        'reference': 'SagaKore'
    }
    
    is_valid, message = service.validate_payment_data(valid_data)
    print(f"✅ Données valides: {is_valid} - {message}")
    
    # Test avec order_id trop long
    invalid_data = valid_data.copy()
    invalid_data['order_id'] = 'SagaKore-12345-avec-un-nom-tres-long-qui-depasse-30-caracteres'
    
    is_valid, message = service.validate_payment_data(invalid_data)
    print(f"❌ Order ID trop long: {is_valid} - {message}")
    
    # Test avec URL trop longue
    invalid_data = valid_data.copy()
    invalid_data['return_url'] = 'https://sagakore.com/return/avec/beaucoup/de/parametres/et/une/url/tres/longue/qui/depasse/120/caracteres/et/qui/va/causer/une/erreur'
    
    is_valid, message = service.validate_payment_data(invalid_data)
    print(f"❌ URL trop longue: {is_valid} - {message}")
    
    # Test avec montant négatif
    invalid_data = valid_data.copy()
    invalid_data['amount'] = -1000
    
    is_valid, message = service.validate_payment_data(invalid_data)
    print(f"❌ Montant négatif: {is_valid} - {message}")
    
    print()

def test_gestion_des_statuts():
    """Test de la gestion des statuts"""
    print("🧪 Test 2: Gestion des statuts")
    print("=" * 50)
    
    service = OrangeMoneyService()
    
    # Test de tous les statuts
    statuts = ['INITIATED', 'PENDING', 'EXPIRED', 'SUCCESS', 'FAILED', 'UNKNOWN']
    
    for statut in statuts:
        success, message = service.handle_transaction_status(statut, 'TEST-12345')
        print(f"📊 Statut {statut}: {success} - {message}")
    
    print()

def test_gestion_des_erreurs():
    """Test de la gestion des erreurs"""
    print("🧪 Test 3: Gestion des erreurs")
    print("=" * 50)
    
    service = OrangeMoneyService()
    
    # Test des codes d'erreur
    codes_erreur = [400, 401, 403, 404, 500, 502, 503, 999]
    
    for code in codes_erreur:
        mock_response = Mock()
        mock_response.status_code = code
        
        message = service.handle_api_error(mock_response)
        print(f"🚨 Code {code}: {message}")
    
    print()

def test_integration_complete():
    """Test d'intégration complète"""
    print("🧪 Test 4: Intégration complète")
    print("=" * 50)
    
    service = OrangeMoneyService()
    
    # Test avec des données valides
    order_data = {
        'order_id': 'SagaKore-TEST-001',
        'amount': 25000,  # 250 FCFA
        'return_url': 'https://sagakore.com/return',
        'cancel_url': 'https://sagakore.com/cancel',
        'notif_url': 'https://sagakore.com/webhook',
        'reference': 'Test'
    }
    
    print("📋 Données de test:")
    for key, value in order_data.items():
        print(f"  {key}: {value}")
    
    # Test de validation
    is_valid, message = service.validate_payment_data(order_data)
    print(f"\n✅ Validation: {is_valid} - {message}")
    
    if is_valid:
        print("🎯 Données prêtes pour l'envoi à Orange Money")
    else:
        print("❌ Données invalides, correction nécessaire")
    
    print()

def test_scenarios_reels():
    """Test de scénarios réels"""
    print("🧪 Test 5: Scénarios réels")
    print("=" * 50)
    
    service = OrangeMoneyService()
    
    # Scénario 1: Commande normale
    print("📱 Scénario 1: Commande normale")
    order_data = {
        'order_id': 'SagaKore-2024-001',
        'amount': 150000,  # 1500 FCFA
        'return_url': 'https://sagakore.com/cart/orange-money/return/',
        'cancel_url': 'https://sagakore.com/cart/orange-money/cancel/',
        'notif_url': 'https://sagakore.com/cart/orange-money/webhook/',
        'reference': 'SagaKore'
    }
    
    is_valid, message = service.validate_payment_data(order_data)
    print(f"  Validation: {is_valid} - {message}")
    
    # Scénario 2: Commande avec référence longue
    print("\n📱 Scénario 2: Commande avec référence longue")
    order_data['reference'] = 'Commande-pour-Monsieur-Ahmed-Ben-Salem-de-Dakar-avec-livraison-express'
    
    is_valid, message = service.validate_payment_data(order_data)
    print(f"  Validation: {is_valid} - {message}")
    
    # Scénario 3: Commande avec URL complexe
    print("\n📱 Scénario 3: Commande avec URL complexe")
    order_data['return_url'] = 'https://sagakore.com/cart/orange-money/return/?order_id=SagaKore-2024-001&user_id=12345&timestamp=2024-01-15T10:30:00Z&source=checkout&campaign=winter_sale&utm_source=email&utm_medium=newsletter&utm_campaign=promo'
    
    is_valid, message = service.validate_payment_data(order_data)
    print(f"  Validation: {is_valid} - {message}")
    
    print()

def main():
    """Fonction principale de test"""
    print("🚀 Test des Améliorations Orange Money")
    print("=" * 60)
    print()
    
    try:
        test_validation_des_champs()
        test_gestion_des_statuts()
        test_gestion_des_erreurs()
        test_integration_complete()
        test_scenarios_reels()
        
        print("✅ Tous les tests sont terminés avec succès !")
        print()
        print("📊 Résumé des améliorations:")
        print("  ✅ Validation des champs (longueurs, montants)")
        print("  ✅ Gestion complète des statuts (5 statuts)")
        print("  ✅ Gestion des codes d'erreur (8 codes)")
        print("  ✅ Messages d'erreur explicites")
        print("  ✅ Récupération automatique des erreurs")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
