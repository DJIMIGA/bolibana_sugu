/**
 * Script de test pour Facebook Pixel
 * À utiliser uniquement en développement
 */

// Fonction de test pour simuler les événements e-commerce
function testFacebookPixelEvents() {
    console.log('🧪 Test des événements Facebook Pixel...');
    
    // Test ViewContent
    if (typeof fbq !== 'undefined') {
        console.log('✅ Facebook Pixel disponible');
        
        // Simuler un événement ViewContent
        fbq('track', 'ViewContent', {
            content_name: 'Test Product',
            content_category: 'Test Category',
            value: 1000,
            currency: 'XOF'
        });
        console.log('🎯 Événement ViewContent envoyé');
        
        // Simuler un événement AddToCart
        fbq('track', 'AddToCart', {
            content_name: 'Test Product',
            content_category: 'Test Category',
            value: 1000,
            currency: 'XOF',
            quantity: 1
        });
        console.log('🎯 Événement AddToCart envoyé');
        
    } else {
        console.log('❌ Facebook Pixel non disponible');
    }
}

// Exposer la fonction globalement pour les tests
window.testFacebookPixelEvents = testFacebookPixelEvents;

// Auto-test en développement
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🧪 Mode développement détecté - Test automatique Facebook Pixel');
    setTimeout(testFacebookPixelEvents, 2000); // Attendre 2 secondes
} 