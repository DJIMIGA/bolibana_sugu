from django.db import models

# Create your models here.
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='suppliers_images')
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return self.name