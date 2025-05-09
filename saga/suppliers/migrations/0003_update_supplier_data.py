from django.db import migrations
from django.utils import timezone

def update_supplier_data(apps, schema_editor):
    Supplier = apps.get_model('suppliers', 'Supplier')
    now = timezone.now()
    
    # Mettre à jour les timestamps
    Supplier.objects.filter(created_at__isnull=True).update(created_at=now)
    
    # Mettre à jour les champs obligatoires qui sont null
    Supplier.objects.filter(company_name__isnull=True).update(company_name='')
    Supplier.objects.filter(description__isnull=True).update(description='')
    Supplier.objects.filter(specialty__isnull=True).update(specialty='Fournisseur de TELEPHONE')

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0002_update_supplier_model'),
    ]

    operations = [
        migrations.RunPython(update_supplier_data),
    ] 