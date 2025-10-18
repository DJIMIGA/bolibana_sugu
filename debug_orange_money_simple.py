#!/usr/bin/env python3
"""
Diagnostic simple pour l'erreur 500 Orange Money Return
"""

import os
import sys

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_orange_money_return_logic():
    """Test de la logique de retour Orange Money"""
    print("🔍 Diagnostic Orange Money Return - Erreur 500")
    print("=" * 60)
    
    # Simuler les données de session
    print("\n📋 Simulation des données de session")
    print("-" * 40)
    
    # Scénario 1: Session vide
    print("Scénario 1: Session vide")
    order_id = None
    pay_token = None
    
    if not order_id or not pay_token:
        print("❌ Session de paiement invalide - Redirection vers panier")
    else:
        print("✅ Session valide")
    
    # Scénario 2: Session avec données
    print("\nScénario 2: Session avec données")
    order_id = 123
    pay_token = "test_token_123"
    
    if not order_id or not pay_token:
        print("❌ Session de paiement invalide")
    else:
        print("✅ Session valide - Traitement de la commande")
        
        # Simuler la récupération de la commande
        try:
            # Simuler une commande
            order = {
                'id': order_id,
                'order_number': 'SagaKore-2024-001',
                'total': 50000.0,
                'user_id': 1
            }
            print(f"✅ Commande trouvée: {order['order_number']}")
            
            # Simuler la vérification du statut
            print("🔄 Vérification du statut Orange Money...")
            
            # Simuler différents statuts
            statuts_test = ['SUCCESS', 'FAILED', 'PENDING', 'EXPIRED']
            
            for statut in statuts_test:
                print(f"\n  Test statut: {statut}")
                
                if statut == 'SUCCESS':
                    print("    ✅ Paiement réussi - Mise à jour commande")
                    print("    ✅ Panier vidé")
                    print("    ✅ Session nettoyée")
                    print("    ✅ Redirection vers succès")
                else:
                    print(f"    ⚠️ Statut: {statut} - Redirection vers détail commande")
                    
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {str(e)}")

def test_common_errors():
    """Test des erreurs communes"""
    print("\n🚨 Test des erreurs communes")
    print("=" * 60)
    
    errors = [
        "Order.DoesNotExist",
        "AttributeError: 'NoneType' object has no attribute 'order_number'",
        "KeyError: 'status'",
        "TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'",
        "ValueError: invalid literal for int()",
        "ConnectionError: Failed to connect to Orange Money API"
    ]
    
    for error in errors:
        print(f"❌ {error}")
        print("   → Vérifier la gestion d'erreur dans la vue")
        print("   → Ajouter des logs de debug")
        print("   → Tester avec des données valides")
        print()

def test_recommendations():
    """Recommandations pour corriger l'erreur 500"""
    print("\n💡 Recommandations pour corriger l'erreur 500")
    print("=" * 60)
    
    recommendations = [
        {
            "problème": "Session vide ou invalide",
            "solution": "Vérifier la présence des données de session avant traitement",
            "code": "if not order_id or not pay_token: return redirect('cart:cart')"
        },
        {
            "problème": "Commande introuvable",
            "solution": "Gérer l'exception Order.DoesNotExist",
            "code": "except Order.DoesNotExist: messages.error(request, 'Commande introuvable')"
        },
        {
            "problème": "Erreur API Orange Money",
            "solution": "Gérer les erreurs de l'API avec try/catch",
            "code": "try: status_data = orange_money_service.check_transaction_status(...)"
        },
        {
            "problème": "Données manquantes dans la réponse",
            "solution": "Vérifier la présence des clés avant utilisation",
            "code": "status = status_data.get('status', 'UNKNOWN')"
        },
        {
            "problème": "Utilisateur non connecté",
            "solution": "Ajouter @login_required ou vérifier l'authentification",
            "code": "@login_required\ndef orange_money_return(request):"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['problème']}")
        print(f"   Solution: {rec['solution']}")
        print(f"   Code: {rec['code']}")
        print()

def test_url_analysis():
    """Analyse de l'URL problématique"""
    print("\n🔗 Analyse de l'URL problématique")
    print("=" * 60)
    
    url = "https://www.bolibana.com/cart/orange-money/return/"
    
    print(f"URL: {url}")
    print("Problèmes potentiels:")
    print("1. ❌ Utilisateur non connecté")
    print("2. ❌ Session expirée ou vide")
    print("3. ❌ Commande introuvable")
    print("4. ❌ Erreur API Orange Money")
    print("5. ❌ Données manquantes dans la réponse")
    print()
    
    print("Solutions:")
    print("1. ✅ Ajouter des logs de debug détaillés")
    print("2. ✅ Gérer tous les cas d'erreur")
    print("3. ✅ Vérifier la session avant traitement")
    print("4. ✅ Tester avec des données valides")
    print("5. ✅ Ajouter des messages d'erreur clairs")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic Orange Money Return - Erreur 500")
    print("=" * 70)
    
    test_orange_money_return_logic()
    test_common_errors()
    test_recommendations()
    test_url_analysis()
    
    print("\n✅ Diagnostic terminé")
    print("\n📋 Actions à effectuer:")
    print("1. Vérifier les logs Django pour l'erreur exacte")
    print("2. Tester l'URL avec un utilisateur connecté")
    print("3. Vérifier que la session contient les bonnes données")
    print("4. Ajouter plus de logs de debug dans la vue")
    print("5. Tester avec des données Orange Money valides")

if __name__ == "__main__":
    main()
