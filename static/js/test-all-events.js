/**
 * Script de test complet pour tous les événements analytics
 * À utiliser pour vérifier que tous les événements fonctionnent correctement
 */

// Fonction de test pour Google Analytics
function testGoogleAnalyticsEvents() {
    console.log('🧪 Test des événements Google Analytics...');
    
    if (typeof gtag === 'undefined') {
        console.log('❌ Google Analytics non disponible');
        return false;
    }
    
    console.log('✅ Google Analytics disponible, test des événements...');
    
    // Test 1: PageView (déjà envoyé automatiquement)
    console.log('📊 PageView: envoyé automatiquement');
    
    // Test 2: ViewContent (Vue produit)
    gtag('event', 'view_content', {
        'product_id': 'test-product-123',
        'product_name': 'Test Product - Bazin Super Riche',
        'category': 'Fabric',
        'price': 15000,
        'currency': 'XOF'
    });
    console.log('🎯 Événement ViewContent envoyé');
    
    // Test 3: AddToCart (Ajout au panier)
    gtag('event', 'add_to_cart', {
        'product_id': 'test-product-123',
        'product_name': 'Test Product - Bazin Super Riche',
        'quantity': 2,
        'price': 15000,
        'currency': 'XOF'
    });
    console.log('🎯 Événement AddToCart envoyé');
    
    // Test 4: ViewCart (Vue panier)
    gtag('event', 'view_cart', {
        'total_amount': 30000,
        'currency': 'XOF',
        'items_count': 2,
        'cart_id': 'test-cart-123'
    });
    console.log('🎯 Événement ViewCart envoyé');
    
    // Test 5: InitiateCheckout (Début commande)
    gtag('event', 'initiate_checkout', {
        'total_amount': 30000,
        'currency': 'XOF',
        'items_count': 2,
        'cart_id': 'test-cart-123'
    });
    console.log('🎯 Événement InitiateCheckout envoyé');
    
    // Test 6: Purchase (Achat)
    gtag('event', 'purchase', {
        'order_id': 'test-order-123',
        'total_amount': 30000,
        'currency': 'XOF',
        'items_count': 2
    });
    console.log('🎯 Événement Purchase envoyé');
    
    // Test 7: Search (Recherche)
    gtag('event', 'search', {
        'search_term': 'bazin super riche',
        'results_count': 15
    });
    console.log('🎯 Événement Search envoyé');
    
    // Test 8: User Registration
    gtag('event', 'user_registration', {
        'method': 'email',
        'source': 'website'
    });
    console.log('🎯 Événement User Registration envoyé');
    
    // Test 9: Login
    gtag('event', 'login', {
        'method': 'email',
        'source': 'website'
    });
    console.log('🎯 Événement Login envoyé');
    
    // Test 10: Logout
    gtag('event', 'logout', {
        'session_duration': 1800
    });
    console.log('🎯 Événement Logout envoyé');
    
    console.log('✅ Tous les événements Google Analytics testés !');
    return true;
}

// Fonction de test pour Facebook Pixel
function testFacebookPixelEvents() {
    console.log('🧪 Test des événements Facebook Pixel...');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return false;
    }
    
    console.log('✅ Facebook Pixel disponible, test des événements...');
    
    // Test 1: PageView (déjà envoyé automatiquement)
    console.log('📊 PageView: envoyé automatiquement');
    
    // Test 2: ViewContent (Vue produit)
    fbq('track', 'ViewContent', {
        'content_name': 'Test Product - Bazin Super Riche',
        'content_category': 'Fabric',
        'content_type': 'product',
        'value': 15000,
        'currency': 'XOF',
        'content_ids': ['test-product-123']
    });
    console.log('🎯 Événement ViewContent envoyé');
    
    // Test 3: AddToCart (Ajout au panier)
    fbq('track', 'AddToCart', {
        'content_name': 'Test Product - Bazin Super Riche',
        'content_category': 'Fabric',
        'content_type': 'product',
        'value': 15000,
        'currency': 'XOF',
        'content_ids': ['test-product-123'],
        'quantity': 2
    });
    console.log('🎯 Événement AddToCart envoyé');
    
    // Test 4: ViewCart (Vue panier)
    fbq('track', 'ViewCart', {
        'value': 30000,
        'currency': 'XOF',
        'content_type': 'product',
        'content_ids': ['test-product-123', 'test-product-456']
    });
    console.log('🎯 Événement ViewCart envoyé');
    
    // Test 5: InitiateCheckout (Début commande)
    fbq('track', 'InitiateCheckout', {
        'value': 30000,
        'currency': 'XOF',
        'content_type': 'product',
        'content_ids': ['test-product-123', 'test-product-456'],
        'num_items': 2
    });
    console.log('🎯 Événement InitiateCheckout envoyé');
    
    // Test 6: Purchase (Achat)
    fbq('track', 'Purchase', {
        'value': 30000,
        'currency': 'XOF',
        'content_type': 'product',
        'content_ids': ['test-product-123', 'test-product-456'],
        'num_items': 2,
        'order_id': 'test-order-123'
    });
    console.log('🎯 Événement Purchase envoyé');
    
    // Test 7: Search (Recherche)
    fbq('track', 'Search', {
        'search_string': 'bazin super riche',
        'content_category': 'Fabric'
    });
    console.log('🎯 Événement Search envoyé');
    
    // Test 8: CompleteRegistration (Inscription)
    fbq('track', 'CompleteRegistration', {
        'value': 0,
        'currency': 'XOF'
    });
    console.log('🎯 Événement CompleteRegistration envoyé');
    
    console.log('✅ Tous les événements Facebook Pixel testés !');
    return true;
}

// Fonction de test pour les événements d'engagement
function testEngagementEvents() {
    console.log('🧪 Test des événements d\'engagement...');
    
    if (typeof gtag === 'undefined') {
        console.log('❌ Google Analytics non disponible pour les événements d\'engagement');
        return false;
    }
    
    // Test 1: Scroll
    gtag('event', 'scroll', {
        'scroll_percentage': 50,
        'scroll_depth': 50
    });
    console.log('🎯 Événement Scroll envoyé');
    
    // Test 2: Engagement
    gtag('event', 'engagement', {
        'time_spent_seconds': 45,
        'engagement_level': 'medium'
    });
    console.log('🎯 Événement Engagement envoyé');
    
    // Test 3: Button Click
    gtag('event', 'button_click', {
        'button_text': 'Ajouter au panier',
        'button_class': 'btn btn-primary',
        'button_id': 'add-to-cart-btn',
        'button_type': 'button'
    });
    console.log('🎯 Événement Button Click envoyé');
    
    // Test 4: Link Click
    gtag('event', 'link_click', {
        'link_text': 'Voir le produit',
        'link_url': '/product/test-product',
        'is_external': false,
        'link_type': 'product'
    });
    console.log('🎯 Événement Link Click envoyé');
    
    // Test 5: Form Submit
    gtag('event', 'form_submit', {
        'form_id': 'checkout-form',
        'form_action': '/checkout/',
        'form_method': 'POST',
        'form_type': 'checkout'
    });
    console.log('🎯 Événement Form Submit envoyé');
    
    // Test 6: Product Image Click
    gtag('event', 'product_image_click', {
        'product_id': 'test-product-123',
        'image_src': '/media/products/test-image.jpg'
    });
    console.log('🎯 Événement Product Image Click envoyé');
    
    // Test 7: Favorite Toggle
    gtag('event', 'favorite_toggle', {
        'product_id': 'test-product-123',
        'action': 'add'
    });
    console.log('🎯 Événement Favorite Toggle envoyé');
    
    // Test 8: JavaScript Error
    gtag('event', 'javascript_error', {
        'error_message': 'Test error message',
        'error_filename': 'test.js',
        'error_lineno': 42,
        'error_colno': 10
    });
    console.log('🎯 Événement JavaScript Error envoyé');
    
    // Test 9: Page Performance
    gtag('event', 'page_performance', {
        'load_time': 1500,
        'dom_content_loaded': 800,
        'first_paint': 600,
        'first_contentful_paint': 700
    });
    console.log('🎯 Événement Page Performance envoyé');
    
    console.log('✅ Tous les événements d\'engagement testés !');
    return true;
}

// Fonction principale de test
function testAllEvents() {
    console.log('🚀 Démarrage du test complet de tous les événements...');
    console.log('=' * 60);
    
    let results = {
        googleAnalytics: false,
        facebookPixel: false,
        engagement: false
    };
    
    // Test Google Analytics
    console.log('\n📊 TEST GOOGLE ANALYTICS');
    console.log('-'.repeat(30));
    results.googleAnalytics = testGoogleAnalyticsEvents();
    
    // Test Facebook Pixel
    console.log('\n🎯 TEST FACEBOOK PIXEL');
    console.log('-'.repeat(30));
    results.facebookPixel = testFacebookPixelEvents();
    
    // Test Événements d'Engagement
    console.log('\n🎮 TEST ÉVÉNEMENTS D\'ENGAGEMENT');
    console.log('-'.repeat(30));
    results.engagement = testEngagementEvents();
    
    // Résumé
    console.log('\n📋 RÉSUMÉ DES TESTS');
    console.log('='.repeat(60));
    console.log(`Google Analytics: ${results.googleAnalytics ? '✅' : '❌'}`);
    console.log(`Facebook Pixel: ${results.facebookPixel ? '✅' : '❌'}`);
    console.log(`Événements d'Engagement: ${results.engagement ? '✅' : '❌'}`);
    
    if (results.googleAnalytics && results.facebookPixel && results.engagement) {
        console.log('\n🎉 TOUS LES TESTS SONT PASSÉS !');
        console.log('📱 Vérifiez maintenant dans :');
        console.log('   - Google Analytics (Temps réel > Événements)');
        console.log('   - Facebook Events Manager (Test Events)');
    } else {
        console.log('\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ');
        console.log('🔧 Vérifiez la configuration des scripts');
    }
    
    return results;
}

// Exposer les fonctions globalement
window.testAllEvents = testAllEvents;
window.testGoogleAnalyticsEvents = testGoogleAnalyticsEvents;
window.testFacebookPixelEvents = testFacebookPixelEvents;
window.testEngagementEvents = testEngagementEvents;

console.log('🧪 Script de test des événements chargé');
console.log('💡 Utilisez testAllEvents() pour tester tous les événements'); 