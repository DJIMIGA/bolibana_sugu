from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_add_is_b2b_to_externalproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalproduct',
            name='api_key_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID clé API'),
        ),
        migrations.AddField(
            model_name='externalproduct',
            name='api_key_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nom clé API'),
        ),
    ]
