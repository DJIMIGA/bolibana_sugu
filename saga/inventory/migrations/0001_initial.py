# Generated migration for inventory app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart', '0001_initial'),
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    
    # Note: Les index seront créés dans la migration 0002_fix_index_names

    operations = [
        migrations.CreateModel(
            name='InventoryConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_base_url', models.URLField(verbose_name='URL de base de l\'API')),
                # Note: api_token supprimé - le token vient de settings.B2B_API_KEY
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('last_sync_at', models.DateTimeField(blank=True, null=True, verbose_name='Dernière synchronisation')),
                ('sync_frequency', models.IntegerField(default=60, verbose_name='Fréquence de synchronisation (minutes)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_connections', to=settings.AUTH_USER_MODEL, verbose_name='Commerçant')),
            ],
            options={
                'verbose_name': 'Connexion à l\'app de gestion',
                'verbose_name_plural': 'Connexions à l\'app de gestion',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StockSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_site_id', models.IntegerField(verbose_name='ID site externe')),
                ('name', models.CharField(max_length=255, verbose_name='Nom du site')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Adresse')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_sites', to='inventory.inventoryconnection', verbose_name='Connexion')),
            ],
            options={
                'verbose_name': 'Site de stock',
                'verbose_name_plural': 'Sites de stock',
                'unique_together': {('connection', 'external_site_id')},
            },
        ),
        migrations.CreateModel(
            name='ExternalCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(verbose_name='ID externe')),
                ('external_parent_id', models.IntegerField(blank=True, null=True, verbose_name='ID parent externe')),
                ('last_synced_at', models.DateTimeField(blank=True, null=True, verbose_name='Dernière synchronisation')),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='external_category', to='product.category', verbose_name='Catégorie')),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_categories', to='inventory.inventoryconnection', verbose_name='Connexion')),
            ],
            options={
                'verbose_name': 'Catégorie externe',
                'verbose_name_plural': 'Catégories externes',
                'unique_together': {('connection', 'external_id')},
            },
        ),
        migrations.CreateModel(
            name='ExternalProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(verbose_name='ID externe')),
                ('external_sku', models.CharField(max_length=100, verbose_name='SKU externe')),
                ('external_category_id', models.IntegerField(blank=True, null=True, verbose_name='ID catégorie externe')),
                ('last_synced_at', models.DateTimeField(blank=True, null=True, verbose_name='Dernière synchronisation')),
                ('sync_status', models.CharField(choices=[('synced', 'Synchronisé'), ('pending', 'En attente'), ('error', 'Erreur')], default='pending', max_length=20, verbose_name='Statut de synchronisation')),
                ('sync_error', models.TextField(blank=True, null=True, verbose_name='Erreur de synchronisation')),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_products', to='inventory.inventoryconnection', verbose_name='Connexion')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='external_product', to='product.product', verbose_name='Produit')),
            ],
            options={
                'verbose_name': 'Produit externe',
                'verbose_name_plural': 'Produits externes',
                'unique_together': {('connection', 'external_id')},
            },
        ),
        migrations.CreateModel(
            name='SaleSync',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_sale_id', models.IntegerField(blank=True, null=True, verbose_name='ID vente externe')),
                ('sync_status', models.CharField(choices=[('pending', 'En attente'), ('synced', 'Synchronisé'), ('error', 'Erreur')], default='pending', max_length=20, verbose_name='Statut de synchronisation')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Message d\'erreur')),
                ('synced_at', models.DateTimeField(blank=True, null=True, verbose_name='Date de synchronisation')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_syncs', to='inventory.inventoryconnection', verbose_name='Connexion')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_syncs', to='cart.order', verbose_name='Commande')),
            ],
            options={
                'verbose_name': 'Synchronisation de vente',
                'verbose_name_plural': 'Synchronisations de ventes',
                'unique_together': {('order', 'connection')},
            },
        ),
        # Les index seront créés dans la migration 0002_fix_index_names
    ]

