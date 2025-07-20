/**
 * Vérification rapide du Facebook Pixel
 * Script simple pour diagnostiquer immédiatement le problème
 */

console.log('🔍 === VÉRIFICATION RAPIDE FACEBOOK PIXEL ===');

// 1. Vérifier si fbq existe
if (typeof fbq === 'undefined') {
    console.log('❌ PROBLÈME: fbq n\'est pas défini');
    console.log('🔧 CAUSE: Le script Facebook Pixel n\'est pas chargé');
    console.log('🔧 SOLUTION: Vérifier le consentement marketing');
    
    // Vérifier les cookies
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
    }, {});
    
    console.log('🍪 Cookies de consentement:', cookies);
    console.log('🎯 Consentement marketing:', cookies['cookie_consent_marketing']);
    
    if (cookies['cookie_consent_marketing'] !== 'true') {
        console.log('💡 SOLUTION: Accepter les cookies marketing dans la bannière');
        console.log('💡 OU: Taper simulateMarketingConsent() dans la console');
    }
} else {
    console.log('✅ fbq est défini');
    
    // 2. Tester un événement
    try {
        fbq('track', 'TestEvent', { test: true });
        console.log('✅ Événement de test envoyé');
        console.log('📋 Vérifiez Meta Pixel Helper pour voir l\'événement');
    } catch (e) {
        console.log('❌ Erreur lors de l\'envoi:', e.message);
    }
}

// 3. Vérifier les scripts chargés
const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
const fbScripts = scripts.filter(s => s.includes('facebook') || s.includes('fbevents'));
console.log('📜 Scripts Facebook chargés:', fbScripts);

if (fbScripts.length === 0) {
    console.log('❌ Aucun script Facebook détecté');
} else {
    console.log('✅ Scripts Facebook détectés');
}

console.log('🔍 === FIN VÉRIFICATION ==='); 