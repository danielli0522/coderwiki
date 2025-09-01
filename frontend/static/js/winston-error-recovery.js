/**
 * Winston Architecture - 错误处理和降级机制
 * 提供健壮的错误恢复和优雅降级功能
 */

class WinstonErrorRecovery {
    constructor() {
        this.errors = [];
        this.recoveryAttempts = 0;
        this.maxRecoveryAttempts = 3;
        this.criticalServices = ['ApiClient', 'UnifiedUIFramework', 'UnifiedAuthSystem'];
        
        // 初始化错误统计对象
        this.errorStats = {
            jsErrors: 0,
            promiseRejections: 0,
            networkErrors: 0,
            totalErrors: 0
        };
        
        this.init();
    }
    
    init() {
        this.setupGlobalErrorHandling();
        this.setupServiceAvailabilityCheck();
        this.setupGracefulDegradation();
        this.setupEmergencyRecovery();
        
        console.log('🛡️ Winston Error Recovery System initialized');
    }
    
    // =================================================================
    // 全局错误处理
    // =================================================================
    
    setupGlobalErrorHandling() {
        // 捕获未处理的Promise拒绝
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'unhandled_promise_rejection',
                error: event.reason,
                timestamp: new Date().toISOString()
            });
        });
        
        // 捕获JavaScript错误
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript_error',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
                timestamp: new Date().toISOString()
            });
        });
        
        // 捕获资源加载错误
        window.addEventListener('error', (event) => {
            if (event.target !== window) {
                this.handleError({
                    type: 'resource_load_error',
                    source: event.target.src || event.target.href,
                    tagName: event.target.tagName,
                    timestamp: new Date().toISOString()
                });
            }
        }, true);
    }
    
    handleError(errorInfo) {
        this.errors.push(errorInfo);
        
        // 记录错误
        console.error('🚨 Winston Error Recovery:', errorInfo);
        
        // 根据错误类型采取相应措施
        switch (errorInfo.type) {
            case 'resource_load_error':
                this.handleResourceLoadError(errorInfo);
                break;
            case 'javascript_error':
                this.handleJavaScriptError(errorInfo);
                break;
            case 'unhandled_promise_rejection':
                this.handlePromiseRejection(errorInfo);
                break;
        }
        
        // 如果错误过多，触发紧急恢复
        if (this.errors.length > 10) {
            this.triggerEmergencyRecovery();
        }
    }
    
    // =================================================================
    // 资源加载错误处理
    // =================================================================
    
    handleResourceLoadError(errorInfo) {
        const source = errorInfo.source;
        
        // 检查是否是关键JS文件
        if (source && source.includes('.js')) {
            if (source.includes('api_client.js')) {
                this.provideApiClientFallback();
            } else if (source.includes('login-modal-fix.js')) {
                this.provideModalFixFallback();
            } else if (source.includes('repository-modal-fix.js')) {
                this.provideModalFixFallback();
            } else if (source.includes('disable-delete-modal.js')) {
                // 这个文件的功能已整合，不需要降级
                console.log('✅ disable-delete-modal.js 功能已整合到 ui-framework.js');
            }
        }
    }
    
    provideApiClientFallback() {
        if (typeof window.api === 'undefined' && typeof window.ApiClient === 'undefined') {
            console.log('🔧 Providing ApiClient fallback...');
            
            // 创建基本的API客户端降级版本
            window.api = {
                get: (endpoint, params = {}) => {
                    return this.basicFetch(endpoint, { method: 'GET' });
                },
                post: (endpoint, data = {}) => {
                    return this.basicFetch(endpoint, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: { 'Content-Type': 'application/json' }
                    });
                },
                put: (endpoint, data = {}) => {
                    return this.basicFetch(endpoint, {
                        method: 'PUT',
                        body: JSON.stringify(data),
                        headers: { 'Content-Type': 'application/json' }
                    });
                },
                delete: (endpoint) => {
                    return this.basicFetch(endpoint, { method: 'DELETE' });
                }
            };
            
            // 提供常用的API方法
            window.api.getUserProfile = () => window.api.get('/api/auth/profile');
            window.api.getRepositories = () => window.api.get('/api/repositories');
            window.api.getTasks = () => window.api.get('/api/tasks');
            window.api.getDocuments = () => window.api.get('/api/documents');
            window.api.getRecentDocuments = () => window.api.get('/api/documents/recent');
            
            console.log('✅ ApiClient fallback provided');
        }
    }
    
    basicFetch(endpoint, options = {}) {
        const baseUrl = '/api';
        const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
        
        return fetch(url, {
            credentials: 'include',
            ...options
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API request failed:', error);
            throw error;
        });
    }
    
    provideModalFixFallback() {
        console.log('🔧 Providing modal fix fallback...');
        
        // 基本的模态框修复功能
        document.addEventListener('DOMContentLoaded', () => {
            // 监听所有模态框
            document.querySelectorAll('.modal').forEach(modal => {
                modal.addEventListener('show.bs.modal', () => {
                    modal.removeAttribute('aria-hidden');
                });
                
                modal.addEventListener('hide.bs.modal', () => {
                    modal.setAttribute('aria-hidden', 'true');
                });
                
                modal.addEventListener('hidden.bs.modal', () => {
                    // 清理可能的残留backdrop
                    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                        if (!backdrop.closest('.modal.show')) {
                            backdrop.remove();
                        }
                    });
                    
                    // 恢复body状态
                    if (!document.querySelector('.modal.show')) {
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }
                });
            });
        });
        
        console.log('✅ Modal fix fallback provided');
    }
    
    // =================================================================
    // 服务可用性检查
    // =================================================================
    
    setupServiceAvailabilityCheck() {
        // 检查关键服务是否可用
        this.checkCriticalServices();
        
        // 定期检查服务状态
        setInterval(() => {
            this.checkCriticalServices();
        }, 30000); // 每30秒检查一次
    }
    
    checkCriticalServices() {
        const serviceStatus = {};
        
        this.criticalServices.forEach(service => {
            serviceStatus[service] = typeof window[service] !== 'undefined';
            
            if (!serviceStatus[service]) {
                this.handleMissingService(service);
            }
        });
        
        // 更新服务状态
        this.serviceStatus = serviceStatus;
        
        return serviceStatus;
    }
    
    handleMissingService(serviceName) {
        console.warn(`⚠️ Critical service missing: ${serviceName}`);
        
        switch (serviceName) {
            case 'ApiClient':
                this.provideApiClientFallback();
                break;
            case 'UnifiedUIFramework':
                this.provideUIFrameworkFallback();
                break;
            case 'UnifiedAuthSystem':
                this.provideAuthSystemFallback();
                break;
        }
    }
    
    provideUIFrameworkFallback() {
        if (typeof window.UnifiedUIFramework === 'undefined') {
            console.log('🔧 Providing UI Framework fallback...');
            
            window.UnifiedUIFramework = {
                modalSystem: {
                    show: (modalId) => {
                        const modal = document.getElementById(modalId);
                        if (modal && typeof bootstrap !== 'undefined') {
                            const bsModal = new bootstrap.Modal(modal);
                            bsModal.show();
                        }
                    },
                    hide: (modalId) => {
                        const modal = document.getElementById(modalId);
                        if (modal && typeof bootstrap !== 'undefined') {
                            const bsModal = bootstrap.Modal.getInstance(modal);
                            if (bsModal) bsModal.hide();
                        }
                    }
                },
                emergencyRecovery: () => {
                    this.performEmergencyRecovery();
                }
            };
            
            console.log('✅ UI Framework fallback provided');
        }
    }
    
    provideAuthSystemFallback() {
        if (typeof window.UnifiedAuthSystem === 'undefined') {
            console.log('🔧 Providing Auth System fallback...');
            
            window.UnifiedAuthSystem = {
                isAuthenticated: () => {
                    // 基本的认证检查
                    return document.cookie.includes('session') ||
                           localStorage.getItem('auth_token') ||
                           false;
                },
                getCurrentUser: () => {
                    return null; // 降级模式下无法获取用户信息
                },
                login: (credentials) => {
                    return window.api.post('/api/auth/login', credentials);
                },
                logout: () => {
                    return window.api.post('/api/auth/logout');
                }
            };
            
            console.log('✅ Auth System fallback provided');
        }
    }
    
    // =================================================================
    // 优雅降级机制
    // =================================================================
    
    setupGracefulDegradation() {
        // 检查浏览器支持
        this.checkBrowserSupport();
        
        // 检查网络状态
        this.checkNetworkStatus();
        
        // 设置降级策略
        this.setupDegradationStrategies();
    }
    
    checkBrowserSupport() {
        const supportStatus = {
            fetch: typeof fetch !== 'undefined',
            promise: typeof Promise !== 'undefined',
            arrow: (() => { try { eval('() => {}'); return true; } catch (e) { return false; } })(),
            modules: 'noModule' in document.createElement('script'),
            intersectionObserver: 'IntersectionObserver' in window,
            mutationObserver: 'MutationObserver' in window
        };
        
        // 为不支持的功能提供polyfill
        if (!supportStatus.fetch) {
            this.provideFetchPolyfill();
        }
        
        if (!supportStatus.promise) {
            console.warn('⚠️ Promise not supported, some features may not work');
        }
        
        this.browserSupport = supportStatus;
        return supportStatus;
    }
    
    provideFetchPolyfill() {
        if (typeof fetch === 'undefined') {
            window.fetch = (url, options = {}) => {
                return new Promise((resolve, reject) => {
                    const xhr = new XMLHttpRequest();
                    xhr.open(options.method || 'GET', url);
                    
                    // 设置请求头
                    if (options.headers) {
                        Object.keys(options.headers).forEach(key => {
                            xhr.setRequestHeader(key, options.headers[key]);
                        });
                    }
                    
                    xhr.onload = () => {
                        resolve({
                            ok: xhr.status >= 200 && xhr.status < 300,
                            status: xhr.status,
                            statusText: xhr.statusText,
                            json: () => Promise.resolve(JSON.parse(xhr.responseText)),
                            text: () => Promise.resolve(xhr.responseText)
                        });
                    };
                    
                    xhr.onerror = () => reject(new Error('Network request failed'));
                    xhr.send(options.body);
                });
            };
            
            console.log('✅ Fetch polyfill provided');
        }
    }
    
    checkNetworkStatus() {
        // 检查在线状态
        if (navigator.onLine === false) {
            this.handleOfflineMode();
        }
        
        // 监听网络状态变化
        window.addEventListener('online', () => {
            console.log('📶 Network back online');
            this.handleOnlineMode();
        });
        
        window.addEventListener('offline', () => {
            console.log('📵 Network went offline');
            this.handleOfflineMode();
        });
    }
    
    handleOfflineMode() {
        console.log('🔧 Switching to offline mode...');
        
        // 显示离线提示
        this.showOfflineNotification();
        
        // 禁用需要网络的功能
        this.disableNetworkFeatures();
    }
    
    handleOnlineMode() {
        console.log('🔧 Switching to online mode...');
        
        // 隐藏离线提示
        this.hideOfflineNotification();
        
        // 重新启用网络功能
        this.enableNetworkFeatures();
        
        // 重新同步数据
        this.syncOfflineData();
    }
    
    // =================================================================
    // 紧急恢复机制
    // =================================================================
    
    setupEmergencyRecovery() {
        // Ctrl+Alt+R 紧急恢复快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'r') {
                e.preventDefault();
                this.triggerEmergencyRecovery();
            }
        });
        
        // Ctrl+双击也可以触发
        let clickTimeout;
        document.addEventListener('click', (e) => {
            if (e.ctrlKey) {
                if (clickTimeout) {
                    clearTimeout(clickTimeout);
                    clickTimeout = null;
                    this.triggerEmergencyRecovery();
                } else {
                    clickTimeout = setTimeout(() => {
                        clickTimeout = null;
                    }, 300);
                }
            }
        });
    }
    
    triggerEmergencyRecovery() {
        console.log('🚨 Emergency recovery triggered!');
        
        if (this.recoveryAttempts >= this.maxRecoveryAttempts) {
            console.warn('⚠️ Max recovery attempts reached');
            this.showFatalErrorMessage();
            return;
        }
        
        this.recoveryAttempts++;
        this.performEmergencyRecovery();
    }
    
    performEmergencyRecovery() {
        console.log('🔧 Performing emergency recovery...');
        
        try {
            // 1. 清理模态框问题
            this.fixModalIssues();
            
            // 2. 恢复页面交互
            this.restorePageInteraction();
            
            // 3. 重新初始化关键服务
            this.reinitializeCriticalServices();
            
            // 4. 清理错误状态
            this.clearErrorState();
            
            console.log('✅ Emergency recovery completed');
            this.showRecoverySuccessMessage();
            
        } catch (error) {
            console.error('❌ Emergency recovery failed:', error);
            this.showRecoveryFailureMessage();
        }
    }
    
    fixModalIssues() {
        // 关闭所有模态框
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        });
        
        // 移除所有backdrop
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.remove();
        });
        
        // 恢复body状态
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }
    
    restorePageInteraction() {
        // 重新启用所有被禁用的元素
        document.querySelectorAll('[disabled]').forEach(element => {
            if (!element.dataset.permanentlyDisabled) {
                element.disabled = false;
            }
        });
        
        // 移除可能的覆盖层
        document.querySelectorAll('.loading-overlay, .blocking-overlay').forEach(overlay => {
            overlay.remove();
        });
    }
    
    reinitializeCriticalServices() {
        // 重新检查并初始化关键服务
        this.checkCriticalServices();
        
        // 如果有缺失的服务，提供降级版本
        Object.keys(this.serviceStatus).forEach(service => {
            if (!this.serviceStatus[service]) {
                this.handleMissingService(service);
            }
        });
    }
    
    clearErrorState() {
        // 清空错误记录
        this.errors = [];
        
        // 重置恢复计数器
        setTimeout(() => {
            this.recoveryAttempts = Math.max(0, this.recoveryAttempts - 1);
        }, 60000); // 1分钟后减少恢复计数
    }
    
    // =================================================================
    // 降级策略实现 (修复缺失方法)
    // =================================================================
    
    setupDegradationStrategies() {
        console.log('🔧 Setting up degradation strategies...');
        
        // API降级策略
        this.apiDegradationStrategy = {
            fallbackToCache: true,
            offlineMode: true,
            retryAttempts: 3
        };
        
        // UI降级策略
        this.uiDegradationStrategy = {
            disableAnimations: false,
            simplifyLayout: false,
            fallbackToBasicComponents: true
        };
        
        // 服务降级策略
        this.serviceDegradationStrategy = {
            disableRealtime: false,
            disableNotifications: false,
            fallbackToPolling: true
        };
        
        console.log('✅ Degradation strategies configured');
    }
    
    handleJavaScriptError(errorInfo) {
        console.error('🚨 JavaScript Error Handler:', errorInfo);
        
        // 根据错误类型采取相应措施
        if (errorInfo.message) {
            // 检查是否是已知的可修复错误
            if (errorInfo.message.includes('not a function')) {
                this.handleMissingMethodError(errorInfo);
            } else if (errorInfo.message.includes('undefined')) {
                this.handleUndefinedVariableError(errorInfo);
            } else if (errorInfo.message.includes('TypeError')) {
                this.handleTypeError(errorInfo);
            }
        }
        
        // 如果是重复错误，避免无限循环
        const errorSignature = `${errorInfo.filename}:${errorInfo.lineno}:${errorInfo.message}`;
        if (this.recentErrors && this.recentErrors.includes(errorSignature)) {
            console.warn('Ignoring duplicate error to prevent infinite loop');
            return;
        }
        
        if (!this.recentErrors) this.recentErrors = [];
        this.recentErrors.push(errorSignature);
        
        // 清理旧错误记录
        setTimeout(() => {
            const index = this.recentErrors.indexOf(errorSignature);
            if (index > -1) this.recentErrors.splice(index, 1);
        }, 30000);
    }
    
    handlePromiseRejection(errorInfo) {
        console.error('🚨 Promise Rejection Handler:', errorInfo);
        
        // 检查是否是网络相关错误
        if (errorInfo.error && errorInfo.error.message) {
            if (errorInfo.error.message.includes('fetch') || 
                errorInfo.error.message.includes('Network')) {
                this.handleNetworkError(errorInfo);
                return;
            }
        }
        
        // API相关错误处理
        if (errorInfo.error && errorInfo.error.message && 
            errorInfo.error.message.includes('API')) {
            this.handleApiError(errorInfo);
            return;
        }
        
        // 通用Promise错误处理
        this.handleGenericPromiseError(errorInfo);
    }
    
    handleMissingMethodError(errorInfo) {
        console.log('🔧 Attempting to fix missing method error...');
        
        // 尝试提供缺失方法的降级实现
        const methodName = this.extractMethodName(errorInfo.message);
        if (methodName && this.provideFallbackMethod) {
            this.provideFallbackMethod(methodName);
        }
    }
    
    handleUndefinedVariableError(errorInfo) {
        console.log('🔧 Attempting to fix undefined variable error...');
        
        // 检查是否是未加载的依赖
        if (errorInfo.message.includes('ApiClient')) {
            this.provideApiClientFallback();
        } else if (errorInfo.message.includes('ComponentManager')) {
            this.provideComponentManagerFallback();
        }
    }
    
    handleTypeError(errorInfo) {
        console.log('🔧 Attempting to fix type error...');
        
        // 类型错误通常是因为null/undefined调用
        // 提供基本的类型保护
        this.implementTypeGuards();
    }
    
    handleNetworkError(errorInfo) {
        console.log('🌐 Handling network error...');
        
        // 启用离线模式
        this.handleOfflineMode();
        
        // 显示网络错误提示
        this.showToast('网络连接问题，已启用离线模式', 'warning');
    }
    
    handleApiError(errorInfo) {
        console.log('🔌 Handling API error...');
        
        // 切换到API降级模式
        this.enableApiDegradation();
    }
    
    handleGenericPromiseError(errorInfo) {
        console.log('⚠️ Handling generic promise error...');
        
        // 记录错误但不影响系统运行
        this.logErrorForAnalysis(errorInfo);
    }
    
    extractMethodName(errorMessage) {
        const match = errorMessage.match(/(\w+) is not a function/);
        return match ? match[1] : null;
    }
    
    provideFallbackMethod(methodName) {
        // 为常见的缺失方法提供降级实现
        const fallbackMethods = {
            debounce: function(func, wait) {
                let timeout;
                return function(...args) {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(this, args), wait);
                };
            },
            throttle: function(func, limit) {
                let inThrottle;
                return function(...args) {
                    if (!inThrottle) {
                        func.apply(this, args);
                        inThrottle = true;
                        setTimeout(() => inThrottle = false, limit);
                    }
                };
            }
        };
        
        if (fallbackMethods[methodName]) {
            window[methodName] = fallbackMethods[methodName];
            console.log(`✅ Provided fallback for missing method: ${methodName}`);
        }
    }
    
    provideComponentManagerFallback() {
        if (typeof window.ComponentManager === 'undefined') {
            window.ComponentManager = {
                showEnhancedNotification: (message, type) => {
                    console.log(`[${type}] ${message}`);
                },
                debounce: function(func, wait) {
                    let timeout;
                    return function(...args) {
                        clearTimeout(timeout);
                        timeout = setTimeout(() => func.apply(this, args), wait);
                    };
                }
            };
            console.log('✅ ComponentManager fallback provided');
        }
    }
    
    implementTypeGuards() {
        // 为常见的类型错误提供保护
        const originalSetTimeout = window.setTimeout;
        window.setTimeout = function(callback, delay) {
            if (typeof callback === 'function') {
                return originalSetTimeout(callback, delay);
            }
            console.warn('setTimeout called with non-function callback');
            return null;
        };
    }
    
    enableApiDegradation() {
        // 启用API降级模式
        if (window.api) {
            window.api._degradationMode = true;
            console.log('✅ API degradation mode enabled');
        }
    }
    
    logErrorForAnalysis(errorInfo) {
        // 错误分析日志
        if (!window.errorAnalysisLog) {
            window.errorAnalysisLog = [];
        }
        
        window.errorAnalysisLog.push({
            ...errorInfo,
            userAgent: navigator.userAgent,
            timestamp: Date.now(),
            url: window.location.href
        });
        
        // 限制日志大小
        if (window.errorAnalysisLog.length > 50) {
            window.errorAnalysisLog.shift();
        }
    }

    // =================================================================
    // 用户通知
    // =================================================================
    
    showOfflineNotification() {
        if (!document.getElementById('offline-notification')) {
            const notification = document.createElement('div');
            notification.id = 'offline-notification';
            notification.className = 'alert alert-warning fixed-top m-3';
            notification.innerHTML = `
                <i class="fas fa-wifi-off"></i> 
                网络连接已断开，部分功能可能不可用
            `;
            document.body.appendChild(notification);
        }
    }
    
    hideOfflineNotification() {
        const notification = document.getElementById('offline-notification');
        if (notification) {
            notification.remove();
        }
    }
    
    showRecoverySuccessMessage() {
        this.showToast('🛡️ 紧急恢复成功！页面功能已恢复正常。', 'success');
    }
    
    showRecoveryFailureMessage() {
        this.showToast('❌ 紧急恢复失败，请刷新页面重试。', 'danger');
    }
    
    showFatalErrorMessage() {
        this.showToast('🚨 系统遇到严重错误，建议刷新页面。', 'danger', 0);
    }
    
    showToast(message, type = 'info', autohide = 5000) {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast, {
                autohide: autohide > 0,
                delay: autohide
            });
            bsToast.show();
        }
    }
    
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    // =================================================================
    // 公共API
    // =================================================================
    
    getErrorReport() {
        return {
            errors: this.errors,
            recoveryAttempts: this.recoveryAttempts,
            serviceStatus: this.serviceStatus,
            browserSupport: this.browserSupport
        };
    }
    
    clearErrors() {
        this.errors = [];
    }
    
    isHealthy() {
        return this.errors.length < 5 && 
               this.recoveryAttempts < this.maxRecoveryAttempts &&
               Object.values(this.serviceStatus || {}).every(status => status);
    }

    // ==================== 缺失方法实现 ====================
    
    setupDegradationStrategies() {
        console.log('🔧 Setting up degradation strategies...');
        
        this.degradationStrategies = {
            level1: () => {
                // 轻度降级：禁用非关键功能
                this.disableNonCriticalFeatures();
            },
            level2: () => {
                // 中度降级：使用备用组件
                this.enableFallbackComponents();
            },
            level3: () => {
                // 重度降级：最小功能模式
                this.enableMinimalMode();
            }
        };
        
        console.log('✅ Degradation strategies configured');
    }
    
    handleJavaScriptError(error, source, lineno, colno, errorObj) {
        console.log('🚨 JavaScript Error Handler activated:', {
            message: error,
            source,
            line: lineno,
            column: colno
        });
        
        // 错误分类 - 安全的字符串检查
        const errorMessage = typeof error === 'string' ? error : (error && error.message ? error.message : String(error || ''));
        
        if (errorMessage.includes('is not a function')) {
            this.handleMissingMethodError({ message: errorMessage, source });
        } else if (errorMessage.includes('is not defined')) {
            this.handleUndefinedVariableError({ message: errorMessage, source });
        } else if (errorMessage.includes('already been declared')) {
            this.handleDuplicateDeclarationError({ message: errorMessage, source });
        }
        
        // 记录错误统计
        this.errorStats.jsErrors = (this.errorStats.jsErrors || 0) + 1;
        
        // 触发恢复机制
        if (this.errorStats.jsErrors > 5) {
            this.triggerEmergencyRecovery();
        }
        
        return true; // 阻止默认错误处理
    }
    
    handlePromiseRejection(event) {
        console.log('🚨 Promise Rejection Handler activated:', event.reason);
        
        // Promise错误分类
        const reason = event.reason;
        if (reason && typeof reason === 'object') {
            if (reason.name === 'TypeError') {
                this.handleJavaScriptError(reason.message, reason.stack);
            } else if (reason.name === 'NetworkError') {
                this.handleNetworkError(reason);
            }
        }
        
        // 记录错误统计  
        this.errorStats.promiseRejections = (this.errorStats.promiseRejections || 0) + 1;
        
        // 预防错误传播
        event.preventDefault();
    }
    
    // 辅助方法实现
    disableNonCriticalFeatures() {
        document.body.style.setProperty('--animation-duration', '0s', 'important');
        if (window.performanceOptimizations) {
            window.performanceOptimizations.disabled = true;
        }
    }
    
    enableFallbackComponents() {
        document.body.classList.add('fallback-mode');
        this.replaceComplexComponents();
    }
    
    enableMinimalMode() {
        document.body.classList.add('minimal-mode');
        this.disableAllNonEssentialFeatures();
    }
    
    replaceComplexComponents() {
        const failedCharts = document.querySelectorAll('canvas[data-chart-failed]');
        failedCharts.forEach(canvas => {
            const table = this.createFallbackTable(canvas);
            canvas.parentNode.replaceChild(table, canvas);
        });
    }
    
    createFallbackTable(canvas) {
        const table = document.createElement('table');
        table.className = 'table table-striped fallback-chart';
        table.innerHTML = `
            <thead><tr><th>数据项</th><th>值</th></tr></thead>
            <tbody><tr><td colspan="2">图表加载失败，数据暂时无法显示</td></tr></tbody>
        `;
        return table;
    }
    
    disableAllNonEssentialFeatures() {
        const nonEssential = ['.animation', '.fancy-effect', '.performance-monitor', '[data-optional]'];
        nonEssential.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => el.style.display = 'none');
        });
    }
    
    handleDuplicateDeclarationError(errorInfo) {
        console.log('🔧 Handling duplicate declaration error...');
        if (errorInfo.message.includes('ComponentPerformanceMonitor')) {
            this.removeDuplicateComponent('ComponentPerformanceMonitor');
        }
    }
    
    removeDuplicateComponent(componentName) {
        if (window[componentName]) {
            console.log(`🔧 Removing duplicate ${componentName}`);
            delete window[componentName];
        }
    }
    
    handleNetworkError(error) {
        console.log('🔧 Handling network error:', error);
        document.body.classList.add('offline-mode');
        this.enableOfflineMode();
    }
    
    enableOfflineMode() {
        document.body.classList.add('offline-mode');
        const offlineElements = document.querySelectorAll('[data-offline-message]');
        offlineElements.forEach(el => {
            el.textContent = '网络连接中断，部分功能可能不可用';
            el.style.display = 'block';
        });
    }
    
    // API错误恢复增强
    enhanceApiErrorHandling() {
        // 拦截并增强fetch请求
        if (window.fetch && !window.fetch._winstonEnhanced) {
            const originalFetch = window.fetch;
            
            window.fetch = async function(...args) {
                try {
                    const response = await originalFetch.apply(this, args);
                    
                    // 检查响应是否为HTML错误页面
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('text/html') && !response.ok) {
                        console.warn('🚨 API返回HTML错误页面，可能是认证问题');
                        throw new Error(`API端点返回HTML错误页面 (${response.status})`);
                    }
                    
                    return response;
                } catch (error) {
                    // 统一处理网络和解析错误
                    console.error('🔌 Fetch请求失败:', error);
                    
                    // 如果是认证相关错误，尝试刷新页面
                    if (error.message.includes('401') || error.message.includes('认证')) {
                        setTimeout(() => {
                            if (confirm('会话已过期，是否重新登录？')) {
                                window.location.reload();
                            }
                        }, 1000);
                    }
                    
                    throw error;
                }
            };
            
            window.fetch._winstonEnhanced = true;
        }
    }
    
    // 修复异步任务分片问题
    fixAsyncTaskFragmentation() {
        // 确保长任务被适当分割
        if (!window.requestIdleCallback) {
            window.requestIdleCallback = function(callback, options = {}) {
                const timeout = options.timeout || 0;
                const startTime = performance.now();
                
                return setTimeout(() => {
                    callback({
                        timeRemaining() {
                            return Math.max(0, 50 - (performance.now() - startTime));
                        },
                        didTimeout: timeout > 0 && (performance.now() - startTime) >= timeout
                    });
                }, 1);
            };
        }
    }
}

// 全局初始化
if (typeof window.WinstonErrorRecovery === 'undefined') {
    window.WinstonErrorRecovery = WinstonErrorRecovery;
    window.winstonErrorRecovery = new WinstonErrorRecovery();
    
    // 激活增强功能
    window.winstonErrorRecovery.enhanceApiErrorHandling();
    window.winstonErrorRecovery.fixAsyncTaskFragmentation();
    
    // 提供全局恢复函数
    window.emergencyRecovery = () => {
        window.winstonErrorRecovery.triggerEmergencyRecovery();
    };
}

console.log('🛡️ Winston Error Recovery System loaded');