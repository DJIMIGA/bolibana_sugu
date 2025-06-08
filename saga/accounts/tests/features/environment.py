from behave import fixture, use_fixture
from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import LoginTwoFactorCode

@fixture
def django_client(context):
    context.client = Client()
    yield context.client

def before_all(context):
    use_fixture(django_client, context)

def before_scenario(context, scenario):
    # Nettoyer la base de données avant chaque scénario
    get_user_model().objects.all().delete()
    LoginTwoFactorCode.objects.all().delete()

def after_scenario(context, scenario):
    # Nettoyer la base de données après chaque scénario
    get_user_model().objects.all().delete()
    LoginTwoFactorCode.objects.all().delete() 