# Composants de l'application Suppliers

Ce dossier contient les composants réutilisables pour l'affichage des fournisseurs et des produits.

## Structure des composants

### `_filters.html`
Composant de filtrage des produits avec les options suivantes :
- Filtre par marque
- Filtre par modèle
- Filtre par stockage
- Filtre par RAM
- Filtre par prix (min/max)
- Bouton de réinitialisation

Utilisation :
```django
{% include "suppliers/components/_filters.html" with is_detail=True %}
```
ou
```django
{% include "suppliers/components/_filters.html" with is_detail=False %}
```

### `_product_grid.html`
Composant d'affichage de la grille des produits avec :
- Grille responsive (1 à 4 colonnes selon la taille d'écran)
- Pagination
- Message si aucun produit disponible

Utilisation :
```django
{% include "suppliers/components/_product_grid.html" %}
```

### `product_card.html`
Composant d'affichage d'un produit individuel avec :
- Image du produit
- Titre
- Caractéristiques (stockage, RAM)
- Prix
- Bouton d'ajout au panier

Utilisation :
```django
{% include "suppliers/components/product_card.html" with product=product %}
```

## Intégration HTMX

Les composants utilisent HTMX pour les mises à jour dynamiques :
- Les filtres déclenchent une requête HTMX lors du changement
- La grille est mise à jour sans rechargement complet de la page
- La pagination est gérée via HTMX

## Variables de contexte requises

### Pour `_filters.html`
- `brands` : Liste des marques disponibles
- `models` : Liste des modèles disponibles
- `storages` : Liste des capacités de stockage disponibles
- `rams` : Liste des capacités RAM disponibles
- `selected_brand` : Marque sélectionnée
- `selected_model` : Modèle sélectionné
- `selected_storage` : Stockage sélectionné
- `selected_ram` : RAM sélectionnée
- `selected_price_min` : Prix minimum sélectionné
- `selected_price_max` : Prix maximum sélectionné
- `is_detail` : Booléen indiquant si on est dans la vue détaillée
- `slug` : Slug de la marque (uniquement pour la vue détaillée)

### Pour `_product_grid.html`
- `products` : Liste paginée des produits à afficher

### Pour `product_card.html`
- `product` : Objet produit à afficher 


Points d'amélioration potentiels :
Validation :
Ajouter une validation plus stricte du numéro de téléphone
Implémenter une vérification d'email par confirmation
Ajouter des règles de complexité pour le mot de passe
Expérience utilisateur :
Ajouter une barre de progression pour l'inscription
Implémenter une validation en temps réel des champs
Ajouter des messages d'aide pour chaque champ
Sécurité :
Ajouter une authentification à deux facteurs (2FA)
Implémenter une protection contre les bots (reCAPTCHA)
Ajouter une journalisation des tentatives d'inscription
Voulez-vous que je vous aide à implémenter certaines de ces améliorations ou souhaitez-vous plus de détails sur un aspect particulier du système d'inscription ?


Pour implémenter la double authentification (2FA) lors de l'inscription, voici la logique à suivre :
Processus d'inscription :
L'utilisateur remplit le formulaire d'inscription normal
Une fois les données validées, au lieu de créer directement le compte
On génère un code de vérification (6 chiffres par exemple)
On envoie ce code par SMS au numéro de téléphone fourni
On stocke temporairement les données d'inscription en session
Page de vérification :
Créer une nouvelle page qui s'affiche après la soumission du formulaire
Cette page contient un champ pour entrer le code reçu
Un bouton "Vérifier" pour valider le code
Un bouton "Renvoyer le code" si nécessaire
Un compteur de temps pour la validité du code (par exemple 5 minutes)
Logique de vérification :
Si le code est correct :
Créer le compte utilisateur avec les données stockées
Connecter automatiquement l'utilisateur
Rediriger vers la page d'accueil
Si le code est incorrect :
Afficher un message d'erreur
Permettre de réessayer ou de demander un nouveau code
Sécurité :
Limiter le nombre de tentatives (3 par exemple)
Limiter le nombre de renvois de code (3 par exemple)
Stocker les données de manière sécurisée en session
Nettoyer les données temporaires après utilisation
Voulez-vous que je commence à implémenter cette logique ?

Oui, l'implémentation de la 2FA pour l'inscription et la connexion se fait séparément car les processus sont différents. Voici comment nous pouvons procéder :
Pour l'inscription :
L'utilisateur remplit le formulaire d'inscription
On génère un code de vérification
On envoie le code par SMS au numéro fourni
On stocke temporairement les données en session
On affiche une page de vérification
Une fois le code validé, on crée le compte
Pour la connexion :
L'utilisateur entre son email/mot de passe
On vérifie les identifiants
Si correct, on génère un code de vérification
On envoie le code par SMS au numéro enregistré
On affiche une page de vérification
Une fois le code validé, on connecte l'utilisateur


nous avons déjà un système de 2FA bien implémenté pour l'admin qui utilise django-otp avec TOTP (Time-based One-Time Password). Voici les éléments transposables pour notre système de connexion utilisateur :
Modèle TwoFactorCode :
Déjà implémenté avec un système de génération de code à 6 chiffres
Gestion de l'expiration (5 minutes)
Stockage sécurisé des codes
Vues de vérification :
Nous avons déjà les templates 2fa_verify.html et 2fa_setup.html
La logique de vérification est en place
Formulaires :
Le TwoFactorForm est déjà défini pour la saisie du code
Pour adapter ce système à la connexion utilisateur, nous devrons :
Pour l'inscription :
Générer un code lors de l'inscription
Envoyer le code par SMS (comme déjà fait pour la réinitialisation de mot de passe)
Stocker temporairement les données en session
Créer une vue de vérification similaire à admin_2fa_required
Pour la connexion :
Vérifier les identifiants
Générer et envoyer un code par SMS
Rediriger vers une page de vérification
Connecter l'utilisateur après vérification
