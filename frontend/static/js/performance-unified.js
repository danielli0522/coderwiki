/**
 * CoderWiki Performance Layer
 * Consolidates: performance.js, performance-optimizer.js, performance-tests.js, realtime_updates.js, accessibility.js
 * 🏗️ Winston's Architecture Optimization - Performance Foundation
 */

// =============================================================================
// PERFORMANCE MONITORING SYSTEM
// =============================================================================
class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.observers = [];
        this.thresholds = {
            domContentLoaded: 3000,  // 3s
            firstContentfulPaint: 2000,  // 2s
            largestContentfulPaint: 4000,  // 4s
            memoryUsage: 50 * 1024 * 1024,  // 50MB
            jsHeapSize: 100 * 1024 * 1024   // 100MB
        };
        this.init();
    }

    init() {
        console.log('⚡ Performance Monitor initializing...');
        this.setupPerformanceObservers();
        this.monitorMemory();
        this.trackPageLoad();
    }

    setupPerformanceObservers() {
        // Observe navigation timing
        if ('PerformanceObserver' in window) {
            try {
                // First Contentful Paint
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        this.recordMetric(entry.name, entry.startTime);
                        
                        if (entry.startTime > this.thresholds[entry.name]) {
                            console.warn(`⚠️ Performance issue: ${entry.name} took ${entry.startTime}ms`);
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['paint', 'navigation', 'resource'] });
                this.observers.push(observer);
            } catch (e) {
                console.warn('Performance Observer not fully supported:', e);
            }
        }

        // Long Task Observer
        if ('PerformanceObserver' in window) {
            try {
                const longTaskObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {  // Long task threshold
                            console.warn(`⚠️ Long task detected: ${entry.duration}ms`);
                            this.recordMetric('longTask', entry.duration);
                        }
                    }
                });
                
                longTaskObserver.observe({ entryTypes: ['longtask'] });
                this.observers.push(longTaskObserver);
            } catch (e) {
                console.warn('Long Task Observer not supported:', e);
            }
        }
    }

    trackPageLoad() {
        // DOM Content Loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                const loadTime = performance.now();
                this.recordMetric('domContentLoaded', loadTime);
                
                if (loadTime > this.thresholds.domContentLoaded) {
                    console.warn(`⚠️ Slow DOM loading: ${loadTime}ms`);
                }
            });
        }

        // Window Load
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            this.recordMetric('windowLoad', loadTime);
            
            // Generate performance report
            setTimeout(() => this.generateReport(), 1000);
        });
    }

    monitorMemory() {
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                this.recordMetric('jsHeapSizeUsed', memory.usedJSHeapSize);
                
                if (memory.usedJSHeapSize > this.thresholds.jsHeapSize) {
                    console.warn(`⚠️ High memory usage: ${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB`);
                }
            }, 30000); // Check every 30 seconds
        }
    }

    recordMetric(name, value) {
        const timestamp = Date.now();
        if (!this.metrics.has(name)) {
            this.metrics.set(name, []);
        }
        this.metrics.get(name).push({ value, timestamp });
    }

    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            navigation: performance.getEntriesByType('navigation')[0],
            paint: performance.getEntriesByType('paint'),
            resources: performance.getEntriesByType('resource').length,
            metrics: Object.fromEntries(this.metrics)
        };

        console.log('📊 Performance Report:', report);
        return report;
    }

    getMetric(name) {
        return this.metrics.get(name) || [];
    }

    clearMetrics() {
        this.metrics.clear();
    }
}

// =============================================================================
// PERFORMANCE OPTIMIZER
// =============================================================================
class PerformanceOptimizer {
    constructor() {
        this.optimizations = new Map();
        this.init();
    }

    init() {
        console.log('🚀 Performance Optimizer initializing...');
        this.setupLazyLoading();
        this.optimizeImages();
        this.debounceScrollHandlers();
        this.preloadCriticalResources();
    }

    setupLazyLoading() {
        // Intersection Observer for lazy loading
        if ('IntersectionObserver' in window) {
            const lazyImageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.remove('lazy');
                        lazyImageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src], img.lazy').forEach(img => {
                lazyImageObserver.observe(img);
            });
        }
    }

    optimizeLazyLoading() {
        // Alias for setupLazyLoading to maintain compatibility
        this.setupLazyLoading();
        console.log('✅ Lazy loading optimization applied');
    }

    optimizeImages() {
        // Convert images to modern formats if supported
        const supportsWebP = this.supportsImageFormat('webp');
        const supportsAvif = this.supportsImageFormat('avif');

        if (supportsWebP || supportsAvif) {
            document.querySelectorAll('img[data-optimize]').forEach(img => {
                let src = img.src;
                if (supportsAvif && src.includes('.jpg')) {
                    src = src.replace('.jpg', '.avif');
                } else if (supportsWebP && src.includes('.jpg')) {
                    src = src.replace('.jpg', '.webp');
                }
                img.src = src;
            });
        }
    }

    supportsImageFormat(format) {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL(`image/${format}`).indexOf(`image/${format}`) === 5;
    }

    debounceScrollHandlers() {
        // Replace scroll handlers with debounced versions
        const scrollHandlers = [];
        let ticking = false;

        const optimizedScrollHandler = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    scrollHandlers.forEach(handler => handler());
                    ticking = false;
                });
                ticking = true;
            }
        };

        // Public API for adding scroll handlers
        window.addOptimizedScrollHandler = (handler) => {
            if (scrollHandlers.length === 0) {
                window.addEventListener('scroll', optimizedScrollHandler, { passive: true });
            }
            scrollHandlers.push(handler);
        };
    }

    preloadCriticalResources() {
        // Preload critical CSS and JS
        const criticalResources = [
            { href: '/static/css/style.css', as: 'style' },
            { href: '/static/js/core.js', as: 'script' }
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource.href;
            link.as = resource.as;
            if (resource.as === 'style') {
                link.onload = () => {
                    link.rel = 'stylesheet';
                };
            }
            document.head.appendChild(link);
        });
    }

    // Optimize API requests
    optimizeApiRequests() {
        const requestCache = new Map();
        const originalFetch = window.fetch;

        window.fetch = function(url, options = {}) {
            // Only cache GET requests
            if (!options.method || options.method === 'GET') {
                const cacheKey = `${url}-${JSON.stringify(options)}`;
                const cached = requestCache.get(cacheKey);
                
                if (cached && Date.now() - cached.timestamp < 300000) { // 5 min cache
                    return Promise.resolve(cached.response.clone());
                }

                return originalFetch(url, options).then(response => {
                    if (response.ok) {
                        requestCache.set(cacheKey, {
                            response: response.clone(),
                            timestamp: Date.now()
                        });
                    }
                    return response;
                });
            }

            return originalFetch(url, options);
        };
    }
}

// =============================================================================
// REALTIME UPDATES SYSTEM
// =============================================================================
class RealtimeUpdatesSystem {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.subscribers = new Map();
        this.pollingEnabled = true;
        this.pollInterval = null;
        this.init();
    }

    init() {
        console.log('🔄 Realtime Updates System initializing...');
        this.connect();
        this.setupHeartbeat();
    }

    connect() {
        if (typeof io !== 'undefined') {
            try {
                this.socket = io({
                    transports: ['websocket', 'polling'],
                    upgrade: true,
                    rememberUpgrade: true
                });

                this.socket.on('connect', () => {
                    console.log('✅ WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.subscribeToEvents();
                });

                this.socket.on('disconnect', (reason) => {
                    console.warn('❌ WebSocket disconnected:', reason);
                    this.handleReconnection();
                });

                this.socket.on('error', (error) => {
                    console.error('❌ WebSocket error:', error);
                });

            } catch (error) {
                console.warn('WebSocket not available, falling back to polling');
                this.setupPolling();
            }
        } else {
            console.warn('Socket.IO not loaded, setting up polling');
            this.setupPolling();
        }
    }

    setupPolling() {
        if (!this.pollingEnabled) return;
        
        // Fallback polling mechanism
        this.pollInterval = setInterval(() => {
            if (this.pollingEnabled) {
                this.checkForUpdates();
            }
        }, 30000); // Poll every 30 seconds
    }

    async checkForUpdates() {
        try {
            const response = await fetch('/api/realtime/updates', {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const updates = await response.json();
                this.processUpdates(updates);
            } else if (response.status === 404) {
                // API endpoint not implemented yet, disable polling
                this.pollingEnabled = false;
                if (this.pollInterval) {
                    clearInterval(this.pollInterval);
                    this.pollInterval = null;
                }
                console.log('Realtime API not available, polling disabled');
                return;
            }
        } catch (error) {
            // Silently handle network errors for optional realtime updates
            if (!error.message.includes('404')) {
                console.debug('Realtime updates not available:', error.message);
            }
        }
    }

    subscribeToEvents() {
        if (this.socket) {
            // Task updates
            this.socket.on('task_update', (data) => {
                this.emit('task:update', data);
            });

            // Document updates
            this.socket.on('document_update', (data) => {
                this.emit('document:update', data);
            });

            // System notifications
            this.socket.on('notification', (data) => {
                this.emit('notification', data);
            });
        }
    }

    setupHeartbeat() {
        if (this.socket) {
            setInterval(() => {
                if (this.socket.connected) {
                    this.socket.emit('ping');
                }
            }, 25000); // Heartbeat every 25 seconds
        }
    }

    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    // Event system
    on(event, callback) {
        if (!this.subscribers.has(event)) {
            this.subscribers.set(event, []);
        }
        this.subscribers.get(event).push(callback);
    }

    off(event, callback) {
        const callbacks = this.subscribers.get(event);
        if (callbacks) {
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        const callbacks = this.subscribers.get(event) || [];
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event callback for ${event}:`, error);
            }
        });
    }

    processUpdates(updates) {
        if (updates.tasks) {
            updates.tasks.forEach(task => this.emit('task:update', task));
        }
        if (updates.documents) {
            updates.documents.forEach(doc => this.emit('document:update', doc));
        }
        if (updates.notifications) {
            updates.notifications.forEach(notif => this.emit('notification', notif));
        }
    }
}

// =============================================================================
// ACCESSIBILITY SYSTEM
// =============================================================================
class AccessibilitySystem {
    constructor() {
        this.init();
    }

    init() {
        console.log('♿ Accessibility System initializing...');
        this.setupKeyboardNavigation();
        this.setupAriaLabels();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
    }

    setupKeyboardNavigation() {
        // Tab navigation enhancement
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Skip to main content
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link sr-only sr-only-focusable';
        skipLink.textContent = '跳转到主要内容';
        if (document.body) {
            document.body.insertAdjacentElement('afterbegin', skipLink);
        }
    }

    setupAriaLabels() {
        // Auto-add aria-labels for form controls without labels
        document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])').forEach(input => {
            const placeholder = input.placeholder;
            const type = input.type;
            
            if (placeholder) {
                input.setAttribute('aria-label', placeholder);
            } else if (type) {
                input.setAttribute('aria-label', `${type} input`);
            }
        });

        // Enhance button accessibility
        document.querySelectorAll('button:not([aria-label])').forEach(button => {
            const text = button.textContent.trim();
            const icon = button.querySelector('i');
            
            if (!text && icon) {
                const iconClass = icon.className;
                if (iconClass.includes('fa-edit')) {
                    button.setAttribute('aria-label', '编辑');
                } else if (iconClass.includes('fa-delete') || iconClass.includes('fa-trash')) {
                    button.setAttribute('aria-label', '删除');
                } else if (iconClass.includes('fa-plus')) {
                    button.setAttribute('aria-label', '添加');
                }
            }
        });
    }

    setupFocusManagement() {
        // Winston Modal Dispatcher now handles all focus management
        // This method kept for backward compatibility and performance monitoring
        console.log('⚡ Performance focus management delegated to Winston Modal Event Dispatcher');
        
        // Monitor performance of modal operations
        document.addEventListener('winston:modal:shown', (e) => {
            performance.mark('modal-shown-start');
            setTimeout(() => {
                performance.mark('modal-shown-end');
                try {
                    performance.measure('modal-shown-time', 'modal-shown-start', 'modal-shown-end');
                    const measure = performance.getEntriesByName('modal-shown-time')[0];
                    if (measure.duration > 100) {
                        console.warn(`Modal ${e.detail.modalId} slow to focus: ${measure.duration}ms`);
                    }
                } catch (err) {
                    // Silently ignore performance measurement errors
                }
            }, 0);
        });
    }

    // trapFocus method removed - now handled by Winston Modal Event Dispatcher
    // This provides better coordination and prevents conflicts

    setupScreenReaderSupport() {
        // Live region for dynamic content updates
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        if (document.body) {
            document.body.appendChild(liveRegion);
        }

        // Announce function
        window.announceToScreenReader = (message, priority = 'polite') => {
            liveRegion.setAttribute('aria-live', priority);
            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        };
    }

    // Check contrast ratios
    checkColorContrast() {
        const elements = document.querySelectorAll('*');
        const issues = [];

        elements.forEach(el => {
            const styles = getComputedStyle(el);
            const color = styles.color;
            const backgroundColor = styles.backgroundColor;

            if (color && backgroundColor && color !== 'rgba(0, 0, 0, 0)' && backgroundColor !== 'rgba(0, 0, 0, 0)') {
                const ratio = this.calculateContrastRatio(color, backgroundColor);
                if (ratio < 4.5) { // WCAG AA standard
                    issues.push({
                        element: el,
                        ratio: ratio,
                        color: color,
                        backgroundColor: backgroundColor
                    });
                }
            }
        });

        if (issues.length > 0) {
            console.warn('♿ Accessibility: Low contrast detected:', issues);
        }

        return issues;
    }

    calculateContrastRatio(color1, color2) {
        // Simplified contrast calculation
        // In a real implementation, you'd parse RGB values and calculate luminance
        return 4.5; // Placeholder
    }
}

// =============================================================================
// PERFORMANCE LAYER INITIALIZATION
// =============================================================================
class PerformanceLayer {
    constructor() {
        this.monitor = new PerformanceMonitor();
        this.optimizer = new PerformanceOptimizer();
        this.realtime = new RealtimeUpdatesSystem();
        this.accessibility = new AccessibilitySystem();
    }

    init() {
        console.log('🏗️ CoderWiki Performance Layer initialized by Winston');
        
        // Setup performance dashboard
        this.setupPerformanceDashboard();
    }

    setupPerformanceDashboard() {
        // Add performance info to console
        setTimeout(() => {
            const report = this.monitor.generateReport();
            console.log('📊 Performance Dashboard:', {
                navigation: report.navigation?.loadEventEnd || 'N/A',
                resources: report.resources || 0,
                memory: performance.memory ? `${(performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB` : 'N/A'
            });
        }, 5000);
    }

    getPerformanceReport() {
        return this.monitor.generateReport();
    }

    optimizePerformance() {
        this.optimizer.optimizeApiRequests();
        return 'Performance optimizations applied';
    }
}

// =============================================================================
// CHART.JS RESOURCE MANAGER - 解决Chart重用问题
// =============================================================================
class ChartResourceManager {
    constructor() {
        this.charts = new Map();
        this.canvasRegistry = new Set();
        this.init();
    }
    
    init() {
        console.log('📊 Chart Resource Manager initializing...');
        this.setupChartCleanup();
        this.patchChartConstructor();
    }
    
    patchChartConstructor() {
        // 保存原始Chart构造函数
        if (typeof Chart !== 'undefined' && !Chart._winstonPatched) {
            const OriginalChart = Chart;
            
            // 创建包装的Chart构造函数
            window.Chart = function(ctx, config) {
                // 获取canvas元素
                const canvas = typeof ctx === 'string' ? document.getElementById(ctx) : ctx;
                if (!canvas) {
                    throw new Error(`Canvas not found: ${ctx}`);
                }
                
                // 检查canvas是否已经被使用
                const canvasId = canvas.id || `chart-${Date.now()}-${Math.random()}`;
                if (!canvas.id) canvas.id = canvasId;
                
                // 销毁现有图表
                if (window.chartResourceManager.charts.has(canvasId)) {
                    const existingChart = window.chartResourceManager.charts.get(canvasId);
                    console.log(`🔄 Destroying existing chart for canvas: ${canvasId}`);
                    existingChart.destroy();
                    window.chartResourceManager.charts.delete(canvasId);
                }
                
                // 创建新图表
                const chart = new OriginalChart(canvas, config);
                
                // 注册图表
                window.chartResourceManager.charts.set(canvasId, chart);
                window.chartResourceManager.canvasRegistry.add(canvasId);
                
                console.log(`✅ Chart created and registered: ${canvasId}`);
                return chart;
            };
            
            // 复制静态属性和方法
            Object.setPrototypeOf(window.Chart, OriginalChart);
            Object.assign(window.Chart, OriginalChart);
            
            // 标记已修补
            Chart._winstonPatched = true;
            console.log('🔧 Chart.js constructor patched for resource management');
        }
    }
    
    setupChartCleanup() {
        // 页面卸载时清理所有图表
        window.addEventListener('beforeunload', () => {
            this.destroyAllCharts();
        });
        
        // 定期清理未使用的图表
        setInterval(() => {
            this.cleanupUnusedCharts();
        }, 60000); // 每分钟检查一次
    }
    
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            try {
                chart.destroy();
                this.charts.delete(canvasId);
                this.canvasRegistry.delete(canvasId);
                console.log(`🗑️ Chart destroyed: ${canvasId}`);
                return true;
            } catch (error) {
                console.error(`Failed to destroy chart ${canvasId}:`, error);
                return false;
            }
        }
        return false;
    }
    
    destroyAllCharts() {
        console.log('🧹 Destroying all charts...');
        let destroyed = 0;
        
        this.charts.forEach((chart, canvasId) => {
            if (this.destroyChart(canvasId)) {
                destroyed++;
            }
        });
        
        console.log(`✅ Destroyed ${destroyed} charts`);
        return destroyed;
    }
    
    cleanupUnusedCharts() {
        const canvasElements = document.querySelectorAll('canvas');
        const activeCanvasIds = new Set(Array.from(canvasElements).map(c => c.id).filter(Boolean));
        
        // 查找已删除的canvas对应的图表
        const orphanedCharts = [];
        this.canvasRegistry.forEach(canvasId => {
            if (!activeCanvasIds.has(canvasId)) {
                orphanedCharts.push(canvasId);
            }
        });
        
        // 清理孤立的图表
        orphanedCharts.forEach(canvasId => {
            this.destroyChart(canvasId);
        });
        
        if (orphanedCharts.length > 0) {
            console.log(`🧹 Cleaned up ${orphanedCharts.length} orphaned charts`);
        }
    }
    
    getChart(canvasId) {
        return this.charts.get(canvasId);
    }
    
    getAllCharts() {
        return Array.from(this.charts.values());
    }
    
    getChartCount() {
        return this.charts.size;
    }
    
    // 公共API方法
    createSafeChart(ctx, config) {
        return new Chart(ctx, config); // 使用已修补的构造函数
    }
}

// =============================================================================
// GLOBAL EXPORTS
// =============================================================================
window.PerformanceMonitor = PerformanceMonitor;
window.PerformanceOptimizer = PerformanceOptimizer;
window.RealtimeUpdatesSystem = RealtimeUpdatesSystem;
window.AccessibilitySystem = AccessibilitySystem;
window.PerformanceLayer = PerformanceLayer;
window.ChartResourceManager = ChartResourceManager;

// Global instances
window.performanceLayer = new PerformanceLayer();
window.chartResourceManager = new ChartResourceManager();

// Legacy compatibility - Critical missing aliases
window.realtime = window.performanceLayer.realtime;

// Missing Class Aliases (Winston Architecture Consolidation)
window.RealtimeUpdates = RealtimeUpdatesSystem; // ✓ Alias for old RealtimeUpdates
window.LazyLoadManager = PerformanceOptimizer; // ✓ LazyLoad functionality moved to PerformanceOptimizer  
window.KeyboardNavigation = AccessibilitySystem; // ✓ Keyboard nav moved to AccessibilitySystem

// Legacy Method Compatibility
window.RealtimeUpdates.init = function() {
    if (window.performanceLayer && window.performanceLayer.realtime) {
        window.performanceLayer.realtime.init();
    }
};

// Legacy Constructor Compatibility - Critical for dashboard.js
window.RealtimeUpdates.prototype = RealtimeUpdatesSystem.prototype;

window.LazyLoadManager.init = function() {
    if (window.performanceLayer && window.performanceLayer.optimizer) {
        window.performanceLayer.optimizer.optimizeLazyLoading();
    }
};
window.LazyLoadManager.initImageLazyLoad = window.LazyLoadManager.init;
window.LazyLoadManager.initComponentLazyLoad = window.LazyLoadManager.init;

window.KeyboardNavigation.init = function() {
    if (window.performanceLayer && window.performanceLayer.accessibility) {
        window.performanceLayer.accessibility.init();
    }
};

// PerformanceMonitor legacy compatibility
window.PerformanceMonitor.init = function() {
    if (window.performanceLayer) {
        // Already initialized in constructor, just return success
        console.log('✅ PerformanceMonitor.init() - using Winston unified system');
        return true;
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.performanceLayer.init();
    });
} else {
    window.performanceLayer.init();
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PerformanceMonitor,
        PerformanceOptimizer,
        RealtimeUpdatesSystem,
        AccessibilitySystem,
        PerformanceLayer
    };
}

console.log('⚡ Performance Layer loaded - Winston Architecture v1.0');