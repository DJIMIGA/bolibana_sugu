from django.core.management.base import BaseCommand
from product.models import Color
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ajoute les couleurs spécifiques au TECNO CAMON 30S'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO CAMON 30S...')
        
        # Couleurs spécifiques au CAMON 30S
        colors_data = [
            {
                'name': 'Noir Céleste',
                'code': '#1a1a1a',
                'description': 'Noir profond avec reflets célestes'
            },
            {
                'name': 'Or Aube',
                'code': '#ffd700',
                'description': 'Or lumineux comme l\'aube'
            },
            {
                'name': 'Violet Nébuleuse',
                'code': '#8a2be2',
                'description': 'Violet mystérieux comme une nébuleuse'
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for color_data in colors_data:
            try:
                color, created = Color.objects.get_or_create(
                    name=color_data['name'],
                    defaults={'code': color_data['code']}
                )
                
                if created:
                    self.stdout.write(f'✅ Couleur créée: {color.name} ({color.code})')
                    created_count += 1
                else:
                    self.stdout.write(f'ℹ️ Couleur existante: {color.name} ({color.code})')
                    existing_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur avec {color_data["name"]}: {str(e)}'))
        
        self.stdout.write(f'\n🎨 Résumé: {created_count} couleurs créées, {existing_count} déjà existantes')
        self.stdout.write(self.style.SUCCESS('✅ Ajout des couleurs TECNO CAMON 30S terminé !'))
        
        if created_count > 0:
            self.stdout.write('\n📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones CAMON 30S') 