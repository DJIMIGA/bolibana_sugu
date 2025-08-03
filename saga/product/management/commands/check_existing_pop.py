from django.core.management.base import BaseCommand
from product.models import Phone, Product


class Command(BaseCommand):
    help = 'Vérifie les modèles POP existants dans la base de données'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Vérification des modèles POP existants...')
        
        # Rechercher tous les modèles contenant "POP"
        pop_phones = Phone.objects.filter(model__icontains='POP')
        
        if not pop_phones.exists():
            self.stdout.write('ℹ️ Aucun modèle POP trouvé dans la base de données')
            return
        
        # Grouper par modèle
        models = {}
        for phone in pop_phones:
            model_name = phone.model
            if model_name not in models:
                models[model_name] = []
            models[model_name].append(phone)
        
        self.stdout.write('')
        self.stdout.write('📱 Modèles POP existants :')
        self.stdout.write('=' * 50)
        
        total_phones = 0
        for model_name, phones in sorted(models.items()):
            self.stdout.write(f'')
            self.stdout.write(f'📋 Modèle: {model_name}')
            self.stdout.write(f'   📊 Nombre de téléphones: {len(phones)}')
            
            # Afficher quelques exemples de variantes
            variants = set()
            for phone in phones[:5]:  # Limiter à 5 exemples
                variant = f"{phone.storage}GB/{phone.ram}GB - {phone.color.name}"
                variants.add(variant)
            
            self.stdout.write(f'   🎨 Exemples de variantes:')
            for variant in sorted(variants):
                self.stdout.write(f'      • {variant}')
            
            if len(phones) > 5:
                self.stdout.write(f'      ... et {len(phones) - 5} autres variantes')
            
            total_phones += len(phones)
        
        self.stdout.write('')
        self.stdout.write('=' * 50)
        self.stdout.write(f'📊 Total: {len(models)} modèles, {total_phones} téléphones')
        
        # Vérifier les incohérences de capitalisation
        self.stdout.write('')
        self.stdout.write('🔍 Vérification des incohérences de capitalisation:')
        model_names = list(models.keys())
        for i, model1 in enumerate(model_names):
            for model2 in model_names[i+1:]:
                if model1.lower() == model2.lower() and model1 != model2:
                    self.stdout.write(f'⚠️ Incohérence détectée: "{model1}" vs "{model2}"')
        
        self.stdout.write('')
        self.stdout.write('💡 Recommandations:')
        self.stdout.write('• Utiliser le modèle de template pour ajouter de nouveaux modèles')
        self.stdout.write('• Normaliser les noms de modèles existants si nécessaire')
        self.stdout.write('• Vérifier les doublons avant d\'ajouter de nouveaux produits') 