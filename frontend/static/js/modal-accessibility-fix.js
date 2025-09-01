/**
 * 模态框可访问性修复
 * 解决 aria-hidden 与焦点管理的冲突问题
 */

class ModalAccessibilityFix {
    constructor() {
        this.init();
    }

    init() {
        this.setupModalAccessibilityFixes();
        this.fixProgressModals();
    }

    setupModalAccessibilityFixes() {
        // 监听所有Bootstrap模态框事件
        document.addEventListener('show.bs.modal', (event) => {
            this.onModalShow(event);
        });

        document.addEventListener('shown.bs.modal', (event) => {
            this.onModalShown(event);
        });

        document.addEventListener('hide.bs.modal', (event) => {
            this.onModalHide(event);
        });

        document.addEventListener('hidden.bs.modal', (event) => {
            this.onModalHidden(event);
        });
    }

    onModalShow(event) {
        const modal = event.target;
        
        // 当模态框即将显示时，移除aria-hidden
        this.removeAriaHidden(modal);
        
        console.log(`🔧 Accessibility fix: Removed aria-hidden from ${modal.id} modal`);
    }

    onModalShown(event) {
        const modal = event.target;
        
        // 确保模态框及其内容不被标记为隐藏
        this.ensureAccessibility(modal);
        
        // 管理焦点
        this.manageFocus(modal);
    }

    onModalHide(event) {
        const modal = event.target;
        
        // 模态框即将隐藏时恢复aria-hidden
        this.restoreAriaHidden(modal);
    }

    onModalHidden(event) {
        const modal = event.target;
        
        // 确保模态框完全隐藏后恢复可访问性属性
        this.cleanupAccessibility(modal);
    }

    removeAriaHidden(modal) {
        // 移除模态框本身的aria-hidden
        modal.removeAttribute('aria-hidden');
        
        // 移除所有子元素的aria-hidden（如果有的话）
        const hiddenElements = modal.querySelectorAll('[aria-hidden="true"]');
        hiddenElements.forEach(element => {
            element.removeAttribute('aria-hidden');
            element.dataset.originalAriaHidden = 'true'; // 保存原始状态
        });
    }

    restoreAriaHidden(modal) {
        // 恢复模态框的aria-hidden
        modal.setAttribute('aria-hidden', 'true');
        
        // 恢复子元素的aria-hidden（如果原本有的话）
        const elementsToRestore = modal.querySelectorAll('[data-original-aria-hidden="true"]');
        elementsToRestore.forEach(element => {
            element.setAttribute('aria-hidden', 'true');
            delete element.dataset.originalAriaHidden;
        });
    }

    ensureAccessibility(modal) {
        // 确保模态框及其内容对辅助技术可见
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('role', 'dialog');
        
        // 确保所有交互元素都可以被访问
        const interactiveElements = modal.querySelectorAll(
            'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
        );
        
        interactiveElements.forEach(element => {
            // 移除可能阻止访问的aria-hidden
            element.removeAttribute('aria-hidden');
            
            // 确保元素可以接收焦点
            if (element.hasAttribute('tabindex') && element.getAttribute('tabindex') === '-1') {
                element.setAttribute('tabindex', '0');
                element.dataset.originalTabindex = '-1';
            }
        });
    }

    manageFocus(modal) {
        // 将焦点设置到模态框内的第一个可聚焦元素
        const focusableElement = this.getFirstFocusableElement(modal);
        if (focusableElement) {
            // 使用requestAnimationFrame确保DOM更新完成后再设置焦点
            requestAnimationFrame(() => {
                focusableElement.focus();
            });
        }

        // 管理焦点陷阱（确保焦点不会跳出模态框）
        this.setupFocusTrap(modal);
    }

    getFirstFocusableElement(modal) {
        const focusableElements = modal.querySelectorAll(
            'button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
            'textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
        );
        
        return focusableElements[0] || modal.querySelector('.btn-close') || modal.querySelector('[data-bs-dismiss="modal"]');
    }

    setupFocusTrap(modal) {
        const focusableElements = modal.querySelectorAll(
            'button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
            'textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // 移除之前的事件监听器
        modal.removeEventListener('keydown', modal._focusTrapHandler);
        
        // 创建新的焦点陷阱处理器
        modal._focusTrapHandler = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    // Tab
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        };
        
        modal.addEventListener('keydown', modal._focusTrapHandler);
    }

    cleanupAccessibility(modal) {
        // 清理焦点陷阱
        if (modal._focusTrapHandler) {
            modal.removeEventListener('keydown', modal._focusTrapHandler);
            delete modal._focusTrapHandler;
        }
        
        // 恢复原始的tabindex值
        const elementsWithOriginalTabindex = modal.querySelectorAll('[data-original-tabindex]');
        elementsWithOriginalTabindex.forEach(element => {
            element.setAttribute('tabindex', element.dataset.originalTabindex);
            delete element.dataset.originalTabindex;
        });
    }

    fixProgressModals() {
        // 特别修复进度模态框（如deleteProgressModal）
        const progressModals = document.querySelectorAll('[id*="Progress"][id*="Modal"], [id*="progress"][id*="modal"]');
        
        progressModals.forEach(modal => {
            // 进度模态框通常不应该有aria-hidden，因为它们需要向用户传达状态
            modal.removeAttribute('aria-hidden');
            modal.setAttribute('aria-live', 'polite'); // 让屏幕阅读器通报进度变化
            modal.setAttribute('aria-relevant', 'additions text'); // 指定要通报的内容类型
            
            // 如果有进度条，确保它有适当的ARIA属性
            const progressBar = modal.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.setAttribute('role', 'progressbar');
                progressBar.setAttribute('aria-valuemin', '0');
                progressBar.setAttribute('aria-valuemax', '100');
                
                // 观察进度变化
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                            const width = progressBar.style.width;
                            if (width) {
                                const value = parseFloat(width.replace('%', ''));
                                progressBar.setAttribute('aria-valuenow', value);
                                progressBar.setAttribute('aria-valuetext', `${value}% 完成`);
                            }
                        }
                    });
                });
                
                observer.observe(progressBar, { attributes: true });
                
                // 清理观察器
                modal.addEventListener('hidden.bs.modal', () => {
                    observer.disconnect();
                });
            }
            
            console.log(`🔧 Progress modal accessibility enhanced: ${modal.id}`);
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.modalAccessibilityFix = new ModalAccessibilityFix();
    console.log('✅ Modal accessibility fixes initialized');
});

// 导出给其他模块使用
window.ModalAccessibilityFix = ModalAccessibilityFix;