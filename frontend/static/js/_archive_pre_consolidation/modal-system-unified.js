/**
 * Unified Modal System for CoderWiki
 * Replaces all existing modal systems with a single, clean implementation
 * 
 * Architecture Principles:
 * 1. Single Responsibility: One system handles all modal functionality
 * 2. Bootstrap Integration: Enhances rather than replaces Bootstrap modals
 * 3. Zero Conflicts: No overlapping z-index or DOM manipulation
 * 4. Minimal API: Simple, intuitive interface
 * 5. Accessibility First: WCAG 2.1 compliant
 */

class UnifiedModalSystem {
    constructor() {
        this.version = '1.0.0';
        this.activeModal = null;
        this.modalStack = [];
        this.lastFocusedElement = null;
        this.isInitialized = false;
        
        // Configuration
        this.config = {
            defaultBackdrop: true,
            defaultKeyboard: true,
            defaultFocus: true,
            zIndexBase: 1050, // Bootstrap's modal z-index
            animationDuration: 150
        };
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.setupBootstrapEventHandlers();
        this.setupGlobalKeyboardHandlers();
        this.enhanceExistingModals();
        this.preventOverlayConflicts();
        
        this.isInitialized = true;
        console.log(`UnifiedModalSystem v${this.version} initialized`);
    }
    
    /**
     * Bootstrap Modal Event Integration
     * Works with existing Bootstrap modals without conflicts
     */
    setupBootstrapEventHandlers() {
        // Listen for Bootstrap modal events
        document.addEventListener('show.bs.modal', (e) => this.handleModalShow(e));
        document.addEventListener('shown.bs.modal', (e) => this.handleModalShown(e));
        document.addEventListener('hide.bs.modal', (e) => this.handleModalHide(e));
        document.addEventListener('hidden.bs.modal', (e) => this.handleModalHidden(e));
    }
    
    handleModalShow(e) {
        const modal = e.target;
        
        // Store current focus
        this.lastFocusedElement = document.activeElement;
        
        // Add to modal stack
        if (!this.modalStack.includes(modal)) {
            this.modalStack.push(modal);
        }
        this.activeModal = modal;
        
        // Prepare modal for accessibility
        this.prepareModalAccessibility(modal);
        
        console.log('Modal opening:', modal.id);
    }
    
    handleModalShown(e) {
        const modal = e.target;
        
        // Setup focus management
        this.setupFocusManagement(modal);
        
        // Focus first interactive element
        this.focusFirstElement(modal);
        
        console.log('Modal opened:', modal.id);
    }
    
    handleModalHide(e) {
        const modal = e.target;
        console.log('Modal closing:', modal.id);
    }
    
    handleModalHidden(e) {
        const modal = e.target;
        
        // Remove from stack
        const index = this.modalStack.indexOf(modal);
        if (index > -1) {
            this.modalStack.splice(index, 1);
        }
        
        // Update active modal
        this.activeModal = this.modalStack.length > 0 ? 
            this.modalStack[this.modalStack.length - 1] : null;
        
        // Restore focus if no modals are open
        this.restoreFocus();
        
        console.log('Modal closed:', modal.id);
    }
    
    /**
     * Accessibility Enhancement
     * Ensures all modals meet WCAG 2.1 standards
     */
    prepareModalAccessibility(modal) {
        // Ensure proper ARIA attributes
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        
        // Link title if present
        const title = modal.querySelector('.modal-title');
        if (title && !modal.getAttribute('aria-labelledby')) {
            if (!title.id) {
                title.id = `modal-title-${Date.now()}`;
            }
            modal.setAttribute('aria-labelledby', title.id);
        }
        
        // Ensure close buttons have labels
        const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            if (!btn.getAttribute('aria-label') && !btn.textContent.trim()) {
                btn.setAttribute('aria-label', '关闭对话框');
            }
        });
    }
    
    /**
     * Focus Management
     * Handles tab navigation and focus restoration
     */
    setupFocusManagement(modal) {
        // Get focusable elements
        const focusableElements = this.getFocusableElements(modal);
        
        // Store for tab navigation
        modal._focusableElements = focusableElements;
        
        // Setup tab trap if needed
        if (focusableElements.length > 1) {
            this.setupTabTrap(modal, focusableElements);
        }
    }
    
    getFocusableElements(container) {
        const selectors = [
            'button:not([disabled]):not([tabindex="-1"])',
            'input:not([disabled]):not([tabindex="-1"])',
            'select:not([disabled]):not([tabindex="-1"])',
            'textarea:not([disabled]):not([tabindex="-1"])',
            'a[href]:not([tabindex="-1"])',
            '[tabindex]:not([tabindex="-1"]):not([disabled])'
        ];
        
        return Array.from(container.querySelectorAll(selectors.join(',')))
            .filter(el => this.isVisible(el));
    }
    
    isVisible(element) {
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               element.offsetParent !== null;
    }
    
    setupTabTrap(modal, focusableElements) {
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        modal._tabHandler = (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };
        
        modal.addEventListener('keydown', modal._tabHandler);
    }
    
    focusFirstElement(modal) {
        const focusableElements = modal._focusableElements || [];
        if (focusableElements.length > 0) {
            // Delay focus to ensure modal is fully rendered
            setTimeout(() => {
                focusableElements[0].focus();
            }, this.config.animationDuration);
        }
    }
    
    restoreFocus() {
        if (this.modalStack.length === 0 && this.lastFocusedElement) {
            setTimeout(() => {
                if (this.lastFocusedElement && 
                    document.contains(this.lastFocusedElement)) {
                    this.lastFocusedElement.focus();
                }
                this.lastFocusedElement = null;
            }, this.config.animationDuration);
        }
    }
    
    /**
     * Global Keyboard Handlers
     */
    setupGlobalKeyboardHandlers() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.closeActiveModal();
            }
        });
    }
    
    /**
     * Prevent Overlay Conflicts
     * Removes problematic overlays and prevents their creation
     */
    preventOverlayConflicts() {
        // Remove any existing problematic overlays
        this.cleanupOverlays();
        
        // Monitor for new overlay creation
        this.observeOverlayCreation();
    }
    
    cleanupOverlays() {
        // Remove high z-index overlays that might block interaction
        const problematicSelectors = [
            '#ui-init-progress',
            '.loading-overlay',
            '.user-feedback-overlay',
            '.modal-focus-overlay'
        ];
        
        problematicSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el.style.zIndex > 10000) {
                    console.log('Removing problematic overlay:', selector);
                    el.remove();
                }
            });
        });
    }
    
    observeOverlayCreation() {
        // Observe DOM for new high z-index elements
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        const style = window.getComputedStyle(node);
                        if (style.position === 'fixed' && 
                            parseInt(style.zIndex) > 10000 &&
                            !node.classList.contains('modal') &&
                            !node.classList.contains('modal-backdrop')) {
                            console.warn('High z-index overlay detected:', node);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * Modal Enhancement
     * Fixes common input and interaction issues
     */
    enhanceExistingModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            this.enhanceModalElements(modal);
        });
    }
    
    enhanceModalElements(modal) {
        // Ensure all inputs are properly interactive
        const inputs = modal.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            // Remove any blocking styles
            input.style.pointerEvents = '';
            input.style.zIndex = '';
            
            // Ensure input is enabled if not explicitly disabled
            if (!input.hasAttribute('data-keep-disabled')) {
                input.disabled = false;
                input.readOnly = false;
            }
        });
        
        // Ensure all buttons are interactive
        const buttons = modal.querySelectorAll('button, .btn');
        buttons.forEach(button => {
            button.style.pointerEvents = '';
            button.style.zIndex = '';
            
            if (!button.hasAttribute('data-keep-disabled')) {
                button.disabled = false;
            }
        });
    }
    
    /**
     * Public API Methods
     */
    show(modalSelector, options = {}) {
        const modal = typeof modalSelector === 'string' ? 
            document.querySelector(modalSelector) : modalSelector;
        
        if (!modal) {
            console.warn('Modal not found:', modalSelector);
            return null;
        }
        
        // Create Bootstrap instance if needed
        let bsModal = bootstrap.Modal.getInstance(modal);
        if (!bsModal) {
            bsModal = new bootstrap.Modal(modal, {
                backdrop: options.backdrop !== false,
                keyboard: options.keyboard !== false,
                focus: options.focus !== false
            });
        }
        
        bsModal.show();
        return bsModal;
    }
    
    hide(modalSelector) {
        const modal = typeof modalSelector === 'string' ? 
            document.querySelector(modalSelector) : modalSelector;
        
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
    
    closeActiveModal() {
        if (this.activeModal) {
            this.hide(this.activeModal);
        }
    }
    
    getActiveModal() {
        return this.activeModal;
    }
    
    hideAll() {
        [...this.modalStack].forEach(modal => {
            this.hide(modal);
        });
    }
}

// Initialize the unified system
let unifiedModalSystem;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        unifiedModalSystem = new UnifiedModalSystem();
    });
} else {
    unifiedModalSystem = new UnifiedModalSystem();
}

// Export to global scope
window.UnifiedModalSystem = UnifiedModalSystem;
window.unifiedModalSystem = unifiedModalSystem;

// Backward compatibility API
window.showModal = (selector, options) => unifiedModalSystem?.show(selector, options);
window.hideModal = (selector) => unifiedModalSystem?.hide(selector);
window.toggleModal = (selector, options) => {
    const modal = document.querySelector(selector);
    if (modal && modal.classList.contains('show')) {
        unifiedModalSystem?.hide(selector);
    } else {
        unifiedModalSystem?.show(selector, options);
    }
};

// Legacy compatibility
window.modalSystem = unifiedModalSystem;