# ⚡ Démarrage Rapide - Intégration API B2B

## 🎯 En 5 Minutes

### 1. Configuration (1 min)

Ajoutez dans votre fichier `.env` :

```env
B2B_API_URL=https://www.bolibanastock.com/api/v1
B2B_API_KEY=b2c_1_votre_token_ici
```

### 2. Tester la Connexion (1 min)

```bash
python manage.py test_b2b_api
```

### 3. Créer une Connexion (1 min)

Via l'interface web : `/inventory/connect/`
- L'URL est optionnelle (utilise `B2B_API_URL` par défaut)
- Le token vient automatiquement de `.env`

### 4. Synchroniser les Catégories (1 min)

```bash
python manage.py sync_categories_from_inventory
```

### 5. Synchroniser les Produits (1 min)

```bash
python manage.py sync_products_from_inventory
```

## ✅ C'est Prêt !

Les produits et catégories de B2B sont maintenant disponibles dans SagaKore :

- **Vues web** : `/inventory/categories/`
- **API REST** : `/api/inventory/categories/synced/`
- **Dans vos templates** : `{% for category in synced_categories %}`

## 🔄 Synchronisation Automatique des Ventes

Les ventes sont automatiquement synchronisées vers B2B lors de la création d'une commande (via les signaux Django).

## 📚 Documentation Complète

- `README.md` : Configuration détaillée
- `GUIDE_UTILISATION.md` : Exemples d'utilisation
- `INTEGRATION_CATEGORIES.md` : Exploitation des catégories

