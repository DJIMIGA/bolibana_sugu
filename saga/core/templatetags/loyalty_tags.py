from django import template

register = template.Library()

@register.filter
def get_username_from_email(email):
    """
    Extrait le nom d'utilisateur de l'email (partie avant @)
    """
    if email and '@' in email:
        return email.split('@')[0].title()
    return email or 'Utilisateur'

@register.filter
def format_loyalty_number(number):
    """
    Formate le numéro de fidélité avec des espaces
    """
    if number:
        # Ajouter des espaces tous les 4 caractères
        return ' '.join([number[i:i+4] for i in range(0, len(number), 4)])
    return number 