from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate, update_session_auth_hash
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
User = get_user_model()

from .models import Shopper, ShippingAddress, TwoFactorCode
from .forms import UserForm, ShippingAddressForm, PasswordChangeForm, CustomPasswordResetForm, \
    CustomSetPasswordForm, LoginForm
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

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


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('supplier_index')
    else:
        form = UserForm()

    return render(request, 'accounts/signup.html', {'form': form})


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('supplier_index')

    def form_valid(self, form):
        # Utilisé auth_login qui déclenche correctement le signal user_logged_in
        auth_login(self.request, form.get_user())
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Email ou mot de passe incorrect.")
        return super().form_invalid(form)

    def get_success_url(self):
        #Ajouté la gestion du paramètre next pour la redirection après connexion
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()


def logout_user(request):
    logout(request)
    return redirect('supplier_index')


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


def update_profile(request):
    old_email = request.user.email
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
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
                updated_user.email = new_email  # Assurez-vous que l'email est mis à jour
                updated_user.save()

                messages.success(request, 'Les modifications ont été apportées avec succès.')
                return redirect("profile")
            else:
                form.add_error('password', "Mot de passe invalide")
                messages.error(request, "Mot de passe invalide")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")
    else:
        form = UserForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})


@ratelimit(key='user', rate='5/m', method=['POST'])
def edit_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            request.user.set_password(new_password)  # ✅ Change le mot de passe
            request.user.save()

            update_session_auth_hash(request, request.user)  # ✅ Garde l'utilisateur connecté après le changement

            messages.success(request, "Votre mot de passe a été mis à jour avec succès !")
            return redirect("profile")  # 🔄 Redirection vers la page du profil
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "edit_password.html", {"form": form})


@login_required
def manage_addresses(request):
    addresses = ShippingAddress.objects.filter(user=request.user, is_default=False)
    addresses_with_default = ShippingAddress.objects.filter(user=request.user)
    default_address = addresses_with_default.filter(is_default=True).first()

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            print(address)
            address.user = request.user
            address.save()
            messages.success(request, "Adresse ajoutée avec succès ! ✅")  # ✅ Succès
            return redirect('manage_addresses')
        else:
            messages.error(request,
                           "Erreur lors de l'ajout de l'adresse. Veuillez vérifier le formulaire. ❌")  # ❌ Erreur

    else:
        form = ShippingAddressForm()

    return render(request, 'addresses.html', {
        "form": form,
        "addresses": addresses,
        "default_address": default_address
    })


def edit_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    if request.method == "POST":
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Adresse modifiée avec succès ! ✅")  # ✅ Succès
            return redirect('manage_addresses')
        else:
            messages.error(request,
                           "Erreur lors de la modification de l'adresse. Veuillez vérifier le formulaire. ❌")  # ❌ Erreur
    else:
        form = ShippingAddressForm(instance=address)
    return render(request, 'edit_address.html', {"form": form, "address": address})


def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Adresse supprimée avec succès ! ✅")  # ✅ Succès
    return redirect("manage_addresses")


@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    return redirect("manage_addresses")
