# Scripts de Gestion des Produits - SagaKore

## Vue d'ensemble

Ce document décrit les scripts disponibles pour gérer les produits dans SagaKore, notamment pour modifier le statut de disponibilité (`is_available`) de tous les produits.

## Scripts Disponibles

### 1. Script de Gestion Django (Recommandé)

**Fichier:** `saga/management/commands/set_all_products_unavailable.py`

**Utilisation:**
```bash
# Voir les statistiques sans modification (dry-run)
python manage.py set_all_products_unavailable --dry-run

# Exécuter avec confirmation
python manage.py set_all_products_unavailable --confirm

# Voir l'aide
python manage.py set_all_products_unavailable --help
```

**Fonctionnalités:**
- ✅ Mode dry-run pour vérifier l'impact
- ✅ Confirmation en double (option + saisie utilisateur)
- ✅ Transaction atomique pour la sécurité
- ✅ Statistiques détaillées avant/après
- ✅ Gestion des erreurs robuste

### 2. Script Python Autonome

**Fichier:** `scripts/set_all_products_unavailable.py`

**Utilisation:**
```bash
# Voir les statistiques sans modification
python scripts/set_all_products_unavailable.py --dry-run

# Exécuter avec confirmation
python scripts/set_all_products_unavailable.py --confirm

# Voir l'aide
python scripts/set_all_products_unavailable.py --help
```

**Utilisation en tant que module:**
```python
from scripts.set_all_products_unavailable import set_all_products_unavailable

# Voir les statistiques
set_all_products_unavailable(dry_run=True)

# Exécuter l'opération
set_all_products_unavailable(confirm=True)
```

## Processus de Sécurité

### Niveaux de Confirmation

1. **Option --confirm** : Première barrière de sécurité
2. **Saisie "CONFIRM"** : Confirmation finale par l'utilisateur
3. **Transaction atomique** : Rollback automatique en cas d'erreur

### Vérifications

- ✅ Statistiques avant l'opération
- ✅ Mode dry-run disponible
- ✅ Gestion des exceptions
- ✅ Vérification des résultats

## Exemples d'Utilisation

### Scénario 1: Vérification Préalable
```bash
python manage.py set_all_products_unavailable --dry-run
```
**Résultat:**
```
📊 Statistiques actuelles des produits:
   • Total des produits: 150
   • Produits disponibles: 120
   • Produits non disponibles: 30

🔍 MODE DRY-RUN - Aucune modification ne sera effectuée
   • 120 produits seraient mis is_available=False
   • 30 produits resteraient is_available=False
```

### Scénario 2: Exécution avec Confirmation
```bash
python manage.py set_all_products_unavailable --confirm
```
**Résultat:**
```
📊 Statistiques actuelles des produits:
   • Total des produits: 150
   • Produits disponibles: 120
   • Produits non disponibles: 30

🚨 CONFIRMATION FINALE:
   • 120 produits vont être mis is_available=False
   • Cette action est IRREVERSIBLE!

Tapez "CONFIRM" pour continuer: CONFIRM

✅ SUCCÈS: 120 produits ont été mis is_available=False

📊 Nouvelles statistiques:
   • Produits disponibles: 0
   • Produits non disponibles: 150

🎉 Opération terminée avec succès!
```

## Cas d'Usage

### 1. Maintenance du Site
- Mettre le site en mode maintenance
- Désactiver temporairement tous les produits
- Préparer une mise à jour majeure

### 2. Gestion des Stocks
- Désactiver les produits en rupture
- Mise à jour en masse des statuts
- Synchronisation avec un système externe

### 3. Tests et Développement
- Réinitialisation de l'environnement de test
- Simulation de scénarios de panne
- Validation des fonctionnalités de gestion

## Précautions

### ⚠️ Attention
- **Action irréversible** : Tous les produits deviendront indisponibles
- **Impact sur les utilisateurs** : Les produits ne seront plus visibles sur le site
- **Base de données** : Modification en masse de la table Product

### 🔒 Sécurité
- Toujours utiliser le mode dry-run d'abord
- Vérifier les statistiques avant l'exécution
- Confirmer l'opération en saisissant "CONFIRM"
- Utiliser en environnement contrôlé

## Récupération

### Si l'opération a été exécutée par erreur

1. **Vérifier la base de données:**
```sql
SELECT COUNT(*) as total, 
       COUNT(CASE WHEN is_available = True THEN 1 END) as available,
       COUNT(CASE WHEN is_available = False THEN 1 END) as unavailable
FROM product_product;
```

2. **Remettre les produits disponibles (si nécessaire):**
```python
from product.models import Product

# Remettre tous les produits disponibles
Product.objects.all().update(is_available=True)

# Ou remettre seulement certains produits
Product.objects.filter(category__slug='telephones').update(is_available=True)
```

## Support et Maintenance

### Logs
- Les opérations sont loggées dans la console
- Vérifier les logs Django pour plus de détails
- Surveiller les performances de la base de données

### Tests
- Tester d'abord en environnement de développement
- Utiliser le mode dry-run pour valider
- Vérifier les résultats après l'exécution

## Conclusion

Ces scripts offrent une solution sécurisée et flexible pour gérer en masse le statut de disponibilité des produits dans SagaKore. Ils respectent les bonnes pratiques Django et incluent plusieurs niveaux de sécurité pour éviter les erreurs accidentelles.

**Recommandation:** Utiliser le script de gestion Django (`python manage.py`) pour une intégration complète avec l'écosystème Django.
