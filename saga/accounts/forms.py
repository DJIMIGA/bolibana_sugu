from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.forms import widgets
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField

from .models import Shopper, ShippingAddress
from django.utils.translation import gettext_lazy as _
import re
from .utils.validators import validate_password


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors duration-200',
            'placeholder': 'Mot de passe actuel',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false'
        }),
        label="Mot de passe actuel"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors duration-200',
            'placeholder': 'Nouveau mot de passe',
            'autocomplete': 'new-password'
        }),
        label="Nouveau mot de passe"
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors duration-200',
            'placeholder': 'Confirmer le nouveau mot de passe',
            'autocomplete': 'new-password'
        }),
        label="Confirmer le nouveau mot de passe"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        # Ne pas pré-remplir le mot de passe actuel
        self.fields['current_password'].initial = None
        # Ajouter les classes CSS pour le style
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors duration-200'
            })

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
            'class': 'block w-24 pl-3 pr-2 py-2 border border-gray-300 bg-gray-50 rounded-l-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm',
            'readonly': 'readonly',
            'aria-label': 'Préfixe pays'
        })
    )
    phone_number = forms.CharField(
        label="Numéro",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 border-l-0 rounded-r-md placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
            'placeholder': 'Ex: 72464294',
            'aria-label': 'Numéro de téléphone'
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
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-yellow-300 placeholder-yellow-400 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
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


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
        'placeholder': 'Adresse E-mail'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
        'placeholder': 'Mot de passe'
    }))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].label = 'Email'


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
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200',
                'placeholder': 'Mot de passe actuel',
                'autocomplete': 'new-password'
            }
        ),
        required=True,
        help_text="Entrez votre mot de passe actuel pour confirmer les modifications"
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200',
                'placeholder': 'ex: 72464294'
            }
        ),
        required=False
    )

    class Meta:
        model = Shopper
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']
        exclude = ['country']
        widgets = {
            'date_of_birth': forms.DateInput(
                format='%d/%m/%Y',
                attrs={
                    'type': 'text',
                    'class': 'w-full pl-10 px-4 py-3 rounded-xl border-gray-200 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200',
                    'pattern': '[0-9]{2}/[0-9]{2}/[0-9]{4}',
                    'placeholder': 'jj/mm/aaaa'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ne pas pré-remplir le mot de passe
        self.fields['password'].initial = None
        # Gérer la date de naissance
        if self.instance and self.instance.date_of_birth:
            self.initial['date_of_birth'] = self.instance.date_of_birth.strftime('%d/%m/%Y')
        # Forcer le format d'entrée jj/mm/aaaa côté formulaire
        if 'date_of_birth' in self.fields:
            self.fields['date_of_birth'].input_formats = ['%d/%m/%Y']


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
