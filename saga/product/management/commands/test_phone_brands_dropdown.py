from django.core.management.base import BaseCommand
from product.models import Phone, Category
from django.db.models import Count

class Command(BaseCommand):
    help = 'Teste la récupération des marques et modèles de téléphones pour le dropdown'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Test du dropdown des marques de téléphones...'))
        
        # Récupérer les marques de téléphones avec leurs modèles
        phone_brands_data = Phone.objects.values('brand', 'model').distinct().order_by('brand', 'model')
        
        # Grouper par marque
        brands_dict = {}
        for phone_data in phone_brands_data:
            brand = phone_data['brand']
            model = phone_data['model']
            
            if brand and brand != 'Inconnu':
                if brand not in brands_dict:
                    brands_dict[brand] = []
                if model and model != 'Inconnu':
                    brands_dict[brand].append(model)
        
        self.stdout.write('\n📱 Marques et modèles disponibles:')
        for brand, models in brands_dict.items():
            self.stdout.write(f'\n  🏷️  {brand}:')
            # Limiter à 5 modèles les plus populaires
            popular_models = models[:5]
            for model in popular_models:
                self.stdout.write(f'    • {model}')
            
            if len(models) > 5:
                self.stdout.write(f'    ... et {len(models) - 5} autres modèles')
        
        # Vérifier la catégorie Téléphones
        try:
            phones_category = Category.objects.get(slug='telephones')
            self.stdout.write(f'\n✅ Catégorie Téléphones trouvée: {phones_category.name} (ID: {phones_category.id})')
            
            # Vérifier les sous-catégories existantes
            subcategories = phones_category.children.all()
            if subcategories.exists():
                self.stdout.write('\n📂 Sous-catégories existantes:')
                for subcat in subcategories:
                    self.stdout.write(f'  • {subcat.name} (slug: {subcat.slug})')
            else:
                self.stdout.write('\n📂 Aucune sous-catégorie existante')
                
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('\n❌ Catégorie Téléphones non trouvée'))
        
        # Statistiques
        total_phones = Phone.objects.count()
        total_brands = len(brands_dict)
        total_models = sum(len(models) for models in brands_dict.values())
        
        self.stdout.write(f'\n📊 Statistiques:')
        self.stdout.write(f'  • Total téléphones: {total_phones}')
        self.stdout.write(f'  • Total marques: {total_brands}')
        self.stdout.write(f'  • Total modèles: {total_models}')
        
        self.stdout.write(self.style.SUCCESS('\n�� Test terminé!')) 