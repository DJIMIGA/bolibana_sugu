"""
Script de test rapide pour l'intégration B2B
À exécuter avec: python manage.py shell < inventory/test_integration.py
"""
from inventory.models import InventoryConnection, ApiKey, ExternalProduct, ExternalCategory, SaleSync
from inventory.services import InventoryAPIClient, ProductSyncService, InventoryAPIError
from inventory.utils import get_synced_categories, get_products_in_synced_category
from product.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def test_configuration():
    """Test 1: Vérifier la configuration"""
    print_section("TEST 1: CONFIGURATION")
    
    from django.conf import settings
    
    api_url = getattr(settings, 'B2B_API_URL', None)
    enc_key = getattr(settings, 'INVENTORY_ENCRYPTION_KEY', None)
    api_key = getattr(settings, 'B2B_API_KEY', None)
    
    print(f"URL API: {api_url or '❌ Non configuré'}")
    print(f"Clé de chiffrement: {'✅ Configurée' if enc_key else '❌ Non configurée'}")
    print(f"Clé API globale: {'✅ Configurée' if api_key else '⚠️  Non configurée (optionnel)'}")

def test_connections():
    """Test 2: Vérifier les connexions"""
    print_section("TEST 2: CONNEXIONS")
    
    connections = InventoryConnection.objects.filter(is_active=True)
    print(f"Connexions actives: {connections.count()}")
    
    for connection in connections:
        api_key = ApiKey.objects.filter(connection=connection, is_active=True).first()
        status = "✅ Clé API active" if api_key else "❌ Pas de clé API"
        print(f"  - {connection.user.email}: {status}")
        if api_key:
            try:
                key_preview = api_key.get_key()
                print(f"    Clé: {key_preview[:6]}...{key_preview[-4:]}")
            except Exception as e:
                print(f"    Erreur: {e}")

def test_api_connection():
    """Test 3: Tester la connexion à l'API B2B"""
    print_section("TEST 3: CONNEXION API B2B")
    
    connection = InventoryConnection.objects.filter(is_active=True).first()
    if not connection:
        print("❌ Aucune connexion active")
        return
    
    try:
        api_client = InventoryAPIClient(connection)
        
        # Test catégories
        categories = api_client.get_categories_list()
        print(f"✅ Catégories: {len(categories)} récupérée(s)")
        
        # Test produits
        products_response = api_client.get_products_list(page=1, page_size=5)
        if isinstance(products_response, dict):
            products = products_response.get('results', [])
            total = products_response.get('count', 0)
        else:
            products = products_response if isinstance(products_response, list) else []
            total = len(products)
        print(f"✅ Produits: {len(products)} récupéré(s) (total: {total})")
        
        # Test sites
        sites = api_client.get_sites_list()
        print(f"✅ Sites: {len(sites)} récupéré(s)")
        
    except InventoryAPIError as e:
        print(f"❌ Erreur API: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_synchronized_data():
    """Test 4: Vérifier les données synchronisées"""
    print_section("TEST 4: DONNÉES SYNCHRONISÉES")
    
    connection = InventoryConnection.objects.filter(is_active=True).first()
    if not connection:
        print("❌ Aucune connexion active")
        return
    
    # Catégories
    ext_categories = ExternalCategory.objects.filter(connection=connection)
    print(f"Catégories synchronisées: {ext_categories.count()}")
    
    # Produits
    ext_products = ExternalProduct.objects.filter(connection=connection)
    synced = ext_products.filter(sync_status='synced').count()
    errors = ext_products.filter(sync_status='error').count()
    pending = ext_products.filter(sync_status='pending').count()
    
    print(f"Produits synchronisés: {synced}")
    print(f"Produits en erreur: {errors}")
    print(f"Produits en attente: {pending}")
    
    # Ventes
    sales = SaleSync.objects.filter(connection=connection)
    synced_sales = sales.filter(sync_status='synced').count()
    pending_sales = sales.filter(sync_status='pending').count()
    error_sales = sales.filter(sync_status='error').count()
    
    print(f"Ventes synchronisées: {synced_sales}")
    print(f"Ventes en attente: {pending_sales}")
    print(f"Ventes en erreur: {error_sales}")

def test_utils():
    """Test 5: Tester les utilitaires"""
    print_section("TEST 5: UTILITAIRES")
    
    connection = InventoryConnection.objects.filter(is_active=True).first()
    if not connection:
        print("❌ Aucune connexion active")
        return
    
    # Catégories synchronisées
    categories = get_synced_categories(connection)
    print(f"Catégories synchronisées (via utils): {categories.count()}")
    
    # Produits par catégorie
    if categories.exists():
        category = categories.first()
        products = get_products_in_synced_category(category, connection)
        print(f"Produits dans '{category.name}': {products.count()}")

def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("TESTS D'INTÉGRATION B2B")
    print("="*60)
    
    test_configuration()
    test_connections()
    test_api_connection()
    test_synchronized_data()
    test_utils()
    
    print("\n" + "="*60)
    print("TESTS TERMINÉS")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()










