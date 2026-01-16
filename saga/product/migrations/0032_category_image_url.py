from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0031_allow_null_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image_url',
            field=models.URLField(blank=True, help_text='URL externe de l\'image (B2B)', max_length=500, null=True),
        ),
    ]
