from django.core.management.base import BaseCommand
from product.models import Color

class Command(BaseCommand):
    help = 'Ajoute les couleurs officielles du TECNO CAMON 40 Pro 5G'

    def handle(self, *args, **options):
        colors_data = [
            {'name': 'Noir Galaxy', 'code': '#000000', 'description': 'Couleur officielle TECNO CAMON 40 Pro 5G - Noir Galaxy élégant'},
            {'name': 'Vert Émeraude', 'code': '#00a86b', 'description': 'Couleur officielle TECNO CAMON 40 Pro 5G - Vert Émeraude moderne'},
            {'name': 'Blanc Glacier', 'code': '#f8f8ff', 'description': 'Couleur officielle TECNO CAMON 40 Pro 5G - Blanc Glacier pur'},
            {'name': 'Titanium Sable', 'code': '#c0c0c0', 'description': 'Couleur officielle TECNO CAMON 40 Pro 5G - Titanium Sable premium'}
        ]

        colors_created = 0
        colors_updated = 0

        for color_data in colors_data:
            try:
                color, created = Color.objects.get_or_create(
                    name=color_data['name'],
                    defaults={'code': color_data['code']}
                )
                if created:
                    colors_created += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Couleur créée: {color.name} ({color.code})'))
                else:
                    if color.code != color_data['code']:
                        color.code = color_data['code']
                        color.save()
                        colors_updated += 1
                        self.stdout.write(self.style.WARNING(f'🔄 Couleur mise à jour: {color.name} ({color.code})'))
                    else:
                        self.stdout.write(self.style.WARNING(f'ℹ️ Couleur existante: {color.name} ({color.code})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur avec {color_data["name"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n🎨 Résumé: {colors_created} couleurs créées, {colors_updated} mises à jour'))
        self.stdout.write(self.style.SUCCESS('\n📋 Couleurs disponibles:'))
        all_colors = Color.objects.all().order_by('name')
        for color in all_colors:
            self.stdout.write(f'  • {color.name} ({color.code})') 