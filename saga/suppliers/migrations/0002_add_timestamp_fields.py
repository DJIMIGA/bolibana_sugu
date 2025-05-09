from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ] 