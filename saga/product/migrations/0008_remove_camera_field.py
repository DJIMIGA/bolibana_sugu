from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_add_remaining_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE product_phone DROP COLUMN IF EXISTS camera;',
            reverse_sql='ALTER TABLE product_phone ADD COLUMN camera varchar(100);'
        ),
    ] 