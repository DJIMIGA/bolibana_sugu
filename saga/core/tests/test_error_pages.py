"""
Tests pour les pages d'erreur personnalisées
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
import os


class ErrorPagesTestCase(TestCase):
    """Tests pour les pages d'erreur personnalisées"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        
    def test_404_template_exists(self):
        """Vérifier que le template 404.html existe"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '404.html')
        self.assertTrue(os.path.exists(template_path), "Le template 404.html doit exister")
        
        # Vérifier le contenu
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifications de base
        self.assertIn('BoliBana', content, "Le template doit contenir 'BoliBana'")
        self.assertIn('404', content, "Le template doit contenir '404'")
        self.assertIn('tailwind', content.lower(), "Le template doit utiliser Tailwind CSS")
        
    def test_500_template_exists(self):
        """Vérifier que le template 500.html existe"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '500.html')
        self.assertTrue(os.path.exists(template_path), "Le template 500.html doit exister")
        
    def test_403_template_exists(self):
        """Vérifier que le template 403.html existe"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '403.html')
        self.assertTrue(os.path.exists(template_path), "Le template 403.html doit exister")
        
    def test_error_views_exist(self):
        """Vérifier que les vues d'erreur existent"""
        from core.views import custom_404, custom_500, custom_403
        
        self.assertTrue(callable(custom_404), "custom_404 doit être une fonction")
        self.assertTrue(callable(custom_500), "custom_500 doit être une fonction")
        self.assertTrue(callable(custom_403), "custom_403 doit être une fonction")
        
    def test_error_handlers_configuration(self):
        """Vérifier la configuration des gestionnaires d'erreur"""
        if not settings.DEBUG:
            # En production, les gestionnaires doivent être configurés
            self.assertTrue(hasattr(settings, 'HANDLER404'), "HANDLER404 doit être configuré")
            self.assertTrue(hasattr(settings, 'HANDLER500'), "HANDLER500 doit être configuré")
            self.assertTrue(hasattr(settings, 'HANDLER403'), "HANDLER403 doit être configuré")
            
    def test_404_response_structure(self):
        """Tester la structure de la réponse 404"""
        # Simuler une erreur 404
        response = self.client.get('/url-qui-nexiste-pas/')
        
        # En mode DEBUG=False, on devrait avoir une erreur 404
        if not settings.DEBUG:
            self.assertEqual(response.status_code, 404, "La réponse doit avoir le statut 404")
            
            # Vérifier que c'est notre template personnalisé
            if 'BoliBana' in response.content.decode():
                self.assertIn('Page d\'erreur personnalisée', response.content.decode())
                
    def test_error_page_design_elements(self):
        """Vérifier les éléments de design des pages d'erreur"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '404.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les éléments de design
        design_elements = [
            'bg-gradient-to-br from-green-50 to-yellow-50',  # Gradient de fond
            'text-red-500',  # Couleur rouge pour le numéro d'erreur
            'text-green-600',  # Couleur verte pour les liens
            'hover:bg-green-700',  # Effet hover
            'rounded-lg',  # Coins arrondis
            'shadow-lg',  # Ombre
        ]
        
        for element in design_elements:
            self.assertIn(element, content, f"Le template doit contenir {element}")
            
    def test_error_page_accessibility(self):
        """Vérifier l'accessibilité des pages d'erreur"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '404.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les éléments d'accessibilité
        accessibility_elements = [
            'alt=',  # Attributs alt pour les images
            'title=',  # Attributs title
            'aria-',  # Attributs ARIA
        ]
        
        # Au moins un élément d'accessibilité doit être présent
        has_accessibility = any(element in content for element in accessibility_elements)
        self.assertTrue(has_accessibility, "Le template doit avoir des éléments d'accessibilité")
        
    def test_error_page_responsive(self):
        """Vérifier que les pages d'erreur sont responsives"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '404.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les classes responsives Tailwind
        responsive_classes = [
            'max-w-md',  # Largeur maximale
            'px-4',  # Padding horizontal
            'text-center',  # Centrage du texte
        ]
        
        for class_name in responsive_classes:
            self.assertIn(class_name, content, f"Le template doit contenir {class_name}")
            
    def test_error_page_navigation(self):
        """Vérifier que les pages d'erreur ont une navigation claire"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '404.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les éléments de navigation
        navigation_elements = [
            'Retour à l\'accueil',  # Lien de retour
            'href="/"',  # Lien vers l'accueil
            'Rechercher',  # Lien de recherche
        ]
        
        for element in navigation_elements:
            self.assertIn(element, content, f"Le template doit contenir {element}")


class ErrorPagesIntegrationTestCase(TestCase):
    """Tests d'intégration pour les pages d'erreur"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        
    def test_404_integration(self):
        """Test d'intégration pour la page 404"""
        # Tester avec différentes URLs inexistantes
        test_urls = [
            '/page-inexistante/',
            '/produit/123456/',
            '/categorie/inexistante/',
            '/admin/inexistant/',
        ]
        
        for url in test_urls:
            response = self.client.get(url)
            
            # En mode DEBUG=False, on devrait avoir une erreur 404
            if not settings.DEBUG:
                self.assertEqual(response.status_code, 404, f"L'URL {url} doit retourner 404")
                
    def test_error_page_performance(self):
        """Tester la performance des pages d'erreur"""
        import time
        
        # Mesurer le temps de réponse pour une page 404
        start_time = time.time()
        response = self.client.get('/url-qui-nexiste-pas/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # La réponse doit être rapide (< 1 seconde)
        self.assertLess(response_time, 1.0, "La page d'erreur doit se charger rapidement")
        
    def test_error_page_seo(self):
        """Vérifier les éléments SEO des pages d'erreur"""
        template_path = os.path.join(settings.BASE_DIR, 'saga', 'templates', '404.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les éléments SEO
        seo_elements = [
            '<title>',  # Balise title
            '<meta name="description"',  # Meta description
            'robots',  # Meta robots
        ]
        
        # Au moins un élément SEO doit être présent
        has_seo = any(element in content for element in seo_elements)
        self.assertTrue(has_seo, "Le template doit avoir des éléments SEO") 