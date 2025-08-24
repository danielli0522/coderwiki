/**
 * 模态框修复脚本
 * 解决所有模态框的交互和显示问题
 */

class ModalFixes {
    constructor() {
        this.init();
    }

    init() {
        console.log('初始化模态框修复...');
        this.fixModalInteractions();
        this.fixModalBackdrop();
        this.fixModalFocus();
        this.bindGlobalEvents();
    }

    fixModalInteractions() {
        // 修复模态框交互问题
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-toggle="modal"]')) {
                const targetId = e.target.getAttribute('data-bs-target');
                if (targetId) {
                    this.ensureModalExists(targetId);
                }
            }
        });

        // 修复模态框关闭问题
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-dismiss="modal"]')) {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });
    }

    fixModalBackdrop() {
        // 修复模态框背景问题
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });
    }

    fixModalFocus() {
        // 修复模态框焦点问题
        document.addEventListener('shown.bs.modal', (e) => {
            const modal = e.target;
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                setTimeout(() => {
                    firstInput.focus();
                }, 100);
            }
        });
    }

    bindGlobalEvents() {
        // 绑定全局事件
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });
    }

    ensureModalExists(modalId) {
        const modal = document.querySelector(modalId);
        if (!modal) {
            console.warn(`模态框 ${modalId} 不存在`);
            return false;
        }
        return true;
    }

    closeModal(modal) {
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            } else {
                modal.classList.remove('show');
                modal.style.display = 'none';
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
            }
        }
    }

    // 全局方法，供其他脚本调用
    static fixModalInteractions() {
        const modalFixes = new ModalFixes();
        return modalFixes;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.modalFixes = new ModalFixes();
});

// 导出全局方法
window.fixModalInteractions = ModalFixes.fixModalInteractions;
