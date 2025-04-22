from django.db import models
from django.contrib.auth.models import User

class Saga(models.Model):
    """
    Modèle représentant une saga dans l'application.
    """
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Saga"
        verbose_name_plural = "Sagas"
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.titre 