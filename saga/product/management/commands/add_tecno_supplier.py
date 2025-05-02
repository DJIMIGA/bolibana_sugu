from django.core.management.base import BaseCommand
from suppliers.models import Supplier
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Ajoute le fournisseur Tecno dans la base de données'

    def handle(self, *args, **kwargs):
        try:
            # Vérifier si le fournisseur existe déjà
            supplier = Supplier.objects.get(name='Tecno')
            self.stdout.write(self.style.SUCCESS('Le fournisseur Tecno existe déjà'))
        except Supplier.DoesNotExist:
            # Créer le fournisseur Tecno
            supplier = Supplier.objects.create(
                name='Tecno',
                slug=slugify('Tecno'),
                description='''TECNO est une marque de smartphones haut de gamme qui se concentre sur l'innovation technologique et le design.
                La marque propose des appareils avec des fonctionnalités avancées, des performances exceptionnelles et des designs élégants.''',
                specialty='Fournisseur de TELEPHONE',
                email='contact@tecno.com',
                address='Siège social : Shenzhen, Chine',
                phone='+223 20 22 23 24'
            )
            self.stdout.write(self.style.SUCCESS('Le fournisseur Tecno a été créé avec succès'))

        self.stdout.write(self.style.SUCCESS('Opération terminée')) 