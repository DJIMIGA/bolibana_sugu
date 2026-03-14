# Migration pour corriger les noms d'index en conflit

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        # Supprimer TOUS les index existants (anciens et nouveaux) pour éviter les conflits
        migrations.RunSQL(
            """
            DROP INDEX IF EXISTS inventory_e_externa_idx;
            DROP INDEX IF EXISTS inventory_s_externa_idx;
            DROP INDEX IF EXISTS inventory_e_sync_st_idx;
            DROP INDEX IF EXISTS inventory_s_sync_st_idx;
            DROP INDEX IF EXISTS inventory_s_order_i_idx;
            DROP INDEX IF EXISTS inventory_stocksite_external_idx;
            DROP INDEX IF EXISTS inventory_externalproduct_external_idx;
            DROP INDEX IF EXISTS inventory_externalproduct_sync_status_idx;
            DROP INDEX IF EXISTS inventory_externalcategory_external_idx;
            DROP INDEX IF EXISTS inventory_salesync_sync_status_idx;
            DROP INDEX IF EXISTS inventory_salesync_order_connection_idx;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Recréer les index avec des noms uniques
        migrations.AddIndex(
            model_name='stocksite',
            index=models.Index(fields=['external_site_id', 'connection'], name='inventory_stocksite_external_idx'),
        ),
        migrations.AddIndex(
            model_name='externalproduct',
            index=models.Index(fields=['external_id', 'connection'], name='inventory_externalproduct_external_idx'),
        ),
        migrations.AddIndex(
            model_name='externalproduct',
            index=models.Index(fields=['sync_status'], name='inventory_externalproduct_sync_status_idx'),
        ),
        migrations.AddIndex(
            model_name='externalcategory',
            index=models.Index(fields=['external_id', 'connection'], name='inventory_externalcategory_external_idx'),
        ),
        migrations.AddIndex(
            model_name='salesync',
            index=models.Index(fields=['sync_status'], name='inventory_salesync_sync_status_idx'),
        ),
        migrations.AddIndex(
            model_name='salesync',
            index=models.Index(fields=['order', 'connection'], name='inventory_salesync_order_connection_idx'),
        ),
    ]

