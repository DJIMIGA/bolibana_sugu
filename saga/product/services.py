from typing import Dict, Any
from product.models import Product, Clothing

class ProductAttributeValidator:
    def __init__(self, product: Product):
        self.product = product
        self.clothing = self._get_clothing()
        
    def _get_clothing(self) -> Clothing | None:
        try:
            return self.product.clothing_product if hasattr(self.product, 'clothing_product') else None
        except Clothing.DoesNotExist:
            return None
            
    def validate_attributes(self, attributes: Dict[str, Any]) -> Dict[str, str]:
        """Valide les attributs du produit"""
        errors = {}
        
        # Si ce n'est pas un vêtement, pas besoin de validation
        if not self.clothing:
            return errors
            
        # Validation uniquement si le produit a des couleurs/tailles
        if self.clothing.color.all().exists():
            if not attributes.get('color_id'):
                errors['color'] = "Veuillez sélectionner une couleur"
                
        if self.clothing.size.all().exists():
            if not attributes.get('size_id'):
                errors['size'] = "Veuillez sélectionner une taille"
                
        return errors 