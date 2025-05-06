from django.db import migrations
from django.core.management import call_command
import os

def load_initial_data(apps, schema_editor):
    # Récupérer les modèles
    Supplier = apps.get_model('suppliers', 'Supplier')
    Category = apps.get_model('product', 'Category')
    Product = apps.get_model('product', 'Product')
    
    print("\n=== Début de la vérification de la base de données Heroku ===")
    
    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
    
    # Vérifier et charger les suppliers
    supplier_count = Supplier.objects.count()
    print(f"\nNombre de suppliers dans la base : {supplier_count}")
    if supplier_count == 0:
        print("Aucun supplier trouvé, chargement des suppliers...")
        fixture_path = os.path.join(fixtures_dir, 'suppliers.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print(f"Suppliers chargés avec succès. Nouveau nombre : {Supplier.objects.count()}")
        else:
            print("ERREUR: Fichier suppliers.json non trouvé")
    else:
        print("Des suppliers existent déjà, pas de chargement nécessaire")
    
    # Vérifier et charger les catégories
    category_count = Category.objects.count()
    print(f"\nNombre de catégories dans la base : {category_count}")
    if category_count == 0:
        print("Aucune catégorie trouvée, chargement des catégories...")
        fixture_path = os.path.join(fixtures_dir, 'categories.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print(f"Catégories chargées avec succès. Nouveau nombre : {Category.objects.count()}")
        else:
            print("ERREUR: Fichier categories.json non trouvé")
    else:
        print("Des catégories existent déjà, pas de chargement nécessaire")
    
    # Vérifier et charger les produits
    product_count = Product.objects.count()
    print(f"\nNombre de produits dans la base : {product_count}")
    if product_count == 0:
        print("Aucun produit trouvé, chargement des produits...")
        fixture_path = os.path.join(fixtures_dir, 'phones.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print(f"Produits chargés avec succès. Nouveau nombre : {Product.objects.count()}")
        else:
            print("ERREUR: Fichier phones.json non trouvé")
    else:
        print("Des produits existent déjà, pas de chargement nécessaire")
    
    print("\n=== Fin de la vérification de la base de données Heroku ===\n")

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0004_merge_0002_add_network_field_0003_add_camera_fields'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ] 