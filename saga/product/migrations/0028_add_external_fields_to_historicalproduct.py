# Generated migration to add external fields to HistoricalProduct

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0027_add_external_fields_to_historicalcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID externe (app de gestion)'),
        ),
        migrations.AddField(
            model_name='historicalproduct',
            name='external_sku',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='SKU externe (app de gestion)'),
        ),
    ]

