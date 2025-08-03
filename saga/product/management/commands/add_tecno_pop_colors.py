from django.core.management.base import BaseCommand
from product.models import Color


class Command(BaseCommand):
    help = 'Ajoute toutes les couleurs pour les téléphones TECNO POP'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO POP...')
        
        # Normalisation des marques TECNO
        self.stdout.write('🔧 Normalisation des marques TECNO...')
        
        colors_data = [
            # POP 8
            {
                'name': 'Noir Mystérieux',
                'code': '#1a1a1a'  # Noir profond
            },
            {
                'name': 'Bleu Océan',
                'code': '#0066cc'  # Bleu océan
            },
            {
                'name': 'Vert Émeraude',
                'code': '#00a86b'  # Vert émeraude
            },
            {
                'name': 'Or Doré',
                'code': '#ffd700'  # Or doré
            },
            # POP 7
            {
                'name': 'Noir Infini',
                'code': '#000000'  # Noir pur
            },
            {
                'name': 'Bleu Capri',
                'code': '#1e90ff'  # Bleu capri
            },
            {
                'name': 'Vert Ice Lake',
                'code': '#90ee90'  # Vert ice lake
            },
            # POP 6
            {
                'name': 'Noir Minuit',
                'code': '#191970'  # Noir minuit
            },
            {
                'name': 'Bleu Cyan',
                'code': '#00ffff'  # Bleu cyan
            },
            {
                'name': 'Violet Étoilé',
                'code': '#8a2be2'  # Violet étoilé
            },
            # POP 5
            {
                'name': 'Noir Obsidien',
                'code': '#1a1a1a'  # Noir obsidien
            },
            {
                'name': 'Bleu Ice',
                'code': '#87ceeb'  # Bleu ice
            },
            {
                'name': 'Vert Ice',
                'code': '#90ee90'  # Vert ice
            },
            # POP 4
            {
                'name': 'Noir Gravité',
                'code': '#2f2f2f'  # Noir gravité
            },
            {
                'name': 'Bleu Ville',
                'code': '#4169e1'  # Bleu ville
            },
            {
                'name': 'Magic Skin (Vert)',
                'code': '#32cd32'  # Magic skin vert
            },
            # POP 3
            {
                'name': 'Or Alpenglow',
                'code': '#ffd700'  # Or alpenglow
            },
            {
                'name': 'Blanc Mystère',
                'code': '#f5f5f5'  # Blanc mystère
            },
            {
                'name': 'Violet Étoilé',
                'code': '#8a2be2'  # Violet étoilé
            },
            # POP 2
            {
                'name': 'Bleu Océan',
                'code': '#0066cc'  # Bleu océan
            },
            {
                'name': 'Noir Brillant',
                'code': '#1a1a1a'  # Noir brillant
            },
            {
                'name': 'Bleu Uyuni',
                'code': '#87ceeb'  # Bleu uyuni
            },
            # POP 1
            {
                'name': 'Violet Nébuleuse',
                'code': '#8a2be2'  # Violet nébuleuse
            },
            {
                'name': 'Bleu Capri',
                'code': '#1e90ff'  # Bleu capri
            },
            {
                'name': 'Gris Argent',
                'code': '#c0c0c0'  # Gris argent
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
        self.stdout.write('✅ Ajout des couleurs TECNO POP terminé !')
        self.stdout.write('')
        self.stdout.write('📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones TECNO POP') 