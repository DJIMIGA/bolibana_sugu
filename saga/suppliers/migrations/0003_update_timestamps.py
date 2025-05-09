from django.db import migrations
from django.utils import timezone

def update_timestamps(apps, schema_editor):
    Supplier = apps.get_model('suppliers', 'Supplier')
    now = timezone.now()
    # Mettre à jour tous les fournisseurs qui n'ont pas de created_at
    Supplier.objects.filter(created_at__isnull=True).update(created_at=now)

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0002_add_timestamp_fields'),
    ]

    operations = [
        migrations.RunPython(update_timestamps),
    ] 