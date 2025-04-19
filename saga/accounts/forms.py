from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.forms import widgets

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
    class Meta:
        model = Shopper
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'type': 'text',
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'type': 'text',
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'type': 'email',
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Adresse E-mail'
            }),
            'phone_number': forms.TextInput(attrs={
                'type': 'tel',
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Numéro de téléphone'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Date de naissance'
            }),
            'password': forms.PasswordInput(attrs={
                'type': 'password',
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-yellow-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm',
                'placeholder': 'Mot de passe'
            }),
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
        return password  # Retournez le mot de passe non haché

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hache le mot de passe
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
    class Meta:
        model = Shopper
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth']
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
