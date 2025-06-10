from behave import given, when, then
from django.urls import reverse
from accounts.models import Shopper, TOTPDevice
from django.contrib import messages
import time

@given('un utilisateur avec email "{email}" et mot de passe "{password}"')
def step_impl(context, email, password):
    context.user = Shopper.objects.create_user(
        email=email,
        password=password,
        phone_number='+33612345678'
    )
    context.device = TOTPDevice.objects.create(user=context.user, name='default')
    context.device.confirmed = True
    context.device.save()

@when('je me connecte avec email "{email}" et mot de passe "{password}"')
def step_impl(context, email, password):
    context.response = context.client.post(reverse('accounts:login'), {
        'username': email,
        'password': password
    })

@when('je saisis le code 2FA valide')
def step_impl(context):
    token = context.device.generate_token()
    context.verify_response = context.client.post(reverse('accounts:verify_2fa'), {
        'token': token
    })

@when('je saisis un code 2FA invalide')
def step_impl(context):
    context.verify_response = context.client.post(reverse('accounts:verify_2fa'), {
        'token': '000000'
    })

@then('je suis redirigé vers la page de vérification 2FA')
def step_impl(context):
    assert context.response.status_code == 302
    assert context.response.url == reverse('accounts:verify_2fa')

@then('je suis connecté avec succès')
def step_impl(context):
    assert context.verify_response.status_code == 302
    assert context.verify_response.url == reverse('profile')
    assert context.verify_response.wsgi_request.user.is_authenticated

@then('je reste sur la page de connexion')
def step_impl(context):
    assert context.response.status_code == 200
    assert not context.response.wsgi_request.user.is_authenticated

@then('je vois un message d\'erreur pour le code 2FA')
def step_impl(context):
    assert context.verify_response.status_code == 200
    assert not context.verify_response.wsgi_request.user.is_authenticated
    assert "Code invalide" in context.verify_response.content.decode() 