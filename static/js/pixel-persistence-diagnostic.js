/**
 * Script de diagnostic pour la persistance des événements Meta Pixel
 * Vérifie pourquoi les événements ne persistent pas après avoir quitté la page
 */

console.log('🔍 === DIAGNOSTIC PERSISTANCE META PIXEL ===');

// Fonction pour vérifier l'état du pixel au chargement de la page
function checkPixelOnLoad() {
    console.log('📱 === VÉRIFICATION AU CHARGEMENT DE LA PAGE ===');
    
    // Attendre que le DOM soit chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', performLoadCheck);
    } else {
        performLoadCheck();
    }
}

function performLoadCheck() {
    console.log('🔄 DOM chargé, vérification du pixel...');
    
    // Vérifier si fbq est disponible
    if (typeof fbq === 'undefined') {
        console.log('❌ fbq non disponible au chargement');
        console.log('💡 Cela peut indiquer un problème de chargement du script Facebook');
        return;
    }
    
    console.log('✅ fbq disponible au chargement');
    
    // Vérifier l'ID du pixel
    let pixelId = null;
    
    // Essayer plusieurs méthodes pour récupérer l'ID
    if (window._fbq && window._fbq.id) {
        pixelId = window._fbq.id;
    } else if (fbq._pixelId) {
        pixelId = fbq._pixelId;
    } else {
        // Rechercher dans les scripts
        const scripts = Array.from(document.querySelectorAll('script'));
        const fbScript = scripts.find(s => s.innerHTML && s.innerHTML.includes('fbevents.js'));
        if (fbScript) {
            const match = fbScript.innerHTML.match(/fbevents\.js\?id=(\d+)/);
            if (match) {
                pixelId = match[1];
            }
        }
    }
    
    if (pixelId) {
        console.log('🎯 ID du pixel détecté:', pixelId);
        if (pixelId === '2046663719482491') {
            console.log('✅ ID du pixel correct');
        } else {
            console.log('⚠️  ID du pixel incorrect');
        }
    } else {
        console.log('❌ ID du pixel non détecté');
    }
    
    // Vérifier les cookies de consentement
    checkConsentCookies();
    
    // Vérifier les scripts Facebook
    checkFacebookScripts();
    
    // Test d'événement automatique
    setTimeout(() => {
        console.log('🧪 Test d\'événement automatique...');
        if (typeof fbq !== 'undefined') {
            fbq('track', 'PageView');
            console.log('✅ PageView envoyé automatiquement');
        }
    }, 2000);
}

// Fonction pour vérifier les cookies de consentement
function checkConsentCookies() {
    console.log('🍪 === VÉRIFICATION COOKIES DE CONSENTEMENT ===');
    
    const cookies = document.cookie.split(';').map(c => c.trim());
    const consentCookies = cookies.filter(c => 
        c.includes('consent') || 
        c.includes('marketing') || 
        c.includes('analytics') ||
        c.includes('facebook')
    );
    
    console.log('📋 Cookies de consentement trouvés:', consentCookies.length);
    consentCookies.forEach((cookie, index) => {
        console.log(`   ${index + 1}. ${cookie}`);
    });
    
    // Vérifier spécifiquement le consentement marketing
    const marketingConsent = cookies.find(c => c.includes('marketing'));
    if (marketingConsent) {
        console.log('✅ Consentement marketing détecté');
    } else {
        console.log('❌ Consentement marketing non détecté');
        console.log('💡 Cela peut empêcher le chargement du pixel');
    }
}

// Fonction pour vérifier les scripts Facebook
function checkFacebookScripts() {
    console.log('📜 === VÉRIFICATION SCRIPTS FACEBOOK ===');
    
    const scripts = Array.from(document.querySelectorAll('script[src]'));
    const fbScripts = scripts.filter(s => 
        s.src.includes('facebook') || 
        s.src.includes('fbevents') ||
        s.src.includes('connect.facebook.net')
    );
    
    console.log('📋 Scripts Facebook trouvés:', fbScripts.length);
    fbScripts.forEach((script, index) => {
        console.log(`   ${index + 1}. ${script.src}`);
    });
    
    if (fbScripts.length === 0) {
        console.log('❌ Aucun script Facebook trouvé');
        console.log('💡 Le pixel ne peut pas fonctionner sans les scripts Facebook');
    } else {
        console.log('✅ Scripts Facebook chargés');
    }
}

// Fonction pour forcer le rechargement du pixel
function forcePixelReload() {
    console.log('🔄 === FORCER LE RECHARGEMENT DU PIXEL ===');
    
    // Supprimer les scripts Facebook existants
    const existingScripts = document.querySelectorAll('script[src*="facebook"], script[src*="fbevents"]');
    existingScripts.forEach(script => {
        console.log('🗑️  Suppression du script:', script.src);
        script.remove();
    });
    
    // Recréer le script Facebook
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    script.setAttribute('data-pixel-id', '2046663719482491');
    
    script.onload = function() {
        console.log('✅ Script Facebook rechargé');
        // Réinitialiser fbq
        if (typeof fbq !== 'undefined') {
            fbq('init', '2046663719482491');
            fbq('track', 'PageView');
            console.log('✅ Pixel réinitialisé et PageView envoyé');
        }
    };
    
    script.onerror = function() {
        console.log('❌ Erreur lors du rechargement du script Facebook');
    };
    
    document.head.appendChild(script);
}

// Fonction pour simuler le consentement marketing
function simulateMarketingConsent() {
    console.log('🎭 === SIMULATION CONSENTEMENT MARKETING ===');
    
    // Définir le cookie de consentement marketing
    document.cookie = 'marketing_consent=true; path=/; max-age=31536000';
    document.cookie = 'analytics_consent=true; path=/; max-age=31536000';
    
    console.log('✅ Cookies de consentement définis');
    
    // Recharger le pixel
    setTimeout(() => {
        forcePixelReload();
    }, 1000);
}

// Fonction pour vérifier l'état complet
function checkCompleteState() {
    console.log('🔍 === VÉRIFICATION ÉTAT COMPLET ===');
    
    // Vérifier fbq
    if (typeof fbq === 'undefined') {
        console.log('❌ fbq non disponible');
        return;
    }
    
    console.log('✅ fbq disponible');
    
    // Vérifier l'ID du pixel
    let pixelId = null;
    if (window._fbq && window._fbq.id) {
        pixelId = window._fbq.id;
    }
    
    if (pixelId) {
        console.log('🎯 ID du pixel:', pixelId);
    } else {
        console.log('❌ ID du pixel non détecté');
    }
    
    // Vérifier les cookies
    checkConsentCookies();
    
    // Vérifier les scripts
    checkFacebookScripts();
    
    // Test d'événement
    console.log('🧪 Test d\'événement...');
    fbq('track', 'TestEvent', { test: 'complete_state_check' });
    console.log('✅ Événement de test envoyé');
}

// Exposer les fonctions globalement
window.checkPixelOnLoad = checkPixelOnLoad;
window.forcePixelReload = forcePixelReload;
window.simulateMarketingConsent = simulateMarketingConsent;
window.checkCompleteState = checkCompleteState;

// Auto-vérification au chargement
checkPixelOnLoad();

console.log('📋 Commandes disponibles:');
console.log('  - checkPixelOnLoad() : Vérifier l\'état au chargement');
console.log('  - forcePixelReload() : Forcer le rechargement du pixel');
console.log('  - simulateMarketingConsent() : Simuler le consentement marketing');
console.log('  - checkCompleteState() : Vérification complète de l\'état'); 