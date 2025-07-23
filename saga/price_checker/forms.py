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
    # Champ de recherche pour le produit
    product_search = forms.CharField(
        label='Rechercher un produit',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
            'placeholder': 'Tapez le nom du produit (ex: iPhone 13, Samsung Galaxy...)',
            'autocomplete': 'off',
            'id': 'product-search'
        })
    )
    
    class Meta:
        model = PriceSubmission
        fields = ['price', 'city', 'product', 'supplier_name', 'supplier_phone', 'supplier_address', 'proof_image']
        widgets = {
            'price': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': 'Prix en FCFA',
                'min': '0'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
            'product': forms.HiddenInput(attrs={
                'id': 'product-id'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': 'Nom du fournisseur (ex: Magasin ABC, Boutique XYZ)'
            }),
            'supplier_phone': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': 'Téléphone du fournisseur (optionnel)'
            }),
            'supplier_address': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': 'Adresse du fournisseur (optionnel)',
                'rows': '3'
            }),
            'proof_image': forms.FileInput(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'accept': 'image/*'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        product_id = cleaned_data.get('product')
        product_search = cleaned_data.get('product_search')
        
        # Si un produit est sélectionné via l'autocomplétion, on l'utilise
        if product_id:
            return cleaned_data
        
        # Sinon, essayer de trouver le produit par le nom de recherche
        if product_search:
            from product.models import Product as ProductModel
            try:
                product = ProductModel.objects.filter(title__icontains=product_search).first()
                if product:
                    cleaned_data['product'] = product
                else:
                    self.add_error('product_search', 'Produit non trouvé. Veuillez sélectionner un produit dans la liste.')
            except Exception:
                self.add_error('product_search', 'Erreur lors de la recherche du produit.')
        
        return cleaned_data
        
        labels = {
            'price': 'Prix (FCFA)',
            'city': 'Ville',
            'product': 'Produit',
            'supplier_name': 'Nom du fournisseur',
            'supplier_phone': 'Téléphone du fournisseur',
            'supplier_address': 'Adresse du fournisseur',
            'proof_image': 'Preuve en image'
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