from django.core.management.base import BaseCommand
from product.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Génère les slugs manquants pour les catégories'

    def handle(self, *args, **kwargs):
        categories = Category.objects.filter(slug__isnull=True)
        self.stdout.write(f"Trouvé {categories.count()} catégories sans slug")
        
        for category in categories:
            old_name = category.name
            category.slug = slugify(category.name)
            category.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Slug généré pour '{old_name}': {category.slug}"
                )
            ) 