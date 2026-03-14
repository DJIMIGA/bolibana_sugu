from django.test import TestCase
from product.services import ProductAttributeValidator
from product.models import Product, Clothing

class ProductAttributeValidatorTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product")
        self.clothing = Clothing.objects.create(product=self.product)
        
    def test_validate_attributes_with_required_color(self):
        validator = ProductAttributeValidator(self.product)
        errors = validator.validate_attributes({})
        self.assertIn('color', errors)

    def test_validate_attributes_for_non_clothing_product(self):
        # Test avec un produit qui n'est pas un vêtement
        simple_product = Product.objects.create(name="Simple Product")
        validator = ProductAttributeValidator(simple_product)
        errors = validator.validate_attributes({})
        self.assertEqual(len(errors), 0)

    def test_validate_attributes_for_clothing_without_attributes(self):
        # Test avec un vêtement sans couleurs ni tailles
        clothing = Clothing.objects.create(product=self.product)
        validator = ProductAttributeValidator(self.product)
        errors = validator.validate_attributes({})
        self.assertEqual(len(errors), 0) 