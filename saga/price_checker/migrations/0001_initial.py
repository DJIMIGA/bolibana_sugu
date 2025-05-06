from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom de la ville')),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Ville',
                'verbose_name_plural': 'Villes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PriceSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('status', models.CharField(choices=[('PENDING', 'En attente'), ('APPROVED', 'Validé'), ('REJECTED', 'Rejeté')], default='PENDING', max_length=20)),
                ('validation_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('validated_at', models.DateTimeField(blank=True, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_submissions', to='price_checker.city')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_submissions', to='product.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_submissions', to=settings.AUTH_USER_MODEL)),
                ('validated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='validated_prices', to=settings.AUTH_USER_MODEL)),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='price_submissions', to='product.phone')),
            ],
            options={
                'verbose_name': 'Soumission de prix',
                'verbose_name_plural': 'Soumissions de prix',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PriceEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='XOF', max_length=3)),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_entries', to='price_checker.city')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_entries', to='product.product')),
                ('submission', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='price_entry', to='price_checker.pricesubmission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_entries', to=settings.AUTH_USER_MODEL)),
                ('validated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='validated_price_entries', to=settings.AUTH_USER_MODEL)),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='price_entries', to='product.phone')),
            ],
            options={
                'verbose_name': 'Entrée de prix',
                'verbose_name_plural': 'Entrées de prix',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PriceDeactivation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_deactivations', to=settings.AUTH_USER_MODEL)),
                ('price_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deactivations', to='price_checker.priceentry')),
            ],
            options={
                'verbose_name': 'Désactivation de prix',
                'verbose_name_plural': 'Désactivations de prix',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('DRAFT', 'Brouillon'), ('APPROVED', 'Approuvé'), ('PUBLISHED', 'Publié')], default='DRAFT', max_length=20, verbose_name='Statut')),
                ('visibility', models.CharField(choices=[('PRIVATE', 'Privé'), ('PUBLIC', 'Public')], default='PRIVATE', max_length=20, verbose_name='Visibilité')),
                ('target_price', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, verbose_name='Prix cible')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='product.product')),
            ],
            options={
                'verbose_name': 'Statut du produit',
                'verbose_name_plural': 'Statuts des produits',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PriceValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'En attente'), ('APPROVED', 'Approuvé'), ('REJECTED', 'Rejeté')], default='PENDING', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_validations', to=settings.AUTH_USER_MODEL)),
                ('price_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='validations', to='price_checker.priceentry')),
            ],
            options={
                'verbose_name': 'Validation de prix',
                'verbose_name_plural': 'Validations de prix',
                'ordering': ['-created_at'],
            },
        ),
    ] 