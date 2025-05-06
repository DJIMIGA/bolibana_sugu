import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from django.db import connection

def clean_migrations():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations WHERE app = 'product'")
        print("Migrations nettoyées avec succès.")

if __name__ == '__main__':
    clean_migrations() 