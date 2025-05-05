from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE product_phone DROP COLUMN IF EXISTS battery_capacity;',
            reverse_sql='ALTER TABLE product_phone ADD COLUMN battery_capacity integer DEFAULT 3000;'
        ),
    ] 