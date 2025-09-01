/**
 * CoderWiki 改进的模态框系统
 * 解决焦点捕获、键盘导航和可访问性问题
 */

class ModalSystem {
    constructor() {
        this.activeModal = null;
        this.modalStack = [];
        this.lastFocusedElement = null;
        this.focusTrapElements = [];
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.setupEventListeners();
        this.enhanceExistingModals();
        this.createModalOverlay();
        
        this.isInitialized = true;
        console.log('Modal system initialized');
    }
    
    setupEventListeners() {
        // 监听 Bootstrap 模态框事件
        document.addEventListener('show.bs.modal', (e) => this.handleModalShow(e));
        document.addEventListener('shown.bs.modal', (e) => this.handleModalShown(e));
        document.addEventListener('hide.bs.modal', (e) => this.handleModalHide(e));
        document.addEventListener('hidden.bs.modal', (e) => this.handleModalHidden(e));
        
        // 全局键盘事件
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // 点击事件委托
        document.addEventListener('click', (e) => this.handleClick(e));
        
        // 防止页面滚动时模态框移动
        window.addEventListener('resize', () => this.adjustModalPosition());
    }
    
    handleModalShow(e) {
        const modal = e.target;
        this.prepareModal(modal);
        
        // 记住当前焦点元素
        this.lastFocusedElement = document.activeElement;
        
        // 添加到模态框栈
        this.modalStack.push(modal);
        this.activeModal = modal;
        
        console.log('Modal showing:', modal.id);
    }
    
    handleModalShown(e) {
        const modal = e.target;
        
        // 设置焦点捕获
        this.setupFocusTrap(modal);
        
        // 聚焦到第一个可交互元素
        this.focusFirstElement(modal);
        
        // 通知屏幕阅读器
        if (window.accessibilityManager) {
            window.accessibilityManager.announce('对话框已打开');
        }
        
        console.log('Modal shown:', modal.id);
    }
    
    handleModalHide(e) {
        const modal = e.target;
        console.log('Modal hiding:', modal.id);
    }
    
    handleModalHidden(e) {
        const modal = e.target;
        
        // 从模态框栈中移除
        const index = this.modalStack.indexOf(modal);
        if (index > -1) {
            this.modalStack.splice(index, 1);
        }
        
        // 更新活动模态框
        this.activeModal = this.modalStack.length > 0 ? 
            this.modalStack[this.modalStack.length - 1] : null;
        
        // 恢复焦点
        this.restoreFocus();
        
        // 清理
        this.cleanupModal(modal);
        
        // 通知屏幕阅读器
        if (window.accessibilityManager) {
            window.accessibilityManager.announce('对话框已关闭');
        }
        
        console.log('Modal hidden:', modal.id);
    }
    
    prepareModal(modal) {
        // 确保模态框有正确的属性
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        
        // 设置标题关联
        const title = modal.querySelector('.modal-title');
        if (title && !modal.hasAttribute('aria-labelledby')) {
            if (!title.id) {
                title.id = `modal-title-${Date.now()}`;
            }
            modal.setAttribute('aria-labelledby', title.id);
        }
        
        // 设置描述关联
        const description = modal.querySelector('.modal-description');
        if (description && !modal.hasAttribute('aria-describedby')) {
            if (!description.id) {
                description.id = `modal-desc-${Date.now()}`;
            }
            modal.setAttribute('aria-describedby', description.id);
        }
        
        // 确保关闭按钮有正确的标签
        const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            if (!btn.hasAttribute('aria-label') && !btn.textContent.trim()) {
                btn.setAttribute('aria-label', '关闭对话框');
            }
        });
        
        // 禁用背景滚动
        document.body.style.overflow = 'hidden';
    }
    
    setupFocusTrap(modal) {
        // 获取所有可聚焦元素
        this.focusTrapElements = this.getFocusableElements(modal);
        
        if (this.focusTrapElements.length === 0) {
            // 如果没有可聚焦元素，让模态框本身可聚焦
            modal.setAttribute('tabindex', '-1');
            this.focusTrapElements = [modal];
        }
    }
    
    getFocusableElements(container) {
        const focusableSelectors = [
            'button:not([disabled])',
            '[href]',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"]):not([disabled])',
            'details',
            'summary'
        ];
        
        const elements = container.querySelectorAll(focusableSelectors.join(','));
        return Array.from(elements).filter(el => {
            // 过滤掉不可见元素
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && 
                   style.visibility !== 'hidden' && 
                   el.offsetParent !== null;
        });
    }
    
    focusFirstElement(modal) {
        const firstElement = this.focusTrapElements[0];
        if (firstElement) {
            // 延迟聚焦，确保模态框完全显示
            setTimeout(() => {
                firstElement.focus();
            }, 100);
        }
    }
    
    handleKeyDown(e) {
        if (!this.activeModal) return;
        
        switch (e.key) {
            case 'Escape':
                this.closeActiveModal();
                break;
            case 'Tab':
                this.handleTabKey(e);
                break;
        }
    }
    
    handleTabKey(e) {
        if (!this.activeModal || this.focusTrapElements.length === 0) return;
        
        const currentIndex = this.focusTrapElements.indexOf(document.activeElement);
        let nextIndex;
        
        if (e.shiftKey) {
            // Shift+Tab - 向前导航
            nextIndex = currentIndex <= 0 ? 
                this.focusTrapElements.length - 1 : 
                currentIndex - 1;
        } else {
            // Tab - 向后导航
            nextIndex = currentIndex >= this.focusTrapElements.length - 1 ? 
                0 : 
                currentIndex + 1;
        }
        
        e.preventDefault();
        this.focusTrapElements[nextIndex].focus();
    }
    
    handleClick(e) {
        // 点击背景关闭模态框
        if (e.target.classList.contains('modal') && this.activeModal === e.target) {
            this.closeActiveModal();
        }
        
        // 处理数据属性触发的模态框
        const trigger = e.target.closest('[data-bs-toggle="modal"]');
        if (trigger) {
            const targetSelector = trigger.getAttribute('data-bs-target') || 
                                  trigger.getAttribute('href');
            if (targetSelector) {
                const targetModal = document.querySelector(targetSelector);
                if (targetModal) {
                    this.openModal(targetModal);
                }
            }
        }
    }
    
    closeActiveModal() {
        if (this.activeModal) {
            const bsModal = bootstrap.Modal.getInstance(this.activeModal);
            if (bsModal) {
                bsModal.hide();
            } else {
                this.hideModal(this.activeModal);
            }
        }
    }
    
    openModal(modal, options = {}) {
        // 清理可能存在的Bootstrap实例
        const existingInstance = bootstrap.Modal.getInstance(modal);
        if (existingInstance) {
            existingInstance.dispose();
        }
        
        // 创建新的Bootstrap实例
        const bsModal = new bootstrap.Modal(modal, {
            backdrop: options.backdrop !== false,
            keyboard: options.keyboard !== false,
            focus: options.focus !== false
        });
        
        bsModal.show();
        return bsModal;
    }
    
    hideModal(modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        
        // 移除背景
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // 触发hidden事件
        const event = new CustomEvent('hidden.bs.modal', {
            bubbles: true,
            cancelable: true
        });
        modal.dispatchEvent(event);
    }
    
    restoreFocus() {
        if (this.modalStack.length === 0 && this.lastFocusedElement) {
            // 延迟恢复焦点，确保模态框完全隐藏
            setTimeout(() => {
                if (this.lastFocusedElement && 
                    document.body.contains(this.lastFocusedElement)) {
                    this.lastFocusedElement.focus();
                }
                this.lastFocusedElement = null;
            }, 100);
        }
    }
    
    cleanupModal(modal) {
        // 恢复背景滚动
        if (this.modalStack.length === 0) {
            document.body.style.overflow = '';
        }
        
        // 清理焦点捕获
        this.focusTrapElements = [];
    }
    
    enhanceExistingModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            // 添加改进的样式类
            modal.classList.add('modal-enhanced');
            
            // 确保所有输入元素都可以正常交互
            const inputs = modal.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                this.enhanceInputElement(input);
            });
            
            // 确保所有按钮都可以正常点击
            const buttons = modal.querySelectorAll('button, .btn');
            buttons.forEach(button => {
                this.enhanceButtonElement(button);
            });
        });
    }
    
    enhanceInputElement(input) {
        // 移除可能干扰的样式
        input.style.pointerEvents = '';
        input.style.zIndex = '';
        
        // 确保输入元素可以接收焦点
        if (input.disabled) {
            input.disabled = false;
        }
        
        if (input.readOnly && input.type !== 'hidden') {
            input.readOnly = false;
        }
        
        // 添加焦点事件处理
        input.addEventListener('focus', function() {
            this.parentElement?.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement?.classList.remove('focused');
        });
    }
    
    enhanceButtonElement(button) {
        // 确保按钮可以被点击
        button.style.pointerEvents = '';
        button.style.zIndex = '';
        
        if (button.disabled && !button.hasAttribute('data-keep-disabled')) {
            button.disabled = false;
        }
        
        // 添加键盘支持
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    }
    
    createModalOverlay() {
        // 确保 DOM 已加载
        if (!document.body) {
            console.warn('document.body not available, skipping modal overlay creation');
            return;
        }
        
        // 创建一个全局覆盖层来处理焦点管理
        const overlay = document.createElement('div');
        overlay.className = 'modal-focus-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            display: none;
        `;
        document.body.appendChild(overlay);
    }
    
    adjustModalPosition() {
        if (this.activeModal) {
            const modalDialog = this.activeModal.querySelector('.modal-dialog');
            if (modalDialog) {
                // 重新计算模态框位置
                setTimeout(() => {
                    modalDialog.style.marginTop = '';
                    modalDialog.style.marginBottom = '';
                }, 100);
            }
        }
    }
    
    // 公共API方法
    show(modalSelector, options = {}) {
        const modal = typeof modalSelector === 'string' ? 
            document.querySelector(modalSelector) : modalSelector;
        
        if (modal) {
            return this.openModal(modal, options);
        }
        return null;
    }
    
    hide(modalSelector) {
        const modal = typeof modalSelector === 'string' ? 
            document.querySelector(modalSelector) : modalSelector;
        
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            } else {
                this.hideModal(modal);
            }
        }
    }
    
    toggle(modalSelector, options = {}) {
        const modal = typeof modalSelector === 'string' ? 
            document.querySelector(modalSelector) : modalSelector;
        
        if (modal) {
            if (modal.classList.contains('show')) {
                this.hide(modal);
            } else {
                this.show(modal, options);
            }
        }
    }
    
    // 获取当前活动的模态框
    getActive() {
        return this.activeModal;
    }
    
    // 关闭所有模态框
    hideAll() {
        [...this.modalStack].forEach(modal => {
            this.hide(modal);
        });
    }
}

// 创建全局实例 - 等待 DOM 加载完成
let modalSystem;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        modalSystem = new ModalSystem();
    });
} else {
    modalSystem = new ModalSystem();
}

// 导出到全局
window.ModalSystem = ModalSystem;
window.modalSystem = modalSystem;

// 向后兼容的全局函数
window.showModal = (selector, options) => modalSystem.show(selector, options);
window.hideModal = (selector) => modalSystem.hide(selector);
window.toggleModal = (selector, options) => modalSystem.toggle(selector, options);