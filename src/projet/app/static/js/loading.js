/**
 * Système de loading states
 * Gère l'affichage de spinners et l'état de chargement des formulaires
 */

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
    }

    /**
     * Affiche un spinner sur un élément
     * @param {HTMLElement} element - L'élément sur lequel afficher le spinner
     * @param {string} text - Texte à afficher (optionnel)
     * @param {string} size - Taille du spinner (sm, md, lg)
     */
    show(element, text = 'Chargement...', size = 'md') {
        const loaderId = this.generateId();
        
        // Sauvegarder l'état original
        const originalContent = element.innerHTML;
        const originalDisabled = element.disabled;
        
        // Créer le spinner
        const spinner = this.createSpinner(text, size);
        
        // Remplacer le contenu
        element.innerHTML = spinner;
        element.disabled = true;
        element.classList.add('loading');
        
        // Stocker les infos pour la restauration
        this.activeLoaders.add({
            id: loaderId,
            element: element,
            originalContent: originalContent,
            originalDisabled: originalDisabled
        });
        
        return loaderId;
    }

    /**
     * Masque le spinner et restaure l'élément
     * @param {string} loaderId - ID du loader à masquer
     */
    hide(loaderId) {
        const loader = Array.from(this.activeLoaders).find(l => l.id === loaderId);
        if (loader) {
            loader.element.innerHTML = loader.originalContent;
            loader.element.disabled = loader.originalDisabled;
            loader.element.classList.remove('loading');
            this.activeLoaders.delete(loader);
        }
    }

    /**
     * Masque tous les loaders actifs
     */
    hideAll() {
        this.activeLoaders.forEach(loader => {
            loader.element.innerHTML = loader.originalContent;
            loader.element.disabled = loader.originalDisabled;
            loader.element.classList.remove('loading');
        });
        this.activeLoaders.clear();
    }

    /**
     * Crée un élément spinner
     */
    createSpinner(text, size) {
        const sizes = {
            sm: 'w-4 h-4',
            md: 'w-6 h-6',
            lg: 'w-8 h-8'
        };

        return `
            <div class="flex items-center justify-center">
                <svg class="animate-spin ${sizes[size]} text-accent mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-sm text-text-secondary">${text}</span>
            </div>
        `;
    }

    /**
     * Génère un ID unique
     */
    generateId() {
        return 'loader_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Active le loading sur un formulaire entier
     * @param {HTMLFormElement} form - Le formulaire
     * @param {string} submitButtonText - Texte du bouton de soumission
     */
    showForm(form, submitButtonText = 'Envoi en cours...') {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            return this.show(submitButton, submitButtonText);
        }
        return null;
    }

    /**
     * Masque le loading d'un formulaire
     * @param {string} loaderId - ID du loader
     */
    hideForm(loaderId) {
        this.hide(loaderId);
    }
}

// Instance globale
const loadingManager = new LoadingManager();

// Fonction utilitaire pour gérer les formulaires
function handleFormSubmission(form, options = {}) {
    const {
        onSuccess = () => {},
        onError = () => {},
        submitText = 'Envoi en cours...',
        successMessage = 'Action réussie !',
        errorMessage = 'Une erreur est survenue'
    } = options;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const loaderId = loadingManager.showForm(form, submitText);
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method,
                body: formData
            });

            if (response.ok) {
                toastManager.success(successMessage);
                onSuccess(response);
            } else {
                const errorText = await response.text();
                toastManager.error(errorMessage);
                onError(response, errorText);
            }
        } catch (error) {
            toastManager.error('Erreur de connexion');
            onError(null, error);
        } finally {
            if (loaderId) {
                loadingManager.hide(loaderId);
            }
        }
    });
}

// Export pour utilisation dans d'autres scripts
window.loadingManager = loadingManager;
window.handleFormSubmission = handleFormSubmission;
