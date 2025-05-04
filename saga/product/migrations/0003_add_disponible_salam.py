from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_update_phone_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='disponible_salam',
            field=models.BooleanField(default=False, verbose_name='Disponible en Salam'),
        ),
    ] 