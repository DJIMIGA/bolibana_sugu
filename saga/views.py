"""
Vues de l'application saga
"""
from django.shortcuts import render
from .models import Saga

def index(request):
    """
    Vue principale de l'application saga
    """
    sagas = Saga.objects.all()
    return render(request, 'saga/index.html', {'sagas': sagas}) 