from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_add_network_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='warranty',
            field=models.CharField(default='12 mois', max_length=100),
        ),
    ] 