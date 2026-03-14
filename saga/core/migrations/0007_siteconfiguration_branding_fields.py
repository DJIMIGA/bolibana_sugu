from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_facebook_access_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='logo_small_url',
            field=models.URLField(blank=True, help_text='URL du logo petit format (mobile)'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='brand_primary_color',
            field=models.CharField(default='#008000', help_text='Couleur primaire (ex: #008000 vert)', max_length=7),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='brand_secondary_color',
            field=models.CharField(default='#FFD700', help_text='Couleur secondaire (ex: #FFD700 or)', max_length=7),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='brand_accent_color',
            field=models.CharField(default='#EF4444', help_text="Couleur d'accent (ex: #EF4444 rouge)", max_length=7),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='brand_tagline',
            field=models.CharField(default='Votre intermédiaire expert du marché', help_text='Slogan de la marque', max_length=200),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='brand_short_tagline',
            field=models.CharField(default='SuGu', help_text='Sous-titre court de la marque', max_length=100),
        ),
    ]
