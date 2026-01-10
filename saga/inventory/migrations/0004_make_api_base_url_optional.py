# Migration pour rendre api_base_url optionnel (peut utiliser B2B_API_URL par défaut)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_remove_api_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryconnection',
            name='api_base_url',
            field=models.URLField(
                blank=True,
                help_text='Si vide, utilise B2B_API_URL depuis settings.py',
                null=True,
                verbose_name='URL de base de l\'API'
            ),
        ),
    ]

