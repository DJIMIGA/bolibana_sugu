/**
 * Script de debug pour Facebook Pixel
 * À utiliser pour tester les événements e-commerce
 */

// Fonction pour tester tous les événements e-commerce
function testAllFacebookPixelEvents() {
    console.log('🧪 Test complet des événements Facebook Pixel...');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return;
    }
    
    console.log('✅ Facebook Pixel disponible, test des événements...');
    
    // Test 1: ViewContent (Vue produit)
    fbq('track', 'ViewContent', {
        content_name: 'Test Product - Bazin Super Riche',
        content_category: 'Fabric',
        content_type: 'product',
        value: 15000,
        currency: 'XOF',
        content_ids: ['test-product-123']
    });
    console.log('🎯 Événement ViewContent envoyé');
    
    // Test 2: AddToCart (Ajout au panier)
    fbq('track', 'AddToCart', {
        content_name: 'Test Product - Bazin Super Riche',
        content_category: 'Fabric',
        content_type: 'product',
        value: 15000,
        currency: 'XOF',
        content_ids: ['test-product-123'],
        quantity: 2
    });
    console.log('🎯 Événement AddToCart envoyé');
    
    console.log('✅ Événements de test envoyés !');
    console.log('📱 Vérifie maintenant dans Facebook Pixel Helper');
}

// Exposer la fonction globalement
window.testAllFacebookPixelEvents = testAllFacebookPixelEvents;

// Auto-test en développement
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🧪 Mode développement détecté - Test automatique Facebook Pixel dans 3 secondes...');
    setTimeout(testAllFacebookPixelEvents, 3000);
} 