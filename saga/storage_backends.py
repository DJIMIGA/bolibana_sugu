from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    default_acl = None
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    querystring_auth = True
    object_parameters = settings.AWS_S3_OBJECT_PARAMETERS
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    auto_create_bucket = True
    auto_create_acl = True

class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True
    default_acl = 'public-read'
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    querystring_auth = False
    object_parameters = settings.AWS_S3_OBJECT_PARAMETERS
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    auto_create_bucket = True
    auto_create_acl = True

class ProductImageStorage(S3Boto3Storage):
    """Stockage spécifique pour les images de produits"""
    location = 'media/products'  # Base location pour tous les médias produits
    file_overwrite = False
    default_acl = None
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    querystring_auth = True
    object_parameters = settings.AWS_S3_OBJECT_PARAMETERS
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    auto_create_bucket = True
    auto_create_acl = True

    def get_available_name(self, name, max_length=None):
        """Surcharge pour gérer les noms de fichiers uniques"""
        if self.exists(name):
            name_parts = name.rsplit('.', 1)
            base_name = name_parts[0]
            extension = name_parts[1] if len(name_parts) > 1 else ''
            counter = 1
            while self.exists(f"{base_name}_{counter}.{extension}"):
                counter += 1
            return f"{base_name}_{counter}.{extension}"
        return name

class HeroImageStorage(S3Boto3Storage):
    """Stockage spécifique pour les images du hero"""
    location = 'media/hero'  # Dossier spécifique pour les images du hero
    file_overwrite = True  # On autorise l'écrasement pour le hero
    default_acl = None  # On utilise les paramètres de bucket par défaut
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    querystring_auth = False  # Pas besoin d'authentification pour le hero
    object_parameters = {
        'CacheControl': 'max-age=86400',  # Cache d'un jour
    }
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    auto_create_bucket = True
    auto_create_acl = False  # On désactive la création automatique des ACLs 