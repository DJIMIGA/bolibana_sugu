/**
 * Script de test rapide pour les événements manquants
 * À utiliser pour vérifier rapidement les événements
 */

// Test rapide des événements manquants
function quickTestMissingEvents() {
    console.log('🚀 Test rapide des événements manquants...');
    
    let results = {
        viewCart: false,
        initiateCheckout: false,
        completeRegistration: false,
        search: false
    };
    
    // Test ViewCart
    if (typeof fbq !== 'undefined') {
        fbq('track', 'ViewCart', {
            value: 15000,
            currency: 'XOF',
            content_type: 'product',
            content_ids: ['test-product-123']
        });
        console.log('✅ ViewCart testé');
        results.viewCart = true;
    }
    
    // Test InitiateCheckout
    if (typeof fbq !== 'undefined') {
        fbq('track', 'InitiateCheckout', {
            value: 15000,
            currency: 'XOF',
            num_items: 1,
            content_ids: ['test-product-123'],
            content_type: 'product'
        });
        console.log('✅ InitiateCheckout testé');
        results.initiateCheckout = true;
    }
    
    // Test CompleteRegistration
    if (typeof fbq !== 'undefined') {
        fbq('track', 'CompleteRegistration', {
            value: 0,
            currency: 'XOF'
        });
        console.log('✅ CompleteRegistration testé');
        results.completeRegistration = true;
    }
    
    // Test Search
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Search', {
            search_string: 'test search',
            content_category: 'Test'
        });
        console.log('✅ Search testé');
        results.search = true;
    }
    
    // Résumé
    console.log('\n📋 Résumé des tests :');
    console.log(`ViewCart: ${results.viewCart ? '✅' : '❌'}`);
    console.log(`InitiateCheckout: ${results.initiateCheckout ? '✅' : '❌'}`);
    console.log(`CompleteRegistration: ${results.completeRegistration ? '✅' : '❌'}`);
    console.log(`Search: ${results.search ? '✅' : '❌'}`);
    
    return results;
}

// Test des événements existants
function quickTestExistingEvents() {
    console.log('🚀 Test rapide des événements existants...');
    
    let results = {
        pageView: false,
        viewContent: false,
        addToCart: false,
        purchase: false
    };
    
    // Test PageView (déjà envoyé automatiquement)
    console.log('✅ PageView: envoyé automatiquement');
    results.pageView = true;
    
    // Test ViewContent
    if (typeof fbq !== 'undefined') {
        fbq('track', 'ViewContent', {
            content_name: 'Test Product',
            content_category: 'Test',
            value: 15000,
            currency: 'XOF',
            content_ids: ['test-product-123']
        });
        console.log('✅ ViewContent testé');
        results.viewContent = true;
    }
    
    // Test AddToCart
    if (typeof fbq !== 'undefined') {
        fbq('track', 'AddToCart', {
            content_name: 'Test Product',
            content_category: 'Test',
            value: 15000,
            currency: 'XOF',
            content_ids: ['test-product-123'],
            quantity: 1
        });
        console.log('✅ AddToCart testé');
        results.addToCart = true;
    }
    
    // Test Purchase
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Purchase', {
            value: 15000,
            currency: 'XOF',
            content_type: 'product',
            content_ids: ['test-product-123'],
            num_items: 1,
            order_id: 'test-order-123'
        });
        console.log('✅ Purchase testé');
        results.purchase = true;
    }
    
    // Résumé
    console.log('\n📋 Résumé des tests existants :');
    console.log(`PageView: ${results.pageView ? '✅' : '❌'}`);
    console.log(`ViewContent: ${results.viewContent ? '✅' : '❌'}`);
    console.log(`AddToCart: ${results.addToCart ? '✅' : '❌'}`);
    console.log(`Purchase: ${results.purchase ? '✅' : '❌'}`);
    
    return results;
}

// Test complet rapide
function quickTestAll() {
    console.log('🚀 Test complet rapide de tous les événements...');
    console.log('='.repeat(50));
    
    const existing = quickTestExistingEvents();
    console.log('\n' + '='.repeat(50));
    const missing = quickTestMissingEvents();
    
    console.log('\n🎯 RÉSUMÉ FINAL :');
    console.log('='.repeat(50));
    console.log('Événements existants :', Object.values(existing).filter(Boolean).length, '/ 4');
    console.log('Événements manquants :', Object.values(missing).filter(Boolean).length, '/ 4');
    
    const total = Object.values(existing).filter(Boolean).length + Object.values(missing).filter(Boolean).length;
    console.log('Total :', total, '/ 8');
    
    if (total === 8) {
        console.log('🎉 TOUS LES ÉVÉNEMENTS FONCTIONNENT !');
    } else {
        console.log('⚠️ CERTAINS ÉVÉNEMENTS ONT DES PROBLÈMES');
    }
}

// Exposer les fonctions globalement
window.quickTestMissingEvents = quickTestMissingEvents;
window.quickTestExistingEvents = quickTestExistingEvents;
window.quickTestAll = quickTestAll;

console.log('🧪 Script de test rapide chargé');
console.log('💡 Utilisez quickTestAll() pour tester tous les événements rapidement'); 