# Règles de Développement pour SagaKore

## Évaluation des Mémoires et Bonnes Pratiques

### Critères d'Évaluation (Score 1-5)

#### Score 1-2 (À Éviter)
- Détails spécifiques à une tâche unique
- Préférences vagues ou évidentes
- Détails d'implémentation spécifiques
- Exemples :
  - "Ajouter margin-top: 10px à .card-title" (trop spécifique)
  - "Le code doit être bien organisé" (trop évident)
  - "Utiliser 'userData' pour le résultat de l'API" (détail d'implémentation)
  - "Les tests sont importants" (trop évident)

#### Score 3 (Neutre)
- Préférences spécifiques au projet mais utiles
- Exemples :
  - "Le code frontend utilise Tailwind CSS"
  - "Les modèles Django doivent être dans le dossier models/"
  - "Utiliser les vues basées sur les classes pour les formulaires"

#### Score 4-5 (À Retenir)
- Préférences claires et actionnables
- Règles de développement spécifiques
- Exemples :
  - "Toujours utiliser select_related() pour les relations ForeignKey"
  - "Activer strictNullChecks dans TypeScript"
  - "Écrire les tests avant d'implémenter une nouvelle fonctionnalité"
  - "Utiliser les environnements virtuels pour isoler les dépendances"

### Règles Spécifiques à Django

#### Structure du Projet (Score 4)
- Organiser les applications selon la structure recommandée
- Séparer les modèles, vues et formulaires dans des fichiers distincts
- Utiliser les namespaces pour les URLs

#### Sécurité (Score 5)
- Toujours utiliser les protections CSRF de Django
- Ne jamais exposer de données sensibles dans le code front-end
- Utiliser les variables d'environnement pour les paramètres sensibles

#### Performance (Score 4)
- Utiliser select_related() et prefetch_related() pour les requêtes
- Mettre en cache les données fréquemment accédées
- Optimiser les requêtes de base de données

#### Tests (Score 5)
- Écrire des tests unitaires pour les fonctions critiques
- Utiliser les outils de test de Django
- Maintenir une couverture de tests > 80%

#### Documentation (Score 4)
- Commenter le code de manière claire et concise
- Maintenir une documentation à jour
- Documenter les API et les fonctionnalités principales

#### Versioning (Score 4)
- Utiliser Git pour le contrôle de version
- Faire des commits fréquents avec des messages descriptifs
- Suivre une convention de nommage pour les branches

#### Déploiement (Score 5)
- Suivre une checklist de déploiement
- Utiliser des variables d'environnement
- Tester en environnement de staging avant production

### Règles Spécifiques à SagaKore

#### Authentification (Score 5)
- Implémenter la 2FA pour les utilisateurs sensibles
- Utiliser des mots de passe forts
- Limiter les tentatives de connexion

#### Interface Utilisateur (Score 4)
- Utiliser Tailwind CSS pour le styling
- Suivre les bonnes pratiques d'UX
- Maintenir une interface responsive

#### API (Score 4)
- Documenter toutes les endpoints
- Utiliser la pagination pour les grandes listes
- Implémenter la validation des données

#### Base de Données (Score 5)
- Utiliser les migrations Django
- Faire des sauvegardes régulières
- Optimiser les index et les requêtes

### Processus de Développement

1. **Planification**
   - Définir les objectifs clairement
   - Évaluer les dépendances
   - Estimer le temps nécessaire

2. **Développement**
   - Suivre les standards de code
   - Écrire des tests
   - Documenter les changements

3. **Revue**
   - Vérifier la qualité du code
   - Tester les fonctionnalités
   - Valider la sécurité

4. **Déploiement**
   - Suivre la checklist
   - Vérifier les environnements
   - Monitorer les performances

### Maintenance

1. **Surveillance**
   - Monitorer les logs
   - Vérifier les performances
   - Maintenir les dépendances

2. **Mises à Jour**
   - Planifier les mises à jour
   - Tester les changements
   - Documenter les modifications

3. **Sécurité**
   - Vérifier les vulnérabilités
   - Mettre à jour les dépendances
   - Maintenir les certificats

## Bonnes Pratiques de Développement avec l'IA

### Utilisation des Outils de Développement

#### Recherche et Lecture
- Préférer la recherche sémantique pour trouver du code pertinent
- Lire des sections complètes de fichiers plutôt que des morceaux
- S'assurer d'avoir le contexte complet avant de faire des modifications

#### Modifications de Code
- Ne jamais afficher le code directement à l'utilisateur
- Utiliser les outils d'édition de code pour les modifications
- Grouper les modifications d'un même fichier dans un seul appel
- Créer des fichiers de gestion de dépendances appropriés
- Créer une interface utilisateur moderne et intuitive
- Lire le contenu avant de modifier
- Corriger les erreurs de linter de manière éclairée
- Ne pas faire plus de 3 tentatives de correction d'erreurs

#### Exécution de Commandes
- Suivre exactement le schéma des appels d'outils
- Ne jamais appeler des outils non disponibles
- Ne pas mentionner les noms des outils à l'utilisateur
- N'appeler les outils que lorsque nécessaire
- Expliquer chaque appel d'outil avant de l'effectuer

### Format de Citation du Code
- Utiliser le format ```startLine:endLine:filepath
- Citer uniquement les sections pertinentes du code
- Utiliser les commentaires `// ... existing code ...` pour le code inchangé

### Gestion des Erreurs
- Vérifier les paramètres requis avant d'appeler les outils
- Demander des valeurs manquantes si nécessaire
- Utiliser exactement les valeurs fournies par l'utilisateur
- Analyser les termes descriptifs pour les paramètres requis

## Communication et Développement

### Communication
- Toujours répondre en français
- Utiliser le formatage Markdown pour les noms de fichiers, répertoires, fonctions et classes
- Utiliser `\\(` et `\\)` pour les formules mathématiques en ligne
- Utiliser `\\[` et `\\]` pour les formules mathématiques en bloc

### Utilisation des Outils
- Suivre exactement le schéma des appels d'outils
- Ne jamais appeler des outils non disponibles
- Ne pas mentionner les noms des outils à l'utilisateur
- Préférer les appels d'outils aux questions à l'utilisateur
- Exécuter immédiatement le plan établi
- Utiliser uniquement le format standard d'appel d'outils

### Recherche et Lecture
- Rechercher des informations supplémentaires si nécessaire
- Effectuer plusieurs appels d'outils si les résultats sont insuffisants
- Éviter de demander de l'aide à l'utilisateur si possible

### Modifications de Code
- Ne suggérer des modifications que si l'utilisateur les demande
- Présenter les modifications de manière simplifiée
- Utiliser des commentaires pour indiquer le code inchangé
- Réécrire le fichier entier uniquement si demandé
- Fournir une brève explication des modifications

### Format de Citation du Code
- Utiliser le format ```startLine:endLine:filepath
- Citer uniquement les sections pertinentes du code
- Utiliser les commentaires `// ... existing code ...` pour le code inchangé

### Gestion des Erreurs
- Vérifier les paramètres requis avant d'appeler les outils
- Demander des valeurs manquantes si nécessaire
- Utiliser exactement les valeurs fournies par l'utilisateur
- Analyser les termes descriptifs pour les paramètres requis 