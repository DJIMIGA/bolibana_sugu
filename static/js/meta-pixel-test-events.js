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
    
    console.log('✅ fbq disponible');
    
    // Vérifier l'ID du pixel de plusieurs façons
    let pixelId = null;
    
    // Méthode 1: window._fbq.id
    try {
        if (window._fbq && window._fbq.id) {
            pixelId = window._fbq.id;
            console.log('🎯 ID du pixel (window._fbq.id):', pixelId);
        }
    } catch (e) {
        console.log('⚠️  Impossible de récupérer window._fbq.id');
    }
    
    // Méthode 2: Rechercher dans les scripts
    if (!pixelId) {
        try {
            const scripts = Array.from(document.querySelectorAll('script'));
            const fbScript = scripts.find(s => s.innerHTML && s.innerHTML.includes('fbevents.js'));
            if (fbScript) {
                const match = fbScript.innerHTML.match(/fbevents\.js\?id=(\d+)/);
                if (match) {
                    pixelId = match[1];
                    console.log('🎯 ID du pixel (dans script):', pixelId);
                }
            }
        } catch (e) {
            console.log('⚠️  Impossible de récupérer l\'ID depuis les scripts');
        }
    }
    
    // Méthode 3: Rechercher dans fbq
    if (!pixelId) {
        try {
            if (fbq && fbq._pixelId) {
                pixelId = fbq._pixelId;
                console.log('🎯 ID du pixel (fbq._pixelId):', pixelId);
            }
        } catch (e) {
            console.log('⚠️  Impossible de récupérer fbq._pixelId');
        }
    }
    
    // Méthode 4: Rechercher dans les variables globales
    if (!pixelId) {
        try {
            for (let key in window) {
                if (key.includes('fbq') || key.includes('facebook')) {
                    const value = window[key];
                    if (typeof value === 'string' && /^\d{15,16}$/.test(value)) {
                        pixelId = value;
                        console.log('🎯 ID du pixel (variable globale):', pixelId);
                        break;
                    }
                }
            }
        } catch (e) {
            console.log('⚠️  Impossible de rechercher dans les variables globales');
        }
    }
    
    // Vérifier l'ID
    if (pixelId) {
        if (pixelId === '2046663719482491') {
            console.log('✅ ID du pixel correct');
        } else {
            console.log('⚠️  ID du pixel différent de celui configuré');
            console.log('   Configuré: 2046663719482491');
            console.log('   Détecté:   ' + pixelId);
        }
    } else {
        console.log('❌ ID du pixel non détecté');
        console.log('💡 Le pixel peut fonctionner même sans ID détecté');
    }
    
    // Vérifier les scripts chargés
    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    const fbScripts = scripts.filter(s => s.includes('facebook') || s.includes('fbevents'));
    console.log('📜 Scripts Facebook chargés:', fbScripts.length);
    fbScripts.forEach((script, index) => {
        console.log(`   ${index + 1}. ${script}`);
    });
    
    // Vérifier les cookies
    const cookies = document.cookie.split(';').map(c => c.trim());
    const fbCookies = cookies.filter(c => c.includes('fb') || c.includes('facebook'));
    console.log('🍪 Cookies Facebook:', fbCookies.length);
    fbCookies.forEach((cookie, index) => {
        console.log(`   ${index + 1}. ${cookie}`);
    });
    
    // Test de base
    console.log('🧪 Test d\'envoi d\'événement...');
    testEvent('TestEvent', { test: true, timestamp: new Date().toISOString() });
    
    // Vérifier si fbq est fonctionnel
    console.log('🔧 Test de fonctionnalité fbq...');
    try {
        const testResult = fbq('track', 'TestEvent', { test: 'functionality' });
        console.log('✅ fbq fonctionne correctement');
    } catch (e) {
        console.log('❌ Erreur avec fbq:', e.message);
    }
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