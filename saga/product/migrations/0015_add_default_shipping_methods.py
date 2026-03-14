from django.db import migrations

def add_default_shipping_methods(apps, schema_editor):
    ShippingMethod = apps.get_model('product', 'ShippingMethod')
    
    # Méthodes de livraison par défaut
    default_methods = [
        {
            'name': 'Livraison Standard',
            'price': 5000,
            'min_delivery_days': 3,
            'max_delivery_days': 5,
        },
        {
            'name': 'Livraison Express',
            'price': 10000,
            'min_delivery_days': 1,
            'max_delivery_days': 2,
        },
        {
            'name': 'Livraison Gratuite',
            'price': 0,
            'min_delivery_days': 5,
            'max_delivery_days': 7,
        }
    ]
    
    for method in default_methods:
        ShippingMethod.objects.get_or_create(
            name=method['name'],
            defaults={
                'price': method['price'],
                'min_delivery_days': method['min_delivery_days'],
                'max_delivery_days': method['max_delivery_days']
            }
        )

def remove_default_shipping_methods(apps, schema_editor):
    ShippingMethod = apps.get_model('product', 'ShippingMethod')
    ShippingMethod.objects.filter(
        name__in=['Livraison Standard', 'Livraison Express', 'Livraison Gratuite']
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0014_product_shipping_methods'),
    ]

    operations = [
        migrations.RunPython(add_default_shipping_methods, remove_default_shipping_methods),
    ] 