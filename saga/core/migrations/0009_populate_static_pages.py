"""
Data migration : migre le contenu des champs SiteConfiguration
vers des enregistrements StaticPage individuels.
"""
from django.db import migrations


# Mapping : slug → (title, champ titre dans SiteConfiguration, champ contenu)
PAGE_MAPPING = [
    ('cgv', 'Conditions Générales de Vente', None, None),
    ('terms-conditions', 'Mentions Légales', None, None),
    ('about', 'À propos', None, None),
    ('about-story', 'Notre histoire', 'about_story_title', 'about_story_content'),
    ('about-values', 'Nos valeurs', 'about_values_title', 'about_values_content'),
    ('service-loyalty', 'Fidélité Bolibana', 'service_loyalty_title', 'service_loyalty_content'),
    ('service-express', 'Livraison express', 'service_express_title', 'service_express_content'),
    ('help-center', "Centre d'aide", 'help_center_title', 'help_center_content'),
    ('help-returns', 'Retours faciles', 'help_returns_title', 'help_returns_content'),
    ('help-warranty', 'Garantie qualité', 'help_warranty_title', 'help_warranty_content'),
]


def forwards(apps, schema_editor):
    SiteConfiguration = apps.get_model('core', 'SiteConfiguration')
    StaticPage = apps.get_model('core', 'StaticPage')

    config = SiteConfiguration.objects.first()

    for slug, default_title, title_field, content_field in PAGE_MAPPING:
        title = default_title
        content = ''
        if config and title_field:
            title = getattr(config, title_field, '') or default_title
        if config and content_field:
            content = getattr(config, content_field, '') or ''

        StaticPage.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title,
                'content': content,
                'is_published': True,
            },
        )


def backwards(apps, schema_editor):
    StaticPage = apps.get_model('core', 'StaticPage')
    slugs = [slug for slug, *_ in PAGE_MAPPING]
    StaticPage.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_staticpage'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
