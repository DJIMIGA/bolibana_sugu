from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from cloudinary.models import CloudinaryField
# Create your models here.
from django.db import models



SUPPLIER_SPECIALTY_CHOICES = [
    ('Fournisseur de TELEPHONE', 'Fournisseur de TELEPHONE'),
    ('Fournisseur de TELEVISION', 'Fournisseur de TELEVISION'),

]


class Supplier(models.Model):
    phone = PhoneNumberField(null=True, blank=True, region='ML')
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)
    specialty = models.CharField(max_length=100, choices=SUPPLIER_SPECIALTY_CHOICES)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']
        

