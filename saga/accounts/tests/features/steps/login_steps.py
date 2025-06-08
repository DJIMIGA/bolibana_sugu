from behave import given, when, then
from django.urls import reverse
from accounts.models import Shopper, LoginTwoFactorCode
from django.utils import timezone
from datetime import timedelta

@given('un utilisateur avec email "{email}" et mot de passe "{password}"')
def step_impl(context, email, password):
    context.user = Shopper.objects.create_user(
        email=email,
        password=password,
        phone='+33612345678'
    )

@when('je me connecte avec email "{email}" et mot de passe "{password}"')
def step_impl(context, email, password):
    context.response = context.client.post(
        reverse('accounts:login'),
        {
            'username': email,
            'password': password
        }
    )

@then('je suis redirigé vers la page de vérification 2FA')
def step_impl(context):
    assert context.response.status_code == 302
    assert 'verify-2fa' in context.response.url

@when('j\'entre le code de vérification "{code}"')
def step_impl(context, code):
    context.verify_response = context.client.post(
        reverse('accounts:verify_2fa'),
        {'code': code}
    )

@then('je suis connecté et redirigé vers la page d\'accueil')
def step_impl(context):
    assert context.verify_response.status_code == 302
    assert 'supplier_index' in context.verify_response.url
    assert context.verify_response.wsgi_request.user.is_authenticated

@then('je vois un message d\'erreur "{message}"')
def step_impl(context, message):
    from django.contrib import messages
    messages_list = list(messages.get_messages(context.verify_response.wsgi_request))
    assert any(message in str(msg) for msg in messages_list)

@given('le code 2FA a expiré')
def step_impl(context):
    two_factor_code = LoginTwoFactorCode.objects.filter(user=context.user).first()
    if two_factor_code:
        two_factor_code.created_at = timezone.now() - timedelta(minutes=6)
        two_factor_code.save() 