from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_merge_20250502_1025'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE product_product DROP COLUMN IF EXISTS created_at CASCADE;",
            "SELECT 1;"  # No reverse operation needed
        ),
        migrations.RunSQL(
            "ALTER TABLE product_product DROP COLUMN IF EXISTS updated_at CASCADE;",
            "SELECT 1;"  # No reverse operation needed
        ),
        migrations.RunSQL(
            "ALTER TABLE product_product DROP COLUMN IF EXISTS is_active CASCADE;",
            "SELECT 1;"  # No reverse operation needed
        ),
        migrations.RunSQL(
            "ALTER TABLE product_product DROP COLUMN IF EXISTS is_available CASCADE;",
            "SELECT 1;"  # No reverse operation needed
        ),
    ] 