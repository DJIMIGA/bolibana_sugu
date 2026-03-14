from django.core.management.base import BaseCommand
from product.models import Color


class Command(BaseCommand):
    help = 'Ajoute les couleurs pour tous les modèles TECNO SPARK'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO SPARK...')
        
        # Dictionnaire des couleurs par modèle SPARK (Gamme complète)
        spark_colors = {
            # SPARK Go Series
            'SPARK Go 1': [
                {
                    'name': 'Noir Startrail',
                    'code': '#1a1a1a'  # Noir profond
                },
                {
                    'name': 'Blanc Scintillant',
                    'code': '#f8f8f8'  # Blanc nacré
                }
            ],
            'SPARK Go 1S': [
                {
                    'name': 'Noir Startrail',
                    'code': '#1a1a1a'  # Noir profond
                },
                {
                    'name': 'Blanc Scintillant',
                    'code': '#f8f8f8'  # Blanc nacré
                }
            ],
            'SPARK Go 2': [
                {
                    'name': 'Noir Encre',
                    'code': '#000000'  # Noir encre
                },
                {
                    'name': 'Gris Titane',
                    'code': '#696969'  # Gris titane
                },
                {
                    'name': 'Blanc Voile',
                    'code': '#f5f5f5'  # Blanc voile
                },
                {
                    'name': 'Vert Turquoise',
                    'code': '#40e0d0'  # Vert turquoise
                }
            ],
            # SPARK 10 Series
            'SPARK 10': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 10C': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Vert',
                    'code': '#00aa44'  # Vert TECNO
                }
            ],
            'SPARK 10 Pro': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            # SPARK 20 Series
            'SPARK 20': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                },
                {
                    'name': 'Vert',
                    'code': '#00aa44'  # Vert TECNO
                }
            ],
            'SPARK 20C': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20 Pro': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                },
                {
                    'name': 'Vert',
                    'code': '#00aa44'  # Vert TECNO
                }
            ],
            'SPARK 20C+': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C Pro': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ Pro': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            # SPARK 30 Series
            'SPARK 30': [
                {
                    'name': 'Glace Astrale',
                    'code': '#e6f3ff'  # Blanc glacé astral
                },
                {
                    'name': 'Ombre Stellaire',
                    'code': '#1a1a2e'  # Ombre stellaire
                }
            ],
            'SPARK 30 Pro': [
                {
                    'name': 'Lueur Arctique',
                    'code': '#f0f8ff'  # Lueur arctique
                },
                {
                    'name': 'Bordure Obsidienne',
                    'code': '#0a0a0a'  # Bordure d'obsidienne
                }
            ],
            'SPARK 30 5G': [
                {
                    'name': 'Ombre de Minuit',
                    'code': '#1a1a1a'  # Ombre de minuit
                },
                {
                    'name': 'Nuage d\'Aurore',
                    'code': '#f5f5f5'  # Nuage d'aurore
                },
                {
                    'name': 'Ciel Azur',
                    'code': '#87ceeb'  # Ciel azur
                }
            ],
            'SPARK 30C': [
                {
                    'name': 'Noir Orbite',
                    'code': '#0a0a0a'  # Noir orbit
                },
                {
                    'name': 'Blanc Orbite',
                    'code': '#f0f0f0'  # Blanc orbit
                },
                {
                    'name': 'Peau Magique 3.0',
                    'code': '#8b4513'  # Brun peau magique
                }
            ],
            'SPARK 30C 5G': [
                {
                    'name': 'Ombre de Minuit',
                    'code': '#1a1a1a'  # Ombre de minuit
                },
                {
                    'name': 'Nuage d\'Aurore',
                    'code': '#f5f5f5'  # Nuage d'aurore
                },
                {
                    'name': 'Ciel Azur',
                    'code': '#87ceeb'  # Ciel azur
                }
            ],
            'SPARK 40': [
                {
                    'name': 'Noir Encre',
                    'code': '#000000'  # Noir encre
                },
                {
                    'name': 'Gris Titane',
                    'code': '#696969'  # Gris titane
                },
                {
                    'name': 'Blanc Voile',
                    'code': '#f5f5f5'  # Blanc voile
                },
                {
                    'name': 'Bleu Mirage',
                    'code': '#4169e1'  # Bleu mirage
                }
            ],
            'SPARK 40 Pro': [
                {
                    'name': 'Noir Encre',
                    'code': '#000000'  # Noir encre
                },
                {
                    'name': 'Titane Lunaire',
                    'code': '#c0c0c0'  # Titane lunaire
                },
                {
                    'name': 'Bleu Lac',
                    'code': '#4682b4'  # Bleu lac
                },
                {
                    'name': 'Vert Bambou',
                    'code': '#228b22'  # Vert bambou
                }
            ],
            'SPARK 40 Pro+': [
                {
                    'name': 'Noir Nébuleuse',
                    'code': '#1a1a1a'  # Noir nébuleuse
                },
                {
                    'name': 'Blanc Aurore',
                    'code': '#f8f8ff'  # Blanc aurore
                },
                {
                    'name': 'Titane Lunaire',
                    'code': '#c0c0c0'  # Titane lunaire
                },
                {
                    'name': 'Vert Toundra',
                    'code': '#2e8b57'  # Vert toundra
                }
            ],
            'SPARK 40C': [
                {
                    'name': 'Blanc Voile',
                    'code': '#f5f5f5'  # Blanc voile
                },
                {
                    'name': 'Bleu Ondulation',
                    'code': '#1e90ff'  # Bleu ondulation
                },
                {
                    'name': 'Gris Titane',
                    'code': '#696969'  # Gris titane
                },
                {
                    'name': 'Noir Encre',
                    'code': '#000000'  # Noir encre
                }
            ],
            # SPARK 20 5G Series
            'SPARK 20C+ 5G': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C Pro 5G': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ Pro 5G': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ 5G Pro': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ 5G Pro Max': [
                {
                    'name': 'Noir',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'Blanc',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Bleu',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ]
        }
        
        total_created = 0
        total_existing = 0
        
        for model_name, colors in spark_colors.items():
            self.stdout.write(f'\n📱 {model_name}:')
            
            for color_data in colors:
                # Recherche insensible à la casse pour éviter les doublons
                existing_colors = Color.objects.filter(name__iexact=color_data['name'])
                
                if existing_colors.exists():
                    # Vérifier s'il y a des doublons
                    if existing_colors.count() > 1:
                        self.stdout.write(f'  ⚠️ DOUBLONS DÉTECTÉS pour "{color_data["name"]}":')
                        for existing_color in existing_colors:
                            self.stdout.write(f'    - ID {existing_color.id}: "{existing_color.name}" ({existing_color.code})')
                        
                        # Garder la première et supprimer les autres
                        primary_color = existing_colors.first()
                        duplicates = existing_colors.exclude(id=primary_color.id)
                        
                        for duplicate in duplicates:
                            self.stdout.write(f'    🗑️ Suppression du doublon ID {duplicate.id}')
                            duplicate.delete()
                        
                        self.stdout.write(f'  ✅ Doublons nettoyés pour "{color_data["name"]}"')
                        total_existing += 1
                    else:
                        self.stdout.write(f'  ℹ️ Couleur déjà existante: {existing_colors.first().name}')
                        total_existing += 1
                else:
                    # Créer la nouvelle couleur
                    color = Color.objects.create(
                        name=color_data['name'],
                        code=color_data['code']
                    )
                    self.stdout.write(f'  ✅ Couleur créée: {color.name} ({color.code})')
                    total_created += 1
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'🎨 Résumé: {total_created} couleurs créées, {total_existing} déjà existantes')
        self.stdout.write('✅ Ajout des couleurs TECNO SPARK terminé !')
        self.stdout.write('')
        self.stdout.write('📝 Note: Vous pouvez maintenant exécuter la commande d\'ajout des téléphones SPARK') 