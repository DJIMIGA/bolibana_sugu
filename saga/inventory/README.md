# 📦 Intégration avec l'App de Gestion de Stock (B2B)

## 🔑 Configuration du Token API

### Architecture

Le token API est **stocké uniquement dans les variables d'environnement** (fichier `.env`), **PAS dans la base de données**.

```
┌─────────────────────────────────────┐
│   PROJET B2B (BoliBanaStock)       │
│   ───────────────────────────────   │
│   ✅ Table: core_b2capikey          │
│   ✅ Stocke les tokens               │
│   ✅ Vérifie les tokens              │
└─────────────────────────────────────┘
              ▲
              │ HTTP Request
              │ Header: X-API-Key
              │
┌─────────────┴─────────────────────┐
│   PROJET B2C (SagaKore)           │
│   ───────────────────────────────  │
│   ✅ Variable d'environnement       │
│   ✅ Fichier .env                   │
│   ✅ settings.py                    │
│   ❌ PAS de stockage en BDD         │
└─────────────────────────────────────┘
```

### Configuration

1. **Obtenir le token depuis le projet B2B**
   - Aller dans l'admin B2B : `/admin/core/b2capikey/`
   - Créer ou copier un token existant
   - Exemple : `b2c_1_NUbEpk-vq5vMEdknszvuFEZOYo_QWB8egYjvpp5BMN8`

2. **Ajouter la configuration dans le fichier `.env`**
   ```env
   # URL de base de l'API B2B
   B2B_API_URL=https://www.bolibanastock.com/api/v1
   
   # Token API (NE JAMAIS COMMITER DANS GIT !)
   B2B_API_KEY=b2c_1_NUbEpk-vq5vMEdknszvuFEZOYo_QWB8egYjvpp5BMN8
   ```

3. **Vérifier la configuration dans `settings.py`**
   ```python
   # URL de base de l'API B2B
   B2B_API_URL = os.getenv('B2B_API_URL', 'https://www.bolibanastock.com/api/v1')
   
   # Token API
   B2B_API_KEY = os.getenv('B2B_API_KEY', '')
   ```

### Utilisation

Le token et l'URL sont automatiquement utilisés dans `InventoryAPIClient` :

```python
# L'URL vient de connection.get_api_base_url() ou settings.B2B_API_URL
# Le token est récupéré depuis settings.B2B_API_KEY
api_client = InventoryAPIClient(connection)

# Les requêtes incluent automatiquement le header X-API-Key
# Les endpoints utilisent le préfixe /b2c/ (ex: /b2c/products/)
response = api_client.get_products_list()
```

### Endpoints API Utilisés

Tous les endpoints utilisent le préfixe `/b2c/` :

- **Produits** : `GET /b2c/products/` et `GET /b2c/products/{id}/`
- **Catégories** : `GET /b2c/categories/` et `GET /b2c/categories/{id}/`
- **Sites** : `GET /b2c/sites/`
- **Ventes** : `POST /b2c/sales/` et `PUT /b2c/sales/{id}/`

### Sécurité

- ✅ Token dans `.env` (pas dans le code)
- ✅ `.env` dans `.gitignore` (pas committé)
- ✅ Variables d'environnement en production (Railway, Heroku, etc.)
- ✅ Token unique par site (géré dans B2B)

## 🔄 Flux de synchronisation

### 1. Connexion à l'app de gestion

```python
# Dans la vue connect_inventory
# L'utilisateur fournit uniquement l'URL de base de l'API
# Le token vient automatiquement de settings.B2B_API_KEY
```

### 2. Synchronisation des produits

```python
# Le service utilise automatiquement le token depuis settings
sync_service = ProductSyncService(connection)
stats = sync_service.sync_all_products()
```

### 3. Synchronisation des ventes

```python
# Les signaux Django synchronisent automatiquement
# Le token est utilisé via InventoryAPIClient
```

## 📝 Exemple de configuration

### Fichier `.env`

```env
# URL de base de l'API B2B
B2B_API_URL=https://www.bolibanastock.com/api/v1

# Token API pour l'app de gestion de stock (B2B)
# NE JAMAIS COMMITER DANS GIT !
B2B_API_KEY=b2c_1_NUbEpk-vq5vMEdknszvuFEZOYo_QWB8egYjvpp5BMN8

# Configuration optionnelle
INVENTORY_API_TIMEOUT=30
INVENTORY_API_MAX_RETRIES=3
INVENTORY_SYNC_FREQUENCY=60
```

### Vérification

Pour vérifier que la configuration est correcte :

```python
from django.conf import settings

# Vérifier l'URL
api_url = getattr(settings, 'B2B_API_URL', 'https://www.bolibanastock.com/api/v1')
print(f"URL API: {api_url}")

# Vérifier le token
if hasattr(settings, 'B2B_API_KEY') and settings.B2B_API_KEY:
    print("✅ Token configuré")
else:
    print("❌ Token non configuré - Configurez B2B_API_KEY dans .env")
```

### Exemple d'Utilisation Directe

```python
import requests
from django.conf import settings

# Configuration depuis settings
API_BASE_URL = settings.B2B_API_URL  # https://www.bolibanastock.com/api/v1
API_KEY = settings.B2B_API_KEY

headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Récupérer les produits
response = requests.get(f'{API_BASE_URL}/b2c/products/', headers=headers)
products = response.json()
```

## 🚨 Dépannage

### Erreur : "B2B_API_KEY n'est pas configuré"

1. Vérifier que le fichier `.env` existe à la racine du projet
2. Vérifier que `B2B_API_KEY` est défini dans `.env`
3. Redémarrer le serveur Django après modification de `.env`

### Erreur : "401 Unauthorized"

1. Vérifier que le token est correct dans `.env`
2. Vérifier que le token est actif dans l'admin B2B
3. Vérifier que le header `X-API-Key` est bien envoyé (vérifier les logs)

## 📋 Résumé

| Élément | Où ? | Comment ? |
|---------|------|-----------|
| **URL API** | `.env` ou `settings.py` | Variable `B2B_API_URL` (défaut: `https://www.bolibanastock.com/api/v1`) |
| **Token API** | `.env` | Variable `B2B_API_KEY` |
| **Stockage** | ❌ Pas en BDD | ✅ Variables d'environnement |
| **Création token** | B2B Admin | `/admin/core/b2capikey/` |
| **Utilisation URL** | `InventoryAPIClient` | Via `connection.get_api_base_url()` ou `settings.B2B_API_URL` |
| **Utilisation token** | `InventoryAPIClient` | Automatique via `settings.B2B_API_KEY` |
| **Header HTTP** | `X-API-Key` | Envoyé automatiquement |
| **Endpoints** | `/b2c/*` | Préfixe B2C pour tous les endpoints |

