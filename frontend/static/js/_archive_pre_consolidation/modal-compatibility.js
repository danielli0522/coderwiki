/**
 * 模态框兼容性层
 * 确保旧代码仍然工作，同时使用新的轻量级系统
 */

// 等待新系统加载完成
if (typeof window.modalSystemLite === 'undefined') {
    // 如果新系统还没加载，创建临时兼容层
    window.modalSystemLite = {
        show: function(selector, options) {
            // 降级为Bootstrap原生方法
            const modal = document.querySelector(selector);
            if (modal && window.bootstrap) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                return modal;
            }
        },
        hide: function(selector) {
            const modal = document.querySelector(selector);
            if (modal && window.bootstrap) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        }
    };
}

// 确保旧的API调用仍然工作
if (typeof window.showModal === 'undefined') {
    window.showModal = function(selector, options) {
        return window.modalSystemLite.show(selector, options);
    };
}

if (typeof window.hideModal === 'undefined') {
    window.hideModal = function(selector) {
        return window.modalSystemLite.hide(selector);
    };
}

// 兼容旧的modalSystem对象
if (typeof window.modalSystem === 'undefined') {
    window.modalSystem = window.modalSystemLite;
}

console.log('Modal compatibility layer loaded');