from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from saga.accounts.models import AllowedIP
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Ajoute une IP à la liste des IPs autorisées pour l\'accès admin'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='Adresse IP à autoriser')
        parser.add_argument('--description', type=str, default='', help='Description de l\'IP')
        parser.add_argument('--days', type=int, default=30, help='Nombre de jours de validité (défaut: 30)')
        parser.add_argument('--admin-email', type=str, help='Email de l\'administrateur qui ajoute l\'IP')
        parser.add_argument('--force', action='store_true', help='Forcer la mise à jour si l\'IP existe déjà')

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        description = options['description'] or f'IP ajoutée le {timezone.now().strftime("%Y-%m-%d")}'
        days = options['days']
        admin_email = options['admin_email']
        force = options['force']

        # Récupérer l'utilisateur admin
        admin_user = None
        if admin_email:
            try:
                admin_user = User.objects.get(email=admin_email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Utilisateur avec l\'email {admin_email} non trouvé')
                )
                return

        # Vérifier si l'IP existe déjà
        try:
            existing_ip = AllowedIP.objects.get(ip_address=ip_address)
            if not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'L\'IP {ip_address} existe déjà. Utilisez --force pour la mettre à jour.'
                    )
                )
                return
            
            # Mise à jour de l'IP existante
            existing_ip.description = description
            existing_ip.is_active = True
            existing_ip.expires_at = timezone.now() + timedelta(days=days)
            existing_ip.added_by = admin_user
            existing_ip.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'IP {ip_address} mise à jour avec succès (valide jusqu\'au {existing_ip.expires_at.strftime("%Y-%m-%d")})'
                )
            )
        except AllowedIP.DoesNotExist:
            # Création d'une nouvelle IP
            expires_at = timezone.now() + timedelta(days=days)
            
            allowed_ip = AllowedIP.objects.create(
                ip_address=ip_address,
                description=description,
                is_active=True,
                expires_at=expires_at,
                added_by=admin_user
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'IP {ip_address} ajoutée avec succès (valide jusqu\'au {expires_at.strftime("%Y-%m-%d")})'
                )
            )

        # Afficher la liste des IPs actives
        self.stdout.write('\nIPs actuellement autorisées :')
        active_ips = AllowedIP.objects.filter(is_active=True, expires_at__gt=timezone.now())
        for ip in active_ips:
            status = '✅' if not ip.is_expired else '❌'
            self.stdout.write(f'{status} {ip.ip_address} - {ip.description} (expire: {ip.expires_at.strftime("%Y-%m-%d")})') 