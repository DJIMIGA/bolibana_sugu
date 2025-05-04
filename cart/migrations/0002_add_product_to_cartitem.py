from django.db import migrations, models
import django.db.models.deletion

def set_default_product(apps, schema_editor):
    CartItem = apps.get_model('cart', 'CartItem')
    Product = apps.get_model('product', 'Product')
    # Récupérer le premier produit existant ou en créer un si nécessaire
    default_product = Product.objects.first()
    if not default_product:
        default_product = Product.objects.create(
            title="Produit par défaut",
            price=0,
            description="Produit par défaut pour les anciens éléments du panier"
        )
    # Mettre à jour tous les CartItem existants
    CartItem.objects.filter(product__isnull=True).update(product=default_product)

class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='product.product',
                null=True
            ),
        ),
        migrations.RunPython(set_default_product),
        migrations.AlterField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='product.product'
            ),
        ),
    ] 