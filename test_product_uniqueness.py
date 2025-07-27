#!/usr/bin/env python
"""
Script de test pour vérifier la tolérance de l'unicité des noms de produits
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from product.models import Product, Category
from django.db import IntegrityError

def test_product_uniqueness():
    """
    Teste la tolérance de l'unicité des noms de produits
    """
    print("🧪 Test de tolérance de l'unicité des noms de produits")
    print("=" * 60)
    
    # Récupérer une catégorie existante
    try:
        category = Category.objects.first()
        if not category:
            print("❌ Aucune catégorie trouvée. Créez d'abord une catégorie.")
            return
        print(f"📂 Catégorie utilisée: {category.name}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la catégorie: {e}")
        return
    
    # Tests avec différents niveaux de similarité
    test_cases = [
        # Test 1: Nom identique
        ("iPhone 14 Pro", "iPhone 14 Pro", "Nom identique"),
        
        # Test 2: 1 mot différent
        ("iPhone 14 Pro", "iPhone 14 Pro Max", "1 mot différent"),
        ("Samsung Galaxy S23", "Samsung Galaxy S23 Ultra", "1 mot différent"),
        
        # Test 3: 2 mots différents
        ("iPhone 14 Pro Max", "iPhone 15 Pro Max", "2 mots différents"),
        ("Samsung Galaxy S23", "Samsung Galaxy S24", "2 mots différents"),
        
        # Test 4: 3 mots différents
        ("iPhone 14 Pro Max 128GB", "iPhone 15 Pro Max 256GB", "3 mots différents"),
        
        # Test 5: Ordre des mots différent
        ("iPhone 14 Pro Max", "iPhone Pro Max 14", "Ordre différent"),
        
        # Test 6: Majuscules/minuscules
        ("iPhone 14 Pro", "iphone 14 pro", "Majuscules/minuscules"),
        
        # Test 7: Espaces supplémentaires
        ("iPhone 14 Pro", "iPhone  14  Pro", "Espaces supplémentaires"),
        
        # Test 8: Caractères spéciaux
        ("iPhone 14 Pro", "iPhone 14 Pro!", "Caractères spéciaux"),
    ]
    
    print(f"\n📋 Tests à effectuer: {len(test_cases)}")
    print("-" * 60)
    
    for i, (title1, title2, description) in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {description}")
        print(f"   Titre 1: '{title1}'")
        print(f"   Titre 2: '{title2}'")
        
        # Supprimer les produits existants avec ces titres
        Product.objects.filter(title=title1, category=category).delete()
        Product.objects.filter(title=title2, category=category).delete()
        
        try:
            # Créer le premier produit
            product1 = Product.objects.create(
                title=title1,
                category=category,
                price=100000,
                brand="Test Brand"
            )
            print(f"   ✅ Premier produit créé: {product1.title}")
            
            # Essayer de créer le deuxième produit
            product2 = Product.objects.create(
                title=title2,
                category=category,
                price=100000,
                brand="Test Brand"
            )
            print(f"   ✅ Deuxième produit créé: {product2.title}")
            print(f"   🟢 RÉSULTAT: ACCEPTÉ - Les deux produits peuvent coexister")
            
            # Nettoyer
            product1.delete()
            product2.delete()
            
        except IntegrityError as e:
            print(f"   ❌ Erreur d'intégrité: {e}")
            print(f"   🔴 RÉSULTAT: REJETÉ - Les deux produits ne peuvent pas coexister")
            
            # Nettoyer le premier produit s'il existe
            try:
                product1.delete()
            except:
                pass
                
        except Exception as e:
            print(f"   ⚠️  Erreur inattendue: {e}")
            
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print("La contrainte unique_together('title', 'category') signifie que:")
    print("✅ On peut avoir le même titre dans des catégories différentes")
    print("❌ On ne peut pas avoir le même titre exact dans la même catégorie")
    print("🔍 La tolérance est de 0 mot différent - les titres doivent être exactement identiques pour être rejetés")

if __name__ == "__main__":
    test_product_uniqueness() 