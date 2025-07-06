from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from product.models import Product, Clothing, Color, Size, Category
from cart.models import Cart, CartItem

class CartViewsTest(TestCase):
    def setUp(self):
        # Créer un utilisateur
        User = get_user_model()
        self.user = User.objects.create_user(email='test@example.com', password='12345')
        self.client.login(email='test@example.com', password='12345')
        
        # Créer une catégorie
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        
        # Créer un produit de test
        self.product = Product.objects.create(
            title="Test Product", 
            slug='test-product',
            price=100,
            category=self.category,
            stock=10  # Ajouter un stock suffisant
        )
        self.clothing = Clothing.objects.create(product=self.product)
        
        # Créer des attributs
        self.color = Color.objects.create(name="Rouge", code="#FF0000")
        self.size = Size.objects.create(name="M")
        
        self.clothing.color.add(self.color)
        self.clothing.size.add(self.size)

    def test_add_same_product_increases_quantity(self):
        """Test que l'ajout du même produit augmente la quantité"""
        data = {
            'quantity': 1
        }
        
        # Premier ajout
        response1 = self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), data)
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième ajout avec les mêmes attributs
        response2 = self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), data)
        self.assertEqual(response2.status_code, 200)
        
        cart = Cart.objects.get(user=self.user)
        cart_items = cart.cart_items.all()
        
        # Vérifier qu'il n'y a qu'un seul article avec quantité = 2
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2)

    def test_add_product_different_attributes(self):
        """Test que l'ajout du même produit avec des attributs différents crée un nouvel article"""
        # Créer un autre produit avec des attributs différents
        product2 = Product.objects.create(
            title="Test Product 2", 
            slug='test-product-2',
            price=100,
            category=self.category,
            stock=10  # Ajouter un stock suffisant
        )
        clothing2 = Clothing.objects.create(product=product2)
        
        # Créer un autre attribut
        color2 = Color.objects.create(name="Bleu", code="#0000FF")
        clothing2.color.add(color2)
        clothing2.size.add(self.size)
        
        # Premier ajout avec produit 1
        response1 = self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), {
            'quantity': 1
        })
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième ajout avec produit 2
        response2 = self.client.post(reverse('cart:add_to_cart', args=[product2.id]), {
            'quantity': 1
        })
        self.assertEqual(response2.status_code, 200)
        
        cart = Cart.objects.get(user=self.user)
        cart_items = cart.cart_items.all()
        
        # Vérifier qu'il y a deux articles différents
        self.assertEqual(cart_items.count(), 2)
        self.assertEqual(cart_items[0].quantity, 1)
        self.assertEqual(cart_items[1].quantity, 1)

    def test_add_product_without_attributes(self):
        """Test l'ajout d'un produit sans attributs"""
        # Créer un produit simple sans attributs
        simple_product = Product.objects.create(
            title="Simple Product", 
            slug='simple-product',
            price=50,
            category=self.category,
            stock=10  # Ajouter un stock suffisant
        )
        
        # Premier ajout
        response1 = self.client.post(reverse('cart:add_to_cart', args=[simple_product.id]), {
            'quantity': 1
        })
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième ajout
        response2 = self.client.post(reverse('cart:add_to_cart', args=[simple_product.id]), {
            'quantity': 1
        })
        self.assertEqual(response2.status_code, 200)
        
        cart = Cart.objects.get(user=self.user)
        cart_items = cart.cart_items.all()
        
        # Vérifier qu'il n'y a qu'un seul article avec quantité = 2
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2) 