/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/templates/**/*.html",
    "./src/**/static/**/*.js",
  ],
  darkMode: 'class', // Active le mode sombre avec la classe 'dark'
  theme: {
    extend: {
      colors: {
        // Palette minimaliste eneky - Mode clair
        'gray-bg': '#F5F5F5',      // Fond principal
        'gray-light': '#FAFAFA',    // Fond cards/sections
        'gray-border': '#E5E5E5',   // Bordures subtiles
        'text-primary': '#4A4A4A',  // Texte principal
        'text-secondary': '#6B7280', // Texte secondaire
        'text-muted': '#9CA3AF',    // Texte discret
        'accent': '#2563EB',        // Accent bleu (liens, boutons)
        'accent-hover': '#1D4ED8',  // Accent hover
        
        // Palette dark mode
        'dark-bg': '#1A1A1A',       // Fond principal sombre
        'dark-card': '#2D2D2D',     // Fond cards sombres
        'dark-border': '#404040',   // Bordures sombres
        'dark-text-primary': '#F5F5F5', // Texte principal sombre
        'dark-text-secondary': '#D1D5DB', // Texte secondaire sombre
        'dark-text-muted': '#9CA3AF',    // Texte discret sombre
        'dark-accent': '#3B82F6',        // Accent bleu sombre
        'dark-accent-hover': '#2563EB',  // Accent hover sombre
      },
      fontFamily: {
        'marianne': ['Marianne', 'system-ui', 'sans-serif'],
        'sans': ['Marianne', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'soft': '0 2px 8px 0 rgba(0, 0, 0, 0.06)',
        'card': '0 4px 12px 0 rgba(0, 0, 0, 0.08)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
