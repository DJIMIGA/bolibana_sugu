from django.db import migrations, models

def fix_migrations(apps, schema_editor):
    Category = apps.get_model('product', 'Category')
    Product = apps.get_model('product', 'Product')
    Phone = apps.get_model('product', 'Phone')
    PhoneVariant = apps.get_model('product', 'PhoneVariant')
    
    # Supprimer toutes les données existantes
    PhoneVariant.objects.all().delete()
    Phone.objects.all().delete()
    Product.objects.all().delete()
    
    # Supprimer les doublons de catégories
    categories = Category.objects.all()
    seen_names = set()
    for category in categories:
        if category.name in seen_names:
            category.delete()
        else:
            seen_names.add(category.name)
    
    # S'assurer que la catégorie Téléphones existe
    phones_category = Category.objects.filter(name='Téléphones').first()
    if not phones_category:
        phones_category = Category.objects.create(name='Téléphones')
    
    # S'assurer que les sous-catégories existent
    subcategories = ['Samsung', 'Apple', 'Huawei']
    for name in subcategories:
        if not Category.objects.filter(name=name, parent=phones_category).exists():
            Category.objects.create(name=name, parent=phones_category)

def reverse_fix_migrations(apps, schema_editor):
    # Cette fonction est vide car nous ne voulons pas recréer les données supprimées
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        # D'abord, ajouter le champ storage
        migrations.AddField(
            model_name='phone',
            name='storage',
            field=models.PositiveIntegerField(verbose_name='Stockage (Go)', null=True, blank=True),
        ),
        # Ensuite, nettoyer la base de données
        migrations.RunPython(fix_migrations, reverse_fix_migrations),
    ] 