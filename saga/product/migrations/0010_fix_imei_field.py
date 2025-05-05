from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_remove_battery_field'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE product_phone ALTER COLUMN imei DROP NOT NULL;',
            reverse_sql='ALTER TABLE product_phone ALTER COLUMN imei SET NOT NULL;'
        ),
    ] 