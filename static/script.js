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
  
  // Vérifier si l'élément existe avant de continuer
  if (!starRating) {
    console.log('Star rating element not found, skipping star rating initialization');
    return;
  }
  
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
    if (ratingText) {
      ratingText.textContent = texts[rating];
    }
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





















