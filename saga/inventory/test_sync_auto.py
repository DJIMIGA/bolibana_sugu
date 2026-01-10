"""
Script de test pour la synchronisation automatique des produits B2B
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from inventory.tasks import sync_products_auto, sync_categories_auto, should_sync_products
from inventory.models import ApiKey, ExternalProduct
from inventory.utils import get_b2b_products
from product.models import Product
from django.core.cache import cache
from django.utils import timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_api_key():
    """Test 1: Vérifier qu'une clé API est configurée"""
    print("\n" + "="*80)
    print("TEST 1: Vérification de la clé API")
    print("="*80)
    
    api_key = ApiKey.get_active_key()
    if api_key:
        masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
        print(f"✅ Clé API trouvée: {masked_key}")
        return True
    else:
        print("❌ Aucune clé API active trouvée")
        print("   → Configurez une clé API dans /admin/inventory/apikey/")
        return False


def test_should_sync():
    """Test 2: Vérifier la logique de synchronisation"""
    print("\n" + "="*80)
    print("TEST 2: Logique de synchronisation")
    print("="*80)
    
    # Nettoyer le cache pour le test
    cache.delete('b2b_last_sync_time')
    
    should_sync = should_sync_products()
    print(f"Devrait synchroniser (cache vide): {should_sync}")
    
    if should_sync:
        print("✅ La logique de synchronisation fonctionne correctement")
    else:
        print("⚠️  La synchronisation ne devrait pas être nécessaire")
    
    # Simuler une synchronisation récente
    cache.set('b2b_last_sync_time', timezone.now(), 7200)
    should_sync_after = should_sync_products()
    print(f"Devrait synchroniser (sync récente): {should_sync_after}")
    
    if not should_sync_after:
        print("✅ La protection contre les synchronisations trop fréquentes fonctionne")
    else:
        print("⚠️  La protection ne fonctionne pas correctement")
    
    return True


def test_sync_products():
    """Test 3: Tester la synchronisation automatique des produits"""
    print("\n" + "="*80)
    print("TEST 3: Synchronisation automatique des produits")
    print("="*80)
    
    # Compter les produits avant
    products_before = ExternalProduct.objects.filter(sync_status='synced').count()
    print(f"Produits synchronisés avant: {products_before}")
    
    try:
        # Lancer la synchronisation (force=False pour respecter le cache)
        print("\nLancement de la synchronisation...")
        result = sync_products_auto(force=False)
        
        if result['success']:
            stats = result['stats']
            print(f"✅ Synchronisation réussie!")
            print(f"   - Total: {stats['total']}")
            print(f"   - Créés: {stats['created']}")
            print(f"   - Mis à jour: {stats['updated']}")
            print(f"   - Erreurs: {stats['errors']}")
            
            # Compter les produits après
            products_after = ExternalProduct.objects.filter(sync_status='synced').count()
            print(f"\nProduits synchronisés après: {products_after}")
            
            if stats['errors'] > 0:
                print(f"\n⚠️  {stats['errors']} erreurs détectées:")
                for error in stats['errors_list'][:5]:  # Afficher les 5 premières
                    print(f"   - Produit {error.get('product_id')}: {error.get('error')}")
            
            return True
        else:
            print(f"⚠️  Synchronisation: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_get_b2b_products():
    """Test 4: Vérifier la récupération des produits B2B"""
    print("\n" + "="*80)
    print("TEST 4: Récupération des produits B2B")
    print("="*80)
    
    try:
        products = get_b2b_products(limit=5)
        print(f"✅ {len(products)} produits B2B récupérés")
        
        if products:
            print("\nPremiers produits:")
            for i, product in enumerate(products[:3], 1):
                print(f"\n{i}. {product.title}")
                print(f"   - ID: {product.id}")
                print(f"   - Prix: {product.format_price()}")
                print(f"   - Stock: {product.stock}")
                print(f"   - Catégorie: {product.category.name if product.category else 'N/A'}")
                print(f"   - Disponible: {product.is_available}")
                
                # Vérifier les informations externes
                if hasattr(product, 'external_product'):
                    ext = product.external_product
                    print(f"   - ID B2B: {ext.external_id}")
                    print(f"   - Statut: {ext.sync_status}")
                    print(f"   - Dernière sync: {ext.last_synced_at}")
        else:
            print("⚠️  Aucun produit B2B trouvé")
            print("   → Exécutez d'abord la synchronisation")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sync_categories():
    """Test 5: Tester la synchronisation des catégories"""
    print("\n" + "="*80)
    print("TEST 5: Synchronisation automatique des catégories")
    print("="*80)
    
    try:
        result = sync_categories_auto(force=True)
        
        if result['success']:
            stats = result['stats']
            print(f"✅ Synchronisation des catégories réussie!")
            print(f"   - Total: {stats['total']}")
            print(f"   - Créées: {stats['created']}")
            print(f"   - Mises à jour: {stats['updated']}")
            print(f"   - Erreurs: {stats['errors']}")
            return True
        else:
            print(f"⚠️  Synchronisation: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cache():
    """Test 6: Vérifier le système de cache"""
    print("\n" + "="*80)
    print("TEST 6: Système de cache")
    print("="*80)
    
    # Nettoyer le cache
    cache.delete('b2b_last_sync_time')
    last_sync = cache.get('b2b_last_sync_time')
    print(f"Cache après nettoyage: {last_sync}")
    
    if last_sync is None:
        print("✅ Le cache est bien nettoyé")
    else:
        print("⚠️  Le cache n'a pas été nettoyé correctement")
    
    # Définir une valeur
    now = timezone.now()
    cache.set('b2b_last_sync_time', now, 7200)
    cached_value = cache.get('b2b_last_sync_time')
    
    if cached_value:
        print(f"✅ Le cache fonctionne (valeur: {cached_value})")
        return True
    else:
        print("❌ Le cache ne fonctionne pas")
        return False


def main():
    """Fonction principale de test"""
    print("\n" + "="*80)
    print("TESTS DE SYNCHRONISATION AUTOMATIQUE B2B")
    print("="*80)
    
    results = {
        'api_key': False,
        'should_sync': False,
        'sync_products': False,
        'get_products': False,
        'sync_categories': False,
        'cache': False,
    }
    
    # Test 1: Clé API
    results['api_key'] = test_api_key()
    
    if not results['api_key']:
        print("\n⚠️  Les tests suivants nécessitent une clé API configurée")
        return
    
    # Test 2: Logique de synchronisation
    results['should_sync'] = test_should_sync()
    
    # Test 6: Cache (avant la synchronisation)
    results['cache'] = test_cache()
    
    # Test 3: Synchronisation des produits
    results['sync_products'] = test_sync_products()
    
    # Test 4: Récupération des produits
    results['get_products'] = test_get_b2b_products()
    
    # Test 5: Synchronisation des catégories
    results['sync_categories'] = test_sync_categories()
    
    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ DES TESTS")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'PASSÉ' if result else 'ÉCHOUÉ'}")
    
    print(f"\nTotal: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
    
    print("="*80)


if __name__ == '__main__':
    main()

