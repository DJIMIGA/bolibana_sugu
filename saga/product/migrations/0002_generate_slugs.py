from django.db import migrations
from django.utils.text import slugify

def generate_slugs(apps, schema_editor):
    Category = apps.get_model('product', 'Category')
    for category in Category.objects.all():
        if not category.slug:
            base_slug = slugify(category.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=category.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            category.slug = slug
            category.save()

def reverse_slugs(apps, schema_editor):
    Category = apps.get_model('product', 'Category')
    Category.objects.all().update(slug=None)

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_slugs, reverse_slugs),
    ] 