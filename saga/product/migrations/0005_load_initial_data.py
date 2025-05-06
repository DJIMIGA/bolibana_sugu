from django.db import migrations
from django.core.management import call_command
import os

def load_initial_data(apps, schema_editor):
    # Récupérer les modèles
    Supplier = apps.get_model('suppliers', 'Supplier')
    Category = apps.get_model('product', 'Category')
    Product = apps.get_model('product', 'Product')
    
    print("Vérification de la base de données...")
    
    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
    
    # Vérifier et charger les suppliers
    if not Supplier.objects.exists():
        print("Aucun supplier trouvé, chargement des suppliers...")
        fixture_path = os.path.join(fixtures_dir, 'suppliers.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print("Suppliers chargés avec succès")
    else:
        print("Des suppliers existent déjà, pas de chargement nécessaire")
    
    # Vérifier et charger les catégories
    if not Category.objects.exists():
        print("Aucune catégorie trouvée, chargement des catégories...")
        fixture_path = os.path.join(fixtures_dir, 'categories.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print("Catégories chargées avec succès")
    else:
        print("Des catégories existent déjà, pas de chargement nécessaire")
    
    # Vérifier et charger les produits
    if not Product.objects.exists():
        print("Aucun produit trouvé, chargement des produits...")
        fixture_path = os.path.join(fixtures_dir, 'phones.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print("Produits chargés avec succès")
    else:
        print("Des produits existent déjà, pas de chargement nécessaire")

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0004_merge_0002_add_network_field_0003_add_camera_fields'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ] 