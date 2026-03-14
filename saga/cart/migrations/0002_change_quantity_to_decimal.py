# Generated migration to change quantity fields from PositiveIntegerField to DecimalField

from django.db import migrations, models
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.DecimalField(
                decimal_places=3,
                default=Decimal('1'),
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal('0.001'))]
            ),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.DecimalField(
                decimal_places=3,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal('0.001'))]
            ),
        ),
    ]
