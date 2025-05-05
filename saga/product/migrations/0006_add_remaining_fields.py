from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_add_warranty_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='box_included',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='phone',
            name='accessories',
            field=models.TextField(blank=True, null=True),
        ),
    ] 