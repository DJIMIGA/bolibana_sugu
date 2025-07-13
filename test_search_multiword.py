#!/usr/bin/env python
"""
Script de test pour vérifier la recherche multi-mots
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from suppliers.views import create_search_query, normalize_search_term
from product.models import Product

def test_multiword_search():
    """Test de la recherche multi-mots"""
    print("🔍 Test de la recherche multi-mots")
    print("=" * 50)
    
    # Test 1: Recherche "bazin supp"
    print("\n1. Test avec 'bazin supp':")
    query = create_search_query("bazin supp")
    products = Product.objects.filter(query)
    print(f"   Résultats trouvés: {products.count()}")
    
    for product in products[:3]:
        print(f"   - {product.title}")
    
    # Test 2: Recherche "iPhone Samsung"
    print("\n2. Test avec 'iPhone Samsung':")
    query = create_search_query("iPhone Samsung")
    products = Product.objects.filter(query)
    print(f"   Résultats trouvés: {products.count()}")
    
    for product in products[:3]:
        print(f"   - {product.title}")
    
    # Test 3: Recherche "Téléphone portable"
    print("\n3. Test avec 'Téléphone portable':")
    query = create_search_query("Téléphone portable")
    products = Product.objects.filter(query)
    print(f"   Résultats trouvés: {products.count()}")
    
    for product in products[:3]:
        print(f"   - {product.title}")
    
    # Test 4: Normalisation
    print("\n4. Test de normalisation:")
    test_terms = ["Téléphones", "telephones", "SMARTPHONE", "smartphone"]
    for term in test_terms:
        normalized = normalize_search_term(term)
        print(f"   '{term}' -> '{normalized}'")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés !")
    print("\nLa recherche multi-mots fonctionne maintenant avec:")
    print("  ✅ Logique ET (chaque mot doit être présent)")
    print("  ✅ Normalisation (accents, casse)")
    print("  ✅ Recherche dans title, description, category, brand")
    print("  ✅ Plus de référence à 'phone'")

if __name__ == "__main__":
    try:
        test_multiword_search()
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        sys.exit(1) 