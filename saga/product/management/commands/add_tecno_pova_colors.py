from django.core.management.base import BaseCommand
from product.models import Color


class Command(BaseCommand):
    help = 'Ajoute toutes les couleurs pour les téléphones TECNO POVA'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO POVA...')
        
        # Normalisation des marques TECNO
        self.stdout.write('🔧 Normalisation des marques TECNO...')
        
        colors_data = [
            # POVA 7 Pro 5G
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
            # POVA 7 5G
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
                         # POVA 7 Ultra 5G
             {
                 'name': 'Blanc Geek',
                 'code': '#ffffff'  # Blanc geek
             },
             {
                 'name': 'Noir Geek',
                 'code': '#1a1a1a'  # Noir geek
             },
            # POVA 7
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
                         # POVA Curve 5G
             {
                 'name': 'Noir Geek',
                 'code': '#1a1a1a'  # Noir geek
             },
             {
                 'name': 'Argent Magique',
                 'code': '#c0c0c0'  # Argent magique
             },
             {
                 'name': 'Cyan Néon',
                 'code': '#00ffff'  # Cyan néon
             },
             # POVA 7
             {
                 'name': 'Titanium Hyper',
                 'code': '#b8860b'  # Titanium hyper
             },
             {
                 'name': 'Argent Magique',
                 'code': '#c0c0c0'  # Argent magique
             },
             {
                 'name': 'Noir Geek',
                 'code': '#1a1a1a'  # Noir geek
             },
                         # POVA 6 Pro 5G
             {
                 'name': 'Vert Comète',
                 'code': '#00a86b'  # Vert comète
             },
             {
                 'name': 'Gris Météorite',
                 'code': '#696969'  # Gris météorite
             },
                         # POVA 6 NEO
             {
                 'name': 'Argent Étoilé',
                 'code': '#c0c0c0'  # Argent étoilé
             },
             {
                 'name': 'Noir Vitesse',
                 'code': '#1a1a1a'  # Noir vitesse
             },
             {
                 'name': 'Vert Comète',
                 'code': '#00a86b'  # Vert comète
             },
                         # POVA 6
             {
                 'name': 'Vert Comète',
                 'code': '#00ff7f'  # Vert comète
             },
             {
                 'name': 'Gris Météorite',
                 'code': '#696969'  # Gris météorite
             },
             {
                 'name': 'Bleu Interstellaire',
                 'code': '#4169e1'  # Bleu interstellaire
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
        self.stdout.write('✅ Ajout des couleurs TECNO POVA terminé !')
        self.stdout.write('')
        self.stdout.write('📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones TECNO POVA')
        self.stdout.write('')
        self.stdout.write('💡 Gamme POVA : Smartphones gaming et performance TECNO avec batteries haute capacité') 