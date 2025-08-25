/**
 * CoderWiki 性能优化模块
 * 处理资源加载、缓存和性能监控
 */

class PerformanceOptimizer {
    constructor() {
        this.loadedScripts = new Set();
        this.loadedStyles = new Set();
        this.criticalResources = new Set();
        this.performanceMetrics = {};
        this.resourceCache = new Map();
        this.intersectionObserver = null;
        
        this.init();
    }
    
    init() {
        this.setupIntersectionObserver();
        this.preloadCriticalResources();
        this.optimizeExistingResources();
        this.setupPerformanceMonitoring();
        this.implementLazyLoading();
        this.setupServiceWorker();
        
        console.log('Performance optimizer initialized');
    }
    
    // 预加载关键资源
    preloadCriticalResources() {
        const criticalResources = [
            { href: '/static/css/style.css', as: 'style' },
            { href: '/static/css/components.css', as: 'style' },
            { href: '/static/js/main.js', as: 'script' },
            { href: '/static/js/api_client.js', as: 'script' }
        ];
        
        criticalResources.forEach(resource => {
            this.preloadResource(resource.href, resource.as);
        });
    }
    
    // 预加载资源
    preloadResource(href, as, crossorigin = false) {
        if (this.criticalResources.has(href)) return;
        
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        
        if (crossorigin) {
            link.crossOrigin = 'anonymous';
        }
        
        link.onload = () => {
            console.log(`Preloaded: ${href}`);
        };
        
        link.onerror = () => {
            console.warn(`Failed to preload: ${href}`);
        };
        
        document.head.appendChild(link);
        this.criticalResources.add(href);
    }
    
    // 异步加载CSS
    loadCSS(href, media = 'all', callback = null) {
        if (this.loadedStyles.has(href)) {
            if (callback) callback();
            return Promise.resolve();
        }
        
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = 'only x'; // 临时设置为不匹配的媒体查询
            
            link.onload = () => {
                link.media = media;
                this.loadedStyles.add(href);
                console.log(`CSS loaded: ${href}`);
                if (callback) callback();
                resolve();
            };
            
            link.onerror = () => {
                console.error(`Failed to load CSS: ${href}`);
                reject(new Error(`Failed to load CSS: ${href}`));
            };
            
            document.head.appendChild(link);
        });
    }
    
    // 异步加载JavaScript
    loadJS(src, callback = null) {
        if (this.loadedScripts.has(src)) {
            if (callback) callback();
            return Promise.resolve();
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.async = true;
            
            script.onload = () => {
                this.loadedScripts.add(src);
                console.log(`JS loaded: ${src}`);
                if (callback) callback();
                resolve();
            };
            
            script.onerror = () => {
                console.error(`Failed to load JS: ${src}`);
                reject(new Error(`Failed to load JS: ${src}`));
            };
            
            document.head.appendChild(script);
        });
    }
    
    // 批量加载CSS
    loadCSSBundle(hrefs) {
        const promises = hrefs.map(href => this.loadCSS(href));
        return Promise.all(promises);
    }
    
    // 批量加载JavaScript
    loadJSBundle(srcs) {
        const promises = srcs.map(src => this.loadJS(src));
        return Promise.all(promises);
    }
    
    // 条件加载资源
    loadConditional(condition, resources) {
        if (typeof condition === 'function' ? condition() : condition) {
            const cssResources = resources.css || [];
            const jsResources = resources.js || [];
            
            return Promise.all([
                this.loadCSSBundle(cssResources),
                this.loadJSBundle(jsResources)
            ]);
        }
        return Promise.resolve();
    }
    
    // 按页面类型加载资源
    loadPageResources(pageType) {
        const pageResources = {
            dashboard: {
                css: [
                    '/static/css/dashboard.css'
                ],
                js: [
                    '/static/js/dashboard.js',
                    '/static/js/components/stats.js',
                    '/static/js/components/repository_list.js'
                ]
            },
            document: {
                css: [
                    '/static/css/document_viewer.css'
                ],
                js: [
                    '/static/js/document_viewer.js',
                    '/static/js/viewer_utils.js'
                ]
            },
            repository: {
                css: [
                    '/static/css/repository.css'
                ],
                js: [
                    '/static/js/repository.js'
                ]
            }
        };
        
        const resources = pageResources[pageType];
        if (resources) {
            return Promise.all([
                this.loadCSSBundle(resources.css),
                this.loadJSBundle(resources.js)
            ]);
        }
        
        return Promise.resolve();
    }
    
    // 优化现有资源
    optimizeExistingResources() {
        // 移除重复的样式表
        this.removeDuplicateStyles();
        
        // 延迟加载非关键CSS
        this.deferNonCriticalCSS();
        
        // 优化图片加载
        this.optimizeImages();
        
        // 压缩内联样式
        this.compressInlineStyles();
    }
    
    // 移除重复的样式表
    removeDuplicateStyles() {
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        const seen = new Set();
        
        stylesheets.forEach(link => {
            const href = link.href;
            if (seen.has(href)) {
                link.remove();
                console.log(`Removed duplicate stylesheet: ${href}`);
            } else {
                seen.add(href);
            }
        });
    }
    
    // 延迟加载非关键CSS
    deferNonCriticalCSS() {
        const nonCriticalSelectors = [
            'link[href*="font-awesome"]',
            'link[href*="modal-fixes"]',
            'link[href*="repository-modal-fixes"]'
        ];
        
        nonCriticalSelectors.forEach(selector => {
            const links = document.querySelectorAll(selector);
            links.forEach(link => {
                const href = link.href;
                link.remove();
                
                // 在页面加载后异步加载
                window.addEventListener('load', () => {
                    this.loadCSS(href);
                });
            });
        });
    }
    
    // 优化图片加载
    optimizeImages() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            // 添加loading="lazy"属性
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            
            // 添加decode="async"属性
            if (!img.hasAttribute('decode')) {
                img.setAttribute('decode', 'async');
            }
            
            // 为图片添加占位符
            this.addImagePlaceholder(img);
        });
    }
    
    // 为图片添加占位符
    addImagePlaceholder(img) {
        if (img.classList.contains('placeholder-added')) return;
        
        const placeholder = document.createElement('div');
        placeholder.className = 'image-placeholder';
        placeholder.style.cssText = `
            width: ${img.offsetWidth || 200}px;
            height: ${img.offsetHeight || 150}px;
            background-color: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-size: 14px;
        `;
        placeholder.textContent = '加载中...';
        
        img.parentNode.insertBefore(placeholder, img);
        img.style.display = 'none';
        
        img.onload = () => {
            img.style.display = '';
            placeholder.remove();
        };
        
        img.onerror = () => {
            placeholder.textContent = '加载失败';
            placeholder.style.backgroundColor = '#ffe6e6';
            placeholder.style.color = '#d00';
        };
        
        img.classList.add('placeholder-added');
    }
    
    // 压缩内联样式
    compressInlineStyles() {
        const styleElements = document.querySelectorAll('style');
        
        styleElements.forEach(style => {
            const css = style.textContent;
            const compressed = css
                .replace(/\/\*[\s\S]*?\*\//g, '') // 移除注释
                .replace(/\s{2,}/g, ' ') // 压缩空白
                .replace(/;\s*}/g, '}') // 移除最后的分号
                .trim();
            
            if (compressed !== css) {
                style.textContent = compressed;
                console.log('Compressed inline CSS');
            }
        });
    }
    
    // 设置交叉观察器
    setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            this.intersectionObserver = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.handleElementIntersection(entry.target);
                        }
                    });
                },
                { rootMargin: '50px' }
            );
        }
    }
    
    // 处理元素进入视口
    handleElementIntersection(element) {
        // 懒加载图片
        if (element.tagName === 'IMG' && element.dataset.src) {
            element.src = element.dataset.src;
            element.removeAttribute('data-src');
            this.intersectionObserver.unobserve(element);
        }
        
        // 懒加载组件
        if (element.classList.contains('lazy-component')) {
            this.loadComponent(element);
            this.intersectionObserver.unobserve(element);
        }
    }
    
    // 实现懒加载
    implementLazyLoading() {
        // 懒加载图片
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            if (this.intersectionObserver) {
                this.intersectionObserver.observe(img);
            }
        });
        
        // 懒加载组件
        const lazyComponents = document.querySelectorAll('.lazy-component');
        lazyComponents.forEach(component => {
            if (this.intersectionObserver) {
                this.intersectionObserver.observe(component);
            }
        });
    }
    
    // 加载组件
    loadComponent(element) {
        const componentName = element.dataset.component;
        const componentSrc = element.dataset.src;
        
        if (componentSrc) {
            this.loadJS(componentSrc).then(() => {
                if (componentName && window[componentName]) {
                    new window[componentName](element);
                }
            });
        }
    }
    
    // 设置性能监控
    setupPerformanceMonitoring() {
        if ('performance' in window) {
            // 监控页面加载性能
            window.addEventListener('load', () => {
                this.measurePagePerformance();
            });
            
            // 监控资源加载性能
            this.monitorResourcePerformance();
            
            // 监控用户交互性能
            this.monitorInteractionPerformance();
        }
    }
    
    // 测量页面性能
    measurePagePerformance() {
        const navigation = performance.getEntriesByType('navigation')[0];
        
        if (navigation) {
            this.performanceMetrics = {
                dns: navigation.domainLookupEnd - navigation.domainLookupStart,
                connection: navigation.connectEnd - navigation.connectStart,
                request: navigation.responseStart - navigation.requestStart,
                response: navigation.responseEnd - navigation.responseStart,
                domParsing: navigation.domContentLoadedEventStart - navigation.responseEnd,
                domReady: navigation.domContentLoadedEventEnd - navigation.navigationStart,
                pageLoad: navigation.loadEventEnd - navigation.navigationStart
            };
            
            console.log('Page Performance Metrics:', this.performanceMetrics);
            
            // 发送性能数据到服务器
            this.sendPerformanceData();
        }
    }
    
    // 监控资源性能
    monitorResourcePerformance() {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (entry.duration > 1000) { // 超过1秒的资源
                    console.warn(`Slow resource: ${entry.name} (${entry.duration}ms)`);
                }
            });
        });
        
        observer.observe({ entryTypes: ['resource'] });
    }
    
    // 监控交互性能
    monitorInteractionPerformance() {
        // 监控长任务
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    console.warn(`Long task detected: ${entry.duration}ms`);
                });
            });
            
            observer.observe({ entryTypes: ['longtask'] });
        }
        
        // 监控页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseNonEssentialTasks();
            } else {
                this.resumeNonEssentialTasks();
            }
        });
    }
    
    // 暂停非必要任务
    pauseNonEssentialTasks() {
        // 暂停动画
        document.querySelectorAll('.loading').forEach(el => {
            el.style.animationPlayState = 'paused';
        });
        
        // 暂停定时器（需要组件配合）
        window.dispatchEvent(new CustomEvent('pauseTimers'));
    }
    
    // 恢复非必要任务
    resumeNonEssentialTasks() {
        // 恢复动画
        document.querySelectorAll('.loading').forEach(el => {
            el.style.animationPlayState = 'running';
        });
        
        // 恢复定时器
        window.dispatchEvent(new CustomEvent('resumeTimers'));
    }
    
    // 发送性能数据
    sendPerformanceData() {
        if (window.CoderWiki && window.CoderWiki.api) {
            window.CoderWiki.api.post('/api/performance', {
                metrics: this.performanceMetrics,
                userAgent: navigator.userAgent,
                timestamp: Date.now()
            }).catch(error => {
                console.log('Failed to send performance data:', error);
            });
        }
    }
    
    // 设置Service Worker
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }
    
    // 获取性能建议
    getPerformanceRecommendations() {
        const recommendations = [];
        
        if (this.performanceMetrics.pageLoad > 3000) {
            recommendations.push('页面加载时间过长，建议优化资源加载');
        }
        
        if (this.loadedStyles.size > 10) {
            recommendations.push('CSS文件过多，建议合并压缩');
        }
        
        if (this.loadedScripts.size > 15) {
            recommendations.push('JavaScript文件过多，建议按需加载');
        }
        
        return recommendations;
    }
    
    // 清理缓存
    clearCache() {
        this.resourceCache.clear();
        localStorage.removeItem('performance-cache');
        console.log('Performance cache cleared');
    }
}

// 资源管理器类
class ResourceManager {
    constructor() {
        this.bundles = new Map();
        this.dependencies = new Map();
    }
    
    // 定义资源包
    defineBundle(name, resources) {
        this.bundles.set(name, resources);
    }
    
    // 加载资源包
    loadBundle(name) {
        const resources = this.bundles.get(name);
        if (!resources) {
            console.warn(`Bundle not found: ${name}`);
            return Promise.resolve();
        }
        
        const optimizer = window.performanceOptimizer;
        return Promise.all([
            optimizer.loadCSSBundle(resources.css || []),
            optimizer.loadJSBundle(resources.js || [])
        ]);
    }
    
    // 设置依赖关系
    setDependency(resource, dependencies) {
        this.dependencies.set(resource, dependencies);
    }
    
    // 加载资源及其依赖
    loadWithDependencies(resource) {
        const deps = this.dependencies.get(resource);
        const optimizer = window.performanceOptimizer;
        
        if (deps && deps.length > 0) {
            return Promise.all(deps.map(dep => 
                this.loadWithDependencies(dep)
            )).then(() => {
                return optimizer.loadJS(resource);
            });
        } else {
            return optimizer.loadJS(resource);
        }
    }
}

// 创建全局实例
const performanceOptimizer = new PerformanceOptimizer();
const resourceManager = new ResourceManager();

// 定义常用资源包
resourceManager.defineBundle('dashboard', {
    css: ['/static/css/dashboard.css'],
    js: [
        '/static/js/dashboard.js',
        '/static/js/components/stats.js',
        '/static/js/components/repository_list.js',
        '/static/js/components/task_progress.js'
    ]
});

resourceManager.defineBundle('modal', {
    css: [
        '/static/css/modal-enhanced.css'
    ],
    js: [
        '/static/js/modal-system.js'
    ]
});

resourceManager.defineBundle('accessibility', {
    css: ['/static/css/accessibility.css'],
    js: ['/static/js/accessibility.js']
});

// 导出到全局
window.PerformanceOptimizer = PerformanceOptimizer;
window.ResourceManager = ResourceManager;
window.performanceOptimizer = performanceOptimizer;
window.resourceManager = resourceManager;