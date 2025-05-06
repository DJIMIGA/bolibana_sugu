from django.db import migrations
from django.core.management import call_command
import os

def load_initial_data(apps, schema_editor):
    # Récupérer les modèles
    Supplier = apps.get_model('suppliers', 'Supplier')
    Category = apps.get_model('product', 'Category')
    Product = apps.get_model('product', 'Product')
    
    print("\n" + "="*80)
    print("DÉBUT DU CHARGEMENT DES FIXTURES SUR HEROKU")
    print("="*80)
    
    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
    print(f"\nRépertoire des fixtures : {fixtures_dir}")
    
    # Vérifier et charger les suppliers
    print("\n" + "-"*80)
    print("VÉRIFICATION DES SUPPLIERS")
    print("-"*80)
    supplier_count = Supplier.objects.count()
    print(f"Nombre de suppliers dans la base : {supplier_count}")
    if supplier_count == 0:
        print("\n>>> Aucun supplier trouvé, chargement des suppliers...")
        fixture_path = os.path.join(fixtures_dir, 'suppliers.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print(f">>> Suppliers chargés avec succès. Nouveau nombre : {Supplier.objects.count()}")
        else:
            print("!!! ERREUR: Fichier suppliers.json non trouvé !!!")
    else:
        print("\n>>> Des suppliers existent déjà, pas de chargement nécessaire")
    
    # Vérifier et charger les catégories
    print("\n" + "-"*80)
    print("VÉRIFICATION DES CATÉGORIES")
    print("-"*80)
    category_count = Category.objects.count()
    print(f"Nombre de catégories dans la base : {category_count}")
    if category_count == 0:
        print("\n>>> Aucune catégorie trouvée, chargement des catégories...")
        fixture_path = os.path.join(fixtures_dir, 'categories.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print(f">>> Catégories chargées avec succès. Nouveau nombre : {Category.objects.count()}")
        else:
            print("!!! ERREUR: Fichier categories.json non trouvé !!!")
    else:
        print("\n>>> Des catégories existent déjà, pas de chargement nécessaire")
    
    # Vérifier et charger les produits
    print("\n" + "-"*80)
    print("VÉRIFICATION DES PRODUITS")
    print("-"*80)
    product_count = Product.objects.count()
    print(f"Nombre de produits dans la base : {product_count}")
    if product_count == 0:
        print("\n>>> Aucun produit trouvé, chargement des produits...")
        fixture_path = os.path.join(fixtures_dir, 'phones.json')
        if os.path.exists(fixture_path):
            call_command("loaddata", fixture_path)
            print(f">>> Produits chargés avec succès. Nouveau nombre : {Product.objects.count()}")
        else:
            print("!!! ERREUR: Fichier phones.json non trouvé !!!")
    else:
        print("\n>>> Des produits existent déjà, pas de chargement nécessaire")
    
    print("\n" + "="*80)
    print("FIN DU CHARGEMENT DES FIXTURES SUR HEROKU")
    print("="*80 + "\n")

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0004_merge_0002_add_network_field_0003_add_camera_fields'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ] 