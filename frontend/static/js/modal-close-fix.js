/**
 * 模态框关闭修复脚本
 * 解决模态框无法关闭的问题
 */

// 强制关闭所有模态框
function forceCloseAllModals() {
    console.log('强制关闭所有模态框...');

    // 关闭所有Bootstrap模态框
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    });

    // 移除所有模态框的show类
    const visibleModals = document.querySelectorAll('.modal.show');
    visibleModals.forEach(modal => {
        modal.classList.remove('show');
        modal.style.display = 'none';
    });

    // 移除模态框背景
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
        backdrop.remove();
    });

    // 恢复body的滚动
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    console.log('所有模态框已强制关闭');
}

// 特别处理删除进度模态框
function forceCloseDeleteProgressModal() {
    console.log('强制关闭删除进度模态框...');

    const progressModal = document.getElementById('deleteProgressModal');
    if (progressModal) {
        // 获取Bootstrap模态框实例
        const bsModal = bootstrap.Modal.getInstance(progressModal);
        if (bsModal) {
            bsModal.hide();
        }

        // 强制移除show类
        progressModal.classList.remove('show');
        progressModal.style.display = 'none';

        // 移除模态框背景
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            backdrop.remove();
        });

        // 恢复body的滚动
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        console.log('删除进度模态框已强制关闭');
    }
}

// 页面加载时自动检查并关闭意外的模态框
document.addEventListener('DOMContentLoaded', () => {
    console.log('检查是否有意外的模态框...');

    // 延迟执行，确保所有脚本都加载完成
    setTimeout(() => {
        const visibleModals = document.querySelectorAll('.modal.show');
        if (visibleModals.length > 0) {
            console.log(`发现 ${visibleModals.length} 个打开的模态框，尝试关闭...`);
            forceCloseAllModals();
        }

        // 特别检查删除进度模态框
        const progressModal = document.getElementById('deleteProgressModal');
        if (progressModal && progressModal.classList.contains('show')) {
            console.log('发现删除进度模态框意外打开，强制关闭...');
            forceCloseDeleteProgressModal();
        }
    }, 1000);
});

// 添加键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+M 强制关闭所有模态框
    if (e.ctrlKey && e.shiftKey && e.key === 'M') {
        e.preventDefault();
        forceCloseAllModals();
    }

    // ESC键关闭模态框
    if (e.key === 'Escape') {
        const visibleModals = document.querySelectorAll('.modal.show');
        if (visibleModals.length > 0) {
            forceCloseAllModals();
        }
    }
});

// 导出函数供其他脚本使用
window.forceCloseAllModals = forceCloseAllModals;
window.forceCloseDeleteProgressModal = forceCloseDeleteProgressModal;
