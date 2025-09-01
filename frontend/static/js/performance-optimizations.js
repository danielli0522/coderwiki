/**
 * 性能优化补丁
 * 减少长任务和提升页面响应性
 */

class PerformanceOptimizations {
    constructor() {
        this.init();
    }

    init() {
        this.optimizeScriptLoading();
        this.implementTaskScheduling();
        this.optimizeDOMOperations();
        this.setupIdleCallbacks();
        this.optimizeEventHandlers();
    }

    /**
     * 优化脚本加载 - 使用异步分块加载
     */
    optimizeScriptLoading() {
        // 分块加载脚本，避免阻塞主线程
        this.scheduleTask(() => {
            const scripts = document.querySelectorAll('script[data-defer-load]');
            scripts.forEach((script, index) => {
                setTimeout(() => {
                    const newScript = document.createElement('script');
                    newScript.src = script.dataset.src;
                    newScript.async = true;
                    document.head.appendChild(newScript);
                }, index * 50); // 每个脚本间隔50ms加载
            });
        });
    }

    /**
     * 实现任务调度器 - 将长任务分解为小任务
     */
    implementTaskScheduling() {
        window.scheduleWork = (work, options = {}) => {
            const { 
                chunkSize = 5, 
                timeSlice = 10,
                priority = 'normal'
            } = options;

            if (Array.isArray(work)) {
                return this.scheduleArrayWork(work, { chunkSize, timeSlice, priority });
            } else if (typeof work === 'function') {
                return this.scheduleTask(work, { timeSlice, priority });
            }
        };
    }

    /**
     * 分块处理数组工作
     */
    scheduleArrayWork(items, { chunkSize, timeSlice, priority }) {
        return new Promise((resolve) => {
            let index = 0;
            const results = [];

            const processChunk = () => {
                const start = performance.now();
                
                while (index < items.length && (performance.now() - start) < timeSlice) {
                    for (let i = 0; i < chunkSize && index < items.length; i++) {
                        results.push(items[index]);
                        index++;
                    }
                }

                if (index < items.length) {
                    // 使用适当的调度方法
                    if (priority === 'high') {
                        requestAnimationFrame(processChunk);
                    } else {
                        this.scheduleTask(processChunk);
                    }
                } else {
                    resolve(results);
                }
            };

            processChunk();
        });
    }

    /**
     * 调度单个任务
     */
    scheduleTask(task, { timeSlice = 10, priority = 'normal' } = {}) {
        if ('scheduler' in window && window.scheduler.postTask) {
            // 使用原生调度器（如果可用）- 修复TaskPriority枚举值
            const validPriorities = {
                'high': 'user-blocking',
                'normal': 'user-visible', 
                'low': 'background'
            };
            const schedulerPriority = validPriorities[priority] || 'user-visible';
            
            // 添加兼容性检查，如果API不支持则降级
            try {
                return window.scheduler.postTask(task, { priority: schedulerPriority });
            } catch (error) {
                console.warn('Scheduler API not supported, falling back to alternative:', error);
                // 降级到requestIdleCallback或setTimeout
                if (priority === 'low' && 'requestIdleCallback' in window) {
                    return new Promise(resolve => {
                        requestIdleCallback(() => resolve(task()));
                    });
                } else {
                    return new Promise(resolve => {
                        setTimeout(() => resolve(task()), priority === 'high' ? 0 : 16);
                    });
                }
            }
        } else if (priority === 'high') {
            return requestAnimationFrame(task);
        } else {
            return new Promise((resolve) => {
                if ('requestIdleCallback' in window) {
                    requestIdleCallback((deadline) => {
                        if (deadline.timeRemaining() > timeSlice) {
                            resolve(task());
                        } else {
                            // 时间不够，重新调度
                            this.scheduleTask(task, { timeSlice, priority }).then(resolve);
                        }
                    });
                } else {
                    setTimeout(() => resolve(task()), 0);
                }
            });
        }
    }

    /**
     * 优化DOM操作 - 批量处理
     */
    optimizeDOMOperations() {
        // 创建DOM操作队列
        let domOperationQueue = [];
        let isProcessing = false;

        window.batchDOMOperation = (operation) => {
            domOperationQueue.push(operation);
            
            if (!isProcessing) {
                isProcessing = true;
                requestAnimationFrame(() => {
                    const operations = domOperationQueue.splice(0);
                    
                    // 批量执行DOM操作
                    operations.forEach(op => {
                        try {
                            op();
                        } catch (error) {
                            console.warn('DOM operation failed:', error);
                        }
                    });
                    
                    isProcessing = false;
                });
            }
        };

        // 优化表格渲染
        this.optimizeTableRendering();
    }

    /**
     * 优化表格渲染 - 虚拟滚动
     */
    optimizeTableRendering() {
        const tables = document.querySelectorAll('table[data-virtual-scroll]');
        
        tables.forEach(table => {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;

            const rowHeight = 50; // 假设每行高度
            const visibleRows = Math.ceil(window.innerHeight / rowHeight) + 10; // 缓冲区
            let allRows = Array.from(tbody.querySelectorAll('tr'));
            
            if (allRows.length <= visibleRows) return; // 行数太少，不需要虚拟滚动

            // 创建虚拟滚动容器
            const container = document.createElement('div');
            container.style.height = `${allRows.length * rowHeight}px`;
            container.style.position = 'relative';
            container.style.overflow = 'auto';
            container.style.maxHeight = '400px';
            
            table.parentNode.insertBefore(container, table);
            container.appendChild(table);

            const renderVisibleRows = () => {
                const scrollTop = container.scrollTop;
                const startIndex = Math.floor(scrollTop / rowHeight);
                const endIndex = Math.min(startIndex + visibleRows, allRows.length);
                
                // 清空tbody
                tbody.innerHTML = '';
                
                // 渲染可见行
                for (let i = startIndex; i < endIndex; i++) {
                    tbody.appendChild(allRows[i].cloneNode(true));
                }
                
                // 调整表格位置
                table.style.transform = `translateY(${startIndex * rowHeight}px)`;
            };

            // 防抖滚动处理
            let scrollTimeout;
            container.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(renderVisibleRows, 10);
            });

            // 初始渲染
            renderVisibleRows();
        });
    }

    /**
     * 设置空闲回调优化
     */
    setupIdleCallbacks() {
        if (!('requestIdleCallback' in window)) return;

        // 在空闲时进行性能统计收集
        const collectPerformanceStats = () => {
            if (window.performanceMonitor) {
                window.performanceMonitor.collectStats();
            }
        };

        // 在空闲时清理缓存
        const cleanupCaches = () => {
            if (window.apiClient && window.apiClient.cache) {
                const now = Date.now();
                const cacheEntries = Array.from(window.apiClient.cache.entries());
                
                cacheEntries.forEach(([key, value]) => {
                    if (now - value.timestamp > 5 * 60 * 1000) { // 5分钟过期
                        window.apiClient.cache.delete(key);
                    }
                });
            }
        };

        // 定期执行优化任务
        const scheduleIdleTasks = () => {
            requestIdleCallback((deadline) => {
                if (deadline.timeRemaining() > 10) {
                    collectPerformanceStats();
                }
                
                if (deadline.timeRemaining() > 20) {
                    cleanupCaches();
                }
                
                // 继续调度
                setTimeout(scheduleIdleTasks, 30000); // 30秒后再次调度
            });
        };

        scheduleIdleTasks();
    }

    /**
     * 优化事件处理器 - 防抖和节流
     */
    optimizeEventHandlers() {
        // 为所有滚动事件添加节流
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type === 'scroll' && typeof listener === 'function') {
                listener = window.performanceOptimizations.throttle(listener, 16); // ~60fps
            } else if (type === 'resize' && typeof listener === 'function') {
                listener = window.performanceOptimizations.debounce(listener, 250);
            } else if (type === 'input' && typeof listener === 'function') {
                listener = window.performanceOptimizations.debounce(listener, 300);
            }
            
            return originalAddEventListener.call(this, type, listener, options);
        };
    }

    /**
     * 节流函数
     */
    throttle(func, wait) {
        let timeout;
        let previous = 0;
        
        return function(...args) {
            const now = Date.now();
            const remaining = wait - (now - previous);
            
            if (remaining <= 0 || remaining > wait) {
                if (timeout) {
                    clearTimeout(timeout);
                    timeout = null;
                }
                previous = now;
                func.apply(this, args);
            } else if (!timeout) {
                timeout = setTimeout(() => {
                    previous = Date.now();
                    timeout = null;
                    func.apply(this, args);
                }, remaining);
            }
        };
    }

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    /**
     * 优化图片加载 - 懒加载
     */
    optimizeImageLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy-load');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                img.classList.add('lazy-load');
                imageObserver.observe(img);
            });
        }
    }
}

// 立即创建实例，避免依赖问题
if (!window.performanceOptimizations) {
    window.performanceOptimizations = new PerformanceOptimizations();
}

// 添加全局方法快捷访问，防止上下文错误
window.debounce = function(func, wait) {
    return window.performanceOptimizations.debounce(func, wait);
};

window.throttle = function(func, wait) {
    return window.performanceOptimizations.throttle(func, wait);
};

// 页面加载后确保初始化完成
document.addEventListener('DOMContentLoaded', () => {
    if (!window.performanceOptimizations) {
        window.performanceOptimizations = new PerformanceOptimizations();
    }
    console.log('✅ Performance optimizations initialized');
});

// 导出给其他模块使用
window.PerformanceOptimizations = PerformanceOptimizations;