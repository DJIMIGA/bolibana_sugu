from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_add_camera_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='network',
            field=models.CharField(default='4G', max_length=100),
        ),
    ] 