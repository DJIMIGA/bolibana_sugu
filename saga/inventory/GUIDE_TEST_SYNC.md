# Guide de Test de la Synchronisation Automatique B2B

## Tests à Effectuer

### 1. Test via la Commande de Management

Activez d'abord votre environnement virtuel, puis :

```bash
# Activer l'environnement virtuel (selon votre configuration)
# Windows:
venv\Scripts\activate
# ou
.venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Puis exécuter le test
python manage.py test_sync_auto

# Pour forcer la synchronisation même si récente
python manage.py test_sync_auto --force
```

### 2. Test via l'Interface Web

1. **Vérifier la page d'accueil** :
   - Visitez `http://localhost:8000/` (ou votre URL)
   - Les produits B2B devraient apparaître automatiquement
   - Vérifiez les logs pour voir si la synchronisation s'est déclenchée

2. **Vérifier l'API** :
   - Visitez `http://localhost:8000/api/inventory/products/synced/`
   - Devrait déclencher une synchronisation automatique si nécessaire
   - Devrait retourner les produits B2B synchronisés

3. **Vérifier le statut** :
   - Visitez `http://localhost:8000/inventory/status/`
   - Devrait afficher les statistiques de synchronisation

### 3. Test du Middleware

Le middleware devrait :
- Se déclencher automatiquement lors de l'accès à la page d'accueil
- Ne pas synchroniser plus d'une fois toutes les 2 heures
- Ne pas bloquer les requêtes utilisateur

**Vérification** :
1. Visitez la page d'accueil
2. Vérifiez les logs Django pour voir les messages de synchronisation
3. Visitez à nouveau la page d'accueil immédiatement - ne devrait pas synchroniser
4. Attendez 2 heures ou forcez avec `--force` pour tester à nouveau

### 4. Test de la Synchronisation Manuelle

```bash
# Synchronisation normale (respecte le cache)
python manage.py sync_products_from_inventory --auto

# Synchronisation forcée (ignore le cache)
python manage.py sync_products_from_inventory --auto --force

# Synchronisation manuelle classique
python manage.py sync_products_from_inventory
```

### 5. Vérification des Logs

Les logs devraient contenir :
- Messages de synchronisation automatique
- Statistiques de synchronisation
- Erreurs éventuelles

**Localisation des logs** :
- Fichier : `django.log` ou `django_debug.log`
- Console : si `DEBUG=True`

### 6. Vérification dans l'Admin

1. Accédez à `/admin/inventory/externalproduct/`
2. Vérifiez que les produits sont bien synchronisés (`sync_status='synced'`)
3. Vérifiez que les informations sont complètes (nom, prix, description, etc.)

### 7. Test de Performance

La synchronisation automatique devrait :
- Ne pas ralentir le chargement de la page d'accueil
- S'exécuter en arrière-plan
- Ne pas bloquer les requêtes utilisateur

**Test** :
1. Visitez la page d'accueil plusieurs fois
2. Mesurez le temps de chargement
3. Vérifiez que c'est rapide même lors d'une synchronisation

## Checklist de Vérification

- [ ] Clé API configurée dans `/admin/inventory/apikey/`
- [ ] Middleware activé dans `settings.py`
- [ ] Page d'accueil affiche les produits B2B
- [ ] Synchronisation se déclenche automatiquement
- [ ] Protection contre les synchronisations trop fréquentes fonctionne
- [ ] Les produits ont toutes leurs informations (nom, prix, description, images)
- [ ] Les logs montrent les synchronisations
- [ ] L'API retourne les produits B2B
- [ ] Pas d'erreurs dans les logs

## Dépannage

### La synchronisation ne se déclenche pas

1. Vérifiez que le middleware est dans `settings.py`
2. Vérifiez les logs pour les erreurs
3. Vérifiez qu'une clé API est configurée
4. Testez avec `python manage.py test_sync_auto --force`

### Les produits n'ont que le nom

1. Vérifiez que la synchronisation récupère les détails complets
2. Exécutez `python manage.py sync_products_from_inventory --auto --force`
3. Vérifiez les logs pour voir quelles données sont récupérées

### Erreurs de connexion API

1. Vérifiez la clé API dans `/admin/inventory/apikey/`
2. Testez la connexion avec `python manage.py test_sync_auto`
3. Vérifiez l'URL de l'API dans `settings.py` (B2B_API_URL)

## Résultats Attendus

Après les tests, vous devriez avoir :
- ✅ Des produits B2B affichés sur la page d'accueil
- ✅ Des produits avec toutes leurs informations (nom, prix, description, images)
- ✅ Une synchronisation automatique qui fonctionne
- ✅ Des logs propres sans erreurs critiques
- ✅ Une API qui retourne les produits B2B

