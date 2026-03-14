from django.core.management.base import BaseCommand
from core.models import SiteConfiguration

class Command(BaseCommand):
    help = 'Configure Google Analytics ID'

    def handle(self, *args, **options):
        try:
            # Récupérer ou créer la configuration
            config = SiteConfiguration.get_config()
            
            # Configurer l'ID Google Analytics
            config.google_analytics_id = 'G-CX5XPTXF1V'
            config.save()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Google Analytics configuré avec succès!')
            )
            self.stdout.write(f"📊 Measurement ID: {config.google_analytics_id}")
            self.stdout.write(f"🌐 Site: {config.site_name}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la configuration: {e}')
            ) 