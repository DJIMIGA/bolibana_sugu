from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0002_fix_all'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='storage',
            field=models.PositiveIntegerField(verbose_name='Stockage (Go)', null=True, blank=True),
        ),
    ] 