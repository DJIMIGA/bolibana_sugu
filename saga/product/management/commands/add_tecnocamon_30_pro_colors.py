from django.core.management.base import BaseCommand
from product.models import Color


class Command(BaseCommand):
    help = 'Ajoute les couleurs pour les TECNO CAMON 30 Pro 5G'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO CAMON 30 Pro 5G...')
        
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
                'name': 'Argent Neigeux Alpes',
                'code': '#f5f5f5'  # Blanc neigeux
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for color_data in colors_data:
            # Recherche insensible à la casse pour éviter les doublons
            existing_colors = Color.objects.filter(name__iexact=color_data['name'])
            
            if existing_colors.exists():
                # Vérifier s'il y a des doublons
                if existing_colors.count() > 1:
                    self.stdout.write(f'⚠️ DOUBLONS DÉTECTÉS pour "{color_data["name"]}":')
                    for existing_color in existing_colors:
                        self.stdout.write(f'  - ID {existing_color.id}: "{existing_color.name}" ({existing_color.code})')
                    
                    # Garder la première et supprimer les autres
                    primary_color = existing_colors.first()
                    duplicates = existing_colors.exclude(id=primary_color.id)
                    
                    for duplicate in duplicates:
                        self.stdout.write(f'  🗑️ Suppression du doublon ID {duplicate.id}')
                        duplicate.delete()
                    
                    self.stdout.write(f'✅ Doublons nettoyés pour "{color_data["name"]}"')
                    existing_count += 1
                else:
                    self.stdout.write(f'ℹ️ Couleur déjà existante: {existing_colors.first().name}')
                    existing_count += 1
            else:
                # Créer la nouvelle couleur
                color = Color.objects.create(
                    name=color_data['name'],
                    code=color_data['code']
                )
                self.stdout.write(f'✅ Couleur créée: {color.name} ({color.code})')
                created_count += 1
        
        self.stdout.write('')
        self.stdout.write(f'🎨 Résumé: {created_count} couleurs créées, {existing_count} déjà existantes')
        self.stdout.write('✅ Ajout des couleurs TECNO CAMON 30 Pro 5G terminé !')
        self.stdout.write('')
        self.stdout.write('📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones CAMON 30 Pro 5G') 