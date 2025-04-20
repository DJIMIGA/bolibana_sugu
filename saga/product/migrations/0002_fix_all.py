from django.db import migrations

def fix_migrations(apps, schema_editor):
    # Supprimer toutes les données existantes
    PhoneVariant = apps.get_model('product', 'PhoneVariant')
    Phone = apps.get_model('product', 'Phone')
    Product = apps.get_model('product', 'Product')
    Category = apps.get_model('product', 'Category')

    # Supprimer les données dans l'ordre inverse des dépendances
    PhoneVariant.objects.all().delete()
    Phone.objects.all().delete()
    Product.objects.all().delete()

    # Supprimer les catégories en double
    seen_names = set()
    for category in Category.objects.all():
        if category.name in seen_names:
            category.delete()
        else:
            seen_names.add(category.name)

    # S'assurer que la catégorie Téléphones existe
    phone_category, _ = Category.objects.get_or_create(
        name='Téléphones',
        defaults={'name': 'Téléphones'}
    )

    # Créer les sous-catégories si elles n'existent pas
    subcategories = ['Samsung', 'Apple', 'Huawei']
    for subcategory_name in subcategories:
        Category.objects.get_or_create(
            name=subcategory_name,
            parent=phone_category,
            defaults={'name': subcategory_name, 'parent': phone_category}
        )

def reverse_fix_migrations(apps, schema_editor):
    # Ne rien faire en reverse car on ne veut pas recréer les données supprimées
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_migrations, reverse_fix_migrations),
    ] 