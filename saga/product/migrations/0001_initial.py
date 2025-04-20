from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('suppliers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='product.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('price', models.DecimalField(decimal_places=0, max_digits=10, verbose_name='Prix')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('highlight', models.TextField(blank=True, null=True, verbose_name='Points forts')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.category', verbose_name='Catégorie')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='suppliers.supplier', verbose_name='Fournisseur')),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=100, verbose_name='Modèle')),
                ('operating_system', models.CharField(max_length=50, verbose_name='Système d\'exploitation')),
                ('screen_size', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Taille d\'écran (pouces)')),
                ('resolution', models.CharField(max_length=50, verbose_name='Résolution')),
                ('processor', models.CharField(max_length=100, verbose_name='Processeur')),
                ('ram', models.PositiveIntegerField(verbose_name='RAM (Go)')),
                ('battery_capacity', models.PositiveIntegerField(verbose_name='Capacité batterie (mAh)')),
                ('camera_main', models.CharField(max_length=100, verbose_name='Appareil photo principal')),
                ('camera_front', models.CharField(max_length=100, verbose_name='Appareil photo frontal')),
                ('network', models.CharField(max_length=100, verbose_name='Réseaux supportés')),
                ('warranty', models.CharField(max_length=100, verbose_name='Garantie')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='phone', to='product.product', verbose_name='Produit associé')),
            ],
            options={
                'verbose_name': 'Téléphone',
                'verbose_name_plural': 'Téléphones',
                'ordering': ['model'],
            },
        ),
        migrations.CreateModel(
            name='PhoneVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage', models.PositiveIntegerField(verbose_name='Stockage (Go)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Prix')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='Stock disponible')),
                ('sku', models.CharField(max_length=50, unique=True, verbose_name='SKU')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.color', verbose_name='Couleur')),
                ('phone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='product.phone', verbose_name='Téléphone')),
            ],
            options={
                'verbose_name': 'Variante de téléphone',
                'verbose_name_plural': 'Variantes de téléphone',
                'unique_together': {('phone', 'color', 'storage')},
            },
        ),
        migrations.CreateModel(
            name='PhoneVariantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='phone_variants/images/')),
                ('is_primary', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.phonevariant')),
            ],
            options={
                'ordering': ['order', 'created_at'],
                'verbose_name': 'Image de variante',
                'verbose_name_plural': 'Images de variantes',
            },
        ),
    ] 