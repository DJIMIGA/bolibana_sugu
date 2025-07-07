from django import forms
from .models import PriceEntry, City, PriceSubmission
from product.models import Product

class PriceEntryForm(forms.ModelForm):
    class Meta:
        model = PriceEntry
        fields = ['product', 'city', 'price', 'is_active']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'id': 'id_product'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': 'Prix en FCFA',
                'min': '0'
            }),
            'is_active': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("\n=== Debug PriceEntryForm - __init__ ===")
        print(f"Instance: {self.instance}")
        print(f"Instance PK: {self.instance.pk if self.instance else None}")
        print(f"Initial data: {self.initial}")
        print(f"Data: {self.data}")
        
        # Initialiser les querysets de base
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['city'].queryset = City.objects.filter(is_active=True)
        self.fields['is_active'].initial = True
        
        # Si c'est une mise à jour et que l'instance a un produit
        if self.instance and self.instance.pk and self.instance.product:
            print(f"\n=== Valeurs de l'instance ===")
            print(f"Product: {self.instance.product}")
            print(f"City: {self.instance.city}")
            print(f"Price: {self.instance.price}")
            
            # Définir les valeurs initiales
            self.initial['product'] = self.instance.product
            self.initial['city'] = self.instance.city
            self.initial['price'] = self.instance.price
        
        print("=========================\n")

class PriceCheckForm(forms.Form):
    product_name = forms.CharField(
        label='Nom du produit',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
            'placeholder': 'Ex: iPhone 13, Samsung Galaxy S21...',
            'hx-get': '/prix/check_price/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#price-results',
            'hx-indicator': '.htmx-indicator',
            'hx-swap': 'innerHTML',
            'autocomplete': 'off'
        })
    )
    city = forms.ModelChoiceField(
        label='Ville',
        queryset=City.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
            'hx-get': '/price_checker/check/',
            'hx-trigger': 'change',
            'hx-target': '#price-results'
        })
    )

class PriceSubmissionForm(forms.ModelForm):
    class Meta:
        model = PriceSubmission
        fields = ['price', 'city', 'product']
        widgets = {
            'price': forms.NumberInput(attrs={'min': 0}),
        }

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Nom de la ville'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            })
        }
        labels = {
            'name': 'Nom de la ville',
            'is_active': 'Ville active'
        } 