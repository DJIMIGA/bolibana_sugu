from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import boto3

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    default_acl = 'private'
    querystring_auth = True
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True
    default_acl = 'public-read'
    querystring_auth = False
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    auto_create_bucket = True
    auto_create_acl = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Créer le dossier static dans S3 s'il n'existe pas
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        try:
            s3.put_object(
                Bucket=self.bucket_name,
                Key=f'{self.location}/',
                Body=''
            )
        except Exception as e:
            print(f"Erreur lors de la création du dossier static: {e}")

class ProductImageStorage(S3Boto3Storage):
    location = 'products'
    file_overwrite = False
    default_acl = 'public-read'
    querystring_auth = False
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

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