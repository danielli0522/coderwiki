/**
 * Repository Modal Fix
 * 修复仓库管理页面的模态框问题
 */

class RepositoryModalFix {
    constructor() {
        this.init();
    }

    init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupModalFix());
        } else {
            this.setupModalFix();
        }
    }

    setupModalFix() {
        console.log('RepositoryModalFix: 初始化模态框修复...');

        // 确保Bootstrap已加载
        this.ensureBootstrapLoaded();

        // 修复模态框事件监听
        this.fixModalEventListeners();

        // 修复模态框DOM结构
        this.fixModalDOM();

        // 设置全局错误处理
        this.setupErrorHandling();

        console.log('RepositoryModalFix: 模态框修复完成');
    }

    ensureBootstrapLoaded() {
        // 检查Bootstrap是否已加载
        if (typeof bootstrap === 'undefined') {
            console.error('RepositoryModalFix: Bootstrap未加载，尝试重新加载...');
            this.loadBootstrap();
        } else {
            console.log('RepositoryModalFix: Bootstrap已加载');
        }
    }

    loadBootstrap() {
        // 动态加载Bootstrap
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js';
        script.onload = () => {
            console.log('RepositoryModalFix: Bootstrap加载完成');
            this.setupModalFix();
        };
        script.onerror = () => {
            console.error('RepositoryModalFix: Bootstrap加载失败');
        };
        document.head.appendChild(script);
    }

    fixModalEventListeners() {
        // 修复添加仓库模态框
        const addRepoBtn = document.querySelector('[data-bs-target="#addRepositoryModal"]');
        if (addRepoBtn) {
            // 移除可能存在的旧事件监听器
            addRepoBtn.replaceWith(addRepoBtn.cloneNode(true));

            // 重新获取按钮并添加事件监听器
            const newAddRepoBtn = document.querySelector('[data-bs-target="#addRepositoryModal"]');
            newAddRepoBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openAddRepositoryModal();
            });
        }

        // 修复模态框关闭按钮
        const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal(btn.closest('.modal'));
            });
        });

        // 修复模态框背景点击关闭
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }

    openAddRepositoryModal() {
        console.log('RepositoryModalFix: 打开添加仓库模态框...');

        const modal = document.getElementById('addRepositoryModal');
        if (!modal) {
            console.error('RepositoryModalFix: 找不到添加仓库模态框');
            return;
        }

        // 确保模态框DOM结构正确
        this.fixModalStructure(modal);

        // 使用Bootstrap API打开模态框
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = new bootstrap.Modal(modal, {
                backdrop: true,
                keyboard: true,
                focus: true
            });
            bsModal.show();
        } else {
            // 备用方法：手动显示模态框
            this.showModalManually(modal);
        }

        // 修复模态框内的交互元素
        setTimeout(() => {
            this.fixModalInteractions(modal);
        }, 100);
    }

    closeModal(modal) {
        if (!modal) return;

        console.log('RepositoryModalFix: 关闭模态框...');

        // 使用Bootstrap API关闭模态框
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }

        // 手动关闭模态框
        this.hideModalManually(modal);
    }

    fixModalStructure(modal) {
        // 确保模态框有正确的类名
        if (!modal.classList.contains('modal')) {
            modal.classList.add('modal');
        }
        if (!modal.classList.contains('fade')) {
            modal.classList.add('fade');
        }

        // 确保模态框有正确的属性
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-labelledby', 'modalLabel');
        modal.setAttribute('aria-hidden', 'true');

        // 确保模态框内容结构正确
        const modalDialog = modal.querySelector('.modal-dialog');
        if (!modalDialog) {
            console.error('RepositoryModalFix: 模态框缺少modal-dialog元素');
            return;
        }

        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) {
            console.error('RepositoryModalFix: 模态框缺少modal-content元素');
            return;
        }
    }

    showModalManually(modal) {
        // 手动显示模态框
        modal.style.display = 'block';
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');

        // 添加模态框背景
        this.addModalBackdrop();

        // 禁用body滚动
        document.body.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
    }

    hideModalManually(modal) {
        // 手动隐藏模态框
        modal.style.display = 'none';
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');

        // 移除模态框背景
        this.removeModalBackdrop();

        // 恢复body滚动
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
    }

    addModalBackdrop() {
        // 移除现有的背景
        this.removeModalBackdrop();

        // 创建新的背景
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.style.zIndex = '1040';
        document.body.appendChild(backdrop);
    }

    removeModalBackdrop() {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
    }

    fixModalInteractions(modal) {
        // 修复输入框
        const inputs = modal.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.style.pointerEvents = 'auto';
            input.style.zIndex = '10000';
            input.disabled = false;
            input.readOnly = false;
        });

        // 修复按钮
        const buttons = modal.querySelectorAll('button, .btn');
        buttons.forEach(button => {
            button.style.pointerEvents = 'auto';
            button.style.zIndex = '10000';
            button.style.cursor = 'pointer';
            button.disabled = false;
        });

        // 修复表单
        const form = modal.querySelector('form');
        if (form) {
            form.style.pointerEvents = 'auto';
            form.style.zIndex = '10000';
        }
    }

    fixModalDOM() {
        // 修复所有模态框的DOM结构
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            this.fixModalStructure(modal);
        });
    }

    setupErrorHandling() {
        // 全局错误处理
        window.addEventListener('error', (e) => {
            if (e.message.includes('backdrop') || e.message.includes('modal')) {
                console.warn('RepositoryModalFix: 捕获到模态框相关错误，尝试修复...');
                this.fixModalDOM();
            }
        });

        // 未处理的Promise拒绝
        window.addEventListener('unhandledrejection', (e) => {
            if (e.reason && e.reason.message &&
                (e.reason.message.includes('backdrop') || e.reason.message.includes('modal'))) {
                console.warn('RepositoryModalFix: 捕获到模态框相关Promise错误，尝试修复...');
                this.fixModalDOM();
            }
        });
    }
}

// 初始化修复
new RepositoryModalFix();

// 导出到全局
window.RepositoryModalFix = RepositoryModalFix;
