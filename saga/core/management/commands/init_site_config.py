from django.core.management.base import BaseCommand
from core.models import SiteConfiguration

class Command(BaseCommand):
    help = 'Initialise la configuration du site avec des valeurs par défaut'

    def handle(self, *args, **options):
        config, created = SiteConfiguration.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'BoliBana Sugu',
                'phone_number': '72464294',
                'email': 'bolibanasugu@gmail.com',
                'address': 'Bamako, Mali',
                'rccm': 'MA.BKO.2025.A.2936',
                'company_name': 'BoliBana Sugu',
                'company_type': 'Entreprise individuelle',
                'company_address': 'Bamako, Mali',
                'opening_hours': 'Lun-Ven: 8h-18h, Sam: 9h-17h',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Configuration du site créée avec succès !')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Configuration du site existe déjà.')
            )
        
        self.stdout.write(f'📞 Téléphone: {config.phone_number}')
        self.stdout.write(f'📧 Email: {config.email}')
        self.stdout.write(f'🏢 Entreprise: {config.company_name}')
        self.stdout.write(f'📍 Adresse: {config.company_address}') 