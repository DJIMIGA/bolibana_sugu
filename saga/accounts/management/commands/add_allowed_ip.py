from django.core.management.base import BaseCommand
from accounts.models import AllowedIP
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Ajoute une IP autorisée pour l\'accès à l\'administration'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='Adresse IP à autoriser')
        parser.add_argument('--description', type=str, default='Ajouté via commande', help='Description de l\'IP')
        parser.add_argument('--duration', type=int, default=30, help='Durée de validité en jours')
        parser.add_argument('--admin-email', type=str, help='Email de l\'administrateur qui ajoute l\'IP')

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        description = options['description']
        duration = options['duration']
        admin_email = options['admin_email']

        try:
            # Trouver l'administrateur
            if admin_email:
                admin_user = User.objects.get(email=admin_email, is_staff=True)
            else:
                # Utiliser le premier superutilisateur trouvé
                admin_user = User.objects.filter(is_superuser=True).first()
                if not admin_user:
                    self.stdout.write(self.style.ERROR('Aucun superutilisateur trouvé'))
                    return

            # Calculer la date d'expiration
            expires_at = timezone.now() + datetime.timedelta(days=duration)

            # Créer l'IP autorisée
            allowed_ip = AllowedIP.objects.create(
                ip_address=ip_address,
                description=description,
                is_active=True,
                expires_at=expires_at,
                added_by=admin_user
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'IP {ip_address} ajoutée avec succès. '
                    f'Expire le {expires_at.strftime("%Y-%m-%d %H:%M:%S")}'
                )
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Aucun utilisateur trouvé avec l\'email {admin_email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de l\'ajout de l\'IP: {str(e)}')
            ) 