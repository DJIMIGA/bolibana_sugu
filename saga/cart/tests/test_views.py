from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from product.models import Product, Clothing, Color, Size
from cart.models import Cart, CartItem

class CartViewsTest(TestCase):
    def setUp(self):
        # Créer un utilisateur
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        # Créer un produit de test
        self.product = Product.objects.create(name="Test Product", price=100)
        self.clothing = Clothing.objects.create(product=self.product)
        
        # Créer des attributs
        self.color = Color.objects.create(name="Rouge", color_code="#FF0000")
        self.size = Size.objects.create(name="M")
        
        self.clothing.color.add(self.color)
        self.clothing.size.add(self.size)

    def test_add_same_product_increases_quantity(self):
        """Test que l'ajout du même produit augmente la quantité"""
        data = {
            'color_id': self.color.id,
            'size_id': self.size.id
        }
        
        # Premier ajout
        self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), data)
        
        # Deuxième ajout avec les mêmes attributs
        self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), data)
        
        cart = Cart.objects.get(user=self.user)
        cart_items = cart.cart_items.all()
        
        # Vérifier qu'il n'y a qu'un seul article avec quantité = 2
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2)

    def test_add_product_different_attributes(self):
        """Test que l'ajout du même produit avec des attributs différents crée un nouvel article"""
        # Créer un autre attribut
        color2 = Color.objects.create(name="Bleu", color_code="#0000FF")
        self.clothing.color.add(color2)
        
        # Premier ajout avec couleur 1
        self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), {
            'color_id': self.color.id,
            'size_id': self.size.id
        })
        
        # Deuxième ajout avec couleur 2
        self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), {
            'color_id': color2.id,
            'size_id': self.size.id
        })
        
        cart = Cart.objects.get(user=self.user)
        cart_items = cart.cart_items.all()
        
        # Vérifier qu'il y a deux articles différents
        self.assertEqual(cart_items.count(), 2)
        self.assertEqual(cart_items[0].quantity, 1)
        self.assertEqual(cart_items[1].quantity, 1)

    def test_add_product_without_attributes(self):
        """Test l'ajout d'un produit sans attributs"""
        # Créer un produit simple sans attributs
        simple_product = Product.objects.create(name="Simple Product", price=50)
        
        # Premier ajout
        response1 = self.client.post(reverse('cart:add_to_cart', args=[simple_product.id]))
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième ajout
        response2 = self.client.post(reverse('cart:add_to_cart', args=[simple_product.id]))
        self.assertEqual(response2.status_code, 200)
        
        cart = Cart.objects.get(user=self.user)
        cart_items = cart.cart_items.all()
        
        # Vérifier qu'il n'y a qu'un seul article avec quantité = 2
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2) 