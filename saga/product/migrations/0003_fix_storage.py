from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0002_fix_migrations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='storage',
            field=models.PositiveIntegerField(verbose_name='Stockage (Go)', null=True, blank=True),
        ),
    ] 