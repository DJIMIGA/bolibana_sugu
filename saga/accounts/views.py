from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate, update_session_auth_hash
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.contrib.auth.views import LoginView as AuthLoginView
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user
from django_otp.decorators import otp_required
from django.utils.safestring import mark_safe
import qrcode
import base64
from io import BytesIO
User = get_user_model()

from .models import Shopper, ShippingAddress, TwoFactorCode, TOTPDevice
from .forms import UserForm, ShippingAddressForm, PasswordChangeForm, CustomPasswordResetForm, \
    CustomSetPasswordForm, LoginForm, TwoFactorVerificationForm, UpdateProfileForm
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from core.utils import track_user_registration, track_login, track_logout

# Import de la fonction de migration du panier
try:
    from cart.utils import migrate_anonymous_cart
except ImportError:
    # Fallback si l'import échoue
    def migrate_anonymous_cart(sender, request, user, **kwargs):
        pass

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    @ratelimit(key='ip', rate='2/m', method=['POST'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = Shopper.objects.filter(email=email).first()

        if user:
            code = TwoFactorCode.generate_code()
            reset_token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            TwoFactorCode.objects.filter(uidb64=uidb64).delete()
            TwoFactorCode.objects.update_or_create(
                user=user,
                defaults={'reset_token': reset_token, 'code': code, 'uidb64': uidb64}
            )

            context = {
                'email': user.email,
                'domain': self.request.META['HTTP_HOST'],
                'site_name': 'Votre Site',
                'uid': uidb64,
                'user': user,
                'token': reset_token,
                'code': code,
                'protocol': 'https' if self.request.is_secure() else 'http',
            }

            subject = render_to_string('password_reset_subject.txt', context)
            email_body = render_to_string(self.email_template_name, context)

            # Assurez-vous que toutes les variables sont présentes dans le contexte
            print('Contexte de l\'email:', context)  # Debug: Affiche le contexte complet
            print('Corps de l\'email:', email_body)  # Debug: Affiche le corps de l'email

            send_mail(
                subject.strip(),
                email_body,
                None,  # From email (utilisera DEFAULT_FROM_EMAIL des paramètres Django)
                [user.email],
                fail_silently=False,
            )
        else:
            print('Aucun utilisateur trouvé avec cet email:', email)  # Debug: Avertit si aucun utilisateur n'est trouvé

        return redirect(self.success_url)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get(self, request, *args, **kwargs):
        self.uidb64 = kwargs.get('uidb64')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.uidb64 = kwargs.get('uidb64')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        code = self.request.POST.get('code')
        print(f'Code entered: {code}')
        print(f'uidb64 used for search: {self.uidb64}')

        # Afficher tous les TwoFactorCode existants
        all_codes = TwoFactorCode.objects.all()
        print('All existing TwoFactorCodes:')
        for existing_code in all_codes:
            print(f'uidb64: {existing_code.uidb64}, code: {existing_code.code}, created_at: {existing_code.created_at}')

        # Recherche du TwoFactorCode
        two_factor_code = TwoFactorCode.objects.filter(
            uidb64=self.uidb64,
            code=code
        ).first()

        if two_factor_code:
            print('Found TwoFactorCode:')
            print(
                f'uidb64: {two_factor_code.uidb64}, code: {two_factor_code.code}, created_at: {two_factor_code.created_at}')

            if two_factor_code.is_valid():
                print('Code is valid, proceeding with password change')
                user = form.save()
                two_factor_code.delete()
                print('Password changed successfully')
                return super().form_valid(form)
            else:
                print(f'Code has expired. Created at: {two_factor_code.created_at}, Current time: {timezone.now()}')
                messages.error(self.request, "Le code a expiré.")
        else:
            print('No TwoFactorCode found')
            # Recherche séparée pour uidb64 et code
            uidb64_match = TwoFactorCode.objects.filter(uidb64=self.uidb64).exists()
            code_match = TwoFactorCode.objects.filter(code=code).exists()
            print(f'uidb64 match exists: {uidb64_match}')
            print(f'code match exists: {code_match}')

            if not uidb64_match:
                messages.error(self.request, "Lien de réinitialisation invalide.")
            elif not code_match:
                messages.error(self.request, "Code invalide.")
            else:
                messages.error(self.request, "Combinaison uidb64 et code invalide.")

        return self.form_invalid(form)


@ratelimit(key='ip', rate='3/m', method=['POST'])
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Sauvegarder la clé de session anonyme avant login
            old_session_key = request.session.session_key
            if not old_session_key:
                request.session.save()
                old_session_key = request.session.session_key
            user = form.save()
            login(request, user)
            
            # Tracking de l'inscription
            track_user_registration(request, method='email', source='website')
            
            # Migrer le panier anonyme vers le compte utilisateur
            try:
                migrate_anonymous_cart(None, request, user, old_session_key=old_session_key)
            except Exception as e:
                print(f"⚠️ Erreur lors de la migration du panier: {str(e)}")
            # Ajouter un message informatif sur la 2FA
            messages.info(
                request,
                mark_safe(
                    "Bienvenue sur BoliBana! Pour renforcer la sécurité de votre compte, "
                    "nous vous recommandons d'activer l'authentification à deux facteurs (2FA). "
                    "<a href='{}' class='font-semibold underline hover:text-yellow-800'>Cliquez ici pour l'activer</a>."
                    .format(reverse('accounts:setup_2fa'))
                )
            )
            return redirect('suppliers:supplier_index')
    else:
        form = UserForm()

    return render(request, 'accounts/signup.html', {'form': form})


class LoginView(AuthLoginView):
    """
    Vue de connexion avec support 2FA.
    
    Cette vue étend AuthLoginView pour gérer l'authentification à deux facteurs.
    
    Flux:
    1. Vérifie les identifiants via le formulaire
    2. Si 2FA activée:
       - Stocke l'ID utilisateur en session
       - Redirige vers la vérification 2FA
    3. Sinon:
       - Connecte directement l'utilisateur
       - Suggère l'activation de la 2FA
       - Redirige vers le profil
    """
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        """
        Gère la validation du formulaire de connexion.
        
        Args:
            form: Le formulaire de connexion validé
            
        Returns:
            HttpResponse: Redirection vers la vérification 2FA ou le profil
        """
        user = form.get_user()
        if user.has_2fa_enabled():
            # Stocker l'ID utilisateur en session pour la vérification 2FA
            self.request.session['2fa_user_id'] = user.id
            return redirect('accounts:verify_2fa')
        else:
            # Sauvegarder la clé de session anonyme avant login
            old_session_key = self.request.session.session_key
            if not old_session_key:
                self.request.session.save()
                old_session_key = self.request.session.session_key
            auth_login(self.request, user)
            
            # Tracking de la connexion
            track_login(self.request, method='email', source='website')
            
            # Migrer le panier anonyme vers le compte utilisateur
            try:
                migrate_anonymous_cart(None, self.request, user, old_session_key=old_session_key)
            except Exception as e:
                print(f"⚠️ Erreur lors de la migration du panier: {str(e)}")
            
            # Suggérer l'activation de la 2FA
            messages.info(
                self.request,
                mark_safe(
                "Pour renforcer la sécurité de votre compte, nous vous recommandons d'activer l'authentification à deux facteurs (2FA)."
                "<a href='{}' class='font-semibold underline hover:text-yellow-800'>Cliquez ici pour l'activer</a>."
                .format(reverse('accounts:setup_2fa'))
                )
            )
            return redirect('suppliers:supplier_index')


def logout_user(request):
    # Tracking de la déconnexion
    track_logout(request)
    
    logout(request)
    return redirect('suppliers:supplier_index')


@login_required
def profile(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    if request.method == "POST":
        request.user.email = request.POST.get("email")
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.phone_number = request.POST.get("phone_number")
        request.user.date_of_birth = request.POST.get("date_of_birth")
        request.user.save()

    return render(request, 'profile.html', context={"addresses": addresses, "default_address": default_address})


@login_required
def update_profile(request):
    old_email = request.user.email
    if request.method == "POST":
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(email=old_email, password=password)
            if user is not None:
                new_email = form.cleaned_data.get('email')
                if new_email != request.user.email:
                    if Shopper.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                        form.add_error('email', "Cet email est déjà utilisé.")
                        messages.error(request, "Cet email est déjà utilisé.")
                        return render(request, 'update_profile.html', {'form': form})

                # Sauvegarde des modifications
                updated_user = form.save(commit=False)
                updated_user.email = new_email
                updated_user.phone = form.cleaned_data.get('phone')
                updated_user.save()

                messages.success(request, 'Les modifications ont été apportées avec succès.')
                return redirect("accounts:profile")
            else:
                form.add_error('password', "Mot de passe invalide")
                messages.error(request, "Mot de passe invalide")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})


@ratelimit(key='ip', rate='5/m', method=['POST'])
def edit_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            request.user.set_password(new_password)  # ✅ Change le mot de passe
            request.user.save()

            update_session_auth_hash(request, request.user)  # ✅ Garde l'utilisateur connecté après le changement

            messages.success(request, "Votre mot de passe a été mis à jour avec succès !")
            return redirect("accounts:profile")  # 🔄 Redirection vers la page du profil
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "edit_password.html", {"form": form})


@login_required
def manage_addresses(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    # Vérifier quelles adresses sont utilisées par des commandes
    from cart.models import Order
    addresses_with_orders = {}
    for address in addresses:
        orders_count = Order.objects.filter(shipping_address=address).count()
        if orders_count > 0:
            addresses_with_orders[address.id] = orders_count

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            print(address)
            address.user = request.user
            address.save()
            messages.success(request, "Adresse ajoutée avec succès ! ✅")  # ✅ Succès
            return redirect('accounts:manage_addresses')
        else:
            messages.error(request,
                           "Erreur lors de l'ajout de l'adresse. Veuillez vérifier le formulaire. ❌")  # ❌ Erreur

    else:
        form = ShippingAddressForm()

    return render(request, 'addresses.html', {
        "form": form,
        "addresses": addresses,
        "default_address": default_address,
        "addresses_with_orders": addresses_with_orders
    })


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    if request.method == "POST":
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Adresse modifiée avec succès ! ✅")  # ✅ Succès
            return redirect('accounts:manage_addresses')
        else:
            messages.error(request,
                           "Erreur lors de la modification de l'adresse. Veuillez vérifier le formulaire. ❌")  # ❌ Erreur
    else:
        form = ShippingAddressForm(instance=address)
    return render(request, 'edit_address.html', {"form": form, "address": address})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    # Vérifier si l'adresse est utilisée par des commandes
    from cart.models import Order
    orders_using_address = Order.objects.filter(shipping_address=address)
    
    if orders_using_address.exists():
        # L'adresse est utilisée par des commandes
        orders_count = orders_using_address.count()
        messages.error(request, f"❌ **Impossible de supprimer cette adresse** : Elle est utilisée par {orders_count} commande(s). Pour des raisons de sécurité, les adresses liées à des commandes ne peuvent pas être supprimées.")
        return redirect('accounts:manage_addresses')
    
    # Vérifier si c'est l'adresse par défaut
    if address.is_default:
        # Si c'est l'adresse par défaut, vérifier s'il y a d'autres adresses
        other_addresses = ShippingAddress.objects.filter(user=request.user).exclude(id=address_id)
        if not other_addresses.exists():
            messages.error(request, "❌ **Impossible de supprimer cette adresse** : C'est votre seule adresse. Vous devez avoir au moins une adresse de livraison.")
            return redirect('accounts:manage_addresses')
    
    # Supprimer l'adresse
    address.delete()
    messages.success(request, "Adresse supprimée avec succès ! ✅")
    return redirect('accounts:manage_addresses')


@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    # Mettre à jour toutes les autres adresses comme non par défaut
    ShippingAddress.objects.filter(user=request.user).update(is_default=False)
    # Définir la nouvelle adresse par défaut
    address.is_default = True
    address.save()
    return redirect('accounts:manage_addresses')


def setup_2fa(request):
    """Vue pour configurer la 2FA."""
    if not request.user.is_authenticated:
        if '2fa_user_id' not in request.session:
            return redirect('accounts:login')
        user = get_object_or_404(Shopper, id=request.session['2fa_user_id'])
    else:
        user = request.user
    
    # Récupérer l'appareil TOTP existant
    device = TOTPDevice.objects.filter(user=user).first()
    
    if request.method == 'POST':
        if 'disable' in request.POST and device and device.confirmed:
            # Désactivation de la 2FA
            token = request.POST.get('token', '').strip()
            if not token:
                messages.error(request, 'Veuillez entrer un code de vérification.')
                return redirect('accounts:setup_2fa')
            
            if device.verify_token(token):
                device.delete()
                messages.success(request, 'La 2FA a été désactivée avec succès.')
                return redirect('suppliers:supplier_index')
            else:
                messages.error(request, 'Code invalide. Veuillez réessayer.')
                return redirect('accounts:setup_2fa')
        
        elif 'enable' in request.POST:
            # Activation de la 2FA
            if not device:
                device = TOTPDevice.objects.create(user=user, name='default', confirmed=False)
            
            token = request.POST.get('token', '').strip()
            if not token:
                messages.error(request, 'Veuillez entrer un code de vérification.')
                return redirect('accounts:setup_2fa')
            
            if device.verify_token(token):
                device.confirmed = True
                device.save()
                messages.success(request, 'La 2FA a été activée avec succès.')
                if not request.user.is_authenticated:
                    auth_login(request, user)
                return redirect('suppliers:supplier_index')
            else:
                messages.error(request, 'Code invalide. Veuillez réessayer.')
                return redirect('accounts:setup_2fa')
    
    # Si pas d'appareil non confirmé, on en crée un nouveau
    if not device:
        device = TOTPDevice.objects.create(user=user, name='default', confirmed=False)
    
    # Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(device.config_url)
    qr.make(fit=True)
    
    # Créer l'image du QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir l'image en base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    # Préparation du contexte pour le template
    context = {
        'device': device,
        'qr_code': f'data:image/png;base64,{qr_code}',  # QR code en base64
        'is_2fa_enabled': device.confirmed if device else False,
    }
    
    return render(request, 'accounts/2fa_setup.html', context)

@staff_member_required
def admin_2fa_required(request):
    """Vue intermédiaire pour la vérification 2FA."""
    if not request.user.is_authenticated:
        return redirect('admin_login')
        
    if not request.user.is_staff:
        return redirect('suppliers:supplier_index')
        
    # Vérifier si l'utilisateur a la 2FA activée
    if not request.user.has_2fa_enabled():
        messages.warning(request, mark_safe(
            "Vous devez activer l'authentification à deux facteurs pour accéder à l'administration. "
            "<a href='{}' class='font-semibold underline hover:text-yellow-800'>Cliquez ici pour l'activer</a>."
            .format(reverse('accounts:setup_2fa'))
        ))
        return redirect('setup_2fa')
    
    # Si l'utilisateur n'est pas vérifié, afficher la page de vérification
    if not request.user.is_verified():
        if request.method == 'POST':
            token = request.POST.get('token')
            device = request.user.get_totp_device()
            if device.verify_token(token):
                request.user.is_verified = True
                request.user.save()
                return redirect('admin:index')
            else:
                messages.error(request, mark_safe(
                    "Code invalide. Veuillez réessayer ou "
                    "<a href='{}' class='font-semibold underline hover:text-yellow-800'>demander un nouveau code</a>."
                    .format(reverse('accounts:resend_2fa_code'))
                ))
        return render(request, 'admin/2fa_verify.html')
    
    return redirect('admin:index')

def verify_2fa(request):
    """Vue pour la vérification 2FA."""
    if '2fa_user_id' not in request.session:
        return redirect('accounts:login')
    
    user = get_object_or_404(Shopper, id=request.session['2fa_user_id'])
    device = user.get_totp_device()
    
    if device and not device.confirmed:
            return redirect('accounts:setup_2fa')
    
    if request.method == 'POST':
        token = request.POST.get('token')
        
        if user.verify_2fa_code(token):
            # Sauvegarder la clé de session anonyme avant login
            old_session_key = request.session.session_key
            if not old_session_key:
                request.session.save()
                old_session_key = request.session.session_key
            auth_login(request, user)
            user.set_verified(True)
            
            # Migrer le panier anonyme vers le compte utilisateur
            try:
                migrate_anonymous_cart(None, request, user, old_session_key=old_session_key)
            except Exception as e:
                print(f"⚠️ Erreur lors de la migration du panier: {str(e)}")
            
            if '2fa_user_id' in request.session:
                del request.session['2fa_user_id']
            return redirect('suppliers:supplier_index')
        else:
            messages.error(request, mark_safe(
                "Code invalide. Veuillez réessayer ou "
                "<a href='{}' class='font-semibold underline hover:text-yellow-800'>demander un nouveau code</a>."
                .format(reverse('accounts:resend_2fa_code'))
            ))
    
    return render(request, 'accounts/2fa_verify.html')

def resend_2fa_code(request):
    if '2fa_user_id' not in request.session:
        return redirect('accounts:login')
    
    user = get_object_or_404(Shopper, id=request.session['2fa_user_id'])
    
    # Générer et envoyer un nouveau code
    code = TwoFactorCode.generate_code()
    TwoFactorCode.objects.filter(user=user).delete()
    TwoFactorCode.objects.create(user=user, code=code)
    
    # Envoyer le code par SMS (à implémenter avec votre service SMS)
    # send_sms(user.phone, f"Votre nouveau code de vérification est : {code}")
    
    messages.success(request, "Un nouveau code a été envoyé à votre téléphone.")
    return redirect('accounts:verify_2fa')
