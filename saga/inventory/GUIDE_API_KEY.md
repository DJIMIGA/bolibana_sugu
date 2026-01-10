# 🔑 Guide d'Utilisation des Clés API

## Vue d'ensemble

Le modèle `ApiKey` permet de stocker les clés API de manière sécurisée (chiffrées) dans la base de données. Chaque connexion (`InventoryConnection`) peut avoir une ou plusieurs clés API.

## Installation

### 1. Installer la dépendance

```bash
pip install cryptography
```

Ou ajoutez `cryptography==43.0.3` à votre `requirements.txt` (déjà fait).

### 2. Configurer la clé de chiffrement

Ajoutez dans votre fichier `.env` :

```env
# Clé de chiffrement pour les clés API
# Générer avec: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
INVENTORY_ENCRYPTION_KEY=votre_cle_de_chiffrement_ici
```

**Important** : En production, utilisez une clé fixe. Si vous changez la clé, toutes les clés API stockées deviendront illisibles.

### 3. Appliquer les migrations

```bash
python manage.py migrate inventory
```

## Utilisation dans l'Admin Django

### Ajouter une clé API

1. Aller dans `/admin/inventory/apikey/add/`
2. Sélectionner la **Connexion** (InventoryConnection)
3. Donner un **Nom** à la clé (ex: "Clé principale - Site Bamako")
4. Entrer la **Clé API** en clair (elle sera automatiquement chiffrée)
5. Cocher **Active** si vous voulez l'utiliser immédiatement
6. Sauvegarder

### Modifier une clé API

1. Aller dans `/admin/inventory/apikey/`
2. Cliquer sur la clé à modifier
3. Entrer une nouvelle clé dans le champ "Clé API" (laisser vide pour conserver l'actuelle)
4. Sauvegarder

### Voir les clés API d'une connexion

Dans `/admin/inventory/inventoryconnection/`, la colonne "Clé API" indique si une clé est active.

## Fonctionnement

### Priorité des clés API

1. **Clé API stockée** : Si une `ApiKey` active existe pour la connexion, elle est utilisée
2. **Clé globale** : Sinon, utilise `B2B_API_KEY` depuis `.env`

### Chiffrement

- Les clés API sont automatiquement chiffrées avant stockage
- Utilise `Fernet` (cryptographie symétrique)
- La clé de chiffrement est dans `INVENTORY_ENCRYPTION_KEY`

### Utilisation automatique

Quand vous utilisez `InventoryAPIClient` avec une connexion :

```python
from inventory.models import InventoryConnection
from inventory.services import InventoryAPIClient

connection = InventoryConnection.objects.get(id=1)
api_client = InventoryAPIClient(connection)
# La clé API active est automatiquement utilisée
```

## Exemple d'utilisation

### Scénario : Plusieurs sites avec différentes clés

1. **Site Bamako** :
   - Créer `InventoryConnection` pour l'utilisateur du site Bamako
   - Ajouter `ApiKey` avec la clé API du site Bamako

2. **Site Ouagadougou** :
   - Créer `InventoryConnection` pour l'utilisateur du site Ouagadougou
   - Ajouter `ApiKey` avec la clé API du site Ouagadougou

3. **Synchronisation** :
   ```bash
   # Synchroniser le site Bamako
   python manage.py sync_products_from_inventory --connection-id 1
   
   # Synchroniser le site Ouagadougou
   python manage.py sync_products_from_inventory --connection-id 2
   ```

## Sécurité

✅ **Bonnes pratiques** :
- Les clés sont chiffrées en base de données
- Seul l'aperçu (premiers/derniers caractères) est visible dans l'admin
- La clé de chiffrement est dans `.env` (ne pas commiter)

⚠️ **Attention** :
- Ne partagez jamais `INVENTORY_ENCRYPTION_KEY`
- Changez les clés API régulièrement
- Désactivez les clés API non utilisées

## Dépannage

### Erreur : "Impossible de déchiffrer la clé API"

- Vérifiez que `INVENTORY_ENCRYPTION_KEY` est correctement configuré
- La clé de chiffrement doit être la même que celle utilisée lors de la création

### Erreur : "Aucune clé API configurée"

- Vérifiez qu'une `ApiKey` active existe pour la connexion
- Ou configurez `B2B_API_KEY` dans `.env` comme fallback

### Générer une nouvelle clé de chiffrement

**Option 1 : Script Python (recommandé)**
```bash
python saga/generate_encryption_key.py
```

**Option 2 : Ligne de commande (Linux/Mac)**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Option 3 : Ligne de commande (PowerShell Windows)**
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Option 4 : Dans le shell Python**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

Copiez le résultat dans `INVENTORY_ENCRYPTION_KEY` dans votre `.env`.

