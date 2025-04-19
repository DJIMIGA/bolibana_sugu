from django.db import migrations
from product.models import Category

def clean_duplicate_categories(apps, schema_editor):
    # Récupérer toutes les catégories "Téléphones"
    phone_categories = Category.objects.filter(name='Téléphones')
    
    if phone_categories.exists():
        # Prendre la première catégorie "Téléphones"
        phone_category = phone_categories.first()
        
        # Supprimer toutes les catégories Samsung existantes
        Category.objects.filter(name='Samsung', parent=phone_category).delete()
        
        # Créer une nouvelle catégorie Samsung
        Category.objects.create(
            name='Samsung',
            parent=phone_category,
            slug='samsung'
        )
    else:
        # Si la catégorie "Téléphones" n'existe pas, la créer
        phone_category = Category.objects.create(
            name='Téléphones',
            slug='telephones'
        )
        
        # Créer la catégorie Samsung
        Category.objects.create(
            name='Samsung',
            parent=phone_category,
            slug='samsung'
        )

def reverse_clean_duplicate_categories(apps, schema_editor):
    # Cette fonction est vide car nous ne pouvons pas restaurer les catégories supprimées
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clean_duplicate_categories, reverse_clean_duplicate_categories),
    ] 