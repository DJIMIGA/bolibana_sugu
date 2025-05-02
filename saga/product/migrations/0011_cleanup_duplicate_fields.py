from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_category_options_alter_imageproduct_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='product',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_available',
        ),
    ] 