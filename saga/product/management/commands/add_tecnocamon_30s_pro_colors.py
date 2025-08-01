from django.core.management.base import BaseCommand
from product.models import Color, Phone
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ajoute les couleurs spécifiques au TECNO CAMON 30S Pro avec normalisation des marques'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO CAMON 30S Pro...')
        
        # Normalisation des marques TECNO
        self.stdout.write('🔧 Normalisation des marques TECNO...')
        phones_to_update = Phone.objects.filter(
            Q(brand__icontains='TECNO') | 
            Q(brand__icontains='Tecno') | 
            Q(brand__icontains='tecnocamon')
        )
        
        updated_count = 0
        for phone in phones_to_update:
            if phone.brand != 'TECNO':
                old_brand = phone.brand
                phone.brand = 'TECNO'
                phone.save()
                self.stdout.write(f'✅ Marque normalisée: {old_brand} → TECNO')
                updated_count += 1
        
        self.stdout.write(f'🔧 {updated_count} marques TECNO normalisées')
        
        # Couleurs spécifiques au CAMON 30S Pro
        colors_data = [
            {
                'name': 'Gris Interstellaire',
                'code': '#2c3e50',
                'description': 'Gris profond comme l\'espace interstellaire'
            },
            {
                'name': 'Or Perle',
                'code': '#f4e4bc',
                'description': 'Or doux comme une perle'
            },
            {
                'name': 'Vert Argent Shim',
                'code': '#90ee90',
                'description': 'Vert argenté élégant'
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
        self.stdout.write(self.style.SUCCESS('✅ Ajout des couleurs TECNO CAMON 30S Pro terminé !'))
        
        if created_count > 0:
            self.stdout.write('\n📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones CAMON 30S Pro') 