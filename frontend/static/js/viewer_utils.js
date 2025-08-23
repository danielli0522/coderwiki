/**
 * Document Viewer Utilities
 * 
 * This file contains utility functions for the document viewer.
 */

class ViewerUtils {
    constructor() {
        this.cache = new Map();
        this.debounceTimers = new Map();
        this.throttleTimers = new Map();
    }
    
    /**
     * Debounce function to limit how often a function can be called
     */
    debounce(func, wait, immediate = false) {
        const key = `${func.name}_${wait}`;
        return (...args) => {
            const later = () => {
                this.debounceTimers.delete(key);
                if (!immediate) func(...args);
            };
            
            const callNow = immediate && !this.debounceTimers.has(key);
            clearTimeout(this.debounceTimers.get(key));
            this.debounceTimers.set(key, setTimeout(later, wait));
            
            if (callNow) func(...args);
        };
    }
    
    /**
     * Throttle function to limit how often a function can be called
     */
    throttle(func, limit) {
        const key = `${func.name}_${limit}`;
        return (...args) => {
            if (!this.throttleTimers.has(key)) {
                func(...args);
                this.throttleTimers.set(key, setTimeout(() => {
                    this.throttleTimers.delete(key);
                }, limit));
            }
        };
    }
    
    /**
     * Cache management
     */
    setCache(key, value, ttl = 300000) { // 5 minutes default
        const expiry = Date.now() + ttl;
        this.cache.set(key, { value, expiry });
        
        // Clean up expired cache items
        this.cleanupCache();
    }
    
    getCache(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            return null;
        }
        
        return item.value;
    }
    
    clearCache() {
        this.cache.clear();
    }
    
    cleanupCache() {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (now > item.expiry) {
                this.cache.delete(key);
            }
        }
    }
    
    /**
     * Text processing utilities
     */
    extractText(html) {
        const div = document.createElement('div');
        div.innerHTML = html;
        return div.textContent || div.innerText || '';
    }
    
    stripHtml(html) {
        const div = document.createElement('div');
        div.innerHTML = html;
        return div.textContent || div.innerText || '';
    }
    
    truncateText(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    highlightText(text, query, className = 'highlight') {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, `<span class="${className}">$1</span>`);
    }
    
    removeHighlight(text) {
        return text.replace(/<span class="highlight">(.*?)<\/span>/gi, '$1');
    }
    
    /**
     * DOM utilities
     */
    createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else if (key === 'textContent') {
                element.textContent = value;
            } else {
                element.setAttribute(key, value);
            }
        }
        
        if (content) {
            element.innerHTML = content;
        }
        
        return element;
    }
    
    removeElement(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }
    
    addClass(element, className) {
        if (element) {
            element.classList.add(className);
        }
    }
    
    removeClass(element, className) {
        if (element) {
            element.classList.remove(className);
        }
    }
    
    toggleClass(element, className) {
        if (element) {
            element.classList.toggle(className);
        }
    }
    
    hasClass(element, className) {
        return element ? element.classList.contains(className) : false;
    }
    
    /**
     * Event utilities
     */
    on(element, event, handler, options = {}) {
        if (element) {
            element.addEventListener(event, handler, options);
        }
    }
    
    off(element, event, handler, options = {}) {
        if (element) {
            element.removeEventListener(event, handler, options);
        }
    }
    
    once(element, event, handler) {
        if (element) {
            element.addEventListener(event, handler, { once: true });
        }
    }
    
    /**
     * Animation utilities
     */
    fadeIn(element, duration = 300) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.opacity = Math.min(progress / duration, 1);
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    fadeOut(element, duration = 300) {
        if (!element) return;
        
        let start = null;
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.opacity = Math.max(1 - progress / duration, 0);
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    slideDown(element, duration = 300) {
        if (!element) return;
        
        element.style.height = '0';
        element.style.overflow = 'hidden';
        element.style.display = 'block';
        
        const targetHeight = element.scrollHeight;
        let start = null;
        
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.height = `${Math.min((progress / duration) * targetHeight, targetHeight)}px`;
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.height = 'auto';
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    slideUp(element, duration = 300) {
        if (!element) return;
        
        const targetHeight = element.scrollHeight;
        element.style.height = `${targetHeight}px`;
        element.style.overflow = 'hidden';
        
        let start = null;
        
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.height = `${Math.max(targetHeight - (progress / duration) * targetHeight, 0)}px`;
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
                element.style.height = 'auto';
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    /**
     * Format utilities
     */
    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatNumber(number) {
        return new Intl.NumberFormat().format(number);
    }
    
    /**
     * URL utilities
     */
    parseUrl(url) {
        try {
            return new URL(url);
        } catch (e) {
            return null;
        }
    }
    
    isUrlValid(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    getQueryParam(name, url = window.location.href) {
        const urlObj = new URL(url);
        return urlObj.searchParams.get(name);
    }
    
    setQueryParam(name, value, url = window.location.href) {
        const urlObj = new URL(url);
        urlObj.searchParams.set(name, value);
        return urlObj.toString();
    }
    
    /**
     * Storage utilities
     */
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Local storage error:', e);
        }
    }
    
    getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Local storage error:', e);
            return defaultValue;
        }
    }
    
    removeLocalStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Local storage error:', e);
        }
    }
    
    clearLocalStorage() {
        try {
            localStorage.clear();
        } catch (e) {
            console.error('Local storage error:', e);
        }
    }
    
    /**
     * Performance utilities
     */
    measureTime(label) {
        console.time(label);
        return () => console.timeEnd(label);
    }
    
    async measureAsyncTime(label, asyncFunction) {
        const start = performance.now();
        const result = await asyncFunction();
        const end = performance.now();
        console.log(`${label}: ${end - start}ms`);
        return result;
    }
    
    /**
     * Validation utilities
     */
    isEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    isPhoneNumber(phone) {
        const re = /^[\+]?[1-9][\d]{0,15}$/;
        return re.test(phone);
    }
    
    isEmpty(value) {
        return value === null || value === undefined || value === '';
    }
    
    isNotEmpty(value) {
        return !this.isEmpty(value);
    }
    
    /**
     * Array utilities
     */
    unique(array) {
        return [...new Set(array)];
    }
    
    chunk(array, size) {
        const chunks = [];
        for (let i = 0; i < array.length; i += size) {
            chunks.push(array.slice(i, i + size));
        }
        return chunks;
    }
    
    flatten(array) {
        return array.flat();
    }
    
    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    }
    
    /**
     * Object utilities
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const cloned = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    cloned[key] = this.deepClone(obj[key]);
                }
            }
            return cloned;
        }
    }
    
    mergeObjects(target, source) {
        const result = this.deepClone(target);
        for (const key in source) {
            if (source.hasOwnProperty(key)) {
                if (typeof source[key] === 'object' && source[key] !== null) {
                    result[key] = this.mergeObjects(result[key] || {}, source[key]);
                } else {
                    result[key] = source[key];
                }
            }
        }
        return result;
    }
    
    /**
     * String utilities
     */
    slugify(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    }
    
    capitalize(text) {
        return text.charAt(0).toUpperCase() + text.slice(1);
    }
    
    camelCase(text) {
        return text
            .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => 
                index === 0 ? word.toLowerCase() : word.toUpperCase())
            .replace(/\s+/g, '');
    }
    
    kebabCase(text) {
        return text
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .replace(/\s+/g, '-')
            .toLowerCase();
    }
    
    /**
     * Error handling utilities
     */
    safeExecute(func, defaultValue = null) {
        try {
            return func();
        } catch (e) {
            console.error('Safe execute error:', e);
            return defaultValue;
        }
    }
    
    async safeAsyncExecute(asyncFunc, defaultValue = null) {
        try {
            return await asyncFunc();
        } catch (e) {
            console.error('Safe async execute error:', e);
            return defaultValue;
        }
    }
    
    /**
     * Browser detection utilities
     */
    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browserName = 'Unknown';
        let browserVersion = 'Unknown';
        
        if (ua.indexOf('Chrome') > -1) {
            browserName = 'Chrome';
            browserVersion = ua.match(/Chrome\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('Safari') > -1) {
            browserName = 'Safari';
            browserVersion = ua.match(/Version\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('Firefox') > -1) {
            browserName = 'Firefox';
            browserVersion = ua.match(/Firefox\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('MSIE') > -1 || ua.indexOf('Trident') > -1) {
            browserName = 'Internet Explorer';
            browserVersion = ua.match(/(?:MSIE |rv:)(\d+)/)?.[1] || 'Unknown';
        }
        
        return { browserName, browserVersion, userAgent: ua };
    }
    
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    isTablet() {
        return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
    }
    
    isDesktop() {
        return !this.isMobile() && !this.isTablet();
    }
    
    /**
     * Accessibility utilities
     */
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.setAttribute('aria-hidden', 'false');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        
        document.body.appendChild(announcement);
        announcement.textContent = message;
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusableElement = focusableElements[0];
        const lastFocusableElement = focusableElements[focusableElements.length - 1];
        
        const trapFocusHandler = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusableElement) {
                        e.preventDefault();
                        lastFocusableElement.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusableElement) {
                        e.preventDefault();
                        firstFocusableElement.focus();
                    }
                }
            }
        };
        
        element.addEventListener('keydown', trapFocusHandler);
        
        return () => {
            element.removeEventListener('keydown', trapFocusHandler);
        };
    }
}

// Export for global use
window.ViewerUtils = new ViewerUtils();