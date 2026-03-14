from django.core.management.base import BaseCommand
from core.models import SiteConfiguration

class Command(BaseCommand):
    help = 'Initialise la configuration du site avec les valeurs BoliBana'

    def handle(self, *args, **options):
        config, created = SiteConfiguration.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'BoliBana',
                'phone_number': '72464294',
                'email': 'bolibanasugu@gmail.com',
                'address': 'Rue 754, Kalaban Coro, Bamako, Mali',
                'rccm': 'MA.BKO.2025.A.2936',
                'company_name': 'BoliBana SuGu',
                'company_type': 'Entreprise individuelle',
                'company_address': 'Bamako, Mali',
                'opening_hours': 'Lun-Ven: 8h-18h, Sam: 9h-17h',
                'opening_hours_detailed': '8h>21h, dimanche 8h30>13h',
                'meta_description': 'BoliBana SuGu - Votre intermediaire expert du marche. '
                    'Comparateur de prix, selection de fournisseurs fiables, '
                    'gestion livraison, meilleur prix garanti. Paiement a la commande.',
                'meta_keywords': 'BoliBana, SuGu, Mali, Bamako, courses en ligne, '
                    'comparateur prix, livraison, fournisseurs, epicerie, high-tech',
                'delivery_info': 'Livraison gratuite a partir de 10 000 FCFA',
                'return_policy': '30 jours pour changer d\'avis',
                'brand_primary_color': '#008000',
                'brand_secondary_color': '#FFD700',
                'brand_accent_color': '#EF4444',
                'brand_tagline': 'Votre intermediaire expert du marche',
                'brand_short_tagline': 'SuGu',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Configuration BoliBana creee avec succes !')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Configuration du site existe deja.')
            )
        
        self.stdout.write(f'Site: {config.site_name}')
        self.stdout.write(f'Telephone: {config.phone_number}')
        self.stdout.write(f'Email: {config.email}')
        self.stdout.write(f'Entreprise: {config.company_name}')
        self.stdout.write(f'Adresse: {config.company_address}')
        self.stdout.write(f'Couleur primaire: {config.brand_primary_color}')
        self.stdout.write(f'Couleur secondaire: {config.brand_secondary_color}')
        self.stdout.write(f'Couleur accent: {config.brand_accent_color}')
        self.stdout.write(f'Tagline: {config.brand_tagline}') 