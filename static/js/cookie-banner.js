document.addEventListener('DOMContentLoaded', function () {
  const banner = document.getElementById('cookie-banner');
  const acceptBtn = document.getElementById('cookie-accept-btn');
  const rejectBtn = document.getElementById('cookie-reject-btn');
  const preferencesBtn = document.getElementById('cookie-preferences-btn');
  const footerPreferencesBtn = document.getElementById('footer-cookie-preferences');
  const modal = document.getElementById('cookie-preferences-modal');
  const modalCancel = document.getElementById('cookie-modal-cancel');
  const preferencesForm = document.getElementById('cookie-preferences-form');
  const analyticsCheckbox = document.getElementById('analytics-cookies');
  const marketingCheckbox = document.getElementById('marketing-cookies');

  // Fonction pour sauvegarder les préférences côté backend
  function saveCookiePreferences(analytics, marketing) {
    const formData = new FormData();
    formData.append('analytics', analytics);
    formData.append('marketing', marketing);
    
    fetch('/core/api/cookie-consent/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Recharger la page pour appliquer les nouveaux scripts
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        console.error('[Cookies] ❌ Erreur de sauvegarde');
      }
    })
    .catch(error => {
      console.error('[Cookies] ❌ Erreur:', error.message || 'Erreur inconnue');
    });
  }

  // Afficher la bannière si pas de consentement ou si choix explicite de refuser tout
  const consent = JSON.parse(localStorage.getItem('cookieConsent') || '{}');
  const hasExplicitChoice = consent.all === true || (consent.all === false && (consent.analytics === true || consent.marketing === true));
  
  if (!localStorage.getItem('cookieConsent') || !hasExplicitChoice) {
    banner.style.display = 'flex';
  }

  // Fonction pour ouvrir le modal de préférences
  function openPreferencesModal() {
    modal.classList.remove('hidden');
    // Charger les préférences existantes si elles existent
    const consent = JSON.parse(localStorage.getItem('cookieConsent') || '{}');
    analyticsCheckbox.checked = !!consent.analytics;
    marketingCheckbox.checked = !!consent.marketing;
  }

  // Accepter tous les cookies
  acceptBtn.addEventListener('click', function () {
    const consentData = {
      all: true,
      analytics: true,
      marketing: true
    };
    localStorage.setItem('cookieConsent', JSON.stringify(consentData));
    saveCookiePreferences(true, true);
    banner.style.display = 'none';
  });

  // Refuser tous les cookies non essentiels
  rejectBtn.addEventListener('click', function () {
    const consentData = {
      all: false,
      analytics: false,
      marketing: false
    };
    localStorage.setItem('cookieConsent', JSON.stringify(consentData));
    saveCookiePreferences(false, false);
    banner.style.display = 'none';
  });

  // Gérer les préférences depuis la bannière
  preferencesBtn.addEventListener('click', openPreferencesModal);

  // Gérer les préférences depuis le footer
  if (footerPreferencesBtn) {
    footerPreferencesBtn.addEventListener('click', openPreferencesModal);
  }

  // Annuler le modal
  modalCancel.addEventListener('click', function () {
    modal.classList.add('hidden');
  });

  // Enregistrer les préférences
  preferencesForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const analytics = analyticsCheckbox.checked;
    const marketing = marketingCheckbox.checked;
    
    const consentData = {
      all: false,
      analytics: analytics,
      marketing: marketing
    };
    
    localStorage.setItem('cookieConsent', JSON.stringify(consentData));
    saveCookiePreferences(analytics, marketing);
    modal.classList.add('hidden');
    banner.style.display = 'none';
  });
}); 