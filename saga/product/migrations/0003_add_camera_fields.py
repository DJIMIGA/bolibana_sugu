from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='camera_main',
            field=models.CharField(default='Inconnue', max_length=100, verbose_name='Caméra principale'),
        ),
        migrations.AddField(
            model_name='phone',
            name='camera_front',
            field=models.CharField(default='Inconnue', max_length=100, verbose_name='Caméra frontale'),
        ),
    ] 