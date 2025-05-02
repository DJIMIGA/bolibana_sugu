from django import forms
from .models import PriceEntry, City, PriceSubmission
from product.models import Product, PhoneVariant, Phone

class PriceEntryForm(forms.ModelForm):
    class Meta:
        model = PriceEntry
        fields = ['product', 'variant', 'city', 'price', 'is_active']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'id': 'id_product'
            }),
            'variant': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'id': 'id_variant',
                'disabled': True
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
        self.fields['variant'].queryset = PhoneVariant.objects.none()
        self.fields['is_active'].initial = True
        
        # Si c'est une mise à jour et que l'instance a un produit
        if self.instance and self.instance.pk and self.instance.product:
            print(f"\n=== Valeurs de l'instance ===")
            print(f"Product: {self.instance.product}")
            print(f"Variant: {self.instance.variant}")
            print(f"City: {self.instance.city}")
            print(f"Price: {self.instance.price}")
            
            # Définir les valeurs initiales
            self.initial['product'] = self.instance.product
            self.initial['city'] = self.instance.city
            self.initial['price'] = self.instance.price
            
            # Si l'instance a un produit, filtrer les variantes
            try:
                if hasattr(self.instance.product, 'phone'):
                    self.fields['variant'].queryset = self.instance.product.phone.variants.filter(disponible_salam=True)
                    self.initial['variant'] = self.instance.variant
                    self.fields['variant'].widget.attrs['disabled'] = False
                    
                    # Ajouter la valeur initiale comme attribut data pour le JavaScript
                    self.fields['variant'].widget.attrs['data-initial-value'] = str(self.instance.variant.id) if self.instance.variant else ''
            except Exception as e:
                print(f"Erreur lors de l'accès au téléphone: {e}")
                self.fields['variant'].widget.attrs['disabled'] = True
                self.fields['variant'].widget.attrs['data-initial-value'] = ''
        
        # Si un produit est sélectionné dans le formulaire
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                print(f"\n=== Produit sélectionné dans le formulaire ===")
                print(f"Product ID: {product_id}")
                
                product = Product.objects.get(id=product_id)
                try:
                    if hasattr(product, 'phone'):
                        self.fields['variant'].queryset = product.phone.variants.filter(disponible_salam=True)
                        self.fields['variant'].widget.attrs['disabled'] = False
                except Exception as e:
                    print(f"Erreur lors de l'accès au téléphone: {e}")
                    self.fields['variant'].widget.attrs['disabled'] = True
            except (ValueError, TypeError, Product.DoesNotExist) as e:
                print(f"Erreur lors de la récupération du produit: {e}")
                self.fields['variant'].widget.attrs['disabled'] = True
        
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
    brand = forms.ChoiceField(
        required=False,
        label='Marque',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
            'id': 'id_brand'
        })
    )

    class Meta:
        model = PriceSubmission
        fields = ['brand', 'product', 'variant', 'city', 'price']
        labels = {
            'product': 'Modèle',
            'variant': 'Configuration',
            'city': 'Ville',
            'price': 'Prix (FCFA)'
        }
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'id': 'id_product'
            }),
            'variant': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'id': 'id_variant',
                'disabled': True
            }),
            'city': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-gray-200 px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': 'Prix en FCFA',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("\n=== Debug PriceSubmissionForm - __init__ ===")
        print(f"Instance: {self.instance}")
        print(f"Instance PK: {self.instance.pk if self.instance else None}")
        print(f"Initial data: {self.initial}")
        print(f"Data: {self.data}")
        
        # Initialiser les querysets de base
        self.fields['brand'].choices = [('', '---------')] + [
            (brand, brand) for brand in Phone.objects.values_list('brand', flat=True).distinct().order_by('brand')
        ]
        print(f"\n=== Marques disponibles ===")
        print(self.fields['brand'].choices)
        
        # Initialiser le queryset des produits avec un choix vide
        self.fields['product'].queryset = Product.objects.none()
        self.fields['product'].empty_label = "Sélectionnez d'abord une marque"
        print(f"\n=== Queryset produit initial ===")
        print(self.fields['product'].queryset)
        
        self.fields['city'].queryset = City.objects.filter(is_active=True)
        self.fields['variant'].queryset = PhoneVariant.objects.none()
        self.fields['variant'].empty_label = "Sélectionnez d'abord un modèle"

        # Si une marque est sélectionnée dans le formulaire
        if 'brand' in self.data:
            try:
                brand = self.data.get('brand')
                print(f"\n=== Marque sélectionnée dans le formulaire ===")
                print(f"Brand: {brand}")
                
                if brand:
                    self.fields['product'].queryset = Product.objects.filter(
                        is_active=True,
                        phone__brand=brand
                    ).select_related('phone').order_by('phone__model')
                    print(f"\n=== Produits disponibles pour la marque {brand} ===")
                    print(self.fields['product'].queryset)
            except Exception as e:
                print(f"Erreur lors du filtrage des produits par marque: {e}")

        # Si c'est une mise à jour et que l'instance a un produit
        elif self.instance and self.instance.pk and hasattr(self.instance, 'product') and self.instance.product:
            print(f"\n=== Valeurs de l'instance ===")
            print(f"Product: {self.instance.product}")
            print(f"Variant: {self.instance.variant}")
            print(f"City: {self.instance.city}")
            print(f"Price: {self.instance.price}")
            
            try:
                # Définir les valeurs initiales
                if hasattr(self.instance.product, 'phone'):
                    self.initial['brand'] = self.instance.product.phone.brand
                    self.initial['product'] = self.instance.product
                    self.initial['city'] = self.instance.city
                    self.initial['price'] = self.instance.price
                    
                    # Si l'instance a un produit, filtrer les variantes
                    self.fields['product'].queryset = Product.objects.filter(
                        is_active=True,
                        phone__brand=self.instance.product.phone.brand
                    ).select_related('phone').order_by('phone__model')
                    
                    self.fields['variant'].queryset = self.instance.product.phone.variants.all()
                    self.initial['variant'] = self.instance.variant
                    self.fields['variant'].widget.attrs['disabled'] = False
                    
                    # Ajouter la valeur initiale comme attribut data pour le JavaScript
                    self.fields['variant'].widget.attrs['data-initial-value'] = str(self.instance.variant.id) if self.instance.variant else ''
            except Exception as e:
                print(f"Erreur lors de l'accès au téléphone: {e}")
                self.fields['variant'].widget.attrs['disabled'] = True
                self.fields['variant'].widget.attrs['data-initial-value'] = ''
        
        # Si un produit est sélectionné dans le formulaire
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                print(f"\n=== Produit sélectionné dans le formulaire ===")
                print(f"Product ID: {product_id}")
                
                product = Product.objects.get(id=product_id)
                try:
                    if hasattr(product, 'phone'):
                        self.fields['variant'].queryset = product.phone.variants.all()
                        self.fields['variant'].widget.attrs['disabled'] = False
                except Exception as e:
                    print(f"Erreur lors de l'accès au téléphone: {e}")
                    self.fields['variant'].widget.attrs['disabled'] = True
            except (ValueError, TypeError, Product.DoesNotExist) as e:
                print(f"Erreur lors de la récupération du produit: {e}")
                self.fields['variant'].widget.attrs['disabled'] = True
        
        print("=========================\n")

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        product = cleaned_data.get('product')
        variant = cleaned_data.get('variant')
        
        print("\n=== Validation du formulaire ===")
        print(f"Marque: {brand}")
        print(f"Produit: {product}")
        print(f"Variante: {variant}")
        
        # Vérifier que la marque est sélectionnée
        if not brand:
            self.add_error('brand', 'Veuillez sélectionner une marque')
            return cleaned_data
            
        # Vérifier que le produit est sélectionné
        if not product:
            self.add_error('product', 'Veuillez sélectionner un modèle')
            return cleaned_data
            
        # Vérifier que la variante est sélectionnée
        if not variant:
            self.add_error('variant', 'Veuillez sélectionner une configuration')
            return cleaned_data
            
        # Vérifier que la variante appartient bien au produit sélectionné
        if variant and variant.phone != product.phone:
            self.add_error('variant', 'Cette configuration ne correspond pas au modèle sélectionné')
            
        return cleaned_data 

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