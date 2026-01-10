# Generated migration for external fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_historicalproduct_historicalphone_historicalcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID externe (app de gestion)'),
        ),
        migrations.AddField(
            model_name='product',
            name='external_sku',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='SKU externe (app de gestion)'),
        ),
        migrations.AddField(
            model_name='category',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID externe (app de gestion)'),
        ),
        migrations.AddField(
            model_name='category',
            name='external_parent_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID parent externe (app de gestion)'),
        ),
    ]

