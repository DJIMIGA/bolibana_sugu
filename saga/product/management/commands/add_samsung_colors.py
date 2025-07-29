from django.core.management.base import BaseCommand
from product.models import Color

class Command(BaseCommand):
    help = 'Ajoute les couleurs officielles du Samsung Galaxy F16'

    def handle(self, *args, **options):
        colors_data = [
            {
                'name': 'Noir Brillant',
                'code': '#1a1a1a',
                'description': 'Couleur officielle Samsung Galaxy F16 - Noir brillant élégant'
            },
            {
                'name': 'Bleu Vibrant', 
                'code': '#0066cc',
                'description': 'Couleur officielle Samsung Galaxy F16 - Bleu vibrant moderne'
            },
            {
                'name': 'Vert Glamour',
                'code': '#00cc66', 
                'description': 'Couleur officielle Samsung Galaxy F16 - Vert glamour tendance'
            }
        ]

        colors_created = 0
        colors_updated = 0

        for color_data in colors_data:
            try:
                color, created = Color.objects.get_or_create(
                    name=color_data['name'],
                    defaults={
                        'code': color_data['code']
                    }
                )
                
                if created:
                    colors_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Couleur créée: {color.name} ({color.code})')
                    )
                else:
                    # Mettre à jour le code si différent
                    if color.code != color_data['code']:
                        color.code = color_data['code']
                        color.save()
                        colors_updated += 1
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Couleur mise à jour: {color.name} ({color.code})')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'ℹ️ Couleur existante: {color.name} ({color.code})')
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur avec {color_data["name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n🎨 Résumé: {colors_created} couleurs créées, {colors_updated} mises à jour'
        ))

        # Afficher toutes les couleurs disponibles
        self.stdout.write(self.style.SUCCESS('\n📋 Couleurs disponibles:'))
        all_colors = Color.objects.all().order_by('name')
        for color in all_colors:
            self.stdout.write(f'  • {color.name} ({color.code})') 