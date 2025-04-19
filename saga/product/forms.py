from django import forms
from .models import Product, Category, Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['note', 'comment']
        # permet de changer le widget de la note pour un RadioSelect (boutons radio)
        widgets = {
            'note': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        }









