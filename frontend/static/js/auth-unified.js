/**
 * CoderWiki Authentication Layer
 * Consolidates: auth.js, logout.js, login-modal-fix.js
 * 🏗️ Winston's Architecture Optimization - Auth Foundation
 */

// =============================================================================
// UNIFIED AUTHENTICATION SYSTEM
// =============================================================================
class UnifiedAuthSystem {
    constructor() {
        this.config = {
            apiBaseUrl: '/api/auth',
            loginUrl: '/login',
            dashboardUrl: '/dashboard',
            tokenKey: 'auth_token',
            rememberMeKey: 'remember_me',
            debug: false
        };

        this.state = {
            currentUser: null,
            isAuthenticated: false,
            isLoading: false
        };

        this.init();
    }

    init() {
        console.log('🔐 Unified Auth System initializing...');
        this.bindEvents();
        this.checkAuthStatus();
        this.setupModalFixes();
    }

    // =============================================================================
    // EVENT BINDING
    // =============================================================================
    bindEvents() {
        // Login form submission
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Logout buttons
        document.querySelectorAll('[data-action="logout"]').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleLogout(e));
        });

        // Toggle password visibility
        const togglePasswordBtn = document.getElementById('togglePassword');
        if (togglePasswordBtn) {
            togglePasswordBtn.addEventListener('click', () => this.togglePasswordVisibility());
        }

        // Remember me functionality
        const rememberMeCheckbox = document.getElementById('rememberMe');
        if (rememberMeCheckbox) {
            const remembered = localStorage.getItem(this.config.rememberMeKey);
            rememberMeCheckbox.checked = remembered === 'true';
        }

        // Auto-fill from remember me
        this.loadRememberedCredentials();
    }

    // =============================================================================
    // LOGIN HANDLING
    // =============================================================================
    async handleLogin(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const loginData = {
            username: formData.get('username'),
            password: formData.get('password'),
            remember_me: formData.get('remember_me') === 'on'
        };

        this.setLoadingState(true);
        this.clearMessages();

        try {
            const response = await this.makeAuthRequest('/login', {
                method: 'POST',
                body: JSON.stringify(loginData)
            });

            if (response.success) {
                this.state.isAuthenticated = true;
                this.state.currentUser = response.user;
                
                // Handle remember me
                if (loginData.remember_me) {
                    this.saveCredentials(loginData.username);
                } else {
                    this.clearSavedCredentials();
                }

                this.showMessage('登录成功，正在跳转...', 'success');
                
                // Redirect after short delay
                setTimeout(() => {
                    const redirectUrl = new URLSearchParams(window.location.search).get('next') || this.config.dashboardUrl;
                    window.location.href = redirectUrl;
                }, 1000);
            } else {
                throw new Error(response.message || '登录失败');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage(error.message || '登录失败，请检查用户名和密码', 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    // =============================================================================
    // LOGOUT HANDLING
    // =============================================================================
    async handleLogout(e) {
        e.preventDefault();
        
        this.setLoadingState(true);

        try {
            await this.makeAuthRequest('/logout', {
                method: 'POST'
            });
            
            this.state.isAuthenticated = false;
            this.state.currentUser = null;
            
            // Clear any stored session data
            this.clearSavedCredentials();
            
            this.showMessage('已成功退出登录', 'success');
            
            // Redirect to login page
            setTimeout(() => {
                window.location.href = this.config.loginUrl;
            }, 1000);
            
        } catch (error) {
            console.error('Logout error:', error);
            // Even if logout fails, redirect to login
            window.location.href = this.config.loginUrl;
        } finally {
            this.setLoadingState(false);
        }
    }

    // =============================================================================
    // AUTH STATUS CHECKING
    // =============================================================================
    async checkAuthStatus() {
        try {
            const response = await this.makeAuthRequest('/status');
            
            if (response.logged_in) {
                this.state.isAuthenticated = true;
                this.state.currentUser = response.user;
                this.updateUserUI();
            } else {
                this.state.isAuthenticated = false;
                this.state.currentUser = null;
            }
        } catch (error) {
            console.warn('Auth status check failed:', error);
            this.state.isAuthenticated = false;
        }
    }

    // =============================================================================
    // UI UTILITIES
    // =============================================================================
    togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const toggleBtn = document.getElementById('togglePassword');
        
        if (passwordInput && toggleBtn) {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
            }
        }
    }

    setLoadingState(isLoading) {
        this.state.isLoading = isLoading;
        
        // Update submit button
        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = isLoading;
            submitBtn.innerHTML = isLoading 
                ? '<i class="fas fa-spinner fa-spin me-2"></i>处理中...'
                : submitBtn.dataset.originalText || submitBtn.innerHTML;
                
            if (!isLoading && !submitBtn.dataset.originalText) {
                submitBtn.dataset.originalText = submitBtn.innerHTML;
            }
        }
    }

    showMessage(message, type = 'info') {
        // Remove existing messages
        const existing = document.querySelector('.auth-message');
        if (existing) existing.remove();

        // Create new message
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show auth-message`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert message
        const container = document.querySelector('.auth-container') || document.querySelector('main .container');
        if (container) {
            container.insertAdjacentElement('afterbegin', alertDiv);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) alertDiv.remove();
            }, 5000);
        }
    }

    clearMessages() {
        document.querySelectorAll('.auth-message').forEach(msg => msg.remove());
    }

    updateUserUI() {
        // Update user display elements
        const userDisplays = document.querySelectorAll('[data-user-display]');
        userDisplays.forEach(display => {
            const field = display.dataset.userDisplay;
            if (this.state.currentUser && this.state.currentUser[field]) {
                display.textContent = this.state.currentUser[field];
            }
        });
    }

    // =============================================================================
    // REMEMBER ME FUNCTIONALITY
    // =============================================================================
    saveCredentials(username) {
        localStorage.setItem(this.config.rememberMeKey, 'true');
        localStorage.setItem('remembered_username', username);
    }

    loadRememberedCredentials() {
        if (localStorage.getItem(this.config.rememberMeKey) === 'true') {
            const username = localStorage.getItem('remembered_username');
            const usernameInput = document.getElementById('username');
            
            if (username && usernameInput) {
                usernameInput.value = username;
            }
        }
    }

    clearSavedCredentials() {
        localStorage.removeItem(this.config.rememberMeKey);
        localStorage.removeItem('remembered_username');
    }

    // =============================================================================
    // MODAL FIXES (Winston Unified System Integration)
    // =============================================================================
    setupModalFixes() {
        // Fix login modal accessibility issues using Winston Modal Dispatcher
        const loginModal = document.getElementById('loginModal');
        if (loginModal) {
            
            // Register with Winston modal dispatcher for unified handling
            if (window.modalDispatcher) {
                window.modalDispatcher.register('loginModal', {
                    onShown: () => {
                        // Custom login modal behavior
                        const firstInput = loginModal.querySelector('input:not([disabled])');
                        if (firstInput) {
                            setTimeout(() => firstInput.focus(), 100);
                        }
                    },
                    onHidden: () => {
                        this.restorePageInteractions();
                    }
                });
                console.log('🔐 Login modal registered with Winston dispatcher');
            } else {
                // Fallback for legacy compatibility
                this.setupLegacyModalHandlers(loginModal);
            }

            // Handle login form in modal
            const modalLoginForm = document.querySelector('#loginModal form');
            if (modalLoginForm) {
                modalLoginForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    await this.handleLogin(e);
                    
                    // Close modal on successful login
                    if (this.state.isAuthenticated) {
                        const modal = bootstrap.Modal.getInstance(loginModal);
                        if (modal) modal.hide();
                    }
                });
            }
        }
    }
    
    setupLegacyModalHandlers(loginModal) {
        // Legacy event handlers as backup
        loginModal.addEventListener('show.bs.modal', () => {
            loginModal.removeAttribute('aria-hidden');
        });

        loginModal.addEventListener('hide.bs.modal', () => {
            loginModal.setAttribute('aria-hidden', 'true');
        });

        loginModal.addEventListener('shown.bs.modal', () => {
            const firstInput = loginModal.querySelector('input:not([disabled])');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        });

        loginModal.addEventListener('hidden.bs.modal', () => {
            this.restorePageInteractions();
        });
    }

    restorePageInteractions() {
        // Ensure page interactions are restored after modal close
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');
        
        // Remove any orphaned backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            if (!backdrop.closest('.modal.show')) {
                backdrop.remove();
            }
        });
    }

    // =============================================================================
    // API UTILITIES
    // =============================================================================
    async makeAuthRequest(endpoint, options = {}) {
        const url = `${this.config.apiBaseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include',
            ...options
        };

        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // =============================================================================
    // PUBLIC API
    // =============================================================================
    isAuthenticated() {
        return this.state.isAuthenticated;
    }

    getCurrentUser() {
        return this.state.currentUser;
    }

    async refreshAuthStatus() {
        await this.checkAuthStatus();
        return this.state.isAuthenticated;
    }

    log(message) {
        if (this.config.debug) {
            console.log(`[Auth] ${message}`);
        }
    }
}

// =============================================================================
// GLOBAL EXPORTS
// =============================================================================
window.UnifiedAuthSystem = UnifiedAuthSystem;

// Global instance
window.authSystem = new UnifiedAuthSystem();

// Legacy compatibility
window.Auth = {
    login: (credentials) => window.authSystem.handleLogin({ preventDefault: () => {}, target: { elements: credentials } }),
    logout: () => window.authSystem.handleLogout({ preventDefault: () => {} }),
    isAuthenticated: () => window.authSystem.isAuthenticated(),
    getCurrentUser: () => window.authSystem.getCurrentUser(),
    checkAuthStatus: () => window.authSystem.checkAuthStatus()
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Auth system auto-initializes in constructor
    });
}

// =============================================================================
// GLOBAL FUNCTION WRAPPERS (for HTML onclick compatibility)
// =============================================================================
// Critical: These functions are called directly from HTML templates
window.logout = function() {
    if (window.authSystem) {
        return window.authSystem.handleLogout({ preventDefault: () => {} });
    } else {
        console.error('Auth system not initialized');
        // Fallback: direct API call
        fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
            .then(() => window.location.href = '/login')
            .catch(err => console.error('Logout failed:', err));
    }
};

window.login = function(credentials) {
    if (window.authSystem) {
        return window.authSystem.handleLogin({ 
            preventDefault: () => {}, 
            target: { elements: credentials } 
        });
    }
};

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UnifiedAuthSystem };
}

console.log('🔐 Auth Layer loaded - Winston Architecture v1.0');