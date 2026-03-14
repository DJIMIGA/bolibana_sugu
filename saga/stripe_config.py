import stripe
from django.conf import settings

# Configuration de Stripe
stripe.api_version = settings.STRIPE_API_VERSION
stripe.api_key = settings.STRIPE_SECRET_KEY 