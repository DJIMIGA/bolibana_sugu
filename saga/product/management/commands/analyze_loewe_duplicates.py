from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from product.models import Color, Product, Phone, Fabric, Clothing


class Command(BaseCommand):
    help = 'Analyse spécifiquement les doublons de la couleur "Édition LOEWE"'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrige automatiquement les doublons trouvés',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        
        self.stdout.write('🔍 Analyse des doublons "Édition LOEWE"...')
        
        # Recherche de toutes les variations possibles
        loewe_variations = [
            'Édition Loewe',
            'Édition LOEWE',
            'Edition Loewe',
            'Edition LOEWE',
            'édition loewe',
            'edition loewe',
            'Édition Loewe ',
            ' Édition Loewe',
        ]
        
        # Recherche avec des requêtes insensibles à la casse
        all_loewe_colors = Color.objects.filter(
            Q(name__iexact='Édition Loewe') |
            Q(name__iexact='Edition Loewe') |
            Q(name__iexact='édition loewe') |
            Q(name__iexact='edition loewe')
        ).order_by('id')
        
        if not all_loewe_colors.exists():
            self.stdout.write('ℹ️ Aucune couleur "Édition LOEWE" trouvée dans la base de données')
            return
        
        self.stdout.write(f'🎯 {all_loewe_colors.count()} couleur(s) "Édition LOEWE" trouvée(s):')
        
        # Afficher toutes les variations trouvées
        for color in all_loewe_colors:
            self.stdout.write(f'  📌 ID {color.id}: "{color.name}" (Code: {color.code})')
            
            # Vérifier les références
            references = self._get_detailed_references(color)
            if references:
                self.stdout.write(f'    🔗 Références: {references}')
            else:
                self.stdout.write(f'    ℹ️ Aucune référence')
        
        # Identifier les doublons
        if all_loewe_colors.count() > 1:
            self.stdout.write('\n⚠️ DOUBLONS DÉTECTÉS!')
            
            # Garder la première couleur (la plus ancienne)
            primary_color = all_loewe_colors.first()
            duplicate_colors = all_loewe_colors.exclude(id=primary_color.id)
            
            self.stdout.write(f'\n📌 Couleur principale à conserver:')
            self.stdout.write(f'   ID {primary_color.id}: "{primary_color.name}" ({primary_color.code})')
            
            self.stdout.write(f'\n🗑️ Doublons à supprimer:')
            for duplicate in duplicate_colors:
                self.stdout.write(f'   ID {duplicate.id}: "{duplicate.name}" ({duplicate.code})')
                
                # Vérifier les références des doublons
                references = self._get_detailed_references(duplicate)
                if references:
                    self.stdout.write(f'     ⚠️ Références à migrer: {references}')
            
            if fix_mode:
                self.stdout.write('\n🔧 Correction automatique en cours...')
                self._fix_loewe_duplicates(primary_color, duplicate_colors)
            else:
                self.stdout.write('\n💡 Pour corriger automatiquement, utilisez: --fix')
        else:
            self.stdout.write('\n✅ Aucun doublon détecté pour "Édition LOEWE"')

    def _get_detailed_references(self, color):
        """Retourne les références détaillées à cette couleur"""
        references = []
        
        # Vérifier les téléphones
        phones = Phone.objects.filter(color=color)
        if phones.exists():
            phone_list = [f'"{p.model}" (ID: {p.id})' for p in phones[:3]]
            if phones.count() > 3:
                phone_list.append(f'... et {phones.count() - 3} autres')
            references.append(f'Téléphones: {", ".join(phone_list)}')
        
        # Vérifier les tissus
        fabrics = Fabric.objects.filter(color=color)
        if fabrics.exists():
            fabric_list = [f'"{f.product.title}" (ID: {f.id})' for f in fabrics[:3]]
            if fabrics.count() > 3:
                fabric_list.append(f'... et {fabrics.count() - 3} autres')
            references.append(f'Tissus: {", ".join(fabric_list)}')
        
        # Vérifier les vêtements
        clothing = Clothing.objects.filter(color=color)
        if clothing.exists():
            clothing_list = [f'"{c.product.title}" (ID: {c.id})' for c in clothing[:3]]
            if clothing.count() > 3:
                clothing_list.append(f'... et {clothing.count() - 3} autres')
            references.append(f'Vêtements: {", ".join(clothing_list)}')
        
        return ' | '.join(references) if references else None

    def _fix_loewe_duplicates(self, primary_color, duplicate_colors):
        """Corrige les doublons en migrant les références et supprimant les doublons"""
        from django.db import transaction
        
        with transaction.atomic():
            for duplicate in duplicate_colors:
                self.stdout.write(f'  🔄 Migration des références de ID {duplicate.id} vers ID {primary_color.id}...')
                
                # Migrer les références
                phones_updated = Phone.objects.filter(color=duplicate).update(color=primary_color)
                fabrics_updated = Fabric.objects.filter(color=duplicate).update(color=primary_color)
                
                # Migrer les vêtements (ManyToManyField)
                clothing_updated = 0
                clothing_with_old_color = Clothing.objects.filter(color=duplicate)
                for clothing in clothing_with_old_color:
                    clothing.color.add(primary_color)
                    clothing.color.remove(duplicate)
                    clothing_updated += 1
                
                if phones_updated or fabrics_updated or clothing_updated:
                    self.stdout.write(f'    ✅ {phones_updated} téléphone(s), {fabrics_updated} tissu(x), {clothing_updated} vêtement(s) migré(s)')
                
                # Supprimer le doublon
                duplicate.delete()
                self.stdout.write(f'    ✅ Doublon ID {duplicate.id} supprimé')
        
        self.stdout.write('\n✅ Correction des doublons "Édition LOEWE" terminée!') 