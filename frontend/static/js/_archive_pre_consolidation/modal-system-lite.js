/**
 * 轻量级模态框系统
 * 零初始化时间，首屏无感知，渐进式增强
 */

// 基础模态框类 - 立即可用，零初始化时间
class BasicModal {
    constructor() {
        this.activeModal = null;
        this.isEnhanced = false;
    }
    
    show(selector, options = {}) {
        const modal = document.querySelector(selector);
        if (!modal) {
            console.warn(`Modal ${selector} not found`);
            return;
        }
        
        // 基础显示逻辑 - 无需等待任何初始化
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        
        this.activeModal = modal;
        
        // 基础ESC键支持
        this.setupBasicKeyboard();
        
        return modal;
    }
    
    hide(selector) {
        const modal = selector ? document.querySelector(selector) : this.activeModal;
        if (!modal) return;
        
        modal.classList.remove('show');
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
        
        this.activeModal = null;
        this.cleanupBasicKeyboard();
    }
    
    toggle(selector, options = {}) {
        const modal = document.querySelector(selector);
        if (modal && modal.style.display === 'block') {
            this.hide(selector);
        } else {
            this.show(selector, options);
        }
    }
    
    setupBasicKeyboard() {
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.hide();
            }
        };
        document.addEventListener('keydown', this.escapeHandler);
    }
    
    cleanupBasicKeyboard() {
        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
            this.escapeHandler = null;
        }
    }
}

// 增强模态框类 - 后台静默升级
class EnhancedModal extends BasicModal {
    constructor() {
        super();
        this.isEnhanced = true;
        this.focusableElements = [];
        this.lastFocusedElement = null;
        
        // 静默初始化增强功能，无用户可见效果
        this.initEnhancementsAsync();
    }
    
    async initEnhancementsAsync() {
        // 使用requestIdleCallback确保不阻塞主线程
        if (window.requestIdleCallback) {
            window.requestIdleCallback(() => this.setupEnhancements());
        } else {
            setTimeout(() => this.setupEnhancements(), 0);
        }
    }
    
    setupEnhancements() {
        this.createBackdrop();
        this.setupAdvancedKeyboard();
        this.setupWindowResize();
        // console.log('Modal enhancements loaded silently'); // 可选的调试信息
    }
    
    show(selector, options = {}) {
        const modal = super.show(selector, options);
        if (!modal) return;
        
        // 增强功能
        this.setupFocusTrap(modal);
        this.adjustPosition(modal);
        
        return modal;
    }
    
    hide(selector) {
        if (this.lastFocusedElement) {
            this.lastFocusedElement.focus();
            this.lastFocusedElement = null;
        }
        
        super.hide(selector);
        this.cleanupFocusTrap();
    }
    
    setupFocusTrap(modal) {
        // 保存当前焦点
        this.lastFocusedElement = document.activeElement;
        
        // 获取可聚焦元素
        this.focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (this.focusableElements.length > 0) {
            this.focusableElements[0].focus();
        }
    }
    
    cleanupFocusTrap() {
        this.focusableElements = [];
    }
    
    createBackdrop() {
        if (!document.getElementById('modal-backdrop-lite')) {
            const backdrop = document.createElement('div');
            backdrop.id = 'modal-backdrop-lite';
            backdrop.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                z-index: 1040;
                display: none;
            `;
            
            backdrop.addEventListener('click', () => {
                if (this.activeModal) {
                    this.hide();
                }
            });
            
            document.body.appendChild(backdrop);
        }
    }
    
    adjustPosition(modal) {
        const dialog = modal.querySelector('.modal-dialog');
        if (!dialog) return;
        
        const rect = dialog.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        
        if (rect.height > viewportHeight * 0.9) {
            dialog.style.maxHeight = '90vh';
            dialog.style.overflowY = 'auto';
        }
    }
    
    setupAdvancedKeyboard() {
        // 高级键盘处理将在这里实现
    }
    
    setupWindowResize() {
        window.addEventListener('resize', () => {
            if (this.activeModal) {
                this.adjustPosition(this.activeModal);
            }
        });
    }
}

// 立即创建基础版本 - 零延迟可用
window.modalSystemLite = new BasicModal();

// 全局API - 保持向后兼容
window.showModal = (selector, options) => window.modalSystemLite.show(selector, options);
window.hideModal = (selector) => window.modalSystemLite.hide(selector);
window.toggleModal = (selector, options) => window.modalSystemLite.toggle(selector, options);

// 静默升级到增强版本 - 用户完全无感知
setTimeout(() => {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.modalSystemLite = new EnhancedModal();
        });
    } else {
        window.modalSystemLite = new EnhancedModal();
    }
}, 0);

// 导出类定义
window.BasicModal = BasicModal;
window.EnhancedModal = EnhancedModal;