#!/usr/bin/env python
"""
Script de test pour vérifier la configuration des méthodes de paiement
"""

import os
import sys
import django

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from cart.payment_config import (
    get_available_payment_methods, 
    get_payment_method_display_name,
    is_payment_method_available,
    get_disabled_method_message
)

def test_payment_config():
    """Test de la configuration des méthodes de paiement"""
    
    print("=== Test de la Configuration des Méthodes de Paiement ===\n")
    
    # Test 1: Méthodes disponibles
    available_methods = get_available_payment_methods()
    print(f"✅ Méthodes de paiement disponibles : {available_methods}")
    
    # Test 2: Noms d'affichage
    print("\n📋 Noms d'affichage :")
    for method in ['online_payment', 'mobile_money', 'cash_on_delivery']:
        display_name = get_payment_method_display_name(method)
        is_available = is_payment_method_available(method)
        status = "✅ Disponible" if is_available else "❌ Indisponible"
        print(f"  - {method} → {display_name} ({status})")
    
    # Test 3: Messages pour méthodes désactivées
    print("\n⚠️ Messages pour méthodes désactivées :")
    for method in ['mobile_money', 'online_payment']:
        if not is_payment_method_available(method):
            message = get_disabled_method_message(method)
            print(f"  - {method} : {message['title']}")
            print(f"    {message['message']}")
    
    # Test 4: Résumé
    print(f"\n📊 Résumé :")
    print(f"  - Total méthodes configurées : 3")
    print(f"  - Méthodes disponibles : {len(available_methods)}")
    print(f"  - Méthodes indisponibles : {3 - len(available_methods)}")
    
    if 'mobile_money' not in available_methods:
        print("\n🔧 Orange Money est actuellement désactivé.")
        print("   Pour le réactiver, modifiez MOBILE_MONEY_ENABLED = True dans payment_config.py")
    else:
        print("\n🔧 Orange Money est actuellement activé.")
    
    print("\n=== Fin du test ===")

if __name__ == "__main__":
    test_payment_config() 