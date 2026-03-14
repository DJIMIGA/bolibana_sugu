# Generated manually on 2026-01-13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0030_add_rayon_type_and_level_to_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='products', to='product.category', verbose_name='Catégorie'),
        ),
    ]
