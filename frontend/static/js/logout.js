/**
 * 用户登出功能
 */

async function logout() {
    try {
        console.log('开始登出流程...');

        // 显示加载状态
        const logoutBtn = event.target;
        const originalText = logoutBtn.innerHTML;
        logoutBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 退出中...';
        logoutBtn.disabled = true;

        // 调用登出API
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        });

        if (response.ok) {
            console.log('登出成功');
            // 清除本地存储
            localStorage.removeItem('user');
            sessionStorage.clear();

            // 显示成功消息
            showToast('登出成功', 'success');

            // 重定向到登录页面
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        } else {
            console.error('登出失败:', response.status);
            showToast('登出失败，请重试', 'error');
        }
    } catch (error) {
        console.error('登出异常:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        // 恢复按钮状态
        if (logoutBtn) {
            logoutBtn.innerHTML = originalText;
            logoutBtn.disabled = false;
        }
    }
}

// 显示消息提示
function showToast(message, type = 'info') {
    // 检查是否已有toast容器
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    // 创建toast元素
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">${type === 'success' ? '成功' : type === 'error' ? '错误' : '提示'}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    // 显示toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    toast.show();

    // 自动移除toast元素
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('登出功能初始化完成');
});
