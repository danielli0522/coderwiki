/**
 * CoderWiki 用户反馈和加载状态系统
 * 提供统一的用户界面反馈机制
 */

class UserFeedbackSystem {
    constructor() {
        this.toasts = [];
        this.loadingStates = new Map();
        this.progressBars = new Map();
        this.notifications = [];
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.createToastContainer();
        this.createLoadingOverlay();
        this.createProgressContainer();
        this.setupGlobalErrorHandling();
        this.setupNetworkStatusMonitoring();
        
        this.isInitialized = true;
        console.log('User feedback system initialized');
    }
    
    // 创建Toast容器
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'true');
        
        document.body.appendChild(container);
    }
    
    // 创建加载覆盖层
    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                </div>
                <div class="loading-text">正在加载...</div>
                <div class="loading-progress">
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `;
        
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.9);
            display: none;
            z-index: 10000;
            backdrop-filter: blur(2px);
        `;
        
        document.body.appendChild(overlay);
    }
    
    // 创建进度条容器
    createProgressContainer() {
        const container = document.createElement('div');
        container.id = 'progress-container';
        container.className = 'progress-container position-fixed top-0 start-0 w-100';
        container.style.zIndex = '9998';
        
        document.body.appendChild(container);
    }
    
    // 显示Toast消息
    showToast(message, type = 'info', options = {}) {
        const defaults = {
            duration: 5000,
            dismissible: true,
            icon: true,
            position: 'top-end'
        };
        
        const config = { ...defaults, ...options };
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const toast = this.createToast(toastId, message, type, config);
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // 显示Toast
        const bsToast = new bootstrap.Toast(toast, {
            delay: config.duration,
            autohide: true
        });
        
        bsToast.show();
        
        // 记录Toast
        this.toasts.push({
            id: toastId,
            element: toast,
            bsToast: bsToast,
            type: type,
            message: message
        });
        
        // 清理Toast
        toast.addEventListener('hidden.bs.toast', () => {
            this.removeToast(toastId);
        });
        
        // 通知屏幕阅读器
        if (window.accessibilityManager) {
            const priority = type === 'error' ? 'assertive' : 'polite';
            window.accessibilityManager.announce(message, priority);
        }
        
        return toastId;
    }
    
    // 创建Toast元素
    createToast(id, message, type, config) {
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = `toast align-items-center text-bg-${this.getBootstrapType(type)} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const icon = config.icon ? this.getTypeIcon(type) : '';
        const closeBtn = config.dismissible ? `
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="关闭"></button>
        ` : '';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${icon} ${message}
                </div>
                ${closeBtn}
            </div>
        `;
        
        return toast;
    }
    
    // 获取Bootstrap类型
    getBootstrapType(type) {
        const typeMap = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'info',
            primary: 'primary',
            secondary: 'secondary'
        };
        return typeMap[type] || 'info';
    }
    
    // 获取类型图标
    getTypeIcon(type) {
        const iconMap = {
            success: '<i class="fas fa-check-circle me-2"></i>',
            error: '<i class="fas fa-exclamation-triangle me-2"></i>',
            warning: '<i class="fas fa-exclamation-circle me-2"></i>',
            info: '<i class="fas fa-info-circle me-2"></i>',
            primary: '<i class="fas fa-bell me-2"></i>',
            secondary: '<i class="fas fa-comment me-2"></i>'
        };
        return iconMap[type] || '';
    }
    
    // 移除Toast
    removeToast(id) {
        const index = this.toasts.findIndex(toast => toast.id === id);
        if (index > -1) {
            const toast = this.toasts[index];
            toast.element.remove();
            this.toasts.splice(index, 1);
        }
    }
    
    // 清除所有Toast
    clearAllToasts() {
        this.toasts.forEach(toast => {
            toast.bsToast.hide();
        });
        this.toasts = [];
    }
    
    // 显示成功消息
    showSuccess(message, options = {}) {
        return this.showToast(message, 'success', options);
    }
    
    // 显示错误消息
    showError(message, options = {}) {
        return this.showToast(message, 'error', { 
            duration: 8000, 
            ...options 
        });
    }
    
    // 显示警告消息
    showWarning(message, options = {}) {
        return this.showToast(message, 'warning', options);
    }
    
    // 显示信息消息
    showInfo(message, options = {}) {
        return this.showToast(message, 'info', options);
    }
    
    // 显示全屏加载状态
    showLoading(text = '正在加载...', showProgress = false) {
        const overlay = document.getElementById('loading-overlay');
        const textElement = overlay.querySelector('.loading-text');
        const progressElement = overlay.querySelector('.loading-progress');
        
        textElement.textContent = text;
        progressElement.style.display = showProgress ? 'block' : 'none';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        
        // 禁用页面滚动
        document.body.style.overflow = 'hidden';
        
        return 'global-loading';
    }
    
    // 隐藏全屏加载状态
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'none';
        
        // 恢复页面滚动
        document.body.style.overflow = '';
    }
    
    // 更新全屏加载进度
    updateLoadingProgress(percent, text = null) {
        const overlay = document.getElementById('loading-overlay');
        const progressBar = overlay.querySelector('.progress-bar');
        const textElement = overlay.querySelector('.loading-text');
        
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
        
        if (text) {
            textElement.textContent = text;
        }
    }
    
    // 显示元素级加载状态
    showElementLoading(element, text = '加载中...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return null;
        
        const loadingId = `loading-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // 保存原始内容
        element.dataset.originalContent = element.innerHTML;
        element.dataset.loadingId = loadingId;
        
        // 添加加载状态
        element.classList.add('loading-state');
        element.innerHTML = `
            <div class="element-loading">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <span class="ms-2">${text}</span>
            </div>
        `;
        
        // 禁用交互
        if (element.tagName === 'BUTTON' || element.tagName === 'INPUT') {
            element.disabled = true;
        }
        
        this.loadingStates.set(loadingId, {
            element: element,
            originalContent: element.dataset.originalContent
        });
        
        return loadingId;
    }
    
    // 隐藏元素级加载状态
    hideElementLoading(elementOrId) {
        let element, loadingId;
        
        if (typeof elementOrId === 'string') {
            if (elementOrId.startsWith('loading-')) {
                // 传入的是loading ID
                loadingId = elementOrId;
                const loadingState = this.loadingStates.get(loadingId);
                element = loadingState ? loadingState.element : null;
            } else {
                // 传入的是选择器
                element = document.querySelector(elementOrId);
                loadingId = element ? element.dataset.loadingId : null;
            }
        } else {
            // 传入的是DOM元素
            element = elementOrId;
            loadingId = element ? element.dataset.loadingId : null;
        }
        
        if (!element || !loadingId) return;
        
        const loadingState = this.loadingStates.get(loadingId);
        if (loadingState) {
            // 恢复原始内容
            element.innerHTML = loadingState.originalContent;
            element.classList.remove('loading-state');
            
            // 恢复交互
            if (element.tagName === 'BUTTON' || element.tagName === 'INPUT') {
                element.disabled = false;
            }
            
            // 清理
            delete element.dataset.originalContent;
            delete element.dataset.loadingId;
            this.loadingStates.delete(loadingId);
        }
    }
    
    // 创建进度条
    createProgressBar(id, options = {}) {
        const defaults = {
            type: 'primary',
            height: '4px',
            animated: true,
            striped: false,
            showPercentage: false
        };
        
        const config = { ...defaults, ...options };
        
        const progressBar = document.createElement('div');
        progressBar.id = `progress-${id}`;
        progressBar.className = 'progress';
        progressBar.style.height = config.height;
        
        const bar = document.createElement('div');
        bar.className = `progress-bar bg-${config.type}`;
        bar.setAttribute('role', 'progressbar');
        bar.setAttribute('aria-valuenow', '0');
        bar.setAttribute('aria-valuemin', '0');
        bar.setAttribute('aria-valuemax', '100');
        bar.style.width = '0%';
        
        if (config.animated) {
            bar.classList.add('progress-bar-animated');
        }
        
        if (config.striped) {
            bar.classList.add('progress-bar-striped');
        }
        
        progressBar.appendChild(bar);
        
        this.progressBars.set(id, {
            container: progressBar,
            bar: bar,
            config: config
        });
        
        return progressBar;
    }
    
    // 更新进度条
    updateProgress(id, percent, text = null) {
        const progress = this.progressBars.get(id);
        if (!progress) return;
        
        progress.bar.style.width = `${percent}%`;
        progress.bar.setAttribute('aria-valuenow', percent);
        
        if (progress.config.showPercentage) {
            progress.bar.textContent = `${percent}%`;
        }
        
        if (text) {
            progress.bar.textContent = text;
        }
    }
    
    // 完成进度条
    completeProgress(id, message = '完成') {
        this.updateProgress(id, 100, message);
        
        setTimeout(() => {
            const progress = this.progressBars.get(id);
            if (progress) {
                progress.container.remove();
                this.progressBars.delete(id);
            }
        }, 2000);
    }
    
    // 显示确认对话框
    showConfirm(message, options = {}) {
        return new Promise((resolve) => {
            const defaults = {
                title: '确认操作',
                confirmText: '确认',
                cancelText: '取消',
                type: 'warning'
            };
            
            const config = { ...defaults, ...options };
            const modalId = `confirm-modal-${Date.now()}`;
            
            const modal = this.createConfirmModal(modalId, config.title, message, config);
            document.body.appendChild(modal);
            
            const bsModal = new bootstrap.Modal(modal);
            
            // 绑定事件
            modal.querySelector('.btn-confirm').addEventListener('click', () => {
                bsModal.hide();
                resolve(true);
            });
            
            modal.querySelector('.btn-cancel').addEventListener('click', () => {
                bsModal.hide();
                resolve(false);
            });
            
            // 清理模态框
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
            
            bsModal.show();
        });
    }
    
    // 创建确认模态框
    createConfirmModal(id, title, message, config) {
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-labelledby', `${id}-title`);
        modal.setAttribute('aria-hidden', 'true');
        
        const icon = this.getTypeIcon(config.type);
        
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${id}-title">
                            ${icon} ${title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary btn-cancel">
                            ${config.cancelText}
                        </button>
                        <button type="button" class="btn btn-${this.getBootstrapType(config.type)} btn-confirm">
                            ${config.confirmText}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    // 设置全局错误处理
    setupGlobalErrorHandling() {
        // JavaScript错误处理
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.showError(`发生错误: ${e.message}`, {
                duration: 10000
            });
        });
        
        // Promise拒绝处理
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.showError('请求失败，请重试', {
                duration: 8000
            });
        });
        
        // AJAX错误处理
        document.addEventListener('ajaxError', (e) => {
            this.showError('网络请求失败，请检查网络连接');
        });
    }
    
    // 设置网络状态监控
    setupNetworkStatusMonitoring() {
        if ('navigator' in window && 'onLine' in navigator) {
            window.addEventListener('online', () => {
                this.showSuccess('网络连接已恢复');
            });
            
            window.addEventListener('offline', () => {
                this.showWarning('网络连接已断开', {
                    duration: 0 // 不自动隐藏
                });
            });
        }
    }
    
    // 显示网络状态
    showNetworkStatus() {
        if (navigator.onLine) {
            this.showInfo('网络连接正常');
        } else {
            this.showWarning('当前无网络连接');
        }
    }
    
    // 批量操作反馈
    showBatchProgress(operations, onProgress = null, onComplete = null) {
        const progressId = `batch-${Date.now()}`;
        const progressBar = this.createProgressBar(progressId, {
            showPercentage: true,
            animated: true
        });
        
        // 添加到页面
        const container = document.getElementById('progress-container');
        container.appendChild(progressBar);
        
        let completed = 0;
        const total = operations.length;
        
        const updateProgress = () => {
            const percent = Math.round((completed / total) * 100);
            this.updateProgress(progressId, percent);
            
            if (onProgress) {
                onProgress(completed, total, percent);
            }
            
            if (completed === total) {
                this.completeProgress(progressId, '全部完成');
                if (onComplete) {
                    onComplete();
                }
            }
        };
        
        // 执行操作
        operations.forEach(async (operation, index) => {
            try {
                await operation();
                completed++;
                updateProgress();
            } catch (error) {
                console.error(`Operation ${index} failed:`, error);
                this.showError(`第${index + 1}个操作失败`);
                completed++;
                updateProgress();
            }
        });
        
        return progressId;
    }
}

// 创建全局实例
const userFeedback = new UserFeedbackSystem();

// 向后兼容的全局函数
window.showToast = (message, type, options) => userFeedback.showToast(message, type, options);
window.showSuccess = (message, options) => userFeedback.showSuccess(message, options);
window.showError = (message, options) => userFeedback.showError(message, options);
window.showWarning = (message, options) => userFeedback.showWarning(message, options);
window.showInfo = (message, options) => userFeedback.showInfo(message, options);
window.showLoading = (text, showProgress) => userFeedback.showLoading(text, showProgress);
window.hideLoading = () => userFeedback.hideLoading();
window.showConfirm = (message, options) => userFeedback.showConfirm(message, options);

// 增强现有的CoderWiki工具函数
if (window.CoderWiki && window.CoderWiki.utils) {
    const originalShowMessage = window.CoderWiki.utils.showMessage;
    
    window.CoderWiki.utils.showMessage = function(message, type = 'info') {
        // 使用新的Toast系统
        return userFeedback.showToast(message, type);
    };
    
    window.CoderWiki.utils.showLoading = function(element, text = '加载中...') {
        return userFeedback.showElementLoading(element, text);
    };
    
    window.CoderWiki.utils.hideLoading = function(elementOrId) {
        return userFeedback.hideElementLoading(elementOrId);
    };
}

// 导出到全局
window.UserFeedbackSystem = UserFeedbackSystem;
window.userFeedback = userFeedback;