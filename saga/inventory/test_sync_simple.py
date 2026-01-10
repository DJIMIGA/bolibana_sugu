"""
Test simple de la synchronisation automatique B2B
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from inventory.models import ApiKey, ExternalProduct
from inventory.utils import get_b2b_products
from inventory.tasks import should_sync_products, sync_products_auto

print("\n" + "="*60)
print("TEST SYNCHRONISATION AUTOMATIQUE B2B")
print("="*60)

# Test 1: Clé API
print("\n1. Vérification de la clé API...")
api_key = ApiKey.get_active_key()
if api_key:
    print(f"   ✅ Clé API trouvée")
else:
    print(f"   ❌ Aucune clé API - Configurez dans /admin/inventory/apikey/")
    sys.exit(1)

# Test 2: Logique de synchronisation
print("\n2. Test de la logique de synchronisation...")
should_sync = should_sync_products()
print(f"   {'✅ Devrait synchroniser' if should_sync else '⚠️  Synchronisation non nécessaire'}")

# Test 3: Récupération des produits existants
print("\n3. Produits B2B actuellement synchronisés...")
products_count = ExternalProduct.objects.filter(sync_status='synced').count()
print(f"   {products_count} produits synchronisés")

if products_count > 0:
    products = get_b2b_products(limit=3)
    print(f"   {len(products)} produits récupérés pour test")
    if products:
        print(f"   Exemple: {products[0].title}")

# Test 4: Synchronisation (si nécessaire)
print("\n4. Test de synchronisation automatique...")
try:
    result = sync_products_auto(force=False)
    if result['success']:
        stats = result['stats']
        print(f"   ✅ Synchronisation réussie")
        print(f"      - Total: {stats['total']}")
        print(f"      - Créés: {stats['created']}")
        print(f"      - Mis à jour: {stats['updated']}")
        print(f"      - Erreurs: {stats['errors']}")
    else:
        print(f"   ⚠️  {result['message']}")
except Exception as e:
    print(f"   ❌ Erreur: {str(e)}")

print("\n" + "="*60)
print("Test terminé!")
print("="*60)

