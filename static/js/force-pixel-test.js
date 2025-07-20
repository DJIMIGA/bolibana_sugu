/**
 * Script pour forcer le test du Facebook Pixel
 * Simule le consentement marketing et recharge le pixel
 */

console.log('🚀 === FORCE TEST FACEBOOK PIXEL ===');

// 1. Forcer le consentement marketing
function forceMarketingConsent() {
    console.log('🍪 Forçage du consentement marketing...');
    
    // Définir le cookie de consentement
    document.cookie = 'cookie_consent_marketing=true; path=/; max-age=31536000';
    document.cookie = 'cookie_consent_analytics=true; path=/; max-age=31536000';
    
    console.log('✅ Cookies de consentement définis');
}

// 2. Charger manuellement le Facebook Pixel
function loadFacebookPixel() {
    console.log('📜 Chargement manuel du Facebook Pixel...');
    
    // Supprimer l'ancien script s'il existe
    const existingScript = document.querySelector('script[src*="fbevents.js"]');
    if (existingScript) {
        existingScript.remove();
        console.log('🗑️  Ancien script supprimé');
    }
    
    // Créer le nouveau script
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    
    script.onload = function() {
        console.log('✅ Script Facebook Pixel chargé');
        
        // Initialiser le pixel
        if (typeof fbq !== 'undefined') {
            fbq('init', '2046663719482491');
            fbq('track', 'PageView');
            console.log('🎯 Facebook Pixel initialisé avec ID: 2046663719482491');
            
            // Tester un événement
            setTimeout(() => {
                fbq('track', 'TestEvent', {
                    test: true,
                    timestamp: new Date().toISOString()
                });
                console.log('✅ Événement de test envoyé');
                console.log('📋 Vérifiez Meta Pixel Helper maintenant');
            }, 1000);
        } else {
            console.log('❌ fbq non disponible après chargement du script');
        }
    };
    
    script.onerror = function() {
        console.log('❌ Erreur lors du chargement du script Facebook Pixel');
    };
    
    document.head.appendChild(script);
}

// 3. Fonction de test complète
function runForceTest() {
    console.log('🚀 Démarrage du test forcé...');
    
    // Forcer le consentement
    forceMarketingConsent();
    
    // Charger le pixel
    loadFacebookPixel();
    
    console.log('✅ Test forcé terminé');
    console.log('📋 Vérifiez Meta Pixel Helper dans 2-3 secondes');
}

// 4. Fonction pour tester tous les événements
function testAllEventsForced() {
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible, lancement du test forcé...');
        runForceTest();
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
        }, index * 500); // 0.5 seconde entre chaque événement
    });
    
    console.log('✅ Tous les événements programmés');
}

// Exposer les fonctions globalement
window.forceMarketingConsent = forceMarketingConsent;
window.loadFacebookPixel = loadFacebookPixel;
window.runForceTest = runForceTest;
window.testAllEventsForced = testAllEventsForced;

// Auto-test si fbq n'est pas disponible
if (typeof fbq === 'undefined') {
    console.log('🔍 Facebook Pixel non détecté, lancement automatique du test forcé...');
    setTimeout(() => {
        runForceTest();
    }, 1000);
} else {
    console.log('✅ Facebook Pixel détecté, prêt pour les tests');
}

console.log('📋 Commandes disponibles:');
console.log('  - runForceTest() : Test forcé complet');
console.log('  - forceMarketingConsent() : Forcer le consentement');
console.log('  - loadFacebookPixel() : Charger le pixel manuellement');
console.log('  - testAllEventsForced() : Tester tous les événements'); 