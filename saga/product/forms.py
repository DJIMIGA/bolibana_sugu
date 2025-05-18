from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Product, Phone, Category, Color, Review
from django.core.exceptions import ValidationError


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4})
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'description',
            'price',
            'category',
            'supplier',
            'brand',
            'is_available',
            'sku',
            'stock',
            'specifications',
            'weight',
            'dimensions',
            'image',
            'image_urls'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'specifications': forms.Textarea(attrs={'rows': 4}),
            'image_urls': forms.HiddenInput()
        }


class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [
            'brand', 'model', 'operating_system', 'screen_size', 'resolution',
            'processor', 'battery_capacity', 'camera_main', 'camera_front',
            'network', 'warranty', 'imei', 'is_new', 'box_included',
            'accessories', 'storage', 'ram', 'color'
        ]
        widgets = {
            'screen_size': forms.NumberInput(attrs={'step': '0.1'}),
            'storage': forms.NumberInput(attrs={'min': 1}),
            'ram': forms.NumberInput(attrs={'min': 1}),
            'accessories': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        model = cleaned_data.get('model')
        storage = cleaned_data.get('storage')
        ram = cleaned_data.get('ram')
        
        if all([brand, model, storage, ram]):
            # Vérifier si un téléphone avec les mêmes caractéristiques existe déjà
            if Phone.objects.filter(
                brand=brand,
                model=model,
                storage=storage,
                ram=ram
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError(
                    'Un téléphone avec ces caractéristiques existe déjà.'
                )
        
        return cleaned_data









