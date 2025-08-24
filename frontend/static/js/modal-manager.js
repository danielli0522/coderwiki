/**
 * 统一的模态框管理器
 * 解决模态框初始化和事件绑定问题
 */
class ModalManager {
    constructor() {
        this.modals = new Map();
        this.initialized = false;
        this.pendingActions = [];
    }

    /**
     * 初始化模态框管理器
     */
    init() {
        if (this.initialized) return;
        
        // 确保DOM完全加载
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this._initialize());
        } else {
            this._initialize();
        }
    }

    _initialize() {
        console.log('ModalManager: Initializing...');
        this.initialized = true;
        
        // 处理所有待处理的操作
        this.pendingActions.forEach(action => action());
        this.pendingActions = [];
        
        // 绑定全局事件监听
        this.bindGlobalEvents();
        
        console.log('ModalManager: Initialized successfully');
    }

    /**
     * 绑定全局事件监听
     */
    bindGlobalEvents() {
        // 监听所有带有data-modal-action属性的元素点击事件
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-modal-action]');
            if (!target) return;
            
            const action = target.getAttribute('data-modal-action');
            const modalId = target.getAttribute('data-modal-id');
            
            if (action === 'open' && modalId) {
                e.preventDefault();
                this.showModal(modalId);
            }
        });
    }

    /**
     * 注册模态框
     */
    registerModal(modalId, options = {}) {
        if (!this.initialized) {
            this.pendingActions.push(() => this.registerModal(modalId, options));
            return;
        }

        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
            console.warn(`ModalManager: Modal element ${modalId} not found`);
            return;
        }

        // 创建Bootstrap模态框实例
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: options.backdrop !== false,
            keyboard: options.keyboard !== false,
            focus: options.focus !== false
        });

        this.modals.set(modalId, {
            element: modalElement,
            instance: modal,
            options: options
        });

        // 绑定模态框事件
        if (options.onShow) {
            modalElement.addEventListener('show.bs.modal', options.onShow);
        }
        if (options.onShown) {
            modalElement.addEventListener('shown.bs.modal', options.onShown);
        }
        if (options.onHide) {
            modalElement.addEventListener('hide.bs.modal', options.onHide);
        }
        if (options.onHidden) {
            modalElement.addEventListener('hidden.bs.modal', options.onHidden);
        }

        console.log(`ModalManager: Registered modal ${modalId}`);
        return modal;
    }

    /**
     * 显示模态框
     */
    showModal(modalId, options = {}) {
        if (!this.initialized) {
            this.pendingActions.push(() => this.showModal(modalId, options));
            return;
        }

        let modalInfo = this.modals.get(modalId);
        
        // 如果模态框未注册，尝试注册
        if (!modalInfo) {
            const modalElement = document.getElementById(modalId);
            if (!modalElement) {
                console.error(`ModalManager: Modal ${modalId} not found`);
                return;
            }
            
            this.registerModal(modalId, options);
            modalInfo = this.modals.get(modalId);
        }

        if (modalInfo && modalInfo.instance) {
            // 在显示前执行回调
            if (options.beforeShow) {
                options.beforeShow(modalInfo.element);
            }

            // 显示模态框
            modalInfo.instance.show();

            // 确保输入框可交互
            setTimeout(() => {
                this.ensureModalInteractive(modalId);
            }, 300);
        }
    }

    /**
     * 隐藏模态框
     */
    hideModal(modalId) {
        const modalInfo = this.modals.get(modalId);
        if (modalInfo && modalInfo.instance) {
            modalInfo.instance.hide();
        }
    }

    /**
     * 确保模态框元素可交互
     */
    ensureModalInteractive(modalId) {
        const modalElement = document.getElementById(modalId);
        if (!modalElement) return;

        // 修复所有输入元素
        const inputs = modalElement.querySelectorAll('input, textarea, select, button');
        inputs.forEach(input => {
            input.style.pointerEvents = 'auto';
            input.style.opacity = '1';
            input.style.visibility = 'visible';
            input.disabled = false;
            
            if (!input.readOnly) {
                input.readOnly = false;
            }
        });

        // 修复模态框本身
        modalElement.style.pointerEvents = 'auto';
        
        const modalContent = modalElement.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.pointerEvents = 'auto';
        }

        // 尝试聚焦第一个输入框
        const firstInput = modalElement.querySelector('input:not([type="hidden"]), textarea, select');
        if (firstInput && !firstInput.readOnly && !firstInput.disabled) {
            firstInput.focus();
        }
    }

    /**
     * 创建并显示动态模态框
     */
    createDynamicModal(options) {
        const modalId = options.id || `modal-${Date.now()}`;
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1">
                <div class="modal-dialog ${options.size || ''}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${options.title || ''}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${options.body || ''}
                        </div>
                        ${options.footer ? `
                            <div class="modal-footer">
                                ${options.footer}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的同ID模态框
        const existingModal = document.getElementById(modalId);
        if (existingModal) {
            existingModal.remove();
        }

        // 添加到body
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 注册并显示
        this.registerModal(modalId, options);
        this.showModal(modalId);

        return modalId;
    }

    /**
     * 销毁模态框
     */
    destroyModal(modalId) {
        const modalInfo = this.modals.get(modalId);
        if (modalInfo) {
            // 隐藏模态框
            if (modalInfo.instance) {
                modalInfo.instance.hide();
                modalInfo.instance.dispose();
            }
            
            // 从Map中移除
            this.modals.delete(modalId);
            
            // 移除DOM元素
            if (modalInfo.element) {
                modalInfo.element.remove();
            }
        }
    }

    /**
     * 获取模态框实例
     */
    getModal(modalId) {
        const modalInfo = this.modals.get(modalId);
        return modalInfo ? modalInfo.instance : null;
    }

    /**
     * 检查模态框是否显示
     */
    isModalShown(modalId) {
        const modalElement = document.getElementById(modalId);
        return modalElement && modalElement.classList.contains('show');
    }
}

// 创建全局实例并初始化
window.modalManager = new ModalManager();
window.modalManager.init();

// 导出给模块系统使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalManager;
}