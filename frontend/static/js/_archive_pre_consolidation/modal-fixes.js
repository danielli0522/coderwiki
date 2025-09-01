/**
 * 模态框修复脚本 - 强力解决无法输入问题
 */

document.addEventListener('DOMContentLoaded', function() {
    // 确保页面加载时没有模态框显示
    ensureNoModalsOnLoad();

    // 修复模态框交互问题
    fixModalInteractions();

    // 监听模态框事件
    document.addEventListener('shown.bs.modal', function(event) {
        console.log('模态框显示事件触发:', event.target.id);
        fixModalInteractions();
        forceEnableInputs(event.target);
    });

    // 监听模态框隐藏事件
    document.addEventListener('hidden.bs.modal', function(event) {
        cleanupModalInteractions();
    });

    // 定期检查并修复模态框
    setInterval(checkAndFixModals, 1000);
});

// 确保页面加载时没有模态框显示
function ensureNoModalsOnLoad() {
    console.log('确保页面加载时没有模态框显示...');

    // 关闭所有可能打开的模态框
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        // 移除show类
        modal.classList.remove('show');

        // 确保模态框隐藏
        modal.style.display = 'none';
        modal.style.opacity = '0';
        modal.style.visibility = 'hidden';

        // 尝试关闭Bootstrap模态框实例
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    });

    // 移除所有模态框背景
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
        backdrop.remove();
    });

    // 恢复body的滚动
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    console.log('页面加载时的模态框清理完成');
}

function fixModalInteractions() {
    console.log('开始修复模态框交互...');

    // 获取所有模态框
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        // 检查模态框是否应该显示
        const shouldBeVisible = modal.classList.contains('show');

        // 确保模态框可以正常交互，但只在应该显示时才设置可见性
        modal.style.pointerEvents = 'auto';
        modal.style.zIndex = '99999';

        // 只有在模态框应该显示时才设置这些样式
        if (shouldBeVisible) {
            modal.style.display = 'block';
            modal.style.opacity = '1';
            modal.style.visibility = 'visible';
        } else {
            // 确保隐藏的模态框保持隐藏状态
            modal.style.display = 'none';
            modal.style.opacity = '0';
            modal.style.visibility = 'hidden';
        }

        // 修复模态框内容
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.pointerEvents = 'auto';
            modalContent.style.zIndex = '99999';
            if (shouldBeVisible) {
                modalContent.style.opacity = '1';
                modalContent.style.visibility = 'visible';
            } else {
                modalContent.style.opacity = '0';
                modalContent.style.visibility = 'hidden';
            }
        }

        // 修复模态框对话框
        const modalDialog = modal.querySelector('.modal-dialog');
        if (modalDialog) {
            modalDialog.style.pointerEvents = 'auto';
            modalDialog.style.zIndex = '99999';
            if (shouldBeVisible) {
                modalDialog.style.opacity = '1';
                modalDialog.style.visibility = 'visible';
            } else {
                modalDialog.style.opacity = '0';
                modalDialog.style.visibility = 'hidden';
            }
        }

        // 修复所有输入元素
        const inputs = modal.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            forceEnableInput(input);
        });

        // 修复所有按钮
        const buttons = modal.querySelectorAll('button, .btn');
        buttons.forEach(button => {
            forceEnableButton(button);
        });

        // 修复表单
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => {
            forceEnableForm(form);
        });

        // 修复标签
        const labels = modal.querySelectorAll('label');
        labels.forEach(label => {
            forceEnableLabel(label);
        });

        // 修复模态框头部和底部
        const modalHeader = modal.querySelector('.modal-header');
        if (modalHeader) {
            forceEnableElement(modalHeader);
        }

        const modalBody = modal.querySelector('.modal-body');
        if (modalBody) {
            forceEnableElement(modalBody);
        }

        const modalFooter = modal.querySelector('.modal-footer');
        if (modalFooter) {
            forceEnableElement(modalFooter);
        }

        // 修复关闭按钮
        const closeButtons = modal.querySelectorAll('.btn-close, [data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            forceEnableButton(button);
        });
    });

    // 修复模态框背景
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
        backdrop.style.zIndex = '99998';
        backdrop.style.pointerEvents = 'auto';
    });

    console.log('模态框交互修复完成');
}

function forceEnableInput(input) {
    // 强制启用输入框
    input.style.pointerEvents = 'auto';
    input.style.zIndex = '100000';
    input.style.position = 'relative';
    input.style.opacity = '1';
    input.style.visibility = 'visible';
    input.style.display = 'block';
    input.style.width = '100%';
    input.style.boxSizing = 'border-box';
    input.style.backgroundColor = '#fff';
    input.style.color = '#495057';
    input.style.border = '1px solid #ced4da';
    input.style.borderRadius = '0.375rem';
    input.style.padding = '0.375rem 0.75rem';
    input.style.fontSize = '1rem';
    input.style.lineHeight = '1.5';
    input.style.userSelect = 'text';
    input.style.webkitUserSelect = 'text';
    input.style.mozUserSelect = 'text';
    input.style.msUserSelect = 'text';

    // 强制移除禁用状态
    input.disabled = false;
    input.readOnly = false;
    input.removeAttribute('disabled');
    input.removeAttribute('readonly');

    // 确保输入框可以获得焦点
    input.addEventListener('focus', function() {
        this.style.zIndex = '100001';
        this.style.outline = '2px solid #007bff';
        this.style.outlineOffset = '2px';
        this.style.borderColor = '#007bff';
        this.style.boxShadow = '0 0 0 0.2rem rgba(0, 123, 255, 0.25)';
        console.log('输入框获得焦点:', this.id);
    });

    input.addEventListener('blur', function() {
        this.style.outline = '';
        this.style.outlineOffset = '';
        console.log('输入框失去焦点:', this.id);
    });

    input.addEventListener('input', function() {
        console.log('输入框值变化:', this.id, this.value);
    });

    input.addEventListener('click', function() {
        console.log('输入框被点击:', this.id);
        this.focus();
    });

    console.log('强制启用输入框:', input.id);
}

function forceEnableButton(button) {
    // 强制启用按钮
    button.style.pointerEvents = 'auto';
    button.style.zIndex = '100000';
    button.style.position = 'relative';
    button.style.opacity = '1';
    button.style.visibility = 'visible';
    button.style.display = 'inline-block';
    button.style.cursor = 'pointer';
    button.style.userSelect = 'none';
    button.style.webkitUserSelect = 'none';
    button.style.mozUserSelect = 'none';
    button.style.msUserSelect = 'none';

    // 强制移除禁用状态
    button.disabled = false;
    button.removeAttribute('disabled');

    console.log('强制启用按钮:', button.id || button.className);
}

function forceEnableForm(form) {
    // 强制启用表单
    form.style.pointerEvents = 'auto';
    form.style.zIndex = '100000';
    form.style.position = 'relative';
    form.style.opacity = '1';
    form.style.visibility = 'visible';
    form.style.display = 'block';

    console.log('强制启用表单:', form.id);
}

function forceEnableLabel(label) {
    // 强制启用标签
    label.style.pointerEvents = 'auto';
    label.style.zIndex = '100000';
    label.style.position = 'relative';
    label.style.opacity = '1';
    label.style.visibility = 'visible';
    label.style.display = 'block';
    label.style.color = '#212529';
    label.style.fontWeight = '500';

    console.log('强制启用标签:', label.htmlFor || label.textContent);
}

function forceEnableElement(element) {
    // 强制启用元素
    element.style.pointerEvents = 'auto';
    element.style.zIndex = '100000';
    element.style.position = 'relative';
    element.style.opacity = '1';
    element.style.visibility = 'visible';
}

function forceEnableInputs(modal) {
    console.log('强制启用模态框输入元素:', modal.id);

    const inputs = modal.querySelectorAll('input, textarea, select');
    let focused = false;

    inputs.forEach(input => {
        forceEnableInput(input);

        // 尝试聚焦到第一个输入框
        if (!focused && input.type !== 'hidden' && !input.disabled) {
            setTimeout(() => {
                input.focus();
                console.log('尝试聚焦输入框:', input.id);
            }, 100);
            focused = true;
        }
    });
}

function checkAndFixModals() {
    // 定期检查并修复模态框
    const visibleModals = document.querySelectorAll('.modal.show');
    if (visibleModals.length > 0) {
        visibleModals.forEach(modal => {
            const inputs = modal.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.disabled || input.readOnly) {
                    console.log('检测到禁用的输入框，强制启用:', input.id);
                    forceEnableInput(input);
                }
            });
        });
    }

    // 确保没有意外显示的模态框
    const allModals = document.querySelectorAll('.modal');
    allModals.forEach(modal => {
        if (!modal.classList.contains('show')) {
            // 确保隐藏的模态框保持隐藏
            modal.style.display = 'none';
            modal.style.opacity = '0';
            modal.style.visibility = 'hidden';
        }
    });
}

function cleanupModalInteractions() {
    // 清理模态框相关的样式
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (!modal.classList.contains('show')) {
            modal.style.pointerEvents = '';
            modal.style.zIndex = '';
        }
    });
}

// 修复Bootstrap模态框初始化
function initializeModalFixes() {
    // 重写Bootstrap模态框的show方法
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const originalShow = bootstrap.Modal.prototype.show;
        bootstrap.Modal.prototype.show = function() {
            const result = originalShow.call(this);
            setTimeout(() => {
                fixModalInteractions();
                if (this._element) {
                    forceEnableInputs(this._element);
                }
            }, 100);
            return result;
        };

        console.log('Bootstrap模态框修复已初始化');
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeModalFixes);
} else {
    initializeModalFixes();
}

// 导出函数供其他脚本使用
window.fixModalInteractions = fixModalInteractions;
window.cleanupModalInteractions = cleanupModalInteractions;
window.forceEnableInputs = forceEnableInputs;
window.ensureNoModalsOnLoad = ensureNoModalsOnLoad;
