# 🚀 Guide d'Utilisation des API B2B

## 📋 Configuration Initiale

### 1. Configurer le fichier `.env`

```env
# URL de base de l'API B2B
B2B_API_URL=https://www.bolibanastock.com/api/v1

# Token API (obtenu depuis l'admin B2B)
B2B_API_KEY=b2c_1_votre_token_ici
```

### 2. Tester la connexion

```bash
# Tester la connexion à l'API B2B
python manage.py test_b2b_api
```

## 🔄 Synchronisation des Données

### Synchroniser les Catégories

```bash
# Synchroniser toutes les catégories
python manage.py sync_categories_from_inventory
```

**Note** : Le système utilise une clé API active unique. Assurez-vous qu'une clé API est active dans l'admin (`/admin/inventory/apikey/`).

### Synchroniser les Produits

```bash
# Synchroniser tous les produits
python manage.py sync_products_from_inventory

# Pour un site spécifique
python manage.py sync_products_from_inventory --site-id 1
```

### Synchroniser les Ventes

```bash
# Synchroniser les ventes en attente
python manage.py sync_sales_to_inventory
```

## 💻 Utilisation dans le Code Python

### Exemple 1: Récupérer les Produits depuis B2B

```python
from inventory.services import InventoryAPIClient

# Créer le client API (utilise automatiquement la clé API active)
api_client = InventoryAPIClient()

# Récupérer les produits
products = api_client.get_products_list(page=1, page_size=20)
print(f"Produits récupérés: {len(products.get('results', []))}")
```

### Exemple 2: Synchroniser les Produits

```python
from inventory.services import ProductSyncService

# Créer le service de synchronisation (utilise automatiquement la clé API active)
sync_service = ProductSyncService()

# Synchroniser tous les produits
stats = sync_service.sync_all_products()
print(f"Créés: {stats['created']}, Mis à jour: {stats['updated']}, Erreurs: {stats['errors']}")

# Synchroniser les produits d'un site spécifique
stats = sync_service.sync_all_products(site_id=1)
```

### Exemple 3: Utiliser les Catégories Synchronisées

```python
from product.models import Category
from inventory.models import ExternalCategory

# Récupérer les catégories synchronisées (qui ont un ExternalCategory)
categories = Category.objects.filter(external_category__isnull=False).distinct()

# Pour chaque catégorie, récupérer ses produits
for category in categories:
    products = category.product_set.all()
    print(f"{category.name}: {products.count()} produits")
```

## 🌐 Utilisation via API REST

### Endpoints Disponibles

#### 1. Tester une Connexion

```http
POST /api/inventory/test_connection/
Authorization: Bearer {token}
```

#### 2. Synchroniser les Produits

```http
POST /api/inventory/sync_products/
Authorization: Bearer {token}
```

#### 3. Synchroniser les Catégories

```http
POST /api/inventory/sync_categories/
Authorization: Bearer {token}
```

#### 4. Récupérer les Catégories Synchronisées

```http
GET /api/inventory/categories/synced/
```

#### 5. Récupérer l'Arbre des Catégories

```http
GET /api/inventory/categories/tree/
Authorization: Bearer {token}
```

#### 6. Récupérer les Produits d'une Catégorie

```http
GET /api/inventory/categories/{id}/products/
```

#### 7. Récupérer les Produits Synchronisés

```http
GET /api/inventory/products/synced/
```

### Exemples avec cURL

```bash
# Tester la connexion
curl -X POST http://localhost:8000/api/inventory/test_connection/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Synchroniser les produits
curl -X POST http://localhost:8000/api/inventory/sync_products/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Récupérer les catégories synchronisées
curl http://localhost:8000/api/inventory/categories/synced/
```

### Exemples avec JavaScript/Fetch

```javascript
// Tester la connexion
async function testConnection(token) {
    const response = await fetch(
        `/api/inventory/test_connection/`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    );
    const data = await response.json();
    console.log(data);
}

// Synchroniser les produits
async function syncProducts(token) {
    const response = await fetch(
        `/api/inventory/sync_products/`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    );
    const data = await response.json();
    console.log('Stats:', data.stats);
}

// Récupérer les catégories synchronisées
async function getSyncedCategories() {
    const response = await fetch('/api/inventory/categories/synced/');
    const data = await response.json();
    console.log('Catégories:', data.results);
    return data.results;
}
```

## 🎯 Utilisation dans les Vues Django

### Vue pour Afficher les Produits Synchronisés

```python
from django.shortcuts import render
from product.models import Category, Product
from inventory.models import ExternalCategory, ExternalProduct

def products_from_b2b(request):
    # Récupérer les catégories synchronisées (qui ont un ExternalCategory)
    categories = Category.objects.filter(external_category__isnull=False).distinct()
    
    # Récupérer tous les produits synchronisés (qui ont un ExternalProduct)
    products = Product.objects.filter(external_product__isnull=False).distinct()
    
    return render(request, 'inventory/products.html', {
        'categories': categories,
        'products': products
    })
```

## 🔍 Debugging et Logs

### Activer les Logs Détaillés

Les logs sont automatiquement enregistrés. Pour voir les détails :

```python
import logging
logging.getLogger('inventory').setLevel(logging.DEBUG)
```

### Vérifier les Erreurs de Synchronisation

```python
from inventory.models import ExternalProduct

# Produits en erreur
error_products = ExternalProduct.objects.filter(sync_status='error')
for product in error_products:
    print(f"Produit {product.product.title}: {product.sync_error}")
```

## 📊 Monitoring

### Statistiques de Synchronisation

```python
from inventory.models import ExternalProduct, ExternalCategory

stats = {
    'total_products': ExternalProduct.objects.count(),
    'synced_products': ExternalProduct.objects.filter(
        sync_status='synced'
    ).count(),
    'error_products': ExternalProduct.objects.filter(
        sync_status='error'
    ).count(),
    'total_categories': ExternalCategory.objects.count(),
}

print(stats)
```

## ⚡ Automatisation

### Tâche Périodique avec Celery (optionnel)

```python
# tasks.py
from celery import shared_task
from inventory.services import ProductSyncService

@shared_task
def sync_products_periodically():
    """Synchronise les produits toutes les heures"""
    sync_service = ProductSyncService()
    stats = sync_service.sync_all_products()
    print(f"Synchronisation terminée: {stats}")
```

## 🚨 Gestion des Erreurs

### Erreurs Courantes

1. **Token non configuré**
   ```
   ValueError: B2B_API_KEY n'est pas configuré
   ```
   Solution: Vérifier le fichier `.env`

2. **URL incorrecte**
   ```
   ConnectionError: Erreur de connexion
   ```
   Solution: Vérifier `B2B_API_URL` dans `.env`

3. **Token invalide**
   ```
   HTTPError: 401 Unauthorized
   ```
   Solution: Vérifier le token dans l'admin B2B

4. **Endpoint introuvable**
   ```
   HTTPError: 404 Not Found
   ```
   Solution: Vérifier que l'endpoint existe dans l'API B2B

## ✅ Checklist de Démarrage

- [ ] Configurer `B2B_API_URL` dans `.env`
- [ ] Configurer `B2B_API_KEY` dans `.env` (optionnel, peut être remplacé par une clé dans l'admin)
- [ ] Créer une clé API active via l'admin: `/admin/inventory/apikey/add/`
- [ ] Tester la connexion: `python manage.py test_b2b_api`
- [ ] Synchroniser les catégories: `python manage.py sync_categories_from_inventory`
- [ ] Synchroniser les produits: `python manage.py sync_products_from_inventory`
- [ ] Vérifier les données dans l'admin Django
- [ ] Tester les vues et API REST

## 📚 Ressources

- Documentation API B2B: Voir la documentation de l'app de gestion de stock
- Logs: Vérifier `django.log` pour les erreurs détaillées
- Admin Django: `/admin/inventory/apikey/` pour gérer les clés API
- Processus de récupération: Voir `PROCESSUS_RECUPERATION.md` pour les détails techniques

