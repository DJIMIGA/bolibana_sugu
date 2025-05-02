from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_alter_phonevariant_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='created_at',
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
    ] 