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

#### ModuleNotFoundError
- Problème : "ModuleNotFoundError: No module named 'product'" ou autres modules
- Solutions :
  1. Vérifier la structure des dossiers :
     ```
     saga/
     ├── manage.py
     ├── saga/
     │   ├── settings.py
     │   └── ...
     └── product/
         ├── __init__.py
         ├── models.py
         └── ...
     ```
  2. Configurer le PYTHONPATH dans manage.py :
     ```python
     import os
     import sys
     
     if __name__ == "__main__":
         os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saga.settings")
         sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
     ```
  3. Vérifier INSTALLED_APPS dans settings.py :
     ```python
     INSTALLED_APPS = [
         'product',
         'accounts',
         'suppliers',
         # ...
     ]
     ```
  4. Pour les migrations :
     - Utiliser le chemin complet : `python saga/manage.py migrate`
     - Vérifier que le module est dans le PYTHONPATH
     - S'assurer que les fichiers __init__.py sont présents

### Erreurs connues
- Erreur de colonne dupliquée : Si vous rencontrez l'erreur "column already exists" lors des migrations, cela peut indiquer que :
  - La migration a déjà été appliquée
  - Il y a un conflit dans les migrations
  - La base de données n'est pas synchronisée avec l'état des migrations

### Configuration HTTPS
- La redirection HTTPS est configurée à plusieurs niveaux :
  - Dans Django (settings.py) :
    - `SECURE_SSL_REDIRECT = True`
    - `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
  - Dans Heroku (static.json) :
    - `"https_only": true`
    - En-têtes de sécurité configurés
  - Vérification :
    - Accéder à http://bolibana.com devrait rediriger vers https://bolibana.com
    - Si la redirection ne fonctionne pas, vérifier :
      - Les logs Heroku
      - La configuration DNS
      - Les paramètres de sécurité dans settings.py

### Bonnes pratiques
- Toujours utiliser le chemin complet `saga/manage.py` pour les commandes Django sur Heroku
- Vérifier les logs Heroku en cas d'erreur avec `heroku logs --tail`
- Utiliser `--traceback` pour plus de détails sur les erreurs de migration 