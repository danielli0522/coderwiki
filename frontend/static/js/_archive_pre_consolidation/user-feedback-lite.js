/**
 * 轻量级用户反馈系统
 * 无阻塞覆盖层，纯粹的Toast通知和轻量加载指示器
 */

class LiteUserFeedback {
    constructor() {
        this.isInitialized = false;
        this.toastContainer = null;
        this.activeToasts = new Set();
        
        // 立即初始化基础功能
        this.initBasicFeatures();
    }
    
    initBasicFeatures() {
        if (this.isInitialized) return;
        
        // 仅在需要时创建Toast容器
        this.ensureToastContainer();
        
        this.isInitialized = true;
        console.log('Lite User Feedback System initialized');
    }
    
    // 确保Toast容器存在（懒加载）
    ensureToastContainer() {
        if (this.toastContainer || !document.body) return;
        
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'toast-container-lite';
        this.toastContainer.className = 'position-fixed top-0 end-0 p-3';
        this.toastContainer.style.cssText = `
            z-index: 1055;
            pointer-events: none;
        `;
        this.toastContainer.setAttribute('aria-live', 'polite');
        
        document.body.appendChild(this.toastContainer);
    }
    
    // 显示Toast消息
    showToast(message, type = 'info', options = {}) {
        this.ensureToastContainer();
        
        const duration = options.duration || 3000;
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-bg-${this.getToastClass(type)} border-0`;
        toast.style.cssText = 'pointer-events: auto;';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${this.getToastIcon(type)} ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="liteUserFeedback.hideToast('${toastId}')"></button>
            </div>
        `;
        
        this.toastContainer.appendChild(toast);
        this.activeToasts.add(toastId);
        
        // 显示动画
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // 自动隐藏
        if (duration > 0) {
            setTimeout(() => {
                this.hideToast(toastId);
            }, duration);
        }
        
        return toastId;
    }
    
    // 隐藏Toast
    hideToast(toastId) {
        const toast = document.getElementById(toastId);
        if (!toast) return;
        
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
            this.activeToasts.delete(toastId);
        }, 150);
    }
    
    // 清理所有Toast
    clearAllToasts() {
        this.activeToasts.forEach(toastId => this.hideToast(toastId));
    }
    
    // 获取Toast样式类
    getToastClass(type) {
        const classMap = {
            'success': 'success',
            'error': 'danger', 
            'danger': 'danger',
            'warning': 'warning',
            'info': 'info',
            'primary': 'primary'
        };
        return classMap[type] || 'info';
    }
    
    // 获取Toast图标
    getToastIcon(type) {
        const iconMap = {
            'success': '<i class="fas fa-check-circle me-2"></i>',
            'error': '<i class="fas fa-exclamation-circle me-2"></i>',
            'danger': '<i class="fas fa-exclamation-triangle me-2"></i>',
            'warning': '<i class="fas fa-exclamation-triangle me-2"></i>',
            'info': '<i class="fas fa-info-circle me-2"></i>',
            'primary': '<i class="fas fa-bell me-2"></i>'
        };
        return iconMap[type] || '';
    }
    
    // 快捷方法
    showSuccess(message, options = {}) {
        return this.showToast(message, 'success', options);
    }
    
    showError(message, options = {}) {
        return this.showToast(message, 'error', options);
    }
    
    showWarning(message, options = {}) {
        return this.showToast(message, 'warning', options);
    }
    
    showInfo(message, options = {}) {
        return this.showToast(message, 'info', options);
    }
    
    // 轻量级加载指示器（非阻塞）
    showLoading(text = '加载中...', target = null) {
        const loadingId = `loading-${Date.now()}`;
        
        if (target) {
            // 在特定元素上显示加载状态
            const originalContent = target.innerHTML;
            target.dataset.originalContent = originalContent;
            target.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                ${text}
            `;
            target.disabled = true;
            return loadingId;
        } else {
            // 显示页面级别的轻量加载指示器（右下角）
            const indicator = document.createElement('div');
            indicator.id = loadingId;
            indicator.className = 'position-fixed bottom-0 end-0 m-3 bg-primary text-white p-2 rounded';
            indicator.style.cssText = `
                z-index: 1050;
                font-size: 14px;
                opacity: 0.9;
                pointer-events: none;
            `;
            indicator.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                ${text}
            `;
            
            document.body.appendChild(indicator);
            return loadingId;
        }
    }
    
    // 隐藏加载指示器
    hideLoading(loadingId, target = null) {
        if (target && target.dataset.originalContent) {
            target.innerHTML = target.dataset.originalContent;
            target.disabled = false;
            delete target.dataset.originalContent;
        } else {
            const indicator = document.getElementById(loadingId);
            if (indicator) {
                indicator.remove();
            }
        }
    }
    
    // 确认对话框（使用浏览器原生，无覆盖层）
    showConfirm(message, options = {}) {
        const result = confirm(message);
        if (options.onConfirm && result) {
            options.onConfirm();
        } else if (options.onCancel && !result) {
            options.onCancel();
        }
        return result;
    }
}

// 立即创建轻量级实例
window.liteUserFeedback = new LiteUserFeedback();

// 兼容性API - 保持旧代码工作
window.showToast = (message, type, options) => window.liteUserFeedback.showToast(message, type, options);
window.showSuccess = (message, options) => window.liteUserFeedback.showSuccess(message, options);
window.showError = (message, options) => window.liteUserFeedback.showError(message, options);
window.showWarning = (message, options) => window.liteUserFeedback.showWarning(message, options);
window.showInfo = (message, options) => window.liteUserFeedback.showInfo(message, options);
window.showLoading = (text, target) => window.liteUserFeedback.showLoading(text, target);
window.hideLoading = (loadingId, target) => window.liteUserFeedback.hideLoading(loadingId, target);
window.showConfirm = (message, options) => window.liteUserFeedback.showConfirm(message, options);

// 导出类
window.LiteUserFeedback = LiteUserFeedback;