# Generated migration for ApiKey model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_make_api_base_url_optional'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_encrypted', models.TextField(verbose_name='Clé API (chiffrée)')),
                ('name', models.CharField(default='Clé API', help_text='Ex: "Clé principale - Site Bamako"', max_length=255, verbose_name='Nom de la clé')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créée le')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='Dernière utilisation')),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to='inventory.inventoryconnection', verbose_name='Connexion')),
            ],
            options={
                'verbose_name': 'Clé API',
                'verbose_name_plural': 'Clés API',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='apikey',
            index=models.Index(fields=['connection', 'is_active'], name='inventory_a_connect_idx'),
        ),
    ]

