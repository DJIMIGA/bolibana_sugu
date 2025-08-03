from django.core.management.base import BaseCommand
from product.models import Color


class Command(BaseCommand):
    help = 'Ajoute les couleurs pour les TECNO CAMON 30 5G'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO CAMON 30 5G...')
        
        # Normalisation des marques TECNO
        self.stdout.write('🔧 Normalisation des marques TECNO...')
        # Cette normalisation est maintenant gérée automatiquement
        
        colors_data = [
            {
                'name': 'Édition Loewe',
                'code': '#1a1a1a'  # Noir premium
            },
            {
                'name': 'Noir Basaltique Islande',
                'code': '#2d1810'  # Noir basaltique
            },
            {
                'name': 'Blanc Sel Uyuni',
                'code': '#f8f8ff'  # Blanc sel
            },
            {
                'name': 'Vert Lac Émeraude',
                'code': '#00a86b'  # Vert émeraude
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for color_data in colors_data:
            color, created = Color.objects.get_or_create(
                name=color_data['name'],
                defaults={
                    'code': color_data['code']
                }
            )
            
            if created:
                self.stdout.write(f'✅ Couleur créée: {color.name} ({color.code})')
                created_count += 1
            else:
                self.stdout.write(f'ℹ️ Couleur déjà existante: {color.name}')
                existing_count += 1
        
        self.stdout.write('')
        self.stdout.write(f'🎨 Résumé: {created_count} couleurs créées, {existing_count} déjà existantes')
        self.stdout.write('✅ Ajout des couleurs TECNO CAMON 30 5G terminé !')
        self.stdout.write('')
        self.stdout.write('📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones CAMON 30 5G') 