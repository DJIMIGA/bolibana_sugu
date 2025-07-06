# Tests des Commandes Mixtes - SagaKore

## Vue d'ensemble

Ce dossier contient tous les tests pour le système de commandes mixtes de SagaKore, qui permet de commander ensemble des produits Salam (paiement immédiat obligatoire) et des produits classiques (paiement flexible).

## Structure des Tests

### 1. Tests Unitaires (`test_mixed_orders.py`)
- **CartService** : Tests des méthodes de service pour les commandes mixtes
- **Détection de panier mixte** : Vérification de la logique de détection
- **Résumé de panier** : Calculs des totaux et comptages
- **Validation** : Vérification des règles métier
- **Création de commandes** : Tests de création des commandes séparées

### 2. Tests d'Intégration (`test_mixed_orders.py`)
- **Vues Django** : Tests des vues checkout_mixed et payment_mixed
- **Authentification** : Vérification des protections d'accès
- **Contexte des templates** : Validation des données passées aux templates
- **Redirections** : Tests des flux de navigation

### 3. Tests Fonctionnels (`test_mixed_orders_functional.py`)
- **Parcours complet** : Test du flux utilisateur de bout en bout
- **Paiement immédiat** : Tests avec paiement immédiat pour les classiques
- **Paiement à la livraison** : Tests avec paiement à la livraison
- **Réservation de stock** : Vérification de la gestion du stock
- **Gestion d'erreurs** : Tests des cas d'erreur

### 4. Tests de Modèles (`test_mixed_orders_models.py`)
- **Relations** : Tests des relations entre modèles
- **Calculs** : Vérification des calculs de prix
- **Validation** : Tests des contraintes de données
- **Statuts** : Gestion des statuts de commande

## Exécution des Tests

### Tous les tests
```bash
python manage.py test cart.tests
```

### Tests spécifiques
```bash
# Tests unitaires uniquement
python manage.py test cart.tests.test_mixed_orders.MixedOrderServiceTestCase

# Tests fonctionnels uniquement
python manage.py test cart.tests.test_mixed_orders_functional.MixedOrderFunctionalTestCase

# Tests de modèles uniquement
python manage.py test cart.tests.test_mixed_orders_models.MixedOrderModelsTestCase
```

### Script personnalisé
```bash
python cart/tests/run_mixed_order_tests.py
```

## Couverture de Tests

Les tests couvrent les aspects suivants :

### ✅ Fonctionnalités Testées
- [x] Détection automatique des paniers mixtes
- [x] Calcul des totaux séparés (Salam/Classique)
- [x] Validation des règles métier
- [x] Création de commandes séparées
- [x] Gestion des méthodes de paiement
- [x] Réservation de stock (classiques uniquement)
- [x] Flux utilisateur complet
- [x] Gestion des erreurs
- [x] Authentification et autorisations

### 🔄 Scénarios Testés
- **Panier vide** : Redirection appropriée
- **Panier Salam uniquement** : Flux normal
- **Panier classique uniquement** : Flux normal
- **Panier mixte** : Flux spécialisé
- **Stock insuffisant** : Gestion d'erreur
- **Paiement immédiat** : Pour les classiques
- **Paiement à la livraison** : Pour les classiques

## Bonnes Pratiques

### 1. Isolation des Tests
- Chaque test utilise `setUp()` pour créer ses données
- Pas de dépendance entre les tests
- Nettoyage automatique après chaque test

### 2. Données de Test
- Utilisation de données réalistes mais simplifiées
- Prix en FCFA (Francs CFA)
- Produits typiques du contexte malien

### 3. Assertions Claires
- Messages d'erreur explicites
- Vérification des valeurs attendues
- Tests des cas limites

### 4. Performance
- Tests rapides et efficaces
- Pas de requêtes inutiles
- Utilisation de `select_related()` quand nécessaire

## Maintenance

### Ajout de Nouveaux Tests
1. Identifier la fonctionnalité à tester
2. Choisir le bon fichier de test
3. Créer une méthode de test avec un nom descriptif
4. Ajouter des assertions claires
5. Documenter le test si nécessaire

### Mise à Jour des Tests
- Vérifier que les tests passent après chaque modification
- Mettre à jour les tests si les fonctionnalités changent
- Maintenir la cohérence avec les règles métier

## Débogage

### Tests qui Échouent
1. Vérifier les messages d'erreur
2. Examiner les données de test
3. Vérifier les dépendances
4. Tester manuellement si nécessaire

### Tests Lents
- Identifier les requêtes lentes
- Optimiser les requêtes de base de données
- Utiliser des fixtures si nécessaire

## Intégration Continue

Ces tests sont conçus pour s'intégrer dans un pipeline CI/CD :
- Exécution automatique sur chaque commit
- Rapport de couverture de code
- Notification en cas d'échec
- Validation avant déploiement 