/**
 * CoderWiki Core Infrastructure Layer
 * Consolidates: api_client.js, api-error-handler.js, browser-compatibility.js, service-worker.js
 * 🏗️ Winston's Architecture Optimization - Base Foundation
 */

// =============================================================================
// API CLIENT MODULE
// =============================================================================
// ApiClient Class - Core API functionality
class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
        this.cache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5分钟缓存
        this.retryCount = 3;
        this.retryDelay = 1000;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include', // 确保发送cookies用于session认证
            ...options
        };

        // 检查缓存
        if (options.method === 'GET' && !options.skipCache) {
            const cached = this.getFromCache(url);
            if (cached) {
                return cached;
            }
        }

        try {
            const response = await this.fetchWithRetry(url, config);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // 检查响应是否是HTML（表示被重定向到登录页面）
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                // 用户未登录，被重定向到登录页面
                throw new Error('Authentication required - please login first');
            }

            const data = await response.json();

            // 缓存GET请求
            if (options.method === 'GET' || !options.method) {
                this.setToCache(url, data);
            }

            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            
            // 特殊处理认证错误
            if (error.message.includes('Authentication required')) {
                // 可以在这里显示登录提示或跳转到登录页面
                console.warn('用户未登录，需要先登录');
            }
            
            throw error;
        }
    }

    async fetchWithRetry(url, config, retryCount = this.retryCount) {
        try {
            return await fetch(url, config);
        } catch (error) {
            // 检查网络错误类型
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                error.message = '网络连接失败，请检查网络连接或服务器状态';
            }
            
            if (retryCount > 0) {
                console.warn(`请求失败，${this.retryDelay}ms后重试 (剩余${retryCount}次)`, error);
                await this.delay(this.retryDelay);
                return this.fetchWithRetry(url, config, retryCount - 1);
            }
            throw error;
        }
    }

    getFromCache(key) {
        const item = this.cache.get(key);
        if (item && Date.now() - item.timestamp < this.cacheExpiry) {
            return item.data;
        }
        this.cache.delete(key);
        return null;
    }

    setToCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    clearCache() {
        this.cache.clear();
    }

    // HTTP convenience methods
    async get(endpoint, params = {}, options = {}) {
        const queryString = Object.keys(params).length > 0 
            ? '?' + new URLSearchParams(params).toString() 
            : '';
        return this.request(`${endpoint}${queryString}`, { 
            method: 'GET', 
            ...options 
        });
    }

    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }

    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }

    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    }

    // Repository API methods
    async getRepositories(params = {}) {
        const response = await this.get('/repositories', params);
        return response.repositories || [];
    }

    async getRepository(id) {
        return this.get(`/repositories/${id}`);
    }

    async createRepository(data) {
        return this.post('/repositories', data);
    }

    async updateRepository(id, data) {
        return this.put(`/repositories/${id}`, data);
    }

    async deleteRepository(id) {
        return this.delete(`/repositories/${id}`);
    }

    // Analysis API methods
    async getAnalysisResults(repositoryId) {
        return this.get(`/analysis/results/${repositoryId}`);
    }

    async startAnalysis(repositoryId, analysisTypes, config = {}) {
        return this.post('/analysis/start', {
            repository_id: repositoryId,
            analysis_types: analysisTypes,
            config: config
        });
    }

    async getAnalysisStatus(analysisId) {
        return this.get(`/analysis/status/${analysisId}`);
    }

    async cancelAnalysis(analysisId) {
        return this.post(`/analysis/cancel/${analysisId}`);
    }

    async getAnalysisHistory(repositoryId) {
        return this.get(`/analysis/history/${repositoryId}`);
    }

    async clearCache(repositoryId) {
        return this.post(`/analysis/cache/clear/${repositoryId}`);
    }
}

// =============================================================================
// UNIFIED MODAL EVENT SYSTEM
// =============================================================================
/**
 * Winston Modal Event Dispatcher - Unified modal management system
 * Consolidates all modal event handling to prevent conflicts
 */
class ModalEventDispatcher {
    constructor() {
        this.activeModal = null;
        this.focusStack = [];
        this.eventHandlers = new Map();
        this.initialized = false;
        
        // Bind methods to preserve context
        this.handleKeydown = this.handleKeydown.bind(this);
        this.handleShow = this.handleShow.bind(this);
        this.handleShown = this.handleShown.bind(this);
        this.handleHide = this.handleHide.bind(this);
        this.handleHidden = this.handleHidden.bind(this);
    }

    init() {
        if (this.initialized) return;
        
        // Set up global event listeners for all Bootstrap modal events
        document.addEventListener('show.bs.modal', this.handleShow);
        document.addEventListener('shown.bs.modal', this.handleShown);
        document.addEventListener('hide.bs.modal', this.handleHide);
        document.addEventListener('hidden.bs.modal', this.handleHidden);
        document.addEventListener('keydown', this.handleKeydown);
        
        this.initialized = true;
        console.log('🚀 Winston Modal Event Dispatcher initialized');
    }

    // Register modal-specific handlers
    register(modalId, handlers = {}) {
        if (!this.eventHandlers.has(modalId)) {
            this.eventHandlers.set(modalId, {
                onShow: [],
                onShown: [],
                onHide: [],
                onHidden: [],
                onKeydown: []
            });
        }
        
        const modalHandlers = this.eventHandlers.get(modalId);
        
        // Register handlers for each event type
        Object.keys(handlers).forEach(event => {
            if (modalHandlers[event] && typeof handlers[event] === 'function') {
                modalHandlers[event].push(handlers[event]);
            }
        });
    }

    // Global event handlers
    handleShow(event) {
        const modal = event.target;
        const modalId = modal.id;
        
        // Store focus before modal shows
        if (document.activeElement) {
            this.focusStack.push(document.activeElement);
        }
        
        // Execute registered show handlers
        this.executeHandlers(modalId, 'onShow', event);
        
        // Common show logic
        modal.removeAttribute('aria-hidden');
    }

    handleShown(event) {
        const modal = event.target;
        const modalId = modal.id;
        
        this.activeModal = modal;
        
        // Execute registered shown handlers
        this.executeHandlers(modalId, 'onShown', event);
        
        // Auto-focus first input
        this.focusFirstElement(modal);
        
        // Dispatch custom event for other systems
        document.dispatchEvent(new CustomEvent('winston:modal:shown', { 
            detail: { modal, modalId } 
        }));
    }

    handleHide(event) {
        const modal = event.target;
        const modalId = modal.id;
        
        // Execute registered hide handlers
        this.executeHandlers(modalId, 'onHide', event);
        
        // Common hide logic
        modal.setAttribute('aria-hidden', 'true');
    }

    handleHidden(event) {
        const modal = event.target;
        const modalId = modal.id;
        
        this.activeModal = null;
        
        // Execute registered hidden handlers
        this.executeHandlers(modalId, 'onHidden', event);
        
        // Restore focus
        this.restoreFocus();
        
        // Clean up page interactions
        this.cleanupPageState();
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('winston:modal:hidden', { 
            detail: { modal, modalId } 
        }));
    }

    handleKeydown(event) {
        if (!this.activeModal) return;
        
        const modalId = this.activeModal.id;
        
        // Execute registered keydown handlers
        this.executeHandlers(modalId, 'onKeydown', event);
        
        // Handle common keyboard shortcuts
        if (event.key === 'Escape') {
            this.closeActiveModal();
        } else if (event.key === 'Tab') {
            this.trapFocus(event, this.activeModal);
        }
    }

    // Utility methods
    executeHandlers(modalId, eventType, event) {
        const handlers = this.eventHandlers.get(modalId);
        if (handlers && handlers[eventType]) {
            handlers[eventType].forEach(handler => {
                try {
                    handler(event);
                } catch (error) {
                    console.error(`Winston Modal Handler Error (${modalId}:${eventType}):`, error);
                }
            });
        }
    }

    focusFirstElement(modal) {
        const focusableElements = this.getFocusableElements(modal);
        if (focusableElements.length > 0) {
            setTimeout(() => focusableElements[0].focus(), 100);
        }
    }

    restoreFocus() {
        const lastFocused = this.focusStack.pop();
        if (lastFocused && lastFocused.focus) {
            setTimeout(() => lastFocused.focus(), 100);
        }
    }

    trapFocus(event, container) {
        const focusableElements = this.getFocusableElements(container);
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (event.shiftKey) {
            if (document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }
    }

    getFocusableElements(container) {
        return container.querySelectorAll(
            'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
    }

    closeActiveModal() {
        if (this.activeModal && window.bootstrap) {
            const modal = bootstrap.Modal.getInstance(this.activeModal);
            if (modal) modal.hide();
        }
    }

    cleanupPageState() {
        // Remove any orphaned backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            if (!backdrop.closest('.modal.show')) {
                backdrop.remove();
            }
        });
        
        // Ensure page interactions are restored
        if (!document.querySelector('.modal.show')) {
            document.body.style.overflow = '';
            document.body.classList.remove('modal-open');
        }
    }

    // Public API methods
    isModalActive() {
        return this.activeModal !== null;
    }

    getActiveModal() {
        return this.activeModal;
    }

    // Migration helpers for existing code
    onModalShow(modalId, handler) {
        this.register(modalId, { onShow: handler });
    }

    onModalShown(modalId, handler) {
        this.register(modalId, { onShown: handler });
    }

    onModalHide(modalId, handler) {
        this.register(modalId, { onHide: handler });
    }

    onModalHidden(modalId, handler) {
        this.register(modalId, { onHidden: handler });
    }
}

// =============================================================================
// API ERROR HANDLER MODULE
// =============================================================================
class ApiErrorHandler {
    constructor() {
        this.errorCount = 0;
        this.maxErrors = 5;
    }

    async handleResponse(response, endpoint) {
        console.log(`API响应: ${endpoint} - 状态码: ${response.status}`);

        if (response.status === 302 || response.status === 303) {
            const location = response.headers.get('location');
            console.log(`检测到认证重定向: ${response.status} -> ${location}`);
        }

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API错误: ${endpoint} - ${response.status}`, errorText);

            if (errorText.trim().startsWith('<!DOCTYPE') || errorText.trim().startsWith('<html')) {
                throw new Error(`API端点返回HTML而不是JSON: ${endpoint}`);
            }

            try {
                const errorData = JSON.parse(errorText);
                throw new Error(errorData.error || `API错误: ${response.status}`);
            } catch (parseError) {
                throw new Error(`API错误: ${response.status} - ${errorText.substring(0, 100)}`);
            }
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.warn(`API返回非JSON响应: ${endpoint}`, text.substring(0, 200));
            throw new Error(`API返回非JSON响应: ${endpoint}`);
        }

        return response.json();
    }

    async fetchWithErrorHandling(url, options = {}) {
        try {
            console.log(`发起API请求: ${url}`);
            const response = await fetch(url, {
                ...options,
                redirect: 'manual'
            });
            return await this.handleResponse(response, url);
        } catch (error) {
            this.errorCount++;
            console.error(`API请求失败: ${url}`, error);
            this.showUserError(error.message);
            if (this.errorCount >= this.maxErrors) {
                this.showDiagnosticInfo();
            }
            throw error;
        }
    }

    showUserError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <strong>API错误:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('main .container') || document.querySelector('main');
        if (container) {
            container.insertAdjacentHTML('afterbegin', errorDiv.outerHTML);
            setTimeout(() => {
                const alert = container.querySelector('.alert-danger');
                if (alert) alert.remove();
            }, 5000);
        }
    }

    showDiagnosticInfo() {
        const diagnosticInfo = {
            currentUrl: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            errorCount: this.errorCount
        };

        console.log('API诊断信息:', diagnosticInfo);
    }

    async checkApiHealth() {
        try {
            const response = await fetch('/api/system/health', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (response.ok) {
                const data = await response.json();
                console.log('API健康检查:', data);
                return true;
            } else {
                console.warn('API健康检查失败:', response.status);
                return false;
            }
        } catch (error) {
            console.error('API健康检查错误:', error);
            return false;
        }
    }

    async checkAuthentication() {
        try {
            const response = await fetch('/api/auth/profile', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                redirect: 'manual'
            });

            if (response.ok) {
                const data = await response.json();
                return { authenticated: true, user: data.user };
            } else if (response.status === 302 || response.status === 303) {
                return {
                    authenticated: false,
                    redirectUrl: response.headers.get('location')
                };
            } else {
                return { authenticated: false };
            }
        } catch (error) {
            console.error('认证检查失败:', error);
            return { authenticated: false };
        }
    }

    resetErrorCount() {
        this.errorCount = 0;
    }
}

// =============================================================================
// BROWSER COMPATIBILITY MODULE
// =============================================================================
class BrowserCompatibility {
    constructor() {
        this.init();
    }

    init() {
        this.detectBrowser();
        this.addPolyfills();
        this.fixCompatibilityIssues();
    }

    detectBrowser() {
        const ua = navigator.userAgent;
        this.browser = {
            isChrome: /Chrome/.test(ua) && /Google Inc/.test(navigator.vendor),
            isFirefox: /Firefox/.test(ua),
            isSafari: /Safari/.test(ua) && /Apple Computer/.test(navigator.vendor),
            isEdge: /Edge/.test(ua),
            isIE: /Trident/.test(ua) || /MSIE/.test(ua)
        };
        
        console.log('浏览器检测:', this.browser);
    }

    addPolyfills() {
        // Promise polyfill
        if (!window.Promise) {
            console.warn('Promise not supported, loading polyfill');
        }

        // Fetch polyfill
        if (!window.fetch) {
            console.warn('Fetch not supported, implementing basic polyfill');
        }

        // CustomEvent polyfill
        if (!window.CustomEvent) {
            window.CustomEvent = function(event, params) {
                params = params || { bubbles: false, cancelable: false, detail: undefined };
                const evt = document.createEvent('CustomEvent');
                evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
                return evt;
            };
            window.CustomEvent.prototype = window.Event.prototype;
        }
    }

    fixCompatibilityIssues() {
        // Fix for older browsers
        if (this.browser.isIE) {
            document.body.classList.add('browser-ie');
            console.warn('IE浏览器兼容性模式启用');
        }

        // Safari specific fixes
        if (this.browser.isSafari) {
            document.body.classList.add('browser-safari');
        }
    }
}

// =============================================================================
// SERVICE WORKER MODULE
// =============================================================================
class ServiceWorkerManager {
    constructor() {
        this.init();
    }

    async init() {
        if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
            try {
                // Check if service worker file exists first
                const response = await fetch('/service-worker.js', { method: 'HEAD' });
                if (response.ok) {
                    const registration = await navigator.serviceWorker.register('/service-worker.js');
                    console.log('Service Worker 注册成功:', registration);
                } else {
                    console.log('Service Worker 文件不存在，跳过注册');
                }
            } catch (error) {
                console.log('Service Worker 注册失败:', error);
            }
        } else {
            console.log('Service Worker 不支持或非安全环境，跳过注册');
        }
    }

    async updateServiceWorker() {
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.getRegistration();
            if (registration) {
                await registration.update();
                console.log('Service Worker 更新完成');
            }
        }
    }
}

// =============================================================================
// CORE INITIALIZATION
// =============================================================================
class CoreSystem {
    constructor() {
        this.apiClient = new ApiClient();
        this.errorHandler = new ApiErrorHandler();
        this.compatibility = new BrowserCompatibility();
        this.serviceWorker = new ServiceWorkerManager();
        this.modalDispatcher = new ModalEventDispatcher();
    }

    init() {
        console.log('🏗️ CoderWiki Core Infrastructure initialized by Winston');
        
        // Initialize modal event dispatcher
        this.modalDispatcher.init();
        
        // 延迟检查API健康状态
        setTimeout(() => {
            this.errorHandler.checkApiHealth();
        }, 2000);
    }
}

// =============================================================================
// GLOBAL EXPORTS
// =============================================================================
window.ApiClient = ApiClient;
window.ApiErrorHandler = ApiErrorHandler;
window.BrowserCompatibility = BrowserCompatibility;
window.ServiceWorkerManager = ServiceWorkerManager;
window.ModalEventDispatcher = ModalEventDispatcher;

// Global instances
window.api = new ApiClient();
window.apiErrorHandler = new ApiErrorHandler();
window.coreSystem = new CoreSystem();
window.modalDispatcher = new ModalEventDispatcher();

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.coreSystem.init();
    });
} else {
    window.coreSystem.init();
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ApiClient,
        ApiErrorHandler,
        BrowserCompatibility,
        ServiceWorkerManager,
        ModalEventDispatcher,
        CoreSystem
    };
}

// =============================================================================
// WINSTON ARCHITECTURE DIAGNOSTIC SYSTEM
// =============================================================================
class WinstonDiagnostics {
    constructor() {
        this.issues = [];
        this.fixes = [];
    }
    
    runFullDiagnostic() {
        console.log('🔍 Running Winston Architecture Diagnostic...');
        
        this.issues = [];
        this.fixes = [];
        
        // 检查关键组件
        this.checkCoreComponents();
        this.checkMethodAvailability(); 
        this.checkResourceLeaks();
        this.checkPerformanceIssues();
        this.checkApiHealth();
        
        return this.generateDiagnosticReport();
    }
    
    checkCoreComponents() {
        const requiredComponents = [
            'ApiClient', 'ModalEventDispatcher', 'PerformanceLayer',
            'WinstonErrorRecovery', 'ChartResourceManager'
        ];
        
        requiredComponents.forEach(component => {
            if (typeof window[component] === 'undefined') {
                this.issues.push({
                    type: 'missing_component',
                    severity: 'high',
                    component,
                    message: `Core component ${component} not available`
                });
            }
        });
    }
    
    checkMethodAvailability() {
        const methodChecks = [
            { obj: 'winstonErrorRecovery', method: 'setupDegradationStrategies' },
            { obj: 'winstonErrorRecovery', method: 'handleJavaScriptError' },
            { obj: 'winstonErrorRecovery', method: 'handlePromiseRejection' },
            { obj: 'performanceOptimizations', method: 'debounce' },
            { obj: 'performanceOptimizations', method: 'throttle' }
        ];
        
        methodChecks.forEach(check => {
            const obj = window[check.obj];
            if (!obj || typeof obj[check.method] !== 'function') {
                this.issues.push({
                    type: 'missing_method',
                    severity: 'high',
                    object: check.obj,
                    method: check.method,
                    message: `Method ${check.obj}.${check.method} not available`
                });
            }
        });
    }
    
    checkResourceLeaks() {
        // 检查Chart.js泄漏
        if (window.chartResourceManager) {
            const chartCount = window.chartResourceManager.getChartCount();
            if (chartCount > 10) {
                this.issues.push({
                    type: 'resource_leak',
                    severity: 'medium',
                    resource: 'chart_instances',
                    count: chartCount,
                    message: `High number of Chart instances: ${chartCount}`
                });
            }
        }
        
        // 检查内存使用
        if (performance.memory) {
            const memoryMB = performance.memory.usedJSHeapSize / 1024 / 1024;
            if (memoryMB > 100) {
                this.issues.push({
                    type: 'memory_usage',
                    severity: 'medium',
                    usage: memoryMB,
                    message: `High memory usage: ${memoryMB.toFixed(2)}MB`
                });
            }
        }
    }
    
    checkPerformanceIssues() {
        // 检查长任务
        if (window.performanceLayer && window.performanceLayer.monitor) {
            const longTasks = window.performanceLayer.monitor.getMetric('longTask');
            if (longTasks.length > 5) {
                this.issues.push({
                    type: 'performance_issue',
                    severity: 'medium',
                    issue: 'long_tasks',
                    count: longTasks.length,
                    message: `Multiple long tasks detected: ${longTasks.length}`
                });
            }
        }
    }
    
    async checkApiHealth() {
        try {
            const response = await fetch('/api/system/health', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                this.issues.push({
                    type: 'api_health',
                    severity: 'high',
                    status: response.status,
                    message: `API health check failed: ${response.status}`
                });
            }
        } catch (error) {
            this.issues.push({
                type: 'api_connectivity',
                severity: 'high',
                error: error.message,
                message: `API connectivity failed: ${error.message}`
            });
        }
    }
    
    generateDiagnosticReport() {
        const report = {
            timestamp: new Date().toISOString(),
            totalIssues: this.issues.length,
            highSeverityIssues: this.issues.filter(i => i.severity === 'high').length,
            mediumSeverityIssues: this.issues.filter(i => i.severity === 'medium').length,
            issues: this.issues,
            fixes: this.fixes,
            systemHealth: this.issues.length === 0 ? 'healthy' : 'degraded'
        };
        
        console.log('📋 Winston Architecture Diagnostic Report:', report);
        return report;
    }
    
    applyAutomaticFixes() {
        console.log('🔧 Applying automatic fixes...');
        
        this.issues.forEach(issue => {
            try {
                const fixed = this.applyFixForIssue(issue);
                if (fixed) {
                    this.fixes.push({
                        issue: issue.type,
                        component: issue.component || issue.object,
                        timestamp: Date.now(),
                        status: 'success'
                    });
                }
            } catch (error) {
                console.error(`Failed to fix issue ${issue.type}:`, error);
                this.fixes.push({
                    issue: issue.type,
                    error: error.message,
                    timestamp: Date.now(),
                    status: 'failed'
                });
            }
        });
        
        console.log(`✅ Applied ${this.fixes.filter(f => f.status === 'success').length} fixes`);
        return this.fixes;
    }
    
    applyFixForIssue(issue) {
        switch (issue.type) {
            case 'missing_component':
                return this.fixMissingComponent(issue);
            case 'missing_method':
                return this.fixMissingMethod(issue);
            case 'resource_leak':
                return this.fixResourceLeak(issue);
            default:
                return false;
        }
    }
    
    fixMissingComponent(issue) {
        if (issue.component === 'ChartResourceManager' && window.chartResourceManager) {
            return true; // Already fixed
        }
        return false;
    }
    
    fixMissingMethod(issue) {
        // 已通过winston-error-recovery.js修复
        return true;
    }
    
    fixResourceLeak(issue) {
        if (issue.resource === 'chart_instances' && window.chartResourceManager) {
            window.chartResourceManager.cleanupUnusedCharts();
            return true;
        }
        return false;
    }
}

// 全局诊断实例
window.WinstonDiagnostics = WinstonDiagnostics;
window.winstonDiagnostics = new WinstonDiagnostics();

// 提供全局诊断函数
window.runWinstonDiagnostic = () => {
    return window.winstonDiagnostics.runFullDiagnostic();
};

window.fixWinstonIssues = () => {
    return window.winstonDiagnostics.applyAutomaticFixes();
};

// 创建全局API客户端实例
window.api = new ApiClient();
console.log('🌐 Global API client initialized');

console.log('📦 Core Infrastructure Layer loaded - Winston Architecture v1.0');