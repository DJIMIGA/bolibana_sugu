# Rapport de Test : Mode Hors Ligne Haute Sécurité

Ce document décrit les éléments à tester pour vérifier le bon fonctionnement du mode hors ligne.

## 1. Persistance Chiffrée
- **Action** : Ouvrir l'application, naviguer sur quelques produits, puis aller dans `Paramètres` > `Debug Storage (Logs)`.
- **Vérification** : Dans les logs du terminal (Metro), vous devriez voir `🔒 persist:root seems encrypted`.
- **Succès** : Si le log indique que les données ne sont pas parsables en JSON, le chiffrement AES fonctionne.

## 2. Mode Lecture Seule (Hors Ligne)
- **Action** : Activer le mode avion sur le téléphone/émulateur. Relancer l'application.
- **Vérification** : 
    - L'application doit charger les produits consultés précédemment (depuis le cache chiffré).
    - Essayer d'ajouter un produit au panier.
    - Une alerte doit apparaître : "Mode lecture seule : Votre session a expiré ou vous êtes hors ligne".
- **Succès** : L'utilisateur ne peut pas corrompre le panier sans connexion si son token n'est pas vérifiable.

## 3. Téléchargement Manuel
- **Action** : Se reconnecter à internet. Aller dans `Paramètres` > `Préparer le mode hors ligne`.
- **Vérification** : La barre de progression doit s'afficher et monter jusqu'à 100%.
- **Action 2** : Repasser en mode avion et vérifier que les catégories et produits sont toujours là sans avoir à les charger individuellement.
- **Succès** : Les données sont préchargées et persistées de manière sécurisée.

## 4. Sécurité des Tokens
- **Action** : Vérifier le log `🔑 Auth Token in SecureStore`.
- **Vérification** : Il doit être `PRESENT` si vous êtes connecté.
- **Succès** : Les tokens sont gérés par le système de stockage sécurisé natif, séparé d'AsyncStorage.

