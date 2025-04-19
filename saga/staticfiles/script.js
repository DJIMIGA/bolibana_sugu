// bouton de basculement pour le menu homme femme femmé/ouvert
document.addEventListener("DOMContentLoaded", function () {
    // Gestionnaire générique pour l'affichage/masquage des menus
    function setupMenu(toggleButtonId, menuContentId) {
        const toggleButton = document.getElementById(toggleButtonId);
        const menuContent = document.getElementById(menuContentId);

        // Assurez-vous que le menu est caché au départ
        menuContent.classList.add("hidden");

        // Fonction pour afficher le menu
        function showMenu() {
            menuContent.classList.remove("hidden");
            menuContent.classList.add("block");
            toggleButton.setAttribute("aria-expanded", "true");
        }

        // Fonction pour cacher le menu
        function hideMenu() {
            menuContent.classList.add("hidden");
            menuContent.classList.remove("block");
            toggleButton.setAttribute("aria-expanded", "false");
        }

        // Gestion du clic sur le bouton
        toggleButton.addEventListener("click", function () {
            const isExpanded = toggleButton.getAttribute("aria-expanded") === "true";
            if (isExpanded) {
                hideMenu();
            } else {
                showMenu();
            }
        });

        // Gestion du survol (mouseover et mouseleave)
        toggleButton.addEventListener("mouseover", showMenu);
        menuContent.addEventListener("mouseover", showMenu);

        toggleButton.addEventListener("mouseleave", function (event) {
            if (!menuContent.contains(event.relatedTarget)) {
                hideMenu();
            }
        });

        menuContent.addEventListener("mouseleave", function (event) {
            if (!toggleButton.contains(event.relatedTarget)) {
                hideMenu();
            }
        });

        // Optionnel : Fermer le menu si on clique à l'extérieur
        document.addEventListener("click", function (event) {
            if (!toggleButton.contains(event.target) && !menuContent.contains(event.target)) {
                hideMenu();
            }
        });
    }

    // Initialiser les menus pour "Mode femme" et "Mode homme"
    setupMenu("toggleButton", "menuContent");
    setupMenu("toggleButton-2", "menuContent2");
    setupMenu("toggleButton-3", "menuContent3");
    setupMenu("toggleButton-4", "menuContent4");
    setupMenu("toggleButton-5", "menuContent5");
    setupMenu("toggleButton-6", "menuContent6");
});

// Ici, vous pouvez implémenter la logique pour ouvrir la vue rapide d'un produit
document.addEventListener('DOMContentLoaded', function() {
  const productItems = document.querySelectorAll('.product-item');

  productItems.forEach(item => {
    const quickViewBtn = item.querySelector('.quick-view-btn');
    const productLink = item.querySelector('.product-link');

    quickViewBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      openQuickView(this.href);
    });

    item.addEventListener('click', function(e) {
      if (e.target === quickViewBtn || quickViewBtn.contains(e.target)) {
        return;
      }
      productLink.click();
    });
  });


  function openQuickView(url) {

    // Par exemple, en utilisant une requête AJAX pour charger le contenu dans une modale
    fetch(url)
      .then(response => response.text())
      .then(html => {
        // Créez une modale et insérez le HTML reçu
        const modal = document.createElement('div');
        modal.innerHTML = html;
        modal.classList.add('modal');
        document.body.appendChild(modal);

        // Ajoutez la logique pour fermer la modale
        const closeBtn = modal.querySelector('.close-modal');
        if (closeBtn) {
          closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
          });
        }
      })
      .catch(error => console.error('Error:', error));
  }
});

// pour les étoiles de notation des produits formulaire de notation des produits
document.addEventListener('DOMContentLoaded', function() {
  const starRating = document.getElementById('star-rating');
  const ratingText = document.getElementById('rating-text');
  const stars = starRating.querySelectorAll('label');
  const inputs = starRating.querySelectorAll('input[type="radio"]');

  function updateStars(rating) {
    stars.forEach((star, index) => {
      if (index < rating) {
        star.textContent = '★'; // Étoile pleine
        star.classList.add('text-yellow-400');
      } else {
        star.textContent = '☆'; // Étoile vide
        star.classList.remove('text-yellow-400');
      }
    });
  }

// pour les étoiles de notation des produits formulaire de notation des produits
  function updateRatingText(rating) {
    const texts = ['Sélectionnez une note', 'Terrible', 'Mauvais', 'Correct', 'Bien', 'Excellent'];
    ratingText.textContent = texts[rating];
  }

  starRating.addEventListener('mouseover', (e) => {
    if (e.target.tagName === 'LABEL') {
      const rating = parseInt(e.target.getAttribute('for').split('-')[0]);
      updateStars(rating);
      updateRatingText(rating);
    }
  });

  starRating.addEventListener('mouseout', () => {
    const checkedInput = Array.from(inputs).find(input => input.checked);
    const rating = checkedInput ? parseInt(checkedInput.value) : 0;
    updateStars(rating);
    updateRatingText(rating);
  });

  starRating.addEventListener('click', (e) => {
    if (e.target.tagName === 'LABEL') {
      const rating = parseInt(e.target.getAttribute('for').split('-')[0]);
      updateStars(rating);
      updateRatingText(rating);

      // Mettre à jour l'input radio correspondant
      const input = starRating.querySelector(`input[type="radio"][value="${rating}"]`);
      if (input) {
        input.checked = true; // Coche l'input radio correspondant
      }
    }
  });

  // Initialisation
  updateRatingText(0);
});


// pour les images de produits et la galerie d'images
function changeMainImage(imageUrl, button) {
    // Mettre à jour l'image principale
    const mainImage = document.getElementById('main-image');
    mainImage.src = imageUrl;

    // Optionnel : Mettre à jour l'état visuel des boutons
    const tabs = document.querySelectorAll('[role="tab"]');
    tabs.forEach(tab => {
      tab.setAttribute('aria-selected', 'false');
      tab.classList.remove('ring-indigo-500'); // Retirer la classe de sélection
      tab.classList.add('ring-transparent'); // Ajouter la classe non sélectionnée
    });

    // Mettre à jour le bouton sélectionné
    button.setAttribute('aria-selected', 'true');
    button.classList.remove('ring-transparent'); // Retirer la classe non sélectionnée
    button.classList.add('ring-indigo-500'); // Ajouter la classe de sélection
  }

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    const quickViewContent = document.getElementById('quick-view-content');

    document.body.addEventListener('click', function(event) {
        if (event.target.id === 'quick-view-btn' || event.target.closest('#quick-view-btn')) {
            console.log("Close button clicked");
            if (quickViewContent) {
                quickViewContent.style.display = 'none';
            }
        }
    });
});

// pour ouvrir et fermer le menu mobile
document.addEventListener("DOMContentLoaded", () => {
    const openButton = document.getElementById("openMenuButton"); // Bouton pour ouvrir
    const closeButton = document.getElementById("closeMenuButton"); // Bouton pour fermer
    const menu = document.getElementById("mobileMenu"); // Menu mobile
    const overlay = document.getElementById("menuOverlay"); // Overlay sombre
    const body = document.body;

    // Fonction pour ouvrir le menu
    const openMenu = () => {
        menu.classList.remove("hidden"); // Affiche le menu en retirant "hidden"
        menu.classList.add("translate-x-0"); // Applique l'animation d'ouverture
        overlay.classList.remove("opacity-0", "invisible"); // Affiche l'overlay
        overlay.classList.add("opacity-100", "visible");
        body.style.overflow = "hidden"; // Désactive le scroll arrière-plan
    };

    // Fonction pour fermer le menu
    const closeMenu = () => {
        menu.classList.add("hidden"); // Cache le menu
        menu.classList.remove("translate-x-0"); // Enlève l'animation de déplacement
        overlay.classList.remove("opacity-100", "visible"); // Cache l'overlay
        overlay.classList.add("opacity-0", "invisible");
        body.style.overflow = ""; // Réactive le scroll
    };

    // Événements
    openButton.addEventListener("click", openMenu);
    closeButton.addEventListener("click", closeMenu);
    overlay.addEventListener("click", closeMenu); // Fermer le menu en cliquant sur l'overlay
});



// pour les onglets menu latéral hihgtech et maison
document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll("[role='tab']");
    const panels = document.querySelectorAll("[role='tabpanel']");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // Désélectionne tous les onglets et panels
            tabs.forEach(t => t.classList.remove("text-indigo-600", "border-indigo-600"));
            panels.forEach(panel => panel.classList.add("hidden"));

            // Active l'onglet cliqué et son panel associé
            tab.classList.add("text-indigo-600", "border-indigo-600");
            const targetPanel = document.getElementById(tab.getAttribute("aria-controls"));
            targetPanel.classList.remove("hidden");
        });
    });
});



// pour le modal de recherche mobile et desktop
document.addEventListener('DOMContentLoaded', () => {
    function setupSearchModal(modalId, openButtonId, closeButtonId, inputId, formId, resultsId) {
        const openSearchButton = document.getElementById(openButtonId);
        const searchModal = document.getElementById(modalId);
        const closeSearchButton = document.getElementById(closeButtonId);
        const searchInput = document.getElementById(inputId);
        const searchForm = document.getElementById(formId);
        const results = document.getElementById(resultsId);

        function openSearch() {
            searchModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            setTimeout(() => searchInput.focus(), 100);
        }

        function closeSearch() {
            searchModal.classList.add('hidden');
            document.body.style.overflow = '';
            searchInput.value = '';
            results.classList.add('hidden');
            results.innerHTML = '';
        }

        if (openSearchButton) {
            openSearchButton.addEventListener('click', (event) => {
                event.preventDefault();
                openSearch();
            });
        }

        if (closeSearchButton) {
            closeSearchButton.addEventListener('click', (event) => {
                event.preventDefault();
                closeSearch();
            });
        }

        searchModal.addEventListener('click', (event) => {
            if (event.target === searchModal) {
                closeSearch();
            }
        });

        if (searchForm) {
            searchForm.addEventListener('submit', (event) => {
                event.preventDefault();
            });
        }

        searchInput.addEventListener('htmx:afterRequest', (event) => {
            if (searchInput.value.trim() !== '') {
                results.classList.remove('hidden');
            } else {
                results.classList.add('hidden');
            }
        });

        searchInput.addEventListener('input', (event) => {
            if (event.target.value.trim() === '') {
                results.classList.add('hidden');
            }
        });
    }

    // Setup for desktop
    setupSearchModal('search-modal-desktop', 'open-search-modal-desktop', 'close-search-modal-desktop', 'search-input-desktop', 'form-desktop', 'results-desktop');

    // Setup for mobile
    setupSearchModal('search-modal', 'open-search-modal', 'close-search-modal', 'search-input', 'form', 'results');

    // Close modals when pressing Escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('#search-modal-desktop, #search-modal');
            modals.forEach(modal => {
                if (!modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    document.body.style.overflow = '';
                }
            });
        }
    });
});

  // Fonction pour afficher le menu de profil
document.addEventListener('DOMContentLoaded', function() {
    const profileButton = document.getElementById('profileButton');
    const profileMenu = document.getElementById('profileMenu');
    let isOpen = false;

    // Fonction pour ouvrir le menu
    function openMenu() {
    console.log('openMenu est appelée');
      profileMenu.classList.remove('hidden', 'opacity-0', 'scale-95');
      profileMenu.classList.add('opacity-100', 'scale-100');
      isOpen = true;
    }

    // Fonction pour fermer le menu
    function closeMenu() {
      profileMenu.classList.add('opacity-0', 'scale-95');
      isOpen = false;

      // Attendre la fin de l'animation avant de cacher complètement
      setTimeout(() => {
        if (!isOpen) {
          profileMenu.classList.add('hidden');
        }
      }, 300);
    }

    // Ouvrir/fermer le menu au clic sur le bouton
    profileButton.addEventListener('click', function(e) {
      e.stopPropagation();
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    // Fermer le menu au clic en dehors
    document.addEventListener('click', function(e) {
      if (isOpen && !profileMenu.contains(e.target) && e.target !== profileButton) {
        closeMenu();
      }
    });

    // Fermer le menu avec la touche Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && isOpen) {
        closeMenu();
      }
    });
  });















