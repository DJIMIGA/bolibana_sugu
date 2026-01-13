# Diagnostic B2B : Comment voir les logs détaillés de synchronisation

## Problème

Les logs détaillés de synchronisation ne sont pas visibles car la synchronisation automatique est bloquée si elle a été faite récemment (moins de 60 minutes).

## Solution : Forcer la synchronisation

### Via l'API (Recommandé)

Ajoutez le paramètre `?force=true` à l'URL de l'API pour forcer une synchronisation et voir les logs détaillés :

```
GET /api/inventory/products/synced/?force=true
```

**Exemple avec curl :**
```bash
curl "https://www.bolibana.com/api/inventory/products/synced/?force=true"
```

**Exemple dans le navigateur :**
```
https://www.bolibana.com/api/inventory/products/synced/?force=true
```

### Via la commande Django

```bash
python manage.py sync_products_from_inventory --auto --force
```

## Logs détaillés disponibles

Une fois la synchronisation forcée, vous verrez dans les logs Heroku :

### 1. Début de synchronisation
```
[SYNC B2B] 🚀 Démarrage synchronisation produits B2B
```

### 2. Produits par page
```
[SYNC B2B] 📄 Page 1: X produits récupérés
```

### 3. Produits créés/mis à jour
```
[SYNC B2B] ✅ Produit 123 créé: Nom du produit
[SYNC B2B] 🔄 Produit 124 mis à jour: Nom du produit
```

### 4. Erreurs avec catégorisation
```
[SYNC B2B] ❌ Erreur produit 125: Impossible de trouver ou créer la catégorie...
```

### 5. Résumé final
```
[SYNC B2B] 📊 RÉSUMÉ SYNCHRONISATION
Total produits B2B dans l'API: X
Produits traités: Y
  - Créés: Z
  - Mis à jour: W
  - Erreurs: E
  - Ignorés: I

Raisons des produits ignorés:
  - category_missing: X
  - validation_error: Y
  - other_error: Z

Produits synchronisés (sync_status='synced' + is_b2b=True): A
Produits avec relation Product: B
Produits disponibles (is_available=True): C
⚠️  X produits B2B ne sont pas synchronisés
⚠️  Y produits synchronisés ne sont pas disponibles (is_available=False)
```

### 6. Avertissements pour produits non disponibles
```
[SYNC B2B] ⚠️  Produit 123 synchronisé mais is_available=False (ne sera pas visible dans l'API)
```

## Vérifier les logs Heroku

Pour voir les logs en temps réel :

```bash
heroku logs --tail --app bolibana-sugu
```

Pour filtrer uniquement les logs de synchronisation :

```bash
heroku logs --tail --app bolibana-sugu | grep "SYNC B2B"
```

## Causes possibles des produits manquants

D'après les logs, les produits peuvent être manquants pour ces raisons :

1. **Catégorie manquante** (`category_missing`)
   - Le produit B2B n'a pas de catégorie valide
   - Solution : Synchroniser les catégories d'abord

2. **Erreur de validation** (`validation_error`)
   - Les données du produit B2B ne passent pas la validation
   - Vérifier les champs requis dans le JSON B2B

3. **Produit non disponible** (`is_available=False`)
   - Le produit est synchronisé mais marqué comme non disponible
   - Vérifier `is_available_b2c` ou `is_available` dans le JSON B2B

4. **Autre erreur** (`other_error`)
   - Erreur inattendue lors de la synchronisation
   - Vérifier les détails dans les logs

## Exemple d'utilisation

1. Forcer une synchronisation :
   ```bash
   curl "https://www.bolibana.com/api/inventory/products/synced/?force=true"
   ```

2. Consulter les logs Heroku :
   ```bash
   heroku logs --tail --app bolibana-sugu | grep "SYNC B2B"
   ```

3. Analyser le résumé pour identifier les produits manquants et leurs raisons
