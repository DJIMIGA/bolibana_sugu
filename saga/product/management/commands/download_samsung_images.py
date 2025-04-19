from django.core.management.base import BaseCommand
import os
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = 'Crée la structure de base pour les images des téléphones Samsung'

    def handle(self, *args, **options):
        # Créer le dossier pour les images si nécessaire
        images_dir = os.path.join(settings.MEDIA_ROOT, 'phones')
        Path(images_dir).mkdir(parents=True, exist_ok=True)

        # Liste des modèles et leurs variantes
        models = {
            's24_ultra': {
                'black': ['front', 'back', 'side'],
                'violet': ['front', 'back', 'side']
            },
            's24_plus': {
                'black': ['front', 'back', 'side'],
                'blue': ['front', 'back', 'side']
            }
        }

        # Créer les dossiers pour chaque modèle et variante
        for model, colors in models.items():
            model_dir = os.path.join(images_dir, model)
            Path(model_dir).mkdir(exist_ok=True)
            
            for color, views in colors.items():
                color_dir = os.path.join(model_dir, color)
                Path(color_dir).mkdir(exist_ok=True)
                
                for view in views:
                    # Créer un fichier texte vide pour chaque image
                    placeholder_file = os.path.join(color_dir, f"{view}.txt")
                    with open(placeholder_file, 'w') as f:
                        f.write(f"Placeholder pour {model} {color} {view}")
                    
                    self.stdout.write(self.style.SUCCESS(f'Créé: {placeholder_file}'))

        self.stdout.write(self.style.SUCCESS('Structure de base créée avec succès'))
        self.stdout.write(self.style.WARNING('Note: Les images réelles devront être ajoutées manuellement plus tard')) 