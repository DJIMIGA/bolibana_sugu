from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone


class Command(BaseCommand):
    help = 'Teste la configuration email de SagaKore'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Adresse email de destination pour le test',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 === TEST DE CONFIGURATION EMAIL ===')
        )
        
        # Afficher la configuration actuelle
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Non configuré')}")
        self.stdout.write(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non configuré')}")
        self.stdout.write(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Non configuré')}")
        self.stdout.write(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Non configuré')}")
        self.stdout.write(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Non configuré')}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'Configuré' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Non configuré'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré')}")
        
        # Demander l'email de test si pas fourni
        test_email = options['email']
        if not test_email:
            test_email = input("\n📧 Entrez votre adresse email pour le test: ").strip()
        
        if not test_email:
            self.stdout.write(
                self.style.ERROR('❌ Aucune adresse email fournie')
            )
            return
        
        try:
            # Préparer le contexte pour le template
            context = {
                'backend': getattr(settings, 'EMAIL_BACKEND', 'Non configuré'),
                'host': getattr(settings, 'EMAIL_HOST', 'Non configuré'),
                'port': getattr(settings, 'EMAIL_PORT', 'Non configuré'),
                'tls': getattr(settings, 'EMAIL_USE_TLS', 'Non configuré'),
                'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré'),
                'test_date': timezone.now().strftime("%d/%m/%Y à %H:%M")
            }
            
            # Rendre le template HTML
            html_message = render_to_string('cart/emails/test_email.html', context)
            plain_message = strip_tags(html_message)
            
            # Envoyer l'email de test
            subject = "🧪 Test de configuration email - SagaKore"
            
            self.stdout.write(f"📤 Envoi de l'email de test à {test_email}...")
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [test_email],
                html_message=html_message,
                fail_silently=False
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Email de test envoyé avec succès !')
            )
            self.stdout.write('📧 Vérifiez votre boîte de réception (et les spams)')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'envoi de l\'email de test:')
            )
            self.stdout.write(f"   Type d'erreur: {type(e).__name__}")
            self.stdout.write(f"   Message: {str(e)}")
            
            # Conseils selon le type d'erreur
            if "SMTPAuthenticationError" in str(type(e)):
                self.stdout.write(
                    self.style.WARNING('\n🔧 SOLUTIONS POSSIBLES:')
                )
                self.stdout.write("1. Vérifiez que EMAIL_HOST_USER est correct")
                self.stdout.write("2. Vérifiez que EMAIL_HOST_PASSWORD est le mot de passe d'application Gmail")
                self.stdout.write("3. Assurez-vous que l'authentification à 2 facteurs est activée sur Gmail")
                self.stdout.write("4. Générez un nouveau mot de passe d'application dans les paramètres Google")
            elif "SMTPConnectError" in str(type(e)):
                self.stdout.write(
                    self.style.WARNING('\n🔧 SOLUTIONS POSSIBLES:')
                )
                self.stdout.write("1. Vérifiez votre connexion internet")
                self.stdout.write("2. Vérifiez que EMAIL_HOST et EMAIL_PORT sont corrects")
                self.stdout.write("3. Vérifiez que le pare-feu n'empêche pas la connexion")
            elif "SMTPServerDisconnected" in str(type(e)):
                self.stdout.write(
                    self.style.WARNING('\n🔧 SOLUTIONS POSSIBLES:')
                )
                self.stdout.write("1. Vérifiez la configuration SMTP")
                self.stdout.write("2. Essayez de redémarrer l'application")
            elif "SMTPRecipientsRefused" in str(type(e)):
                self.stdout.write(
                    self.style.WARNING('\n🔧 SOLUTIONS POSSIBLES:')
                )
                self.stdout.write("1. Vérifiez que l'adresse email de destination est valide")
                self.stdout.write("2. Vérifiez que l'adresse email n'est pas bloquée")
        
        # Afficher l'aide
        self.stdout.write(
            self.style.SUCCESS('\n📚 === GUIDE DE CONFIGURATION EMAIL ===')
        )
        self.stdout.write("Pour configurer l'envoi d'emails avec Gmail:")
        self.stdout.write()
        self.stdout.write("1. 🛡️ Activez l'authentification à 2 facteurs sur votre compte Gmail")
        self.stdout.write("2. 🔑 Générez un mot de passe d'application:")
        self.stdout.write("   - Allez dans les paramètres Google")
        self.stdout.write("   - Sécurité > Authentification à 2 facteurs")
        self.stdout.write("   - Mots de passe d'application > Générer")
        self.stdout.write("3. 📝 Créez un fichier .env à la racine du projet avec:")
        self.stdout.write("   EMAIL_HOST_USER=votre-email@gmail.com")
        self.stdout.write("   EMAIL_HOST_PASSWORD=votre-mot-de-passe-app")
        self.stdout.write("4. 🔄 Redémarrez l'application Django")
        self.stdout.write()
        self.stdout.write(
            self.style.WARNING("⚠️  IMPORTANT: N'utilisez PAS votre mot de passe Gmail normal!")
        )
        self.stdout.write("   Utilisez UNIQUEMENT le mot de passe d'application généré.") 