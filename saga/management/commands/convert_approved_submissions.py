from django.core.management.base import BaseCommand
from price_checker.models import PriceSubmission, PriceEntry
from accounts.models import Shopper

class Command(BaseCommand):
    help = 'Convertir les PriceSubmission approuvées en PriceEntry'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la conversion même si des PriceEntry existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Conversion des soumissions approuvées en entrées de prix")
        self.stdout.write("=" * 50)
        
        # Récupérer les soumissions approuvées
        approved_submissions = PriceSubmission.objects.filter(status='APPROVED')
        
        if not approved_submissions.exists():
            self.stdout.write(
                self.style.WARNING("⚠️  Aucune soumission approuvée trouvée")
            )
            return
        
        self.stdout.write(f"📊 {approved_submissions.count()} soumissions approuvées trouvées")
        
        # Récupérer un utilisateur admin pour la validation
        admin_user = Shopper.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = Shopper.objects.first()
        
        if not admin_user:
            self.stdout.write(
                self.style.ERROR("❌ Aucun utilisateur trouvé pour la validation")
            )
            return
        
        created_count = 0
        skipped_count = 0
        
        for submission in approved_submissions:
            # Vérifier si une PriceEntry existe déjà pour cette soumission
            if PriceEntry.objects.filter(submission=submission).exists() and not options['force']:
                skipped_count += 1
                continue
            
            # Créer la PriceEntry
            try:
                price_entry = PriceEntry.objects.create(
                    product=submission.product,
                    city=submission.city,
                    price=submission.price,
                    currency='XOF',
                    supplier_name=submission.supplier_name,
                    supplier_phone=submission.supplier_phone,
                    supplier_address=submission.supplier_address,
                    proof_image=submission.proof_image,
                    user=submission.user,
                    submission=submission,
                    validated_by=admin_user,
                    is_active=True,
                    notes=""
                )
                created_count += 1
                self.stdout.write(
                    f"✅ Prix créé: {submission.product.title} - {submission.price} FCFA"
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur pour {submission.product.title}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Conversion terminée!")
        )
        self.stdout.write(f"📊 Résultats:")
        self.stdout.write(f"   - Entrées créées: {created_count}")
        self.stdout.write(f"   - Entrées ignorées: {skipped_count}")
        self.stdout.write(f"   - Total PriceEntry: {PriceEntry.objects.count()}") 