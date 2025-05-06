from django.db import migrations
from django.core.management import call_command
import os

def load_initial_data(apps, schema_editor):
    fixture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures', 'phones.json')
    if os.path.exists(fixture_path):
        call_command("loaddata", fixture_path)
    else:
        print(f"Le fichier de fixture n'existe pas à l'emplacement : {fixture_path}")

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0004_merge_0002_add_network_field_0003_add_camera_fields'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ] 