from django.db import migrations, models

def fix_migrations(apps, schema_editor):
    PhoneVariant = apps.get_model('product', 'PhoneVariant')
    Phone = apps.get_model('product', 'Phone')
    Product = apps.get_model('product', 'Product')
    Category = apps.get_model('product', 'Category')

    # Supprimer toutes les données existantes
    PhoneVariant.objects.all().delete()
    Phone.objects.all().delete()
    Product.objects.all().delete()

    # Supprimer les catégories en double
    categories = Category.objects.all()
    seen_names = set()
    for category in categories:
        if category.name in seen_names:
            category.delete()
        else:
            seen_names.add(category.name)

    # S'assurer que la catégorie Téléphones existe
    phone_category, _ = Category.objects.get_or_create(
        name='Téléphones',
        defaults={'description': 'Catégorie pour les téléphones'}
    )

    # Créer les sous-catégories si elles n'existent pas
    subcategories = ['Samsung', 'Apple', 'Huawei']
    for subcategory_name in subcategories:
        Category.objects.get_or_create(
            name=subcategory_name,
            parent=phone_category,
            defaults={'description': f'Catégorie pour les téléphones {subcategory_name}'}
        )

def reverse_fix_migrations(apps, schema_editor):
    # Cette fonction est vide car nous ne voulons pas recréer les données supprimées
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_migrations, reverse_fix_migrations),
    ] 