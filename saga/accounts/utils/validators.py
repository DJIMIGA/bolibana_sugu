# accounts/utils/validators.py

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_password(password):
    if len(password) < 8:
        raise ValidationError(_("Le mot de passe doit contenir au moins 8 caractères."))

    if not re.search(r"[A-Z]", password):
        raise ValidationError(_("Le mot de passe doit contenir au moins une lettre majuscule."))

    if not re.search(r"[a-z]", password):
        raise ValidationError(_("Le mot de passe doit contenir au moins une lettre minuscule."))

    if not re.search(r"\d", password):
        raise ValidationError(_("Le mot de passe doit contenir au moins un chiffre."))

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError(_("Le mot de passe doit contenir au moins un caractère spécial."))


