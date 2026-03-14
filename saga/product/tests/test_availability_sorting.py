from django.test import TestCase
from product.models import Product, Category
from suppliers.models import Supplier
from decimal import Decimal

class ProductAvailabilitySortingTest(TestCase):
    def setUp(self):
        # Créer un fournisseur et une catégorie
        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        
        # Créer des produits disponibles
        self.p1 = Product.objects.create(
            title="Produit Dispo 1",
            price=Decimal("1000"),
            category=self.category,
            supplier=self.supplier,
            is_available=True
        )
        self.p2 = Product.objects.create(
            title="Produit Dispo 2",
            price=Decimal("2000"),
            category=self.category,
            supplier=self.supplier,
            is_available=True
        )
        
        # Créer des produits indisponibles
        self.p3 = Product.objects.create(
            title="Produit Indispo 1",
            price=Decimal("3000"),
            category=self.category,
            supplier=self.supplier,
            is_available=False
        )
        self.p4 = Product.objects.create(
            title="Produit Indispo 2",
            price=Decimal("4000"),
            category=self.category,
            supplier=self.supplier,
            is_available=False
        )

    def test_default_ordering(self):
        """Vérifie que le tri par défaut met les produits disponibles en premier"""
        products = list(Product.objects.all())
        
        # Les deux premiers doivent être disponibles
        self.assertTrue(products[0].is_available)
        self.assertTrue(products[1].is_available)
        
        # Les deux derniers doivent être indisponibles
        self.assertFalse(products[2].is_available)
        self.assertFalse(products[3].is_available)
        
        # Vérifier le tri par date (le plus récent en premier parmi les disponibles)
        self.assertEqual(products[0].id, self.p2.id)
        self.assertEqual(products[1].id, self.p1.id)
        self.assertEqual(products[2].id, self.p4.id)
        self.assertEqual(products[3].id, self.p3.id)

    def test_view_logic_includes_all(self):
        """Vérifie que Product.objects.all() est utilisé (sous-entendu par le fait qu'on récupère 4 produits)"""
        count = Product.objects.count()
        self.assertEqual(count, 4)
        
        # Simuler le comportement d'une vue qui utiliserait Product.objects.all()
        products = Product.objects.all()
        self.assertEqual(len(products), 4)

