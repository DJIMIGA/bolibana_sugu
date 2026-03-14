from django.core.management.base import BaseCommand
from django.db.models import Count
from product.models import Color, Product, Phone, Fabric, Clothing
from django.db import transaction


class Command(BaseCommand):
    help = 'Identifie et nettoie les doublons de couleurs dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les doublons sans les supprimer',
        )
        parser.add_argument(
            '--color-name',
            type=str,
            help='Nom spécifique de la couleur à nettoyer (ex: "Édition Loewe")',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_color = options['color_name']
        
        self.stdout.write('🔍 Début de l\'analyse des doublons de couleurs...')
        
        if dry_run:
            self.stdout.write('📋 Mode DRY-RUN activé - Aucune modification ne sera effectuée')
        
        # Recherche des doublons
        if specific_color:
            # Recherche pour une couleur spécifique
            duplicates = Color.objects.filter(
                name__iexact=specific_color
            ).order_by('id')
            
            if duplicates.count() <= 1:
                self.stdout.write(f'ℹ️ Aucun doublon trouvé pour "{specific_color}"')
                return
                
            self.stdout.write(f'🎯 Analyse des doublons pour "{specific_color}"...')
        else:
            # Recherche de tous les doublons
            duplicates = Color.objects.values('name').annotate(
                count=Count('id')
            ).filter(count__gt=1).order_by('name')
            
            if not duplicates:
                self.stdout.write('✅ Aucun doublon de couleur trouvé dans la base de données')
                return
        
        total_duplicates_found = 0
        total_duplicates_cleaned = 0
        
        if specific_color:
            # Traitement d'une couleur spécifique
            self._process_color_duplicates(specific_color, dry_run)
        else:
            # Traitement de tous les doublons
            for duplicate in duplicates:
                color_name = duplicate['name']
                count = duplicate['count']
                total_duplicates_found += count - 1
                
                self.stdout.write(f'\n🎨 Couleur: "{color_name}" ({count} occurrences)')
                cleaned = self._process_color_duplicates(color_name, dry_run)
                if cleaned:
                    total_duplicates_cleaned += cleaned
        
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(f'📊 Résumé DRY-RUN: {total_duplicates_found} doublons identifiés')
        else:
            self.stdout.write(f'✅ Résumé: {total_duplicates_cleaned} doublons nettoyés')
        self.stdout.write('🎨 Nettoyage des doublons de couleurs terminé !')

    def _process_color_duplicates(self, color_name, dry_run=False):
        """Traite les doublons d'une couleur spécifique"""
        colors = Color.objects.filter(name__iexact=color_name).order_by('id')
        
        if colors.count() <= 1:
            return 0
        
        # Garder la première couleur (la plus ancienne)
        primary_color = colors.first()
        duplicate_colors = colors.exclude(id=primary_color.id)
        
        self.stdout.write(f'  📌 Couleur principale: ID {primary_color.id} - "{primary_color.name}" ({primary_color.code})')
        
        cleaned_count = 0
        
        for duplicate in duplicate_colors:
            self.stdout.write(f'  🗑️ Doublon: ID {duplicate.id} - "{duplicate.name}" ({duplicate.code})')
            
            # Vérifier les références
            references = self._get_color_references(duplicate)
            
            if references:
                self.stdout.write(f'    ⚠️ Références trouvées: {references}')
                
                if not dry_run:
                    # Migrer les références vers la couleur principale
                    self._migrate_references(duplicate, primary_color)
                    self.stdout.write(f'    ✅ Références migrées vers ID {primary_color.id}')
            
            if not dry_run:
                # Supprimer le doublon
                duplicate.delete()
                self.stdout.write(f'    ✅ Doublon supprimé')
                cleaned_count += 1
            else:
                self.stdout.write(f'    📋 [DRY-RUN] Doublon serait supprimé')
                cleaned_count += 1
        
        return cleaned_count

    def _get_color_references(self, color):
        """Retourne les références à cette couleur dans la base de données"""
        references = []
        
        # Vérifier les téléphones
        phones = Phone.objects.filter(color=color)
        if phones.exists():
            references.append(f'{phones.count()} téléphone(s)')
        
        # Vérifier les tissus
        fabrics = Fabric.objects.filter(color=color)
        if fabrics.exists():
            references.append(f'{fabrics.count()} tissu(x)')
        
        # Vérifier les vêtements (ManyToManyField)
        clothing = Clothing.objects.filter(color=color)
        if clothing.exists():
            references.append(f'{clothing.count()} vêtement(s)')
        
        return ', '.join(references) if references else None

    def _migrate_references(self, old_color, new_color):
        """Migre toutes les références d'une couleur vers une autre"""
        with transaction.atomic():
            # Migrer les téléphones
            Phone.objects.filter(color=old_color).update(color=new_color)
            
            # Migrer les tissus
            Fabric.objects.filter(color=old_color).update(color=new_color)
            
            # Migrer les vêtements (ManyToManyField)
            # Pour les ManyToManyField, on doit ajouter la nouvelle couleur et retirer l'ancienne
            clothing_with_old_color = Clothing.objects.filter(color=old_color)
            for clothing in clothing_with_old_color:
                clothing.color.add(new_color)
                clothing.color.remove(old_color) 