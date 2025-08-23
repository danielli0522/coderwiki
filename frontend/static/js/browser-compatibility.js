// 浏览器兼容性处理脚本

// 浏览器兼容性检测器
const BrowserCompatibility = {
    // 浏览器信息
    browser: {},
    
    // 功能支持检测
    features: {},
    
    // 初始化兼容性检测
    init: function() {
        this.detectBrowser();
        this.detectFeatures();
        this.applyPolyfills();
        this.handleCompatibilityIssues();
        this.logCompatibilityInfo();
    },
    
    // 检测浏览器
    detectBrowser: function() {
        const ua = navigator.userAgent;
        let browserName = 'unknown';
        let browserVersion = 'unknown';
        
        // 检测Chrome
        if (ua.indexOf('Chrome') > -1) {
            browserName = 'chrome';
            browserVersion = ua.match(/Chrome\/(\d+)/)[1];
        }
        // 检测Firefox
        else if (ua.indexOf('Firefox') > -1) {
            browserName = 'firefox';
            browserVersion = ua.match(/Firefox\/(\d+)/)[1];
        }
        // 检测Safari
        else if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) {
            browserName = 'safari';
            browserVersion = ua.match(/Version\/(\d+)/)[1];
        }
        // 检测Edge
        else if (ua.indexOf('Edge') > -1) {
            browserName = 'edge';
            browserVersion = ua.match(/Edge\/(\d+)/)[1];
        }
        // 检测IE
        else if (ua.indexOf('Trident') > -1) {
            browserName = 'ie';
            browserVersion = ua.match(/rv:(\d+)/)[1];
        }
        
        this.browser = {
            name: browserName,
            version: parseInt(browserVersion),
            userAgent: ua,
            isMobile: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua),
            isTablet: /iPad|Android(?!.*Mobile)/i.test(ua)
        };
    },
    
    // 检测功能支持
    detectFeatures: function() {
        this.features = {
            // CSS功能
            cssGrid: this.detectCSSFeature('grid'),
            cssFlexbox: this.detectCSSFeature('flexbox'),
            cssVariables: this.detectCSSFeature('variables'),
            cssAnimations: this.detectCSSFeature('animations'),
            cssTransitions: this.detectCSSFeature('transitions'),
            
            // JavaScript功能
            arrowFunctions: this.detectJSFeature('() => {}'),
            templateLiterals: this.detectJSFeature('`test`'),
            destructuring: this.detectJSFeature('const {a} = {a: 1}'),
            spreadOperator: this.detectJSFeature('[...arr]'),
            asyncAwait: this.detectJSFeature('async function() {}'),
            
            // Web API功能
            intersectionObserver: 'IntersectionObserver' in window,
            mutationObserver: 'MutationObserver' in window,
            fetch: 'fetch' in window,
            promise: 'Promise' in window,
            serviceWorker: 'serviceWorker' in navigator,
            webWorkers: 'Worker' in window,
            webStorage: 'localStorage' in window,
            geolocation: 'geolocation' in navigator,
            notifications: 'Notification' in window,
            canvas: !!document.createElement('canvas').getContext,
            webGL: this.detectWebGL(),
            webSocket: 'WebSocket' in window,
            eventSource: 'EventSource' in window,
            
            // 其他功能
            touchEvents: 'ontouchstart' in window,
            deviceOrientation: 'DeviceOrientationEvent' in window,
            deviceMotion: 'DeviceMotionEvent' in window,
            speechRecognition: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
            vibration: 'vibrate' in navigator,
            battery: 'getBattery' in navigator,
            networkInformation: 'connection' in navigator
        };
    },
    
    // 检测CSS功能支持
    detectCSSFeature: function(feature) {
        const testElement = document.createElement('div');
        const features = {
            grid: 'grid',
            flexbox: 'flex',
            variables: 'variables',
            animations: 'animation',
            transitions: 'transition'
        };
        
        return testElement.style[features[feature]] !== undefined;
    },
    
    // 检测JavaScript功能支持
    detectJSFeature: function(code) {
        try {
            new Function(code);
            return true;
        } catch (e) {
            return false;
        }
    },
    
    // 检测WebGL支持
    detectWebGL: function() {
        try {
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && 
                     (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
            return false;
        }
    },
    
    // 应用polyfills
    applyPolyfills: function() {
        // Array.prototype.includes polyfill
        if (!Array.prototype.includes) {
            Array.prototype.includes = function(searchElement) {
                return this.indexOf(searchElement) !== -1;
            };
        }
        
        // Array.prototype.find polyfill
        if (!Array.prototype.find) {
            Array.prototype.find = function(predicate) {
                if (this === null) {
                    throw new TypeError('Array.prototype.find called on null or undefined');
                }
                if (typeof predicate !== 'function') {
                    throw new TypeError('predicate must be a function');
                }
                const list = Object(this);
                const length = list.length >>> 0;
                const thisArg = arguments[1];
                let value;
                for (let i = 0; i < length; i++) {
                    value = list[i];
                    if (predicate.call(thisArg, value, i, list)) {
                        return value;
                    }
                }
                return undefined;
            };
        }
        
        // Object.assign polyfill
        if (typeof Object.assign !== 'function') {
            Object.assign = function(target) {
                if (target === null) {
                    throw new TypeError('Cannot convert undefined or null to object');
                }
                const to = Object(target);
                for (let index = 1; index < arguments.length; index++) {
                    const nextSource = arguments[index];
                    if (nextSource !== null) {
                        for (const nextKey in nextSource) {
                            if (Object.prototype.hasOwnProperty.call(nextSource, nextKey)) {
                                to[nextKey] = nextSource[nextKey];
                            }
                        }
                    }
                }
                return to;
            };
        }
        
        // String.prototype.includes polyfill
        if (!String.prototype.includes) {
            String.prototype.includes = function(search, start) {
                if (typeof start !== 'number') {
                    start = 0;
                }
                if (start + search.length > this.length) {
                    return false;
                }
                return this.indexOf(search, start) !== -1;
            };
        }
        
        // CustomEvent polyfill
        if (typeof window.CustomEvent !== 'function') {
            function CustomEvent(event, params) {
                params = params || { bubbles: false, cancelable: false, detail: undefined };
                const evt = document.createEvent('CustomEvent');
                evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
                return evt;
            }
            CustomEvent.prototype = window.Event.prototype;
            window.CustomEvent = CustomEvent;
        }
        
        // NodeList.forEach polyfill
        if (window.NodeList && !NodeList.prototype.forEach) {
            NodeList.prototype.forEach = function(callback, thisArg) {
                thisArg = thisArg || window;
                for (let i = 0; i < this.length; i++) {
                    callback.call(thisArg, this[i], i, this);
                }
            };
        }
    },
    
    // 处理兼容性问题
    handleCompatibilityIssues: function() {
        // 处理IE兼容性问题
        if (this.browser.name === 'ie' && this.browser.version < 12) {
            this.handleIECompatibility();
        }
        
        // 处理Safari兼容性问题
        if (this.browser.name === 'safari' && this.browser.version < 10) {
            this.handleSafariCompatibility();
        }
        
        // 处理移动设备兼容性问题
        if (this.browser.isMobile) {
            this.handleMobileCompatibility();
        }
        
        // 处理功能不支持的问题
        this.handleUnsupportedFeatures();
    },
    
    // 处理IE兼容性
    handleIECompatibility: function() {
        // 添加IE特定的CSS类
        document.documentElement.classList.add('ie-browser');
        
        // 禁用某些动画效果
        const animatedElements = document.querySelectorAll('[data-animate]');
        animatedElements.forEach(element => {
            element.style.animation = 'none';
        });
        
        // 显示兼容性警告
        this.showCompatibilityWarning('Internet Explorer', '建议使用现代浏览器以获得最佳体验');
    },
    
    // 处理Safari兼容性
    handleSafariCompatibility: function() {
        // 添加Safari特定的CSS类
        document.documentElement.classList.add('safari-browser');
        
        // 处理Safari的flexbox问题
        const flexContainers = document.querySelectorAll('.d-flex, .flex-row, .flex-column');
        flexContainers.forEach(container => {
            container.style.display = '-webkit-flex';
            container.style.display = 'flex';
        });
    },
    
    // 处理移动设备兼容性
    handleMobileCompatibility: function() {
        // 添加移动设备特定的CSS类
        document.documentElement.classList.add('mobile-device');
        
        // 优化触摸事件
        this.optimizeTouchEvents();
        
        // 处理viewport问题
        this.handleViewport();
    },
    
    // 处理不支持的功能
    handleUnsupportedFeatures: function() {
        const unsupportedFeatures = [];
        
        // 检查关键功能
        if (!this.features.cssGrid) {
            unsupportedFeatures.push('CSS Grid');
        }
        if (!this.features.cssFlexbox) {
            unsupportedFeatures.push('CSS Flexbox');
        }
        if (!this.features.fetch) {
            unsupportedFeatures.push('Fetch API');
        }
        if (!this.features.promise) {
            unsupportedFeatures.push('Promise');
        }
        
        // 如果有不支持的关键功能，显示警告
        if (unsupportedFeatures.length > 0) {
            this.showFeatureWarning(unsupportedFeatures);
        }
    },
    
    // 优化触摸事件
    optimizeTouchEvents: function() {
        // 为移动设备添加触摸事件支持
        const touchElements = document.querySelectorAll('button, .btn, .clickable');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', function() {
                this.classList.remove('touch-active');
            });
        });
    },
    
    // 处理viewport
    handleViewport: function() {
        // 设置移动设备特定的viewport
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 
                'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
        }
    },
    
    // 显示兼容性警告
    showCompatibilityWarning: function(browserName, message) {
        const warning = document.createElement('div');
        warning.className = 'compatibility-warning alert alert-warning alert-dismissible fade show';
        warning.innerHTML = `
            <strong>浏览器兼容性警告:</strong> 您正在使用 ${browserName}，${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(warning, document.body.firstChild);
    },
    
    // 显示功能警告
    showFeatureWarning: function(features) {
        const warning = document.createElement('div');
        warning.className = 'feature-warning alert alert-info alert-dismissible fade show';
        warning.innerHTML = `
            <strong>功能支持警告:</strong> 您的浏览器不支持以下功能: ${features.join(', ')}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(warning, document.body.firstChild);
    },
    
    // 记录兼容性信息
    logCompatibilityInfo: function() {
        console.group('浏览器兼容性信息');
        console.log('浏览器:', this.browser);
        console.log('功能支持:', this.features);
        console.groupEnd();
        
        // 发送兼容性数据到服务器
        this.sendCompatibilityData();
    },
    
    // 发送兼容性数据
    sendCompatibilityData: function() {
        if (this.features.fetch) {
            fetch('/api/system/browser-compatibility', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    browser: this.browser,
                    features: this.features,
                    timestamp: new Date().toISOString()
                })
            }).catch(() => {
                // 静默失败
            });
        }
    },
    
    // 获取浏览器兼容性建议
    getCompatibilityAdvice: function() {
        const advice = [];
        
        // 基于浏览器版本提供建议
        if (this.browser.name === 'ie' && this.browser.version < 12) {
            advice.push('建议升级到Microsoft Edge或Chrome浏览器');
        }
        
        if (this.browser.name === 'safari' && this.browser.version < 12) {
            advice.push('建议升级到最新版本的Safari浏览器');
        }
        
        // 基于功能支持提供建议
        if (!this.features.cssGrid) {
            advice.push('您的浏览器不支持CSS Grid，某些布局可能显示不正常');
        }
        
        if (!this.features.fetch) {
            advice.push('您的浏览器不支持Fetch API，某些功能可能无法正常工作');
        }
        
        return advice;
    }
};

// 初始化浏览器兼容性检测
document.addEventListener('DOMContentLoaded', function() {
    BrowserCompatibility.init();
});

// 导出模块
window.BrowserCompatibility = BrowserCompatibility;