/**
 * Script de test spécifique pour Meta Pixel Helper
 * Force l'envoi de tous les événements e-commerce pour vérifier la détection
 */

console.log('🎯 === TEST META PIXEL HELPER - ÉVÉNEMENTS E-COMMERCE ===');

// Fonction pour tester un événement spécifique
function testEvent(eventName, eventData = {}) {
    if (typeof fbq === 'undefined') {
        console.log(`❌ fbq non disponible pour ${eventName}`);
        return false;
    }
    
    try {
        console.log(`🎯 Envoi événement: ${eventName}`, eventData);
        fbq('track', eventName, eventData);
        console.log(`✅ Événement ${eventName} envoyé`);
        return true;
    } catch (e) {
        console.log(`❌ Erreur lors de l'envoi de ${eventName}:`, e.message);
        return false;
    }
}

// Fonction pour tester tous les événements e-commerce
function testAllEcommerceEvents() {
    console.log('🚀 Test de tous les événements e-commerce...');
    
    const events = [
        {
            name: 'PageView',
            data: {}
        },
        {
            name: 'ViewContent',
            data: {
                content_type: 'product',
                content_ids: ['test-product-123'],
                content_name: 'Test Product - Bazin Super Riche',
                value: 15000,
                currency: 'XOF'
            }
        },
        {
            name: 'AddToCart',
            data: {
                content_type: 'product',
                content_ids: ['test-product-123'],
                content_name: 'Test Product - Bazin Super Riche',
                value: 15000,
                currency: 'XOF',
                num_items: 1
            }
        },
        {
            name: 'ViewCart',
            data: {
                content_type: 'product',
                content_ids: ['test-product-123', 'test-product-456'],
                value: 30000,
                currency: 'XOF',
                num_items: 2
            }
        },
        {
            name: 'InitiateCheckout',
            data: {
                content_type: 'product',
                content_ids: ['test-product-123', 'test-product-456'],
                value: 30000,
                currency: 'XOF',
                num_items: 2
            }
        },
        {
            name: 'Purchase',
            data: {
                content_type: 'product',
                content_ids: ['test-product-123', 'test-product-456'],
                value: 30000,
                currency: 'XOF',
                num_items: 2,
                order_id: 'test-order-123'
            }
        },
        {
            name: 'Search',
            data: {
                search_string: 'bazin super riche',
                content_category: 'Fabric'
            }
        },
        {
            name: 'CompleteRegistration',
            data: {
                value: 0,
                currency: 'XOF'
            }
        }
    ];
    
    let successCount = 0;
    let totalCount = events.length;
    
    events.forEach((event, index) => {
        setTimeout(() => {
            const success = testEvent(event.name, event.data);
            if (success) successCount++;
            
            console.log(`📊 Progression: ${index + 1}/${totalCount} - ${success ? '✅' : '❌'} ${event.name}`);
            
            // Résumé final
            if (index === totalCount - 1) {
                console.log(`\n🎯 RÉSUMÉ DU TEST:`);
                console.log(`✅ Événements réussis: ${successCount}/${totalCount}`);
                console.log(`📋 Vérifiez Meta Pixel Helper maintenant`);
                console.log(`💡 Si certains événements n'apparaissent pas, vérifiez:`);
                console.log(`   - La configuration du pixel dans Facebook Events Manager`);
                console.log(`   - Les paramètres d'événements dans Events Manager`);
                console.log(`   - Les filtres dans Meta Pixel Helper`);
            }
        }, index * 2000); // 2 secondes entre chaque événement
    });
}

// Fonction pour tester un événement spécifique
function testSpecificEvent(eventName) {
    const eventData = {
        'PageView': {},
        'ViewContent': {
            content_type: 'product',
            content_ids: ['test-product-123'],
            content_name: 'Test Product',
            value: 15000,
            currency: 'XOF'
        },
        'AddToCart': {
            content_type: 'product',
            content_ids: ['test-product-123'],
            content_name: 'Test Product',
            value: 15000,
            currency: 'XOF',
            num_items: 1
        },
        'ViewCart': {
            content_type: 'product',
            content_ids: ['test-product-123'],
            value: 15000,
            currency: 'XOF',
            num_items: 1
        },
        'InitiateCheckout': {
            content_type: 'product',
            content_ids: ['test-product-123'],
            value: 15000,
            currency: 'XOF',
            num_items: 1
        },
        'Purchase': {
            content_type: 'product',
            content_ids: ['test-product-123'],
            value: 15000,
            currency: 'XOF',
            num_items: 1,
            order_id: 'test-order-123'
        },
        'Search': {
            search_string: 'test search',
            content_category: 'All'
        },
        'CompleteRegistration': {
            value: 0,
            currency: 'XOF'
        }
    };
    
    if (eventData[eventName]) {
        testEvent(eventName, eventData[eventName]);
    } else {
        console.log(`❌ Événement ${eventName} non reconnu`);
        console.log(`📋 Événements disponibles:`, Object.keys(eventData));
    }
}

// Fonction pour vérifier la configuration du pixel
function checkPixelConfig() {
    console.log('🔍 === VÉRIFICATION CONFIGURATION PIXEL ===');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ fbq non disponible');
        return;
    }
    
    // Vérifier l'ID du pixel
    try {
        const pixelId = window._fbq && window._fbq.id;
        console.log('🎯 ID du pixel détecté:', pixelId || 'Non détecté');
        
        if (pixelId === '2046663719482491') {
            console.log('✅ ID du pixel correct');
        } else {
            console.log('⚠️  ID du pixel différent de celui configuré');
        }
    } catch (e) {
        console.log('⚠️  Impossible de récupérer l\'ID du pixel');
    }
    
    // Vérifier les scripts chargés
    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    const fbScripts = scripts.filter(s => s.includes('facebook') || s.includes('fbevents'));
    console.log('📜 Scripts Facebook chargés:', fbScripts.length);
    
    // Test de base
    testEvent('TestEvent', { test: true, timestamp: new Date().toISOString() });
}

// Exposer les fonctions globalement
window.testAllEcommerceEvents = testAllEcommerceEvents;
window.testSpecificEvent = testSpecificEvent;
window.checkPixelConfig = checkPixelConfig;
window.testEvent = testEvent;

// Auto-vérification au chargement
setTimeout(() => {
    checkPixelConfig();
}, 1000);

console.log('📋 Commandes disponibles:');
console.log('  - testAllEcommerceEvents() : Tester tous les événements e-commerce');
console.log('  - testSpecificEvent("AddToCart") : Tester un événement spécifique');
console.log('  - checkPixelConfig() : Vérifier la configuration du pixel');
console.log('  - testEvent("EventName", data) : Tester un événement personnalisé'); 