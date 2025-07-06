/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './saga/templates/**/*.html',  // ✅ Inclure les templates Django
    './saga/**/templates/**/*.html',  // ✅ Pour toutes les apps Django
    './static/**/*.js',  // ✅ Inclure les fichiers JS si vous avez du DOM dynamic
    './static/**/*.css',  // ✅ Optionnel, si vous avez des styles CSS personnalisés
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', 'sans-serif'],
        bitter: ['"Bitter"', 'serif'],
      },
      colors: {
        new: '#22C55E', // green-500
        promo: '#EF4444', // red-500
        popular: '#FACC15', // yellow-400
        stock: '#9333EA', // purple-600
        salam: '#F59E0B', // amber-500 - Jaune pour SALAM
        classic: '#10B981', // emerald-500 - Vert pour CLASSIQUE
        warranty: '#3B82F6', // blue-500 - Bleu pour garantie
        // Cartes avec couleurs très claires et élégantes
        'card-clothing': '#f5f0ff', // Violet très clair, élégant pour vêtements
        'card-fabric': '#f0fdf4', // Vert très clair, naturel pour tissus
        'card-phone': '#eff6ff', // Bleu très clair, technologique pour téléphones
        'card-cultural': '#fef3c7', // Jaune très clair, chaleureux pour culture
        'card-product': '#ffffff', // Blanc pour produits génériques
        // Variantes hover pour les cartes
        'card-clothing-hover': '#ede9fe', // Violet hover plus prononcé
        'card-fabric-hover': '#dcfce7', // Vert hover plus prononcé
        'card-phone-hover': '#dbeafe', // Bleu hover plus prononcé
        'card-cultural-hover': '#fde68a', // Jaune hover plus prononcé
        'card-product-hover': '#f8fafc', // Gris très clair pour hover
        // Couleurs de bordure pour les cartes
        'card-clothing-border': '#c084fc', // Bordure violette
        'card-fabric-border': '#34d399', // Bordure verte
        'card-phone-border': '#60a5fa', // Bordure bleue
        'card-cultural-border': '#fbbf24', // Bordure jaune
        'card-product-border': '#e2e8f0', // Bordure grise
      },
      animation: {
        wiggle: 'wiggle 0.5s ease-in-out',
        spin: 'spin 0.5s ease-in-out',
        borderPulse: 'border-pulse 0.5s ease-in-out',
        cardHover: 'card-hover 0.3s ease-in-out',
      },
      keyframes: {
        wiggle: {
          '0%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-5px)' },
          '50%': { transform: 'translateX(5px)' },
          '75%': { transform: 'translateX(-5px)' },
          '100%': { transform: 'translateX(0)' },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '50%': { transform: 'rotate(15deg)' },
          '100%': { transform: 'rotate(0deg)' },
        },
        borderPulse: {
          '0%': { borderColor: 'transparent' },
          '50%': { borderColor: '#FFD700' },
          '100%': { borderColor: '#50C878' },
        },
        cardHover: {
          '0%': { transform: 'translateY(0)', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' },
          '100%': { transform: 'translateY(-2px)', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' },
        },
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-clothing': '0 1px 3px 0 rgba(147, 51, 234, 0.1), 0 1px 2px 0 rgba(147, 51, 234, 0.06)',
        'card-fabric': '0 1px 3px 0 rgba(34, 197, 94, 0.1), 0 1px 2px 0 rgba(34, 197, 94, 0.06)',
        'card-phone': '0 1px 3px 0 rgba(59, 130, 246, 0.1), 0 1px 2px 0 rgba(59, 130, 246, 0.06)',
        'card-cultural': '0 1px 3px 0 rgba(250, 204, 21, 0.1), 0 1px 2px 0 rgba(250, 204, 21, 0.06)',
        'card-product': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
  ],
} 