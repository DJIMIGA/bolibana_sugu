# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('price_checker', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pricesubmission',
            name='variant',
        ),
        migrations.RemoveField(
            model_name='priceentry',
            name='variant',
        ),
    ] 