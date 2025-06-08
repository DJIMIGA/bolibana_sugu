from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.forms import widgets
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField

from .models import Shopper, ShippingAddress
from django.utils.translation import gettext_lazy as _
import re
from .utils.validators import validate_password


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe actuel")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nouveau mot de passe")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le nouveau mot de passe")

    def __init__(self, user, *args, **kwargs):
        """ Associe l'utilisateur à l'instance du formulaire """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """ Vérifie si le mot de passe actuel est correct """
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_("Mot de passe actuel invalide."))
        return current_password

    def clean_new_password(self):
        """ Vérifie la sécurité du nouveau mot de passe """
        password = self.cleaned_data.get('new_password')
        validate_password(password)
        return password

    def clean(self):
        """ Vérifie si les deux nouveaux mots de passe correspondent """
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', _("Les nouveaux mots de passe ne correspondent pas."))

        return cleaned_data


class UserForm(forms.ModelForm):
    phone_country = forms.CharField(
        initial='+223',
        label="Pays",
        widget=forms.TextInput(attrs={
            'class': 'block w-1/4 pl-3 pr-2 py-2 text-base border-gray-300 bg-gray-50 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-l-md',
            'readonly': 'readonly'
        })
    )
    phone_number = forms.CharField(
        label="Numéro",
        widget=forms.TextInput(attrs={
            'class': 'appearance-none rounded-r-md relative block w-3/4 px-3 py-2 border border-yellow-300 placeholder-yellow-400 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
            'placeholder': 'Ex: 72464294'
        }),
        required=False
    )

    class Meta:
        model = Shopper
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse email',
            'password': 'Mot de passe'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'type': 'text',
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-yellow-300 placeholder-yellow-400 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Ex: Konimba'
            }),
            'last_name': forms.TextInput(attrs={
                'type': 'text',
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-yellow-300 placeholder-yellow-400 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Ex: Djimiga'
            }),
            'email': forms.EmailInput(attrs={
                'type': 'email',
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-yellow-300 placeholder-yellow-400 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Ex: bolibanasugu@gmail.com'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-yellow-300 placeholder-yellow-400 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Minimum 8 caractères'
            })
        }

  

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = True
        self.fields['password'].label = "Mot de passe"
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'type': 'password',
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
            'placeholder': 'Mot de passe'
        })

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
        'placeholder': 'Adresse E-mail'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
        'placeholder': 'Mot de passe'
    }))


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'address_type', 'quarter', 'street_address', 'city', 'additional_info', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'type': 'text'}),
            'address_type': forms.Select(attrs={'type': 'text'}),
            'quarter': forms.TextInput(attrs={'type': 'text'}),
            'street_address': forms.TextInput(attrs={'type': 'text'}),
            'city': forms.Select(attrs={'type': 'text'}),
            'is_default': forms.CheckboxInput(attrs={'type': 'checkbox'}),
        }


class TwoFactorForm(forms.Form):
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={"placeholder": "Code à 6 chiffres"}))


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'Adresse e-mail'}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Nouveau mot de passe'}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Confirmer le mot de passe'}),
    )


class UpdateProfileForm(forms.ModelForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial='ML',
            attrs={
                'class': 'w-full pl-10 px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200',
                'placeholder': 'Numéro de téléphone'
            }
        ),
        required=False
    )

    class Meta:
        model = Shopper
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full pl-10 px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.date_of_birth:
            # Formatage de la date pour l'affichage
            self.initial['date_of_birth'] = self.instance.date_of_birth.strftime('%Y-%m-%d')


class TwoFactorVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
            'placeholder': 'Code de vérification',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric'
        })
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError("Le code doit contenir exactement 6 chiffres.")
        return code
