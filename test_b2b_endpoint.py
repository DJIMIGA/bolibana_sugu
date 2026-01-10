#!/usr/bin/env python
"""Script pour tester l'endpoint B2B synced"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'saga'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from inventory.api.views import ProductViewSet
from rest_framework.test import APIRequestFactory
import json

# Créer une requête
factory = APIRequestFactory()
request = factory.get('/api/inventory/products/synced/')

# Appeler la vue
view = ProductViewSet()
response = view.synced(request)

# Afficher les résultats
print("=" * 60)
print("TEST ENDPOINT B2B /api/inventory/products/synced/")
print("=" * 60)
print(f"Status: {response.status_code}")
print(f"Count: {response.data.get('count', 0)}")
print(f"Results count: {len(response.data.get('results', []))}")
print(f"\nProduct IDs: {[p.get('id') for p in response.data.get('results', [])]}")

if response.data.get('results'):
    print("\n" + "=" * 60)
    print("PREMIER PRODUIT (détails):")
    print("=" * 60)
    print(json.dumps(response.data['results'][0], indent=2, ensure_ascii=False))
    
    if len(response.data.get('results', [])) > 1:
        print("\n" + "=" * 60)
        print("DEUXIÈME PRODUIT (détails):")
        print("=" * 60)
        print(json.dumps(response.data['results'][1], indent=2, ensure_ascii=False))
else:
    print("\nAucun produit retourné")
    if 'error' in response.data:
        print(f"Erreur: {response.data.get('error')}")






