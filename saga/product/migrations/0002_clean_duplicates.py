from django.db import migrations

def clean_duplicates(apps, schema_editor):
    Category = apps.get_model('product', 'Category')
    
    # Nettoyer les catégories "Téléphones"
    phone_categories = Category.objects.filter(name='Téléphones').order_by('-id')
    if phone_categories.count() > 1:
        # Garder la plus récente et supprimer les autres
        latest_phone = phone_categories.first()
        phone_categories.exclude(id=latest_phone.id).delete()
    
    # Nettoyer les catégories "Samsung"
    samsung_categories = Category.objects.filter(name='Samsung').order_by('-id')
    if samsung_categories.count() > 1:
        # Garder la plus récente et supprimer les autres
        latest_samsung = samsung_categories.first()
        samsung_categories.exclude(id=latest_samsung.id).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clean_duplicates),
    ] 