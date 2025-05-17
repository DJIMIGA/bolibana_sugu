import boto3
from django.conf import settings
import sys

print("\nVérification des fichiers statiques sur S3")
print("=========================================")
print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"Région: {settings.AWS_S3_REGION_NAME}")
print(f"Domaine personnalisé: {settings.AWS_S3_CUSTOM_DOMAIN}")
print("----------------------------------------")

try:
    # Initialiser le client S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # Vérifier si le bucket existe
    try:
        s3.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print("✓ Le bucket existe")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du bucket: {str(e)}")
        sys.exit(1)

    # Lister les objets dans le dossier static/
    try:
        response = s3.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='static/'
        )
        
        if 'Contents' in response:
            print("\nFichiers trouvés dans le dossier static/:")
            print("----------------------------------------")
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj['Key']}"
                print(f"- {obj['Key']} ({size_kb:.1f} KB)")
                print(f"  URL: {url}")
        else:
            print("\n❌ Le dossier static/ est vide ou n'existe pas")
            
            # Vérifier les permissions du bucket
            try:
                policy = s3.get_bucket_policy(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
                print("\nPolitique du bucket:")
                print(policy['Policy'])
            except Exception as e:
                print(f"\n❌ Erreur lors de la récupération de la politique: {str(e)}")
                
    except Exception as e:
        print(f"\n❌ Erreur lors de la liste des objets: {str(e)}")
        
except Exception as e:
    print(f"\n❌ Erreur lors de l'initialisation du client S3: {str(e)}")
    sys.exit(1) 