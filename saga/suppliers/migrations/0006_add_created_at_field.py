from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0005_merge_20250509_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(null=True, blank=True, default=timezone.now),
        ),
    ] 