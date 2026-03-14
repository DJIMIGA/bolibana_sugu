import os
import django
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

def clean_migrations():
    # Supprimer toutes les migrations enregistrées
    MigrationRecorder.Migration.objects.all().delete()
    
    # Supprimer toutes les tables
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS 
            product_product,
            product_category,
            product_color,
            product_size,
            product_clothing,
            product_culturalitem,
            product_imageproduct,
            product_phone,
            product_phonevariant,
            product_phonevariantimage,
            product_review,
            product_shippingmethod
            CASCADE;
        """)

if __name__ == '__main__':
    clean_migrations()
    print("Migrations et tables nettoyées avec succès.") 