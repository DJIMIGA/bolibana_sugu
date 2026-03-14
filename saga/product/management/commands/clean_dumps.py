from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Nettoie les dossiers dumps et backups'

    def handle(self, *args, **options):
        dumps_dir = os.path.join(settings.BASE_DIR, 'product', 'dumps')
        backups_dir = os.path.join(settings.BASE_DIR, 'product', 'backups')

        # Supprimer et recréer le dossier dumps
        if os.path.exists(dumps_dir):
            shutil.rmtree(dumps_dir)
        os.makedirs(dumps_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Dossier dumps nettoyé : {dumps_dir}'))

        # Supprimer et recréer le dossier backups
        if os.path.exists(backups_dir):
            shutil.rmtree(backups_dir)
        os.makedirs(backups_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Dossier backups nettoyé : {backups_dir}')) 