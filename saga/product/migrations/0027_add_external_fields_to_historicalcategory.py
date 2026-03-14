# Generated migration to add external fields to HistoricalCategory

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_product_external_fields_category_external_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalcategory',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID externe (app de gestion)'),
        ),
        migrations.AddField(
            model_name='historicalcategory',
            name='external_parent_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID parent externe (app de gestion)'),
        ),
    ]

