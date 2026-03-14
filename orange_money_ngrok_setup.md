# Configuration Orange Money avec ngrok pour le développement local

## Problème
L'API Orange Money n'accepte pas les URLs avec `localhost` ou `127.0.0.1` pour les callbacks. Pour le développement local, nous devons utiliser un tunnel public.

## Solution : Utiliser ngrok

### 1. Installation de ngrok
```bash
# Télécharger depuis https://ngrok.com/download
# Ou avec npm
npm install -g ngrok

# Ou avec Homebrew (macOS)
brew install ngrok
```

### 2. Configuration de ngrok
```bash
# Exposer le port 8000 (Django)
ngrok http 8000
```

### 3. Récupérer l'URL ngrok
Après avoir lancé ngrok, vous verrez quelque chose comme :
```
Forwarding    https://abc123def.ngrok.io -> http://localhost:8000
```

### 4. Configurer les variables d'environnement
Ajoutez ces lignes dans votre fichier `saga/.env.secrets` :

```bash
# URLs de callback avec ngrok
ORANGE_MONEY_NOTIFICATION_URL=https://abc123def.ngrok.io/cart/orange-money/webhook/
ORANGE_MONEY_RETURN_URL=https://abc123def.ngrok.io/cart/orange-money/return/
ORANGE_MONEY_CANCEL_URL=https://abc123def.ngrok.io/cart/orange-money/cancel/
```

**Important :** Remplacez `abc123def` par votre vraie URL ngrok.

### 5. Redémarrer le serveur Django
```bash
python manage.py runserver
```

### 6. Tester Orange Money
Maintenant vous pouvez tester les paiements Orange Money avec les URLs publiques.

## Alternative : Utiliser un domaine de test
Si vous avez un domaine de test, vous pouvez configurer les URLs directement :
```bash
ORANGE_MONEY_NOTIFICATION_URL=https://test.yourdomain.com/cart/orange-money/webhook/
ORANGE_MONEY_RETURN_URL=https://test.yourdomain.com/cart/orange-money/return/
ORANGE_MONEY_CANCEL_URL=https://test.yourdomain.com/cart/orange-money/cancel/
```

## Notes importantes
- L'URL ngrok change à chaque redémarrage (sauf avec un compte payant)
- Pour la production, utilisez votre vrai domaine
- Assurez-vous que les URLs sont accessibles publiquement
- Les URLs doivent utiliser HTTPS en production
