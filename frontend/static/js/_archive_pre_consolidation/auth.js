/**
 * Authentication JavaScript Module
 * Handles login, logout, and authentication state management
 */

const Auth = {
    // Configuration
    config: {
        apiBaseUrl: '/api/auth',
        loginUrl: '/login',
        dashboardUrl: '/dashboard',
        tokenKey: 'auth_token',
        rememberMeKey: 'remember_me',
        debug: false
    },

    // State
    state: {
        currentUser: null,
        isAuthenticated: false,
        isLoading: false
    },

    /**
     * Initialize the authentication module
     */
    init() {
        this.bindEvents();
        this.checkAuthStatus();
        this.log('Auth module initialized');
    },

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Login form submission
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Logout button
        const logoutBtn = document.querySelector('[data-action="logout"]');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => this.handleLogout(e));
        }

        // Toggle password visibility
        const togglePasswordBtn = document.getElementById('togglePassword');
        if (togglePasswordBtn) {
            togglePasswordBtn.addEventListener('click', () => this.togglePasswordVisibility());
        }

        // Forgot password link (功能已禁用)
        /*
        const forgotPasswordLink = document.getElementById('forgotPasswordLink');
        if (forgotPasswordLink) {
            forgotPasswordLink.addEventListener('click', (e) => this.handleForgotPassword(e));
        }
        */

        // Registration form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Real-time validation for registration
        this.bindRegistrationValidation();

        // Form validation
        this.bindFormValidation();
    },

    /**
     * Handle login form submission
     */
    async handleLogin(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        const loginData = {
            username: formData.get('username'),
            password: formData.get('password'),
            remember: formData.get('remember') === 'on'
        };

        // Validate form
        if (!this.validateLoginForm(loginData)) {
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        try {
            const response = await this.apiRequest('/login', {
                method: 'POST',
                body: JSON.stringify(loginData)
            });

            if (response.success) {
                await this.handleLoginSuccess(response.user, loginData.remember);
            } else {
                this.handleLoginError(response.error || '登录失败');
            }
        } catch (error) {
            this.handleLoginError('网络错误，请稍后重试');
            this.log('Login error:', error);
        } finally {
            this.setLoadingState(false);
        }
    },

    /**
     * Handle logout
     */
    async handleLogout(e) {
        e.preventDefault();

        if (!confirm('确定要退出登录吗？')) {
            return;
        }

        try {
            await this.apiRequest('/logout', {
                method: 'POST'
            });

            this.handleLogoutSuccess();
        } catch (error) {
            this.log('Logout error:', error);
            // Even if API fails, clear local state
            this.handleLogoutSuccess();
        }
    },

    /**
     * Handle login success
     */
    async handleLoginSuccess(user, remember) {
        // Update state
        this.state.currentUser = user;
        this.state.isAuthenticated = true;

        // Store session data
        if (remember) {
            localStorage.setItem(this.config.rememberMeKey, 'true');
        } else {
            localStorage.removeItem(this.config.rememberMeKey);
        }

        // Show success message
        this.showToast('登录成功！', 'success');

        // Update UI
        this.updateAuthUI();

        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = this.config.dashboardUrl;
        }, 1000);
    },

    /**
     * Handle login error
     */
    handleLoginError(message) {
        this.showToast(message, 'error');
        this.clearLoginFormErrors();
        this.showLoginFormError(message);
    },

    /**
     * Handle logout success
     */
    handleLogoutSuccess() {
        // Clear state
        this.state.currentUser = null;
        this.state.isAuthenticated = false;

        // Clear local storage
        localStorage.removeItem(this.config.rememberMeKey);

        // Show success message
        this.showToast('已成功退出登录', 'success');

        // Update UI
        this.updateAuthUI();

        // Redirect to login page
        setTimeout(() => {
            window.location.href = this.config.loginUrl;
        }, 1000);
    },

    /**
     * Check authentication status
     */
    async checkAuthStatus() {
        try {
            const response = await this.apiRequest('/status');

            if (response.logged_in) {
                this.state.currentUser = response.user;
                this.state.isAuthenticated = true;
                this.updateAuthUI();
            } else {
                this.state.currentUser = null;
                this.state.isAuthenticated = false;
                this.updateAuthUI();
            }
        } catch (error) {
            this.log('Error checking auth status:', error);
            this.state.isAuthenticated = false;
            this.updateAuthUI();
        }
    },

    /**
     * Update authentication UI
     */
    updateAuthUI() {
        const authButtons = document.querySelectorAll('[data-auth-required]');
        const noAuthButtons = document.querySelectorAll('[data-no-auth-required]');
        const userInfo = document.querySelector('[data-user-info]');
        const userNameElements = document.querySelectorAll('[data-user-name]');
        const userEmailElements = document.querySelectorAll('[data-user-email]');

        if (this.state.isAuthenticated) {
            // Show auth-required elements
            authButtons.forEach(el => el.style.display = '');
            // Hide no-auth-required elements
            noAuthButtons.forEach(el => el.style.display = 'none');

            // Update user info
            if (userInfo) {
                userInfo.style.display = '';
            }

            if (this.state.currentUser) {
                userNameElements.forEach(el => {
                    el.textContent = this.state.currentUser.username;
                });
                userEmailElements.forEach(el => {
                    el.textContent = this.state.currentUser.email;
                });
            }
        } else {
            // Hide auth-required elements
            authButtons.forEach(el => el.style.display = 'none');
            // Show no-auth-required elements
            noAuthButtons.forEach(el => el.style.display = '');

            // Hide user info
            if (userInfo) {
                userInfo.style.display = 'none';
            }
        }
    },

    /**
     * Toggle password visibility
     */
    togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const toggleBtn = document.getElementById('togglePassword');
        const icon = toggleBtn.querySelector('i');

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    },

    /**
     * Handle forgot password (功能已禁用)
     */
    /*
    handleForgotPassword(e) {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('forgotPasswordModal'));
        modal.show();
    },
    */

    /**
     * Validate login form
     */
    validateLoginForm(data) {
        const errors = [];

        if (!data.username || data.username.trim().length < 3) {
            errors.push('用户名至少需要3个字符');
        }

        if (!data.password || data.password.length < 6) {
            errors.push('密码至少需要6个字符');
        }

        if (errors.length > 0) {
            this.showLoginFormError(errors[0]);
            return false;
        }

        return true;
    },

    /**
     * Show login form error
     */
    showLoginFormError(message) {
        const usernameField = document.getElementById('username');
        const passwordField = document.getElementById('password');

        // Clear previous errors
        this.clearLoginFormErrors();

        // Add error styling
        if (usernameField && (!usernameField.value || usernameField.value.trim().length < 3)) {
            usernameField.classList.add('is-invalid');
            const feedback = usernameField.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = '用户名至少需要3个字符';
            }
        }

        if (passwordField && (!passwordField.value || passwordField.value.length < 6)) {
            passwordField.classList.add('is-invalid');
            const feedback = passwordField.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = '密码至少需要6个字符';
            }
        }
    },

    /**
     * Clear login form errors
     */
    clearLoginFormErrors() {
        const fields = ['username', 'password'];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.classList.remove('is-invalid', 'is-valid');
                const feedback = field.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = '';
                }
            }
        });
    },

    /**
     * Set loading state
     */
    setLoadingState(isLoading) {
        this.state.isLoading = isLoading;

        const loginBtn = document.getElementById('loginBtn');
        const loadingSpinner = document.getElementById('loadingSpinner');

        if (isLoading) {
            if (loginBtn) {
                loginBtn.disabled = true;
                loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 登录中...';
            }
            if (loadingSpinner) {
                loadingSpinner.style.display = 'block';
            }
        } else {
            if (loginBtn) {
                loginBtn.disabled = false;
                loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> 登录';
            }
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
        }
    },

    /**
     * Bind form validation
     */
    bindFormValidation() {
        const usernameField = document.getElementById('username');
        const passwordField = document.getElementById('password');

        if (usernameField) {
            usernameField.addEventListener('input', () => {
                this.validateField(usernameField, usernameField.value.trim().length >= 3, '用户名至少需要3个字符');
            });
        }

        if (passwordField) {
            passwordField.addEventListener('input', () => {
                this.validateField(passwordField, passwordField.value.length >= 6, '密码至少需要6个字符');
            });
        }
    },

    /**
     * Validate individual field
     */
    validateField(field, isValid, message) {
        if (field.value.trim() === '') {
            field.classList.remove('is-valid', 'is-invalid');
            return;
        }

        if (isValid) {
            field.classList.add('is-valid');
            field.classList.remove('is-invalid');
        } else {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            const feedback = field.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = message;
            }
        }
    },

    /**
     * Handle registration form submission
     */
    async handleRegister(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        const registerData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password')
        };

        // Validate form
        if (!this.validateRegisterForm(registerData)) {
            return;
        }

        // Check terms agreement
        const agreeTerms = document.getElementById('agreeTerms');
        if (!agreeTerms || !agreeTerms.checked) {
            this.showToast('请同意服务条款和隐私政策', 'error');
            return;
        }

        // Show loading state
        this.setRegisterLoadingState(true);

        try {
            const response = await this.apiRequest('/register', {
                method: 'POST',
                body: JSON.stringify(registerData)
            });

            if (response.success) {
                await this.handleRegisterSuccess(response.user);
            } else {
                this.handleRegisterError(response.error || '注册失败');
            }
        } catch (error) {
            this.handleRegisterError('网络错误，请稍后重试');
            this.log('Registration error:', error);
        } finally {
            this.setRegisterLoadingState(false);
        }
    },

    /**
     * Handle registration success
     */
    async handleRegisterSuccess(user) {
        // Update state
        this.state.currentUser = user;
        this.state.isAuthenticated = true;

        // Show success message
        this.showToast('注册成功！正在跳转...', 'success');

        // Update UI
        this.updateAuthUI();

        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = this.config.dashboardUrl;
        }, 1500);
    },

    /**
     * Handle registration error
     */
    handleRegisterError(message) {
        this.showToast(message, 'error');
        this.clearRegisterFormErrors();
        this.showRegisterFormError(message);
    },

    /**
     * Validate registration form
     */
    validateRegisterForm(data) {
        const errors = [];

        // Username validation
        if (!data.username || data.username.trim().length < 3) {
            errors.push('用户名至少需要3个字符');
        } else if (data.username.trim().length > 20) {
            errors.push('用户名不能超过20个字符');
        } else if (!/^[a-zA-Z0-9_]+$/.test(data.username.trim())) {
            errors.push('用户名只能包含字母、数字、下划线');
        }

        // Email validation
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!data.email || !emailRegex.test(data.email.trim())) {
            errors.push('邮箱格式不正确');
        }

        // Password validation
        if (!data.password || data.password.length < 8) {
            errors.push('密码至少需要8个字符');
        } else if (data.password.length > 128) {
            errors.push('密码不能超过128个字符');
        } else if (!this.isPasswordStrong(data.password)) {
            errors.push('密码强度不足，请包含更多字符类型');
        }

        // Confirm password validation
        const confirmPassword = document.getElementById('confirmPassword')?.value;
        if (data.password !== confirmPassword) {
            errors.push('两次输入的密码不一致');
        }

        if (errors.length > 0) {
            this.showRegisterFormError(errors[0]);
            return false;
        }

        return true;
    },

    /**
     * Check password strength
     */
    isPasswordStrong(password) {
        let score = 0;

        // Length check
        if (password.length >= 12) score += 2;
        else if (password.length >= 8) score += 1;

        // Character variety
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        if (hasLower) score += 1;
        if (hasUpper) score += 1;
        if (hasDigit) score += 1;
        if (hasSpecial) score += 1;

        return score >= 3;
    },

    /**
     * Show registration form error
     */
    showRegisterFormError(message) {
        const fields = ['username', 'email', 'password', 'confirmPassword'];

        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && field.value.trim() === '') {
                field.classList.add('is-invalid');
                const feedback = field.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = '此字段为必填项';
                }
            }
        });
    },

    /**
     * Clear registration form errors
     */
    clearRegisterFormErrors() {
        const fields = ['username', 'email', 'password', 'confirmPassword'];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.classList.remove('is-invalid', 'is-valid');
                const feedback = field.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = '';
                }
            }
        });
    },

    /**
     * Set registration loading state
     */
    setRegisterLoadingState(isLoading) {
        const registerBtn = document.getElementById('registerBtn');

        if (isLoading) {
            if (registerBtn) {
                registerBtn.disabled = true;
                registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 注册中...';
            }
        } else {
            if (registerBtn) {
                registerBtn.disabled = false;
                registerBtn.innerHTML = '<i class="fas fa-user-plus"></i> 注册账户';
            }
        }
    },

    /**
     * Bind registration validation
     */
    bindRegistrationValidation() {
        // Username validation
        const usernameField = document.getElementById('username');
        if (usernameField) {
            usernameField.addEventListener('input', this.debounce(() => {
                this.validateUsernameField(usernameField);
            }, 500));

            usernameField.addEventListener('blur', () => {
                this.validateUsernameField(usernameField);
            });
        }

        // Email validation
        const emailField = document.getElementById('email');
        if (emailField) {
            emailField.addEventListener('input', this.debounce(() => {
                this.validateEmailField(emailField);
            }, 500));

            emailField.addEventListener('blur', () => {
                this.validateEmailField(emailField);
            });
        }

        // Password validation
        const passwordField = document.getElementById('password');
        if (passwordField) {
            passwordField.addEventListener('input', this.debounce(() => {
                this.validatePasswordField(passwordField);
            }, 300));

            passwordField.addEventListener('blur', () => {
                this.validatePasswordField(passwordField);
            });
        }

        // Confirm password validation
        const confirmPasswordField = document.getElementById('confirmPassword');
        if (confirmPasswordField) {
            confirmPasswordField.addEventListener('input', () => {
                this.validateConfirmPasswordField(confirmPasswordField);
            });

            confirmPasswordField.addEventListener('blur', () => {
                this.validateConfirmPasswordField(confirmPasswordField);
            });
        }

        // Password visibility toggles
        this.setupPasswordToggles();
    },

    /**
     * Setup password visibility toggles
     */
    setupPasswordToggles() {
        const togglePassword = document.getElementById('togglePassword');
        const passwordInput = document.getElementById('password');

        if (togglePassword && passwordInput) {
            togglePassword.addEventListener('click', () => {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                togglePassword.innerHTML = type === 'password' ?
                    '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
            });
        }

        const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
        const confirmPasswordInput = document.getElementById('confirmPassword');

        if (toggleConfirmPassword && confirmPasswordInput) {
            toggleConfirmPassword.addEventListener('click', () => {
                const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                confirmPasswordInput.setAttribute('type', type);
                toggleConfirmPassword.innerHTML = type === 'password' ?
                    '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
            });
        }
    },

    /**
     * Validate username field
     */
    async validateUsernameField(field) {
        const value = field.value.trim();
        const feedback = field.parentNode.querySelector('.invalid-feedback');

        field.classList.remove('is-valid', 'is-invalid');
        if (feedback) feedback.textContent = '';

        if (!value) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '用户名不能为空';
            return false;
        }

        if (value.length < 3 || value.length > 20) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '用户名长度必须在3-20位之间';
            return false;
        }

        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '用户名只能包含字母、数字、下划线';
            return false;
        }

        // Check availability (optional - would need API endpoint)
        // try {
        //     const isAvailable = await this.checkUsernameAvailability(value);
        //     if (!isAvailable) {
        //         field.classList.add('is-invalid');
        //         if (feedback) feedback.textContent = '用户名已被使用';
        //         return false;
        //     }
        // } catch (error) {
        //     this.log('Username availability check failed:', error);
        // }

        field.classList.add('is-valid');
        return true;
    },

    /**
     * Validate email field
     */
    async validateEmailField(field) {
        const value = field.value.trim();
        const feedback = field.parentNode.querySelector('.invalid-feedback');

        field.classList.remove('is-valid', 'is-invalid');
        if (feedback) feedback.textContent = '';

        if (!value) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '邮箱不能为空';
            return false;
        }

        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(value)) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '邮箱格式不正确';
            return false;
        }

        // Check availability (optional - would need API endpoint)
        // try {
        //     const isAvailable = await this.checkEmailAvailability(value);
        //     if (!isAvailable) {
        //         field.classList.add('is-invalid');
        //         if (feedback) feedback.textContent = '邮箱已被使用';
        //         return false;
        //     }
        // } catch (error) {
        //     this.log('Email availability check failed:', error);
        // }

        field.classList.add('is-valid');
        return true;
    },

    /**
     * Validate password field
     */
    validatePasswordField(field) {
        const value = field.value;
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        const strengthBar = document.getElementById('passwordStrength');
        const strengthText = document.getElementById('passwordStrengthText');

        field.classList.remove('is-valid', 'is-invalid');
        if (feedback) feedback.textContent = '';

        if (!value) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '密码不能为空';
            this.updatePasswordStrength(0, '未输入');
            return false;
        }

        if (value.length < 8) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '密码长度至少为8位';
            this.updatePasswordStrength(1, '太短');
            return false;
        }

        if (value.length > 128) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '密码长度不能超过128位';
            return false;
        }

        // Calculate and show password strength
        const strength = this.calculatePasswordStrength(value);
        this.updatePasswordStrength(strength.score, strength.text, strength.color);

        if (strength.score < 3) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '密码强度不足，请包含更多字符类型';
            return false;
        }

        field.classList.add('is-valid');
        return true;
    },

    /**
     * Validate confirm password field
     */
    validateConfirmPasswordField(field) {
        const value = field.value;
        const passwordField = document.getElementById('password');
        const feedback = field.parentNode.querySelector('.invalid-feedback');

        field.classList.remove('is-valid', 'is-invalid');
        if (feedback) feedback.textContent = '';

        if (!value) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '请确认密码';
            return false;
        }

        if (value !== passwordField.value) {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = '两次输入的密码不一致';
            return false;
        }

        field.classList.add('is-valid');
        return true;
    },

    /**
     * Calculate password strength
     */
    calculatePasswordStrength(password) {
        let score = 0;

        // Length check
        if (password.length >= 12) score += 2;
        else if (password.length >= 8) score += 1;

        // Character variety
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        if (hasLower) score += 1;
        if (hasUpper) score += 1;
        if (hasDigit) score += 1;
        if (hasSpecial) score += 1;

        // Determine strength level
        let strengthText, strengthColor;
        if (score <= 2) {
            strengthText = '弱';
            strengthColor = 'bg-danger';
        } else if (score <= 4) {
            strengthText = '中等';
            strengthColor = 'bg-warning';
        } else if (score <= 6) {
            strengthText = '强';
            strengthColor = 'bg-info';
        } else {
            strengthText = '非常强';
            strengthColor = 'bg-success';
        }

        return { score, text: strengthText, color: strengthColor };
    },

    /**
     * Update password strength indicator
     */
    updatePasswordStrength(score, text, color = 'bg-danger') {
        const strengthBar = document.getElementById('passwordStrength');
        const strengthText = document.getElementById('passwordStrengthText');

        if (strengthBar) {
            strengthBar.className = `progress-bar ${color}`;
            strengthBar.style.width = `${(score / 7) * 100}%`;
        }

        if (strengthText) {
            strengthText.textContent = `密码强度: ${text}`;
        }
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Make API request
     */
    async apiRequest(endpoint, options = {}) {
        const url = CoderWiki.config.apiBaseUrl + endpoint;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        this.log('API Request:', { url, config });

        const response = await fetch(url, config);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toastContainer = this.getToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });

        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    /**
     * Get or create toast container
     */
    getToastContainer() {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },

    /**
     * Log debug messages
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[Auth]', ...args);
        }
    }
};

// Initialize auth module when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    Auth.init();
});

// Export for global use
window.Auth = Auth;
