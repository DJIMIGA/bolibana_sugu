from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

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