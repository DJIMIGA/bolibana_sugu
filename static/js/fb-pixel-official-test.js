/**
 * Script de test officiel Facebook Pixel
 * Code de test : TEST91163
 */

// Fonction de test officiel Facebook
function testFacebookPixelOfficial() {
    console.log('🧪 Test officiel Facebook Pixel...');
    console.log('📋 Code de test : TEST91163');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return;
    }
    
    console.log('✅ Facebook Pixel disponible, envoi du test...');
    
    // Test officiel avec le code fourni
    fbq('track', 'Purchase', {
        value: 15000,
        currency: 'XOF',
        content_type: 'product',
        content_ids: ['test-product-123'],
        test_event_code: 'TEST91163'  // Code de test officiel
    });
    
    console.log('🎯 Test officiel envoyé avec le code TEST91163');
    console.log('📱 Vérifie maintenant dans Facebook Events Manager');
}

// Fonction de test complet
function testAllFacebookEvents() {
    console.log('🧪 Test complet de tous les événements Facebook Pixel...');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return;
    }
    
    // Test 1: PageView
    fbq('track', 'PageView', {
        test_event_code: 'TEST91163'
    });
    console.log('🎯 PageView envoyé');
    
    // Test 2: ViewContent
    setTimeout(() => {
        fbq('track', 'ViewContent', {
            content_name: 'Test Product - Bazin Super Riche',
            content_category: 'Fabric',
            value: 15000,
            currency: 'XOF',
            test_event_code: 'TEST91163'
        });
        console.log('🎯 ViewContent envoyé');
    }, 1000);
    
    // Test 3: AddToCart
    setTimeout(() => {
        fbq('track', 'AddToCart', {
            content_name: 'Test Product - Bazin Super Riche',
            content_category: 'Fabric',
            value: 15000,
            currency: 'XOF',
            quantity: 1,
            test_event_code: 'TEST91163'
        });
        console.log('🎯 AddToCart envoyé');
    }, 2000);
    
    // Test 4: Purchase
    setTimeout(() => {
        fbq('track', 'Purchase', {
            value: 15000,
            currency: 'XOF',
            content_type: 'product',
            content_ids: ['test-product-123'],
            test_event_code: 'TEST91163'
        });
        console.log('🎯 Purchase envoyé');
    }, 3000);
    
    console.log('✅ Tous les tests envoyés avec le code TEST91163');
    console.log('📱 Vérifie dans Facebook Events Manager');
}

// Exposer les fonctions globalement
window.testFacebookPixelOfficial = testFacebookPixelOfficial;
window.testAllFacebookEvents = testAllFacebookEvents;

// Instructions
console.log(`
🧪 TEST OFFICIEL FACEBOOK PIXEL:

1. Test officiel simple:
   testFacebookPixelOfficial()

2. Test complet de tous les événements:
   testAllFacebookEvents()

3. Code de test utilisé: TEST91163

4. Vérification:
   - Ouvrir Facebook Events Manager
   - Aller dans la page de test d'événements
   - Les événements doivent apparaître instantanément
`); 