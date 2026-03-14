# 🧪 Guide de Test en Situation Réelle

## 📋 Prérequis

### 1. Configuration de base

Assurez-vous d'avoir configuré dans votre `.env` :

```env
# URL de l'API B2B
B2B_API_URL=https://www.bolibanastock.com/api/v1

# Clé de chiffrement (générée avec generate_encryption_key.py)
INVENTORY_ENCRYPTION_KEY=votre_cle_ici

# Clé API globale (optionnelle, fallback)
B2B_API_KEY=clé_api_globale_si_besoin
```

### 2. Installer les dépendances

```bash
pip install cryptography
pip install -r requirements.txt
```

### 3. Appliquer les migrations

```bash
python manage.py migrate inventory
```

## 🧪 Tests Étape par Étape

### Test 1 : Vérifier la Configuration

```bash
# Tester la configuration
python manage.py shell
```

```python
from django.conf import settings

# Vérifier l'URL
print(f"URL API: {getattr(settings, 'B2B_API_URL', 'Non configuré')}")

# Vérifier la clé de chiffrement
enc_key = getattr(settings, 'INVENTORY_ENCRYPTION_KEY', None)
if enc_key:
    print(f"✅ Clé de chiffrement configurée: {enc_key[:10]}...")
else:
    print("❌ Clé de chiffrement non configurée")

# Vérifier la clé API globale (optionnelle)
api_key = getattr(settings, 'B2B_API_KEY', None)
if api_key:
    print(f"✅ Clé API globale configurée: {api_key[:6]}...")
else:
    print("⚠️  Clé API globale non configurée (sera utilisée comme fallback)")
```

### Test 2 : Créer une Connexion et une Clé API

#### 2.1 Créer un utilisateur/commerçant (si nécessaire)

```python
# Dans le shell Django
from django.contrib.auth import get_user_model
User = get_user_model()

# Créer ou récupérer un utilisateur
user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={
        'username': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Commerçant',
        'is_active': True
    }
)
print(f"Utilisateur: {user.email} ({'créé' if created else 'existant'})")
```

#### 2.2 Créer une connexion via l'admin

1. Aller dans `/admin/inventory/inventoryconnection/add/`
2. Sélectionner l'utilisateur
3. Laisser l'URL vide (utilisera celle par défaut) ou entrer une URL personnalisée
4. Cocher "Actif"
5. Sauvegarder

#### 2.3 Ajouter une clé API

1. Aller dans `/admin/inventory/apikey/add/`
2. Sélectionner la connexion créée
3. Nom : "Clé de test - Site principal"
4. Clé API : Entrer la clé API réelle depuis B2B (ex: `b2c_1_xxxxx`)
5. Cocher "Active"
6. Sauvegarder

#### 2.4 Vérifier que la clé est bien stockée

```python
# Dans le shell Django
from inventory.models import InventoryConnection, ApiKey

connection = InventoryConnection.objects.first()
print(f"Connexion: {connection.user.email}")

api_key = ApiKey.objects.filter(connection=connection, is_active=True).first()
if api_key:
    print(f"✅ Clé API trouvée: {api_key.name}")
    # Tester le déchiffrement
    try:
        key_value = api_key.get_key()
        print(f"✅ Clé déchiffrée: {key_value[:6]}...{key_value[-4:]}")
    except Exception as e:
        print(f"❌ Erreur de déchiffrement: {e}")
else:
    print("❌ Aucune clé API active trouvée")
```

### Test 3 : Tester la Connexion à l'API B2B

```bash
# Utiliser la commande de test
python manage.py test_b2b_api --connection-id 1
```

Ou manuellement dans le shell :

```python
from inventory.models import InventoryConnection
from inventory.services import InventoryAPIClient, InventoryAPIError

connection = InventoryConnection.objects.get(id=1)

try:
    api_client = InventoryAPIClient(connection)
    
    # Test 1: Récupérer les catégories
    print("Test 1: Récupération des catégories...")
    categories = api_client.get_categories_list()
    print(f"✅ {len(categories)} catégorie(s) récupérée(s)")
    if categories:
        print(f"   Première catégorie: {categories[0].get('name', 'N/A')}")
    
    # Test 2: Récupérer les produits
    print("\nTest 2: Récupération des produits...")
    products_response = api_client.get_products_list(page=1, page_size=5)
    
    if isinstance(products_response, dict):
        products = products_response.get('results', products_response.get('products', []))
        total = products_response.get('count', len(products))
    else:
        products = products_response if isinstance(products_response, list) else []
        total = len(products)
    
    print(f"✅ {len(products)} produit(s) récupéré(s) (total: {total})")
    if products:
        first_product = products[0]
        print(f"   Premier produit: {first_product.get('name', first_product.get('title', 'N/A'))}")
    
    # Test 3: Récupérer les sites
    print("\nTest 3: Récupération des sites...")
    sites = api_client.get_sites_list()
    print(f"✅ {len(sites)} site(s) récupéré(s)")
    if sites:
        for site in sites[:3]:
            print(f"   - {site.get('name', 'N/A')} (ID: {site.get('id', 'N/A')})")
    
    # Test 4: Test de connexion général
    print("\nTest 4: Test de connexion général...")
    if api_client.test_connection():
        print("✅ Connexion réussie !")
    else:
        print("❌ Connexion échouée")
        
except InventoryAPIError as e:
    print(f"❌ Erreur API: {e}")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
```

### Test 4 : Synchroniser les Catégories

```bash
# Synchroniser les catégories
python manage.py sync_categories_from_inventory --connection-id 1
```

Vérifier dans l'admin :

1. Aller dans `/admin/product/category/`
2. Vérifier que les catégories ont été créées
3. Vérifier les champs `external_id` et `external_parent_id`

Vérifier dans le shell :

```python
from inventory.models import ExternalCategory
from product.models import Category

# Compter les catégories synchronisées
external_cats = ExternalCategory.objects.all()
print(f"Catégories synchronisées: {external_cats.count()}")

for ext_cat in external_cats[:5]:
    print(f"  - {ext_cat.category.name} (ID externe: {ext_cat.external_id})")
```

### Test 5 : Synchroniser les Produits

```bash
# Synchroniser les produits
python manage.py sync_products_from_inventory --connection-id 1
```

Vérifier dans l'admin :

1. Aller dans `/admin/product/product/`
2. Vérifier que les produits ont été créés
3. Vérifier les champs `external_id` et `external_sku`
4. Vérifier que les produits sont liés aux bonnes catégories

Vérifier dans le shell :

```python
from inventory.models import ExternalProduct
from product.models import Product

# Compter les produits synchronisés
external_prods = ExternalProduct.objects.filter(sync_status='synced')
print(f"Produits synchronisés: {external_prods.count()}")

for ext_prod in external_prods[:5]:
    print(f"  - {ext_prod.product.title} (ID externe: {ext_prod.external_id}, SKU: {ext_prod.external_sku})")
    print(f"    Statut: {ext_prod.get_sync_status_display()}")
```

### Test 6 : Tester la Synchronisation des Ventes

#### 6.1 Créer une commande de test

```python
# Dans le shell Django
from cart.models import Order, OrderItem
from inventory.models import InventoryConnection
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
connection = InventoryConnection.objects.first()

# Créer une commande de test
order = Order.objects.create(
    user=user,
    status=Order.CONFIRMED,
    total=10000,
    subtotal=9500,
    shipping_cost=500
)

# Ajouter des items (si vous avez des produits)
products = Product.objects.filter(external_product__connection=connection)[:2]
for product in products:
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

print(f"Commande créée: {order.order_number}")
```

#### 6.2 Vérifier la synchronisation automatique

```python
from inventory.models import SaleSync

# Vérifier si la synchronisation a été créée (via signal)
sale_sync = SaleSync.objects.filter(order=order).first()
if sale_sync:
    print(f"✅ Synchronisation créée: {sale_sync.get_sync_status_display()}")
    if sale_sync.sync_status == 'synced':
        print(f"   ID externe: {sale_sync.external_sale_id}")
    elif sale_sync.sync_status == 'error':
        print(f"   Erreur: {sale_sync.error_message}")
else:
    print("⚠️  Aucune synchronisation créée (vérifier les signaux)")
```

#### 6.3 Synchroniser manuellement si nécessaire

```bash
python manage.py sync_sales_to_inventory --connection-id 1 --order-id 1
```

### Test 7 : Tester l'Utilisation des Catégories Synchronisées

```python
from inventory.utils import (
    get_synced_categories,
    get_products_in_synced_category,
    get_category_tree_from_b2b
)

connection = InventoryConnection.objects.first()

# Récupérer les catégories synchronisées
categories = get_synced_categories(connection)
print(f"Catégories synchronisées: {categories.count()}")

# Pour chaque catégorie, récupérer ses produits
for category in categories[:3]:
    products = get_products_in_synced_category(category, connection)
    print(f"\n{category.name}: {products.count()} produit(s)")
    for product in products[:3]:
        print(f"  - {product.title} ({product.price} FCFA)")

# Récupérer l'arbre hiérarchique
tree = get_category_tree_from_b2b(connection)
print(f"\nArbre des catégories: {len(tree)} catégorie(s) racine")
```

### Test 8 : Tester via l'Interface Web

#### 8.1 Tester la connexion via l'interface

1. Aller sur `/inventory/connect/`
2. Se connecter avec un utilisateur ayant une connexion
3. Vérifier que la connexion est détectée
4. Tester la connexion

#### 8.2 Tester la synchronisation via l'interface

1. Aller sur `/inventory/status/`
2. Cliquer sur "Synchroniser les produits"
3. Vérifier les messages de succès/erreur

#### 8.3 Tester l'affichage des catégories

1. Aller sur `/inventory/categories/`
2. Vérifier que les catégories synchronisées s'affichent
3. Cliquer sur une catégorie pour voir ses produits

### Test 9 : Tester l'API REST

```bash
# Tester l'API REST (nécessite un token JWT)
# 1. Obtenir un token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "votre_mot_de_passe"}'

# 2. Utiliser le token pour récupérer les catégories synchronisées
curl http://localhost:8000/api/inventory/categories/synced/ \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

### Test 10 : Test de Performance et Robustesse

#### 10.1 Tester avec plusieurs connexions

```python
# Créer plusieurs connexions avec différentes clés API
from inventory.models import InventoryConnection, ApiKey

connections = InventoryConnection.objects.filter(is_active=True)
print(f"Connexions actives: {connections.count()}")

for connection in connections:
    api_key = ApiKey.objects.filter(connection=connection, is_active=True).first()
    if api_key:
        print(f"  - {connection.user.email}: Clé API active")
    else:
        print(f"  - {connection.user.email}: Pas de clé API")
```

#### 10.2 Tester la gestion des erreurs

```python
# Tester avec une clé API invalide
from inventory.models import ApiKey
from inventory.services import InventoryAPIClient, InventoryAPIError

api_key = ApiKey.objects.first()
api_key.set_key("clé_invalide")
api_key.save()

try:
    api_client = InventoryAPIClient(api_key.connection)
    api_client.get_categories_list()
except InventoryAPIError as e:
    print(f"✅ Erreur correctement gérée: {e}")
```

## ✅ Checklist de Validation

- [ ] Configuration `.env` complète
- [ ] Migrations appliquées
- [ ] Connexion créée dans l'admin
- [ ] Clé API ajoutée et chiffrée correctement
- [ ] Test de connexion à l'API B2B réussi
- [ ] Catégories synchronisées
- [ ] Produits synchronisés
- [ ] Ventes synchronisées (automatique ou manuelle)
- [ ] Catégories visibles dans l'interface web
- [ ] Produits visibles dans l'interface web
- [ ] API REST fonctionnelle
- [ ] Gestion des erreurs testée

## 🐛 Dépannage

### Erreur : "B2B_API_KEY n'est pas configuré"

**Solution** : Ajoutez une clé API via l'admin (`/admin/inventory/apikey/add/`) ou configurez `B2B_API_KEY` dans `.env`

### Erreur : "Impossible de déchiffrer la clé API"

**Solution** : Vérifiez que `INVENTORY_ENCRYPTION_KEY` est correctement configuré et identique à celui utilisé lors de la création

### Erreur : "Connection timeout"

**Solution** : Vérifiez que l'URL B2B est accessible et que le firewall autorise les connexions

### Erreur : "401 Unauthorized"

**Solution** : Vérifiez que la clé API est correcte et active dans B2B

### Les produits ne s'affichent pas

**Solution** : 
1. Vérifiez que la synchronisation a réussi (`sync_status='synced'`)
2. Vérifiez que les produits ont `is_available=True`
3. Vérifiez que la connexion est active

## 📊 Monitoring

### Vérifier les statistiques

```python
from inventory.models import (
    InventoryConnection,
    ExternalProduct,
    ExternalCategory,
    SaleSync,
    ApiKey
)

connection = InventoryConnection.objects.first()

stats = {
    'connexion_active': connection.is_active if connection else False,
    'cle_api_active': ApiKey.objects.filter(connection=connection, is_active=True).exists() if connection else False,
    'produits_synchronises': ExternalProduct.objects.filter(connection=connection, sync_status='synced').count() if connection else 0,
    'produits_en_erreur': ExternalProduct.objects.filter(connection=connection, sync_status='error').count() if connection else 0,
    'categories_synchronisees': ExternalCategory.objects.filter(connection=connection).count() if connection else 0,
    'ventes_synchronisees': SaleSync.objects.filter(connection=connection, sync_status='synced').count() if connection else 0,
    'ventes_en_attente': SaleSync.objects.filter(connection=connection, sync_status='pending').count() if connection else 0,
}

for key, value in stats.items():
    print(f"{key}: {value}")
```

## 🎯 Test Final : Scénario Complet

1. **Créer une connexion** avec une clé API réelle
2. **Synchroniser les catégories** → Vérifier dans l'admin
3. **Synchroniser les produits** → Vérifier dans l'admin et sur le site
4. **Créer une commande** → Vérifier la synchronisation automatique
5. **Vérifier l'affichage** sur le site B2C
6. **Tester l'API REST** avec un client HTTP

Si tous ces tests passent, votre intégration est fonctionnelle ! 🎉










