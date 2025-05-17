import boto3
from django.conf import settings
import os

# Configuration S3
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# Vérifier les permissions du bucket
try:
    # Tenter de lister les objets
    response = s3.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        MaxKeys=1
    )
    print("✓ Permission de lecture OK")
    
    # Tenter d'uploader un fichier test
    test_content = b"Test content"
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key='test.txt',
        Body=test_content
    )
    print("✓ Permission d'écriture OK")
    
    # Nettoyer le fichier test
    s3.delete_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key='test.txt'
    )
    print("✓ Permission de suppression OK")
    
except Exception as e:
    print(f"✗ Erreur : {str(e)}") 