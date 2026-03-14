# Migration pour supprimer le champ api_token (le token vient maintenant de settings.B2B_API_KEY)
# Cette migration vérifie si le champ existe avant de le supprimer

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_fix_index_names'),
    ]

    operations = [
        # Supprimer le champ seulement s'il existe dans la base de données
        migrations.RunSQL(
            # PostgreSQL
            sql="ALTER TABLE inventory_inventoryconnection DROP COLUMN IF EXISTS api_token;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

