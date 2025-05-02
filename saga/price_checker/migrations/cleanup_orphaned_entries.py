from django.db import migrations

def cleanup_orphaned_entries(apps, schema_editor):
    if schema_editor.connection.vendor == 'sqlite':
        # Pour SQLite
        schema_editor.execute("""
            DELETE FROM price_checker_priceentry
            WHERE product_id NOT IN (SELECT id FROM product_product)
        """)
    else:
        # Pour les autres bases de données (PostgreSQL, MySQL, etc.)
        schema_editor.execute("""
            DELETE FROM price_checker_priceentry pe
            WHERE NOT EXISTS (
                SELECT 1 FROM product_product pp
                WHERE pe.product_id = pp.id
            )
        """)

class Migration(migrations.Migration):
    dependencies = [
        ('price_checker', '0001_initial'),  # Assurez-vous que c'est la dernière migration
        ('product', '0001_initial'),  # Assurez-vous que c'est la dernière migration
    ]

    operations = [
        migrations.RunPython(cleanup_orphaned_entries),
    ] 