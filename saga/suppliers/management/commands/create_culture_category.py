from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from product.models import Category, CulturalItem

class Command(BaseCommand):
    help = 'Crée la catégorie articles culturels et ses sous-catégories'

    def handle(self, *args, **kwargs):
        # Créer la catégorie principale "Articles Culturels"
        culture_category, created = Category.objects.get_or_create(
            slug='articles-culturels',
            defaults={
                'name': 'Articles Culturels',
                'is_main': True,
                'category_type': 'MODEL',
                'color': 'purple',
                'order': 3,
                'description': 'Découvrez notre sélection de livres et articles culturels.',
                'content_type': ContentType.objects.get_for_model(CulturalItem)
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Catégorie "Articles Culturels" créée avec succès'))
        else:
            self.stdout.write(self.style.SUCCESS('Catégorie "Articles Culturels" existe déjà'))

        # Créer les sous-catégories
        subcategories = [
            {
                'name': 'Livres',
                'slug': 'livres',
                'description': 'Une sélection de livres variés',
                'order': 1
            },
            {
                'name': 'Musique',
                'slug': 'musique',
                'description': 'CDs et vinyles',
                'order': 2
            },
            {
                'name': 'Art',
                'slug': 'art',
                'description': 'Œuvres d\'art et reproductions',
                'order': 3
            }
        ]

        for subcat in subcategories:
            subcategory, created = Category.objects.get_or_create(
                slug=subcat['slug'],
                defaults={
                    'name': subcat['name'],
                    'parent': culture_category,
                    'description': subcat['description'],
                    'order': subcat['order'],
                    'category_type': 'MODEL',
                    'content_type': ContentType.objects.get_for_model(CulturalItem)
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Sous-catégorie "{subcat["name"]}" créée avec succès'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Sous-catégorie "{subcat["name"]}" existe déjà')) 