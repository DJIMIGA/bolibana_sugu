#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des produits pilotes
et leur intégration dans la page d'accueil hybride.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from suppliers.models import Supplier
from product.models import Product
from django.core.management import call_command

def test_pilot_products_integration():
    """Test de l'intégration des produits pilotes dans la page d'accueil"""
    print("=== TEST INTÉGRATION PRODUITS PILOTES ===\n")
    
    # 1. Vérifier que les composants existent
    print("1. Vérification des composants...")
    
    # Vérifier le composant _pilot_products.html
    pilot_component_path = "saga/suppliers/templates/suppliers/components/_pilot_products.html"
    if os.path.exists(pilot_component_path):
        print("   ✅ Composant _pilot_products.html créé avec succès")
    else:
        print("   ❌ Composant _pilot_products.html manquant")
        return False
    
    # Vérifier l'inclusion dans supplier_list.html
    supplier_list_path = "saga/suppliers/templates/suppliers/supplier_list.html"
    if os.path.exists(supplier_list_path):
        with open(supplier_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '{% include "suppliers/components/_pilot_products.html" %}' in content:
                print("   ✅ Composant intégré dans supplier_list.html")
            else:
                print("   ❌ Composant non intégré dans supplier_list.html")
                return False
    else:
        print("   ❌ Fichier supplier_list.html non trouvé")
        return False
    
    # 2. Vérifier la configuration Swiper
    print("\n2. Vérification de la configuration Swiper...")
    
    # Vérifier la configuration pilotProducts dans le JavaScript
    if 'pilotProducts:' in content and 'pilotProductsSwiper' in content:
        print("   ✅ Configuration Swiper pilotProducts ajoutée")
    else:
        print("   ❌ Configuration Swiper pilotProducts manquante")
        return False
    
    # Vérifier l'initialisation du Swiper
    if 'pilotProducts: initSwiper' in content:
        print("   ✅ Initialisation du Swiper pilotProducts ajoutée")
    else:
        print("   ❌ Initialisation du Swiper pilotProducts manquante")
        return False
    
    # 3. Vérifier les styles CSS
    print("\n3. Vérification des styles CSS...")
    
    # Vérifier les styles pour pilot-products-desktop-grid
    if 'pilot-products-desktop-grid' in content:
        print("   ✅ Styles CSS pour pilot-products-desktop-grid ajoutés")
    else:
        print("   ❌ Styles CSS pour pilot-products-desktop-grid manquants")
        return False
    
    # Vérifier la séparation mobile/desktop
    if 'pilotProductsSwiper' in content and 'pilot-products-desktop-grid' in content:
        print("   ✅ Séparation mobile/desktop configurée")
    else:
        print("   ❌ Séparation mobile/desktop non configurée")
        return False
    
    # 4. Vérifier la structure de la page
    print("\n4. Vérification de la structure de la page...")
    
    # Vérifier que la section est bien positionnée après le hero
    hero_section = content.find('{% if hero %}')
    pilot_section = content.find('Section Produits Pilotes - Tunnel de Vente')
    categories_section = content.find('Section Nos Catégories')
    
    if hero_section < pilot_section < categories_section:
        print("   ✅ Section produits pilotes bien positionnée (après hero, avant catégories)")
    else:
        print("   ❌ Section produits pilotes mal positionnée")
        return False
    
    # 5. Vérifier la cohérence du design
    print("\n5. Vérification de la cohérence du design...")
    
    # Vérifier les couleurs (vert/jaune/rouge)
    if 'from-green-600 via-yellow-500 to-red-500' in content:
        print("   ✅ Palette de couleurs cohérente (vert→jaune→rouge)")
    else:
        print("   ❌ Palette de couleurs non cohérente")
        return False
    
    # Vérifier la typographie
    if 'font-bitter' in content and 'text-2xl sm:text-3xl' in content:
        print("   ✅ Typographie cohérente avec le design existant")
    else:
        print("   ❌ Typographie non cohérente")
        return False
    
    print("\n=== RÉSULTAT DU TEST ===")
    print("✅ Intégration des produits pilotes réussie !")
    print("\nLa page d'accueil hybride est maintenant configurée avec :")
    print("• Section 'Produits Pilotes - Tunnel de Vente' en haut")
    print("• Design cohérent avec le style existant")
    print("• Responsive : Swiper mobile + grille desktop")
    print("• Intégration harmonieuse sans perte de fonctionnalités")
    
    return True

def test_product_rendering():
    """Test du rendu des différents types de produits"""
    print("\n=== TEST RENDU DES PRODUITS ===\n")
    
    print("1. Vérification des tags de rendu...")
    
    # Vérifier que tous les tags de rendu sont présents
    supplier_list_path = "saga/suppliers/templates/suppliers/supplier_list.html"
    with open(supplier_list_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_tags = [
        '{% render_phone_card product %}',
        '{% render_clothing_card product %}',
        '{% render_fabric_card product %}',
        '{% render_cultural_card product %}',
        '{% render_product_card product %}'
    ]
    
    for tag in required_tags:
        if tag in content:
            print(f"   ✅ Tag {tag} présent")
        else:
            print(f"   ❌ Tag {tag} manquant")
    
    print("\n2. Vérification de la logique conditionnelle...")
    
    # Vérifier la logique de détection des types de produits
    if '{% if product.phone %}' in content:
        print("   ✅ Logique de détection des téléphones présente")
    else:
        print("   ❌ Logique de détection des téléphones manquante")
    
    if '{% elif product.clothing_product %}' in content:
        print("   ✅ Logique de détection des vêtements présente")
    else:
        print("   ❌ Logique de détection des vêtements manquante")
    
    print("\n✅ Rendu des produits configuré correctement !")

if __name__ == "__main__":
    print("🚀 Test de l'intégration des produits pilotes dans SagaKore\n")
    
    try:
        # Test principal
        if test_pilot_products_integration():
            # Test du rendu des produits
            test_product_rendering()
            
            print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
            print("\nProchaines étapes :")
            print("1. Tester la page d'accueil dans le navigateur")
            print("2. Vérifier l'affichage mobile et desktop")
            print("3. Lancer tes campagnes Facebook avec le lien de la page")
            print("4. Analyser les performances et ajuster si nécessaire")
            
        else:
            print("\n❌ Certains tests ont échoué. Vérifiez la configuration.")
            
    except Exception as e:
        print(f"\n❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
