/**
 * Script de diagnostic complet pour Facebook Pixel
 * À utiliser pour identifier les problèmes avec Meta Pixel Helper
 */

// Fonction de diagnostic principal
function diagnoseFacebookPixel() {
    console.log('🔍 === DIAGNOSTIC FACEBOOK PIXEL ===');
    
    // 1. Vérifier si fbq est défini
    if (typeof fbq === 'undefined') {
        console.log('❌ ERREUR: fbq n\'est pas défini');
        console.log('🔧 Solutions possibles:');
        console.log('   - Vérifier que le consentement marketing est donné');
        console.log('   - Vérifier que le script Facebook Pixel est chargé');
        console.log('   - Vérifier la console pour les erreurs JavaScript');
        return false;
    }
    
    console.log('✅ fbq est défini');
    
    // 2. Vérifier si fbq est une fonction
    if (typeof fbq !== 'function') {
        console.log('❌ ERREUR: fbq n\'est pas une fonction');
        return false;
    }
    
    console.log('✅ fbq est une fonction');
    
    // 3. Vérifier l'ID du pixel
    try {
        // Essayer d'accéder à l'ID du pixel
        const pixelId = window._fbq && window._fbq.id;
        console.log('🎯 ID du pixel détecté:', pixelId || 'Non détecté');
        
        if (!pixelId) {
            console.log('⚠️  ID du pixel non détecté, mais cela peut être normal');
        }
    } catch (e) {
        console.log('⚠️  Impossible de récupérer l\'ID du pixel:', e.message);
    }
    
    // 4. Tester l'envoi d'un événement de test
    try {
        console.log('🧪 Test d\'envoi d\'événement...');
        fbq('track', 'TestEvent', {
            test: true,
            timestamp: new Date().toISOString()
        });
        console.log('✅ Événement de test envoyé avec succès');
    } catch (e) {
        console.log('❌ Erreur lors de l\'envoi de l\'événement:', e.message);
        return false;
    }
    
    // 5. Vérifier les erreurs dans la console
    console.log('📋 Vérifiez la console pour les erreurs JavaScript');
    console.log('📋 Vérifiez l\'onglet Network pour les requêtes vers Facebook');
    
    return true;
}

// Fonction pour forcer le rechargement du pixel
function reloadFacebookPixel() {
    console.log('🔄 Rechargement du Facebook Pixel...');
    
    // Supprimer l'ancien script s'il existe
    const existingScript = document.querySelector('script[src*="fbevents.js"]');
    if (existingScript) {
        existingScript.remove();
        console.log('🗑️  Ancien script Facebook Pixel supprimé');
    }
    
    // Recréer le script
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    script.onload = function() {
        console.log('✅ Script Facebook Pixel rechargé');
        // Réinitialiser le pixel
        if (typeof fbq !== 'undefined') {
            fbq('init', '2046663719482491');
            fbq('track', 'PageView');
            console.log('🎯 Facebook Pixel réinitialisé');
        }
    };
    script.onerror = function() {
        console.log('❌ Erreur lors du rechargement du script Facebook Pixel');
    };
    
    document.head.appendChild(script);
}

// Fonction pour vérifier le consentement des cookies
function checkCookieConsent() {
    console.log('🍪 === VÉRIFICATION CONSENTEMENT COOKIES ===');
    
    // Vérifier les cookies de consentement
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
    }, {});
    
    console.log('🍪 Cookies de consentement:', cookies);
    
    // Vérifier spécifiquement le consentement marketing
    const marketingConsent = cookies['cookie_consent_marketing'];
    console.log('🎯 Consentement marketing:', marketingConsent);
    
    if (marketingConsent === 'true') {
        console.log('✅ Consentement marketing donné');
    } else {
        console.log('❌ Consentement marketing non donné');
        console.log('🔧 Pour tester: accepter les cookies marketing dans la bannière');
    }
    
    return marketingConsent === 'true';
}

// Fonction pour simuler le consentement (développement uniquement)
function simulateMarketingConsent() {
    console.log('🧪 Simulation du consentement marketing...');
    
    // Définir le cookie de consentement
    document.cookie = 'cookie_consent_marketing=true; path=/; max-age=31536000';
    
    // Recharger la page pour appliquer le consentement
    console.log('🔄 Rechargement de la page...');
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Fonction de test complète
function runCompleteDiagnostic() {
    console.log('🚀 === DIAGNOSTIC COMPLET FACEBOOK PIXEL ===');
    
    // 1. Vérifier le consentement
    const hasConsent = checkCookieConsent();
    
    if (!hasConsent) {
        console.log('⚠️  Consentement marketing non donné - diagnostic limité');
        console.log('💡 Utilisez simulateMarketingConsent() pour tester');
        return;
    }
    
    // 2. Diagnostiquer le pixel
    const pixelOk = diagnoseFacebookPixel();
    
    if (!pixelOk) {
        console.log('🔧 Tentative de rechargement du pixel...');
        reloadFacebookPixel();
    }
    
    console.log('✅ Diagnostic terminé');
}

// Fonction pour envoyer tous les événements de test
function testAllEvents() {
    console.log('🎯 === TEST DE TOUS LES ÉVÉNEMENTS ===');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return;
    }
    
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
        }, index * 1000); // 1 seconde entre chaque événement
    });
    
    console.log('✅ Tous les événements de test programmés');
}

// Exposer les fonctions globalement
window.diagnoseFacebookPixel = diagnoseFacebookPixel;
window.reloadFacebookPixel = reloadFacebookPixel;
window.checkCookieConsent = checkCookieConsent;
window.simulateMarketingConsent = simulateMarketingConsent;
window.runCompleteDiagnostic = runCompleteDiagnostic;
window.testAllEvents = testAllEvents;

// Auto-diagnostic au chargement (en mode debug uniquement)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔍 Auto-diagnostic Facebook Pixel activé (mode développement)');
    setTimeout(() => {
        runCompleteDiagnostic();
    }, 2000);
}

console.log('📋 Commandes disponibles:');
console.log('  - runCompleteDiagnostic() : Diagnostic complet');
console.log('  - checkCookieConsent() : Vérifier le consentement');
console.log('  - diagnoseFacebookPixel() : Diagnostiquer le pixel');
console.log('  - reloadFacebookPixel() : Recharger le pixel');
console.log('  - simulateMarketingConsent() : Simuler le consentement (dev)');
console.log('  - testAllEvents() : Tester tous les événements'); 