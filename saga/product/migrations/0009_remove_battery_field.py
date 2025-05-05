from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_remove_camera_field'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE product_phone DROP COLUMN IF EXISTS battery;',
            reverse_sql='ALTER TABLE product_phone ADD COLUMN battery varchar(100);'
        ),
    ] 