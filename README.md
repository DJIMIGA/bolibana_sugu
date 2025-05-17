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

#### Problème de stockage S3
- Problème : Erreur lors du téléchargement d'images dans l'interface d'administration
  ```
  TypeError: _path_normpath: path should be string, bytes or os.PathLike, not NoneType
  ```
- Cause : Configuration incorrecte du stockage S3 dans les modèles Django
- Solution :
  1. Créer une instance explicite de S3Boto3Storage dans les modèles :
     ```python
     s3_storage = S3Boto3Storage(
         bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
         region_name=settings.AWS_S3_REGION_NAME,
         custom_domain=settings.AWS_S3_CUSTOM_DOMAIN,
         access_key=settings.AWS_ACCESS_KEY_ID,
         secret_key=settings.AWS_SECRET_ACCESS_KEY,
         file_overwrite=False,
         default_acl=None,
         querystring_auth=True,
         object_parameters=settings.AWS_S3_OBJECT_PARAMETERS
     )
     ```
  2. Utiliser cette instance pour sauvegarder les fichiers :
     ```python
     self.image = s3_storage.save(filename, ContentFile(file_content))
     ```
  3. Vérifier les variables d'environnement dans .env :
     ```
     AWS_ACCESS_KEY_ID=votre_clé_access
     AWS_SECRET_ACCESS_KEY=votre_clé_secrète
     AWS_STORAGE_BUCKET_NAME=nom_de_votre_bucket
     AWS_S3_REGION_NAME=eu-north-1
     ```
  4. Structure des fichiers sur S3 :
     - Format : `products/YYYY/MM/DD/nom-du-produit_identifiant.extension`
     - Exemple : `products/2025/05/13/samsung-galaxy-a05-64-go-argent_LVkZakf.jpg`

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

## Gestion des fichiers statiques et médias

### Environnement de production (Heroku)
- **WhiteNoise** est utilisé pour servir les fichiers statiques (CSS, JS, images, etc.) directement depuis le serveur Heroku, sans passer par S3.
- **Amazon S3** est utilisé uniquement pour les fichiers médias (uploads utilisateurs, images produits, etc.).
- Les fichiers statiques sont collectés dans le dossier `staticfiles` lors du déploiement et servis de façon optimisée (compression, cache, manifest) par WhiteNoise.
- Les médias sont stockés sur S3 pour garantir la persistance et l'évolutivité.

### Environnement de développement (local)
- Les fichiers statiques sont servis depuis le dossier local `static`.
- Les fichiers médias sont stockés et servis depuis le dossier local `media`.
- Cela permet un développement plus rapide et une gestion simplifiée des fichiers.

### Pourquoi cette configuration ?
- **Performance & Simplicité** : WhiteNoise est optimisé pour la production, gère la compression, le cache et le manifest des fichiers statiques, tout en évitant la complexité d'un stockage S3 pour les fichiers statiques.
- **Développement fluide** : En local, tout reste simple et rapide grâce au stockage local.
- **Économie & Sécurité** : S3 n'est utilisé que pour les médias en production, ce qui réduit les coûts et limite l'exposition des fichiers statiques.
- **Bonne pratique Django** : Cette approche suit les recommandations officielles pour Django sur Heroku.

### Schéma de gestion des fichiers

```
+---------------------+         +-------------------+
|  Utilisateur final  | <-----> |     Heroku        |
+---------------------+         +-------------------+
                                         |  |
                                         |  | (statique)
                                         v  v
                                 +-------------------+
                                 |   WhiteNoise      |
                                 +-------------------+
                                         |
                                         | (médias)
                                         v
                                 +-------------------+
                                 |      S3           |
                                 +-------------------+
```

- **Statique** : WhiteNoise sert les fichiers statiques directement depuis Heroku.
- **Médias** : Les fichiers uploadés sont stockés sur S3 en production.

### Exemple de configuration (settings.py)

```python
# Production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'saga.storage_backends.MediaStorage'  # S3 pour les médias
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
``` 