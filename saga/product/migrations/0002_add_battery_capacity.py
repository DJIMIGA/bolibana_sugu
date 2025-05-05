from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='battery_capacity',
            field=models.IntegerField(default=3000, help_text='Capacité de la batterie en mAh'),
        ),
    ] 