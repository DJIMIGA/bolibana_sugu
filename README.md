# bolibana_sugu

Projet de gestion de téléphones et fournisseurs. 

# SagaKore

## Déploiement Heroku

### Configuration du projet
- Le projet utilise un Procfile configuré pour :
  - `web`: python saga/server.py
  - `worker`: python saga/manage.py process_tasks
  - `release`: python saga/manage.py migrate

### Commandes importantes
Pour exécuter les migrations sur Heroku :
```bash
heroku run python saga/manage.py migrate
```

### Résolution des problèmes courants
- En cas d'erreur "ModuleNotFoundError: No module named 'product'", vérifier que :
  - Le PYTHONPATH est correctement configuré dans manage.py
  - Les migrations sont exécutées avec le bon chemin vers manage.py
  - Le module product est bien dans INSTALLED_APPS

### Erreurs connues
- Erreur de colonne dupliquée : Si vous rencontrez l'erreur "column already exists" lors des migrations, cela peut indiquer que :
  - La migration a déjà été appliquée
  - Il y a un conflit dans les migrations
  - La base de données n'est pas synchronisée avec l'état des migrations

### Bonnes pratiques
- Toujours utiliser le chemin complet `saga/manage.py` pour les commandes Django sur Heroku
- Vérifier les logs Heroku en cas d'erreur avec `heroku logs --tail`
- Utiliser `--traceback` pour plus de détails sur les erreurs de migration 