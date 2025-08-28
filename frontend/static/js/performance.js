// 性能优化脚本
// Winston架构兼容性处理 - 避免与performance-unified.js冲突

// 性能监控 - 只在未定义时创建
if (typeof window.PerformanceMonitor === 'undefined') {
window.PerformanceMonitor = {
    // 页面加载性能指标
    metrics: {
        navigationTiming: {},
        resourceTiming: {},
        paintTiming: {}
    },

    // 初始化性能监控
    init: function() {
        this.collectNavigationTiming();
        this.collectPaintTiming();
        this.collectResourceTiming();
        this.setupPerformanceObserver();
    },

    // 收集导航时间
    collectNavigationTiming: function() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            this.metrics.navigationTiming = {
                pageLoad: timing.loadEventEnd - timing.navigationStart,
                domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaint: timing.responseEnd - timing.navigationStart
            };

            // 发送到后端或本地存储
            this.saveMetrics();
        }
    },

    // 收集绘制时间
    collectPaintTiming: function() {
        if (window.performance && window.performance.getEntriesByType) {
            const paintEntries = window.performance.getEntriesByType('paint');
            paintEntries.forEach(entry => {
                this.metrics.paintTiming[entry.name] = entry.startTime;
            });
        }
    },

    // 收集资源时间
    collectResourceTiming: function() {
        if (window.performance && window.performance.getEntriesByType) {
            const resources = window.performance.getEntriesByType('resource');
            this.metrics.resourceTiming = {
                totalResources: resources.length,
                slowResources: resources.filter(r => r.duration > 1000).length
            };
        }
    },

    // 设置性能观察者
    setupPerformanceObserver: function() {
        if (window.PerformanceObserver) {
            // 观察长任务
            const longTaskObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    console.warn('Long task detected:', entry.duration, 'ms');
                });
            });
            longTaskObserver.observe({ entryTypes: ['longtask'] });

            // 观察布局变化
            const layoutObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    console.warn('Layout shift detected:', entry.value);
                });
            });
            layoutObserver.observe({ entryTypes: ['layout-shift'] });
        }
    },

    // 保存性能指标
    saveMetrics: function() {
        try {
            localStorage.setItem('performanceMetrics', JSON.stringify(this.metrics));

            // 如果有后端API，发送性能数据
            if (typeof fetch !== 'undefined') {
                // 检查用户是否已登录
                fetch('/api/auth/status', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    redirect: 'manual'
                }).then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                    return { logged_in: false };
                }).then(data => {
                    if (data.logged_in) {
                        // 只有登录用户才发送性能数据
                        return fetch('/api/system/performance', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(this.metrics)
                        });
                    }
                }).catch((error) => {
                    // 静默失败，不显示错误消息
                    console.debug('性能数据发送失败:', error);
                });
            }
        } catch (error) {
            // 静默处理错误，避免影响用户体验
            console.debug('性能指标保存失败:', error);
        }
    }
};

// 懒加载管理器
const LazyLoadManager = {
    // 图片懒加载
    initImageLazyLoad: function() {
        const images = document.querySelectorAll('img[data-src]');

        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // 回退方案
            images.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    },

    // 组件懒加载
    initComponentLazyLoad: function() {
        const components = document.querySelectorAll('[data-lazy-component]');

        if ('IntersectionObserver' in window) {
            const componentObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const component = entry.target;
                        const componentName = component.dataset.lazyComponent;

                        // 动态加载组件
                        this.loadComponent(componentName, component);
                        observer.unobserve(component);
                    }
                });
            }, { threshold: 0.1 });

            components.forEach(component => componentObserver.observe(component));
        }
    },

    // 加载组件
    loadComponent: function(componentName, container) {
        // 这里可以实现组件的动态加载
        console.log('Loading component:', componentName);
    }
};
} // 结束 PerformanceMonitor 定义

// 资源预加载器
const ResourcePreloader = {
    // 预加载关键资源
    preloadCriticalResources: function() {
        const criticalResources = [
            '/static/css/style.css',
            '/static/css/components.css'
        ];

        criticalResources.forEach(resource => {
            if (resource.endsWith('.css')) {
                this.preloadCSS(resource);
            }
        });
    },

    // 预加载CSS
    preloadCSS: function(href) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = href;
        link.onload = function() {
            this.rel = 'stylesheet';
        };
        document.head.appendChild(link);
    },

    // 预连接到关键域名
    preconnectToDomains: function() {
        const domains = [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://cdn.jsdelivr.net'
        ];

        domains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = domain;
            document.head.appendChild(link);
        });
    }
};

// 内存管理器
const MemoryManager = {
    // 清理未使用的事件监听器
    cleanupEventListeners: function() {
        // 这里可以实现事件监听器的清理逻辑
    },

    // 清理DOM元素
    cleanupDOM: function() {
        // 移除空的文本节点
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    if (node.nodeValue.trim() === '') {
                        return NodeFilter.FILTER_ACCEPT;
                    }
                    return NodeFilter.FILTER_REJECT;
                }
            }
        );

        while (walker.nextNode()) {
            const node = walker.currentNode;
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        }
    },

    // 优化内存使用
    optimizeMemory: function() {
        // 清理大型对象
        if (window.performance && window.performance.memory) {
            const memory = window.performance.memory;
            if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.8) {
                console.warn('Memory usage high, performing cleanup...');
                this.cleanupDOM();
                this.cleanupEventListeners();
            }
        }
    }
};

// 离线缓存管理器
const OfflineCacheManager = {
    // 初始化Service Worker
    initServiceWorker: function() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(registration => {
                    console.log('ServiceWorker registration successful');
                })
                .catch(error => {
                    // 静默处理Service Worker注册失败
                    console.debug('ServiceWorker registration failed:', error);
                });
        }
    },

    // 检查离线状态
    checkOfflineStatus: function() {
        window.addEventListener('online', () => {
            this.showOnlineStatus();
        });

        window.addEventListener('offline', () => {
            this.showOfflineStatus();
        });
    },

    // 显示在线状态
    showOnlineStatus: function() {
        console.log('Application is online');
        // 可以显示在线状态的UI
    },

    // 显示离线状态
    showOfflineStatus: function() {
        console.log('Application is offline');
        // 可以显示离线状态的UI
    }
};

// 初始化所有性能优化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化性能监控
    PerformanceMonitor.init();

    // 初始化懒加载
    LazyLoadManager.initImageLazyLoad();
    LazyLoadManager.initComponentLazyLoad();

    // 预加载资源
    ResourcePreloader.preloadCriticalResources();
    ResourcePreloader.preconnectToDomains();

    // 初始化离线缓存
    OfflineCacheManager.initServiceWorker();
    OfflineCacheManager.checkOfflineStatus();

    // 定期内存管理
    setInterval(() => {
        MemoryManager.optimizeMemory();
    }, 30000); // 每30秒检查一次
});

// 导出模块 - 只在未定义时设置
if (!window.PerformanceMonitor) {
    window.PerformanceMonitor = PerformanceMonitor;
}
window.LazyLoadManager = LazyLoadManager;
window.ResourcePreloader = ResourcePreloader;
window.MemoryManager = MemoryManager;
window.OfflineCacheManager = OfflineCacheManager;
