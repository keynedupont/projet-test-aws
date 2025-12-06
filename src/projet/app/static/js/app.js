/**
 * Script principal de l'application
 * Initialise les systèmes de toast, loading et améliore l'UX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les systèmes
    initToastSystem();
    initLoadingSystem();
    initFormEnhancements();
    initThemeToggle();
});

/**
 * Initialise le système de toast
 */
function initToastSystem() {
    // Convertir les messages d'erreur existants en toasts
    const errorMessages = document.querySelectorAll('.error-message, .alert-error');
    errorMessages.forEach(msg => {
        const message = msg.textContent.trim();
        if (message) {
            toastManager.error(message);
            msg.style.display = 'none'; // Masquer l'ancien affichage
        }
    });

    // Convertir les messages de succès existants en toasts
    const successMessages = document.querySelectorAll('.success-message, .alert-success');
    successMessages.forEach(msg => {
        const message = msg.textContent.trim();
        if (message) {
            toastManager.success(message);
            msg.style.display = 'none'; // Masquer l'ancien affichage
        }
    });
}

/**
 * Initialise le système de loading
 */
function initLoadingSystem() {
    // Ajouter des loading states aux formulaires
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.method === 'post' && !form.classList.contains('no-loading')) {
            enhanceForm(form);
        }
    });
}

/**
 * Améliore un formulaire avec loading states
 */
function enhanceForm(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;

    // Ajouter un indicateur visuel au bouton
    submitButton.classList.add('relative');
    
    form.addEventListener('submit', function(e) {
        // Ne pas empêcher la soumission normale, juste ajouter le loading
        const loaderId = loadingManager.show(submitButton, 'Envoi en cours...');
        
        // Masquer le loading après un délai (au cas où la page se recharge)
        setTimeout(() => {
            loadingManager.hide(loaderId);
        }, 10000);
    });
}

/**
 * Améliore l'UX des formulaires
 */
function initFormEnhancements() {
    // Validation en temps réel
    const inputs = document.querySelectorAll('input[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });

    // Améliorer les boutons
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.classList.add('transition-all', 'duration-200', 'hover:scale-105');
    });
}

/**
 * Valide un champ en temps réel
 */
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    // Supprimer les erreurs précédentes
    clearFieldError(e);
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'Ce champ est obligatoire');
        return false;
    }
    
    // Validation email
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Format d\'email invalide');
            return false;
        }
    }
    
    // Validation mot de passe
    if (field.type === 'password' && value && field.name === 'password') {
        if (value.length < 8) {
            showFieldError(field, 'Le mot de passe doit contenir au moins 8 caractères');
            return false;
        }
    }
    
    return true;
}

/**
 * Affiche une erreur sur un champ
 */
function showFieldError(field, message) {
    field.classList.add('border-red-500', 'focus:border-red-500');
    
    // Créer le message d'erreur
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error text-red-500 text-sm mt-1';
    errorDiv.textContent = message;
    
    // Insérer après le champ
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
}

/**
 * Supprime les erreurs d'un champ
 */
function clearFieldError(e) {
    const field = e.target;
    field.classList.remove('border-red-500', 'focus:border-red-500');
    
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Initialise le toggle de thème
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Appliquer le thème sauvegardé
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }
}

/**
 * Bascule entre les thèmes clair et sombre
 */
function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Mettre à jour l'icône du bouton
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('svg');
        if (icon) {
            icon.innerHTML = isDark ? 
                // Icône soleil (thème sombre actif)
                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>' :
                // Icône lune (thème clair actif)
                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>';
        }
    }
}

/**
 * Utilitaires pour les autres scripts
 */
window.AppUtils = {
    // Afficher un toast de succès
    showSuccess: (message) => toastManager.success(message),
    
    // Afficher un toast d'erreur
    showError: (message) => toastManager.error(message),
    
    // Afficher un toast d'info
    showInfo: (message) => toastManager.info(message),
    
    // Afficher un toast d'avertissement
    showWarning: (message) => toastManager.warning(message),
    
    // Afficher un loading
    showLoading: (element, text) => loadingManager.show(element, text),
    
    // Masquer un loading
    hideLoading: (loaderId) => loadingManager.hide(loaderId),
    
    // Valider un formulaire
    validateForm: (form) => {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField({ target: input })) {
                isValid = false;
            }
        });
        
        return isValid;
    }
};
