from django.core.management.base import BaseCommand
from product.models import Phone, Product
from django.db.models import Count

class Command(BaseCommand):
    help = 'Optimise l\'affichage du dropdown des téléphones pour gérer beaucoup de modèles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-brands',
            type=int,
            default=8,
            help='Nombre maximum de marques à afficher (défaut: 8)',
        )
        parser.add_argument(
            '--max-models',
            type=int,
            default=4,
            help='Nombre maximum de modèles par marque (défaut: 4)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Optimisation du dropdown des téléphones...'))
        
        max_brands = options['max_brands']
        max_models = options['max_models']
        
        # Analyser les marques par popularité
        brands_analysis = Phone.objects.values('brand').annotate(
            product_count=Count('product')
        ).filter(
            brand__isnull=False
        ).exclude(
            brand='Inconnu'
        ).order_by('-product_count', 'brand')
        
        self.stdout.write(f'\n📊 Analyse des marques (limite: {max_brands} marques):')
        
        # Afficher les marques qui seront dans le dropdown
        for i, brand_data in enumerate(brands_analysis[:max_brands]):
            brand = brand_data['brand']
            count = brand_data['product_count']
            
            # Analyser les modèles de cette marque
            models_analysis = Phone.objects.filter(
                brand=brand
            ).values('model').annotate(
                model_count=Count('product')
            ).filter(
                model__isnull=False
            ).exclude(
                model='Inconnu'
            ).order_by('-model_count', 'model')
            
            self.stdout.write(f'\n  🏷️  {brand} ({count} produits):')
            
            # Afficher les modèles qui seront dans le dropdown
            for j, model_data in enumerate(models_analysis[:max_models]):
                model = model_data['model']
                model_count = model_data['model_count']
                self.stdout.write(f'    • {model} ({model_count} produits)')
            
            # Afficher le nombre de modèles cachés
            total_models = len(models_analysis)
            if total_models > max_models:
                hidden_models = total_models - max_models
                self.stdout.write(f'    ... et {hidden_models} autres modèles')
        
        # Afficher les marques qui ne seront pas dans le dropdown
        if len(brands_analysis) > max_brands:
            hidden_brands = brands_analysis[max_brands:]
            self.stdout.write(f'\n⚠️  Marques non affichées ({len(hidden_brands)} marques):')
            for brand_data in hidden_brands:
                brand = brand_data['brand']
                count = brand_data['product_count']
                self.stdout.write(f'  • {brand} ({count} produits)')
        
        # Statistiques globales
        total_phones = Phone.objects.count()
        total_brands = len(brands_analysis)
        total_models = Phone.objects.values('model').distinct().count()
        
        self.stdout.write(f'\n📈 Statistiques globales:')
        self.stdout.write(f'  • Total téléphones: {total_phones}')
        self.stdout.write(f'  • Total marques: {total_brands}')
        self.stdout.write(f'  • Total modèles: {total_models}')
        self.stdout.write(f'  • Marques affichées: {min(max_brands, total_brands)}')
        self.stdout.write(f'  • Modèles affichés: ~{min(max_brands, total_brands) * max_models}')
        
        # Recommandations
        self.stdout.write(f'\n💡 Recommandations:')
        if total_brands > max_brands:
            self.stdout.write(f'  • Augmenter --max-brands si vous voulez afficher plus de marques')
        if total_models > max_models * max_brands:
            self.stdout.write(f'  • Augmenter --max-models si vous voulez afficher plus de modèles par marque')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Analyse terminée!')) 