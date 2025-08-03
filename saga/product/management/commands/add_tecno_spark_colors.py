from django.core.management.base import BaseCommand
from product.models import Color


class Command(BaseCommand):
    help = 'Ajoute les couleurs pour tous les modèles TECNO SPARK'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Début de l\'ajout des couleurs TECNO SPARK...')
        
        # Dictionnaire des couleurs par modèle SPARK
        spark_colors = {
            'SPARK Go 1': [
                {
                    'name': 'Startrail Black',
                    'code': '#1a1a1a'  # Noir profond
                },
                {
                    'name': 'Glittery White',
                    'code': '#f8f8f8'  # Blanc nacré
                }
            ],
            'SPARK 10': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 10C': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Green',
                    'code': '#00aa44'  # Vert TECNO
                }
            ],
            'SPARK 10 Pro': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                },
                {
                    'name': 'Green',
                    'code': '#00aa44'  # Vert TECNO
                }
            ],
            'SPARK 20C': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20 Pro': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                },
                {
                    'name': 'Green',
                    'code': '#00aa44'  # Vert TECNO
                }
            ],
            'SPARK 20C+': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C Pro': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ Pro': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ 5G': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C Pro 5G': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ Pro 5G': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ 5G Pro': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
                    'code': '#0066cc'  # Bleu TECNO
                }
            ],
            'SPARK 20C+ 5G Pro Max': [
                {
                    'name': 'Black',
                    'code': '#000000'  # Noir classique
                },
                {
                    'name': 'White',
                    'code': '#ffffff'  # Blanc pur
                },
                {
                    'name': 'Blue',
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