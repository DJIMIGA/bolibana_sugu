from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_remove_battery_capacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='battery_capacity',
            field=models.IntegerField(default=3000, help_text='Capacité de la batterie en mAh'),
        ),
    ] 