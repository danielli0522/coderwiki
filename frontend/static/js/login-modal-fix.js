/**
 * 登录页面模态框修复脚本
 * 专门解决忘记密码模态框无法关闭的问题
 * (功能已禁用)
 */

/*
class LoginModalFix {
    constructor() {
        this.init();
    }

    init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupFix());
        } else {
            this.setupFix();
        }
    }

    setupFix() {
        console.log('🔧 登录页面模态框修复已启动');

        // 立即确保模态框不显示
        this.ensureModalHidden();

        // 修复忘记密码模态框
        this.fixForgotPasswordModal();

        // 添加强制关闭功能
        this.addEmergencyClose();

        // 监听页面变化
        this.observePageChanges();

        // 定期检查确保模态框不自动显示
        this.startPeriodicCheck();
    }

    ensureModalHidden() {
        console.log('🔧 确保忘记密码模态框在页面加载时不显示');

        const modalElement = document.getElementById('forgotPasswordModal');
        if (modalElement) {
            // 强制隐藏模态框
            this.resetModalState(modalElement);

            // 确保没有Bootstrap实例
            try {
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (modalInstance) {
                    modalInstance.hide();
                }
            } catch (error) {
                console.log('Bootstrap实例不存在，继续强制隐藏');
            }
        }

        // 清理任何可能的背景遮罩
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());

        // 恢复body样式
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }

    fixForgotPasswordModal() {
        const modalElement = document.getElementById('forgotPasswordModal');
        if (!modalElement) {
            console.log('未找到忘记密码模态框');
            return;
        }

        // 确保模态框初始状态正确
        this.resetModalState(modalElement);

        // 修复关闭按钮
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
        closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.closeModal(modalElement);
            });
        });

        // 修复取消按钮
        const cancelButtons = modalElement.querySelectorAll('.btn-secondary');
        cancelButtons.forEach(button => {
            if (button.textContent.includes('取消') || button.textContent.includes('Cancel')) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.closeModal(modalElement);
                });
            }
        });

        // 监听模态框事件
        modalElement.addEventListener('shown.bs.modal', () => {
            console.log('忘记密码模态框已显示');
            this.ensureModalAccessible(modalElement);
        });

        modalElement.addEventListener('hidden.bs.modal', () => {
            console.log('忘记密码模态框已隐藏');
            this.resetModalState(modalElement);
        });

        // 监听表单提交
        const form = modalElement.querySelector('#forgotPasswordForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(form, modalElement);
            });
        }
    }

    resetModalState(modalElement) {
        // 重置模态框状态
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        modalElement.setAttribute('aria-hidden', 'true');
        modalElement.removeAttribute('aria-modal');
        modalElement.removeAttribute('role');

        // 移除背景遮罩
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());

        // 恢复body样式
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        // 重置表单
        const form = modalElement.querySelector('#forgotPasswordForm');
        if (form) {
            form.reset();
        }
    }

    ensureModalAccessible(modalElement) {
        // 确保模态框可以正常交互
        modalElement.style.zIndex = '9999';
        modalElement.style.pointerEvents = 'auto';

        // 确保输入框可以正常使用
        const inputs = modalElement.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.style.pointerEvents = 'auto';
            input.style.zIndex = '10000';
            input.disabled = false;
            input.readOnly = false;
        });

        // 确保按钮可以正常点击
        const buttons = modalElement.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.pointerEvents = 'auto';
            button.style.zIndex = '10000';
            button.disabled = false;
        });

        // 聚焦到第一个输入框
        const firstInput = modalElement.querySelector('input[type="email"]');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    closeModal(modalElement) {
        console.log('正在关闭忘记密码模态框...');

        try {
            // 方法1: 使用Bootstrap API
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
                return;
            }
        } catch (error) {
            console.log('Bootstrap API关闭失败，使用备用方法');
        }

        // 方法2: 直接操作DOM
        this.resetModalState(modalElement);

        console.log('忘记密码模态框已关闭');
    }

    handleFormSubmit(form, modalElement) {
        const email = form.email.value;

        if (!email) {
            this.showToast('请输入邮箱地址', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        // 显示加载状态
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';

        // 模拟发送过程
        setTimeout(() => {
            this.showToast('密码重置链接已发送到您的邮箱', 'success');

            // 关闭模态框
            this.closeModal(modalElement);

            // 恢复按钮状态
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 1000);
    }

    addEmergencyClose() {
        // 添加强制关闭快捷键
        document.addEventListener('keydown', (e) => {
            // ESC键关闭模态框
            if (e.key === 'Escape') {
                const visibleModals = document.querySelectorAll('.modal.show');
                if (visibleModals.length > 0) {
                    e.preventDefault();
                    e.stopPropagation();
                    visibleModals.forEach(modal => this.closeModal(modal));
                }
            }

            // Ctrl/Cmd + W 强制关闭所有模态框
            if ((e.ctrlKey || e.metaKey) && e.key === 'w') {
                e.preventDefault();
                this.forceCloseAllModals();
            }
        });

        // 添加全局关闭方法
        window.forceCloseLoginModals = () => this.forceCloseAllModals();
    }

    forceCloseAllModals() {
        console.log('🔧 强制关闭所有模态框...');

        const allModals = document.querySelectorAll('.modal');
        allModals.forEach(modal => {
            this.resetModalState(modal);
        });

        console.log('所有模态框已强制关闭');
    }

    observePageChanges() {
        // 监听DOM变化，处理动态添加的元素
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // 检查是否有新的模态框
                        if (node.classList && node.classList.contains('modal')) {
                            this.fixForgotPasswordModal();
                        }
                        // 检查子元素
                        const modals = node.querySelectorAll && node.querySelectorAll('.modal');
                        if (modals && modals.length > 0) {
                            this.fixForgotPasswordModal();
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    startPeriodicCheck() {
        // 定期检查确保模态框不会自动显示
        setInterval(() => {
            const modalElement = document.getElementById('forgotPasswordModal');
            if (modalElement && modalElement.classList.contains('show')) {
                // 检查是否应该显示（通过用户点击触发）
                const shouldShow = this.checkIfShouldShow();
                if (!shouldShow) {
                    console.log('检测到模态框意外显示，正在关闭...');
                    this.closeModal(modalElement);
                }
            }
        }, 2000); // 每2秒检查一次
    }

    checkIfShouldShow() {
        // 检查是否有用户交互应该触发模态框显示
        // 这里可以添加更复杂的逻辑来判断是否应该显示模态框
        return false; // 默认不显示
    }

    showToast(message, type = 'info') {
        // 创建简单的toast通知
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            max-width: 400px;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        // 3秒后自动移除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }
}

// 初始化修复 (功能已禁用)
// const loginModalFix = new LoginModalFix();

// 添加全局方法 (功能已禁用)
// window.LoginModalFix = LoginModalFix;
// window.forceCloseLoginModals = () => loginModalFix.forceCloseAllModals();

console.log('登录页面模态框修复已禁用');
*/
