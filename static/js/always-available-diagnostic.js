/**
 * Script de diagnostic toujours disponible
 * Fonctionne en production et en développement
 */

console.log('🔍 === DIAGNOSTIC FACEBOOK PIXEL - TOUJOURS DISPONIBLE ===');

// Fonction de diagnostic simple
function simpleDiagnostic() {
    console.log('🔍 Diagnostic simple du Facebook Pixel...');
    
    // 1. Vérifier si fbq existe
    if (typeof fbq === 'undefined') {
        console.log('❌ fbq n\'est pas défini');
        console.log('🔧 CAUSE: Consentement marketing non donné ou script non chargé');
        
        // Vérifier les cookies
        const cookies = document.cookie.split(';').reduce((acc, cookie) => {
            const [key, value] = cookie.trim().split('=');
            acc[key] = value;
            return acc;
        }, {});
        
        console.log('🍪 Cookies de consentement:', cookies);
        console.log('🎯 Consentement marketing:', cookies['cookie_consent_marketing']);
        
        if (cookies['cookie_consent_marketing'] !== 'true') {
            console.log('💡 SOLUTION: Accepter les cookies marketing');
            console.log('💡 OU: Utiliser forcePixelTest()');
        }
        
        return false;
    }
    
    console.log('✅ fbq est défini');
    
    // 2. Tester un événement
    try {
        fbq('track', 'TestEvent', { test: true, timestamp: new Date().toISOString() });
        console.log('✅ Événement de test envoyé');
        console.log('📋 Vérifiez Meta Pixel Helper maintenant');
        return true;
    } catch (e) {
        console.log('❌ Erreur lors de l\'envoi:', e.message);
        return false;
    }
}

// Fonction pour forcer le test du pixel
function forcePixelTest() {
    console.log('🚀 Test forcé du Facebook Pixel...');
    
    // 1. Forcer le consentement
    document.cookie = 'cookie_consent_marketing=true; path=/; max-age=31536000';
    document.cookie = 'cookie_consent_analytics=true; path=/; max-age=31536000';
    console.log('✅ Consentement forcé');
    
    // 2. Charger le pixel manuellement
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    
    script.onload = function() {
        console.log('✅ Script Facebook Pixel chargé');
        
        if (typeof fbq !== 'undefined') {
            fbq('init', '2046663719482491');
            fbq('track', 'PageView');
            console.log('🎯 Facebook Pixel initialisé');
            
            // Tester un événement
            setTimeout(() => {
                fbq('track', 'TestEvent', { test: true, timestamp: new Date().toISOString() });
                console.log('✅ Événement de test envoyé');
                console.log('📋 Vérifiez Meta Pixel Helper maintenant');
            }, 1000);
        }
    };
    
    script.onerror = function() {
        console.log('❌ Erreur lors du chargement du script');
    };
    
    document.head.appendChild(script);
}

// Fonction pour tester tous les événements
function testAllEvents() {
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible, lancement du test forcé...');
        forcePixelTest();
        return;
    }
    
    console.log('🎯 Test de tous les événements...');
    
    const events = [
        { name: 'PageView', data: {} },
        { name: 'ViewContent', data: { content_type: 'product', content_ids: ['test-123'] } },
        { name: 'AddToCart', data: { value: 15000, currency: 'XOF', content_ids: ['test-123'] } },
        { name: 'ViewCart', data: { value: 15000, currency: 'XOF', content_ids: ['test-123'] } },
        { name: 'InitiateCheckout', data: { value: 15000, currency: 'XOF', content_ids: ['test-123'] } },
        { name: 'Purchase', data: { value: 15000, currency: 'XOF', content_ids: ['test-123'] } },
        { name: 'Search', data: { search_string: 'test search' } },
        { name: 'CompleteRegistration', data: { value: 0, currency: 'XOF' } }
    ];
    
    events.forEach((event, index) => {
        setTimeout(() => {
            console.log(`🎯 Envoi événement ${index + 1}/${events.length}: ${event.name}`);
            fbq('track', event.name, event.data);
        }, index * 500);
    });
    
    console.log('✅ Tous les événements programmés');
}

// Fonction pour vérifier le consentement
function checkConsent() {
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
    }, {});
    
    console.log('🍪 Cookies de consentement:', cookies);
    console.log('🎯 Consentement marketing:', cookies['cookie_consent_marketing']);
    console.log('📊 Consentement analytics:', cookies['cookie_consent_analytics']);
    
    return {
        marketing: cookies['cookie_consent_marketing'] === 'true',
        analytics: cookies['cookie_consent_analytics'] === 'true'
    };
}

// Exposer les fonctions globalement
window.simpleDiagnostic = simpleDiagnostic;
window.forcePixelTest = forcePixelTest;
window.testAllEvents = testAllEvents;
window.checkConsent = checkConsent;

// Auto-diagnostic au chargement
setTimeout(() => {
    simpleDiagnostic();
}, 2000);

console.log('📋 Commandes disponibles:');
console.log('  - simpleDiagnostic() : Diagnostic simple');
console.log('  - forcePixelTest() : Test forcé du pixel');
console.log('  - testAllEvents() : Tester tous les événements');
console.log('  - checkConsent() : Vérifier le consentement'); 