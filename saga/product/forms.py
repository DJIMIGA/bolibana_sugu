from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Product, Phone, Category, Color, Review, PhoneVariant, PhoneVariantImage


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['note', 'comment']
        # permet de changer le widget de la note pour un RadioSelect (boutons radio)
        widgets = {
            'note': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'price', 'description', 'highlight', 'image', 'supplier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='w-full'),
                css_class='mb-4'
            ),
            Row(
                Column('category', css_class='w-1/2'),
                Column('price', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('description', css_class='w-full'),
                css_class='mb-4'
            ),
            Row(
                Column('highlight', css_class='w-full'),
                css_class='mb-4'
            ),
            Row(
                Column('image', css_class='w-1/2'),
                Column('supplier', css_class='w-1/2'),
                css_class='mb-4'
            ),
        )


class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [
            'model',
            'operating_system',
            'screen_size',
            'resolution',
            'processor',
            'battery_capacity',
            'camera_main',
            'camera_front',
            'network',
            'warranty',
            'imei',
            'is_new',
            'box_included',
            'accessories'
        ]
        widgets = {
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'operating_system': forms.TextInput(attrs={'class': 'form-control'}),
            'screen_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'resolution': forms.TextInput(attrs={'class': 'form-control'}),
            'processor': forms.TextInput(attrs={'class': 'form-control'}),
            'battery_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'camera_main': forms.TextInput(attrs={'class': 'form-control'}),
            'camera_front': forms.TextInput(attrs={'class': 'form-control'}),
            'network': forms.TextInput(attrs={'class': 'form-control'}),
            'warranty': forms.TextInput(attrs={'class': 'form-control'}),
            'imei': forms.TextInput(attrs={'class': 'form-control'}),
            'is_new': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'box_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accessories': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('model', css_class='w-full'),
                css_class='mb-4'
            ),
            Row(
                Column('operating_system', css_class='w-1/2'),
                Column('screen_size', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('resolution', css_class='w-1/2'),
                Column('processor', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('battery_capacity', css_class='w-1/2'),
                Column('camera_main', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('camera_front', css_class='w-1/2'),
                Column('network', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('warranty', css_class='w-1/2'),
                Column('imei', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('is_new', css_class='w-1/2'),
                Column('box_included', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('accessories', css_class='w-full'),
                css_class='mb-4'
            ),
        )

    def save(self, commit=True, product=None):
        phone = super().save(commit=False)
        if product:
            phone.product = product
        if commit:
            phone.save()
            self.save_m2m()  # Pour sauvegarder les relations many-to-many (couleurs)
        return phone


class PhoneVariantForm(forms.ModelForm):
    class Meta:
        model = PhoneVariant
        fields = [
            'color',
            'storage',
            'ram',
            'price',
            'stock',
            'sku'
        ]
        widgets = {
            'color': forms.Select(attrs={'class': 'form-control'}),
            'storage': forms.NumberInput(attrs={'class': 'form-control'}),
            'ram': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('color', css_class='w-1/2'),
                Column('storage', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('ram', css_class='w-1/2'),
                Column('price', css_class='w-1/2'),
                css_class='mb-4'
            ),
            Row(
                Column('stock', css_class='w-1/2'),
                Column('sku', css_class='w-1/2'),
                css_class='mb-4'
            )
        )


class PhoneVariantImageForm(forms.ModelForm):
    class Meta:
        model = PhoneVariantImage
        fields = ['image', 'is_primary', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-green-500 dark:focus:border-green-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True
        self.fields['is_primary'].required = False
        self.fields['order'].required = False


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class PhoneVariantImageFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Vérifier qu'au moins une image est fournie
        if not any(form.cleaned_data.get('image') for form in self.forms if form.cleaned_data):
            raise forms.ValidationError("Au moins une image est requise.")


PhoneVariantImageFormSet = forms.inlineformset_factory(
    PhoneVariant,
    PhoneVariantImage,
    form=PhoneVariantImageForm,
    formset=PhoneVariantImageFormSet,
    extra=5,
    can_delete=True,
    max_num=10
)









