#!/usr/bin/env python
"""
Script de test pour les fonctions de recherche améliorées
"""

import os
import sys
import django

# Ajouter le répertoire saga au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'saga'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from suppliers.views import normalize_search_term, create_search_query
from product.models import Product, Category

def test_normalization():
    """Test de la fonction de normalisation"""
    print("=== Test de normalisation ===")
    
    test_cases = [
        ('telephones', 'telephones'),
        ('Téléphones', 'telephones'),
        ('TÉLÉPHONES', 'telephones'),
        ('smartphone', 'smartphone'),
        ('Smartphone', 'smartphone'),
        ('SMARTPHONE', 'smartphone'),
        ('ordinateur', 'ordinateur'),
        ('Ordinateur', 'ordinateur'),
        ('vêtements', 'vetements'),
        ('Vêtements', 'vetements'),
    ]
    
    for input_term, expected in test_cases:
        result = normalize_search_term(input_term)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_term}' -> '{result}' (attendu: '{expected}')")

def test_search_variants():
    """Test des variantes de recherche"""
    print("\n=== Test des variantes de recherche ===")
    
    test_terms = ['telephones', 'smartphone', 'ordinateur', 'vetements']
    
    for term in test_terms:
        print(f"\nTerme: '{term}'")
        query = create_search_query(term)
        print(f"Requête créée: {query}")

def test_database_search():
    """Test de recherche dans la base de données"""
    print("\n=== Test de recherche dans la base de données ===")
    
    # Test avec différents termes
    test_terms = ['telephones', 'smartphone', 'ordinateur', 'vetements']
    
    for term in test_terms:
        print(f"\nRecherche pour: '{term}'")
        
        # Utiliser la fonction de recherche améliorée
        search_query = create_search_query(term)
        products = Product.objects.filter(search_query).select_related('category')[:5]
        
        print(f"Nombre de produits trouvés: {products.count()}")
        
        for product in products:
            print(f"  - {product.title} (Catégorie: {product.category.name if product.category else 'Aucune'})")

if __name__ == "__main__":
    test_normalization()
    test_search_variants()
    test_database_search() 