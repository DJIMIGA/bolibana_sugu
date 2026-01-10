# 🔄 Processus de Récupération des Données depuis B2B

## 📋 Vue d'Ensemble

Le système de récupération fonctionne en plusieurs étapes pour synchroniser les données depuis l'application B2B (BoliBanaStock) vers SagaKore.

## 🔑 Étape 1 : Authentification

### Configuration de la Clé API

Le système utilise une **clé API active unique** pour s'authentifier auprès de l'API B2B.

**Méthode de récupération de la clé** :
1. **Priorité 1** : Récupère la première clé `ApiKey` avec `is_active=True` depuis la base de données
2. **Priorité 2** : Fallback vers `B2B_API_KEY` dans le fichier `.env`

**Code de récupération** :
```python
# Dans services.py - InventoryAPIClient.__init__()
self.token = ApiKey.get_active_key()

# Dans models.py - ApiKey.get_active_key()
@classmethod
def get_active_key(cls):
    api_key = cls.objects.filter(is_active=True).first()
    if api_key:
        return api_key.get_key()
    # Fallback vers settings
    return getattr(settings, 'B2B_API_KEY', '')
```

### Configuration de l'URL API

L'URL de base est récupérée depuis :
- `settings.B2B_API_URL` (par défaut : `https://www.bolibanastock.com/api/v1`)

## 📥 Étape 2 : Récupération des Données

### Pour les Catégories

**Processus** :
1. Appel API : `GET /b2c/categories/`
2. Récupération de la liste complète des catégories
3. Traitement par pagination si nécessaire

**Code** :
```python
# Dans services.py - InventoryAPIClient.get_categories_list()
endpoint = 'b2c/categories/'
response = self._make_request('GET', endpoint)
```

**Format de réponse attendu** :
- Liste directe : `[{id, name, parent_id, ...}, ...]`
- Ou dict avec clé : `{results: [...], categories: [...]}`

### Pour les Produits

**Processus** :
1. Appel API avec pagination : `GET /api/products/?page=1&page_size=100`
2. Récupération page par page jusqu'à épuisement
3. Traitement de chaque produit individuellement

**Code** :
```python
# Dans services.py - InventoryAPIClient.get_products_list()
params = {'page': page, 'page_size': page_size}
if site_id:
    params['site_id'] = site_id
endpoint = 'api/products/'
return self._make_request('GET', endpoint, params=params)
```

**Pagination** :
- Le système continue tant que `response.next` existe
- Par défaut : 100 produits par page

## 🔄 Étape 3 : Synchronisation dans la Base de Données

### Synchronisation des Catégories

**Processus en 2 passes** :

1. **Passe 1 - Création/Mise à jour** :
   - Pour chaque catégorie reçue :
     - Cherche si `ExternalCategory` existe avec `external_id`
     - Si oui : met à jour la `Category` liée
     - Si non : crée une nouvelle `Category` + `ExternalCategory`
   - Stocke les catégories dans un mapping `{external_id: category}`

2. **Passe 2 - Relations parent/enfant** :
   - Pour chaque catégorie avec un `parent_id` :
     - Établit la relation `category.parent = parent_category`
     - Sauvegarde la relation

**Code** :
```python
# Dans services.py - ProductSyncService.sync_categories()
# Passe 1
for category_data in categories_data:
    result = self.create_or_update_category(category_data)
    categories_by_id[external_id] = result['category']

# Passe 2
for category_data in categories_data:
    if parent_id and external_id in categories_by_id:
        category.parent = categories_by_id[parent_id]
        category.save()
```

### Synchronisation des Produits

**Processus** :
1. Pour chaque produit reçu :
   - Cherche si `ExternalProduct` existe avec `external_id`
   - Récupère ou crée la catégorie associée via `category_id`
   - Si produit existe : met à jour les champs
   - Si produit n'existe pas : crée `Product` + `ExternalProduct`
   - Met à jour `sync_status` et `last_synced_at`

**Mapping des champs** :
- `name` → `title`
- `price` → `price`
- `stock` → `stock`
- `sku` → `sku` et `external_sku`
- `category_id` → `category` (via `ExternalCategory`)

**Code** :
```python
# Dans services.py - ProductSyncService.create_or_update_product()
external_product = ExternalProduct.objects.filter(
    external_id=external_id
).first()

if external_product:
    # Mise à jour
    product = external_product.product
    # ... mise à jour des champs
else:
    # Création
    product = Product(**product_data)
    external_product = ExternalProduct.objects.create(...)
```

## 🛡️ Gestion des Erreurs

### Erreurs API

**Types d'erreurs gérées** :
- `Timeout` : Délai d'attente dépassé (30s par défaut)
- `ConnectionError` : Problème de connexion réseau
- `HTTPError` : Erreur HTTP (4xx, 5xx)
- `RequestException` : Autres erreurs de requête

**Traitement** :
- Log de l'erreur avec `logger.error()`
- Levée d'une `InventoryAPIError`
- Arrêt de la synchronisation pour cette page/requête

### Erreurs de Synchronisation

**Pour chaque produit/catégorie** :
- Erreur capturée individuellement
- Ajoutée à `stats['errors_list']`
- Incrémentation de `stats['errors']`
- Continuation avec les autres éléments

**Statistiques retournées** :
```python
{
    'total': 100,
    'created': 50,
    'updated': 45,
    'errors': 5,
    'errors_list': [
        {'product_id': 123, 'error': '...'},
        ...
    ]
}
```

## 📊 Commandes de Management

### Synchronisation des Catégories

```bash
python manage.py sync_categories_from_inventory
```

**Comportement** :
- Récupère toutes les catégories depuis B2B
- Synchronise dans la base de données
- Affiche les statistiques

**Note** : Cette commande n'accepte **PAS** l'argument `--connection-id` car le système utilise une clé API active globale.

### Synchronisation des Produits

```bash
# Tous les produits
python manage.py sync_products_from_inventory

# Pour un site spécifique
python manage.py sync_products_from_inventory --site-id 1
```

**Comportement** :
- Récupère tous les produits (ou d'un site spécifique)
- Synchronise page par page
- Affiche les statistiques

**Note** : Cette commande n'accepte **PAS** l'argument `--connection-id`.

## 🔍 Flux Détaillé

### Flux Complet de Synchronisation

```
1. Initialisation
   ├─ InventoryAPIClient.__init__()
   │  ├─ Récupère B2B_API_URL depuis settings
   │  └─ Récupère token via ApiKey.get_active_key()
   │
   └─ ProductSyncService.__init__()
      └─ Crée InventoryAPIClient

2. Récupération des Données
   ├─ Appel API (GET /b2c/categories/ ou GET /api/products/)
   ├─ Vérification de la réponse HTTP
   ├─ Parsing JSON
   └─ Gestion des erreurs (timeout, connexion, HTTP)

3. Traitement des Données
   ├─ Pour chaque élément :
   │  ├─ Vérification existence (ExternalProduct/ExternalCategory)
   │  ├─ Création ou mise à jour
   │  ├─ Gestion des relations (catégories parent/enfant)
   │  └─ Mise à jour des métadonnées (sync_status, last_synced_at)
   │
   └─ Collecte des statistiques

4. Retour des Résultats
   └─ Statistiques (total, created, updated, errors)
```

## ⚙️ Configuration Requise

### Variables d'Environnement

```env
# URL de base de l'API B2B
B2B_API_URL=https://www.bolibanastock.com/api/v1

# Clé API (fallback si aucune clé active en BDD)
B2B_API_KEY=b2c_1_votre_token_ici

# Clé de chiffrement pour les clés API stockées
INVENTORY_ENCRYPTION_KEY=votre_cle_fernet

# Timeout des requêtes API (optionnel, défaut: 30s)
INVENTORY_API_TIMEOUT=30
```

### Configuration via l'Admin Django

1. **Créer une clé API** :
   - `/admin/inventory/apikey/add/`
   - Nom : "Clé principale"
   - Clé API : Entrer la clé réelle
   - Active : Cocher
   - Sauvegarder

2. **Vérifier la clé active** :
   - `/admin/inventory/apikey/`
   - Une seule clé doit être active à la fois

## 🎯 Points Importants

1. **Clé API Unique** : Le système utilise une seule clé active à la fois (pas de multi-connexions)

2. **Pagination Automatique** : Les produits sont récupérés page par page automatiquement

3. **Transactions Atomiques** : Chaque produit/catégorie est créé/mis à jour dans une transaction

4. **Gestion des Relations** : Les catégories parent/enfant sont établies en 2 passes

5. **Robustesse** : Les erreurs individuelles n'arrêtent pas toute la synchronisation

6. **Traçabilité** : Chaque synchronisation enregistre `last_synced_at` et `sync_status`


