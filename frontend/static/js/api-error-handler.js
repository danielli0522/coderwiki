/**
 * API错误处理脚本
 * 提供更好的错误诊断和处理
 */

class ApiErrorHandler {
    constructor() {
        this.errorCount = 0;
        this.maxErrors = 5;
    }

    // 处理API响应
    async handleResponse(response, endpoint) {
        console.log(`API响应: ${endpoint} - 状态码: ${response.status}`);

        // 检查认证重定向
        if (response.status === 302 || response.status === 303) {
            const location = response.headers.get('location');
            console.log(`检测到认证重定向: ${response.status} -> ${location}`);

            if (location && location.includes('/auth/login')) {
                // 重定向到登录页面
                window.location.href = location;
                throw new Error('需要登录，正在跳转到登录页面...');
            }
        }

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API错误: ${endpoint} - ${response.status}`, errorText);

            // 检查是否是HTML响应（通常是错误页面）
            if (errorText.trim().startsWith('<!DOCTYPE') || errorText.trim().startsWith('<html')) {
                // 检查是否是登录页面重定向
                if (errorText.includes('login') || errorText.includes('登录')) {
                    console.log('检测到登录页面重定向，跳转到登录页面');
                    window.location.href = '/auth/login';
                    throw new Error('需要登录，正在跳转到登录页面...');
                }
                throw new Error(`API端点返回HTML而不是JSON: ${endpoint}`);
            }

            // 尝试解析JSON错误
            try {
                const errorData = JSON.parse(errorText);
                throw new Error(errorData.error || `API错误: ${response.status}`);
            } catch (parseError) {
                throw new Error(`API错误: ${response.status} - ${errorText.substring(0, 100)}`);
            }
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.warn(`API返回非JSON响应: ${endpoint}`, text.substring(0, 200));

            // 检查是否是登录页面
            if (text.includes('login') || text.includes('登录')) {
                console.log('检测到登录页面响应，跳转到登录页面');
                window.location.href = '/auth/login';
                throw new Error('需要登录，正在跳转到登录页面...');
            }

            throw new Error(`API返回非JSON响应: ${endpoint}`);
        }

        return response.json();
    }

    // 包装fetch调用
    async fetchWithErrorHandling(url, options = {}) {
        try {
            console.log(`发起API请求: ${url}`);

            // 添加重定向处理
            const response = await fetch(url, {
                ...options,
                redirect: 'manual' // 手动处理重定向
            });

            return await this.handleResponse(response, url);
        } catch (error) {
            this.errorCount++;
            console.error(`API请求失败: ${url}`, error);

            // 如果是认证错误，不显示错误消息，直接跳转
            if (error.message.includes('需要登录') || error.message.includes('跳转到登录页面')) {
                return; // 不显示错误，让重定向处理
            }

            // 显示用户友好的错误消息
            this.showUserError(error.message);

            // 如果错误太多，显示诊断信息
            if (this.errorCount >= this.maxErrors) {
                this.showDiagnosticInfo();
            }

            throw error;
        }
    }

    // 显示用户友好的错误消息
    showUserError(message) {
        // 创建错误通知
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <strong>API错误:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // 插入到页面顶部
        const container = document.querySelector('main .container') || document.querySelector('main');
        if (container) {
            container.insertAdjacentHTML('afterbegin', errorDiv.outerHTML);

            // 5秒后自动关闭
            setTimeout(() => {
                const alert = container.querySelector('.alert-danger');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }

    // 显示诊断信息
    showDiagnosticInfo() {
        const diagnosticInfo = {
            currentUrl: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            errorCount: this.errorCount
        };

        console.log('API诊断信息:', diagnosticInfo);

        // 创建诊断面板
        const diagnosticDiv = document.createElement('div');
        diagnosticDiv.className = 'alert alert-warning alert-dismissible fade show';
        diagnosticDiv.innerHTML = `
            <strong>API诊断信息:</strong><br>
            当前页面: ${diagnosticInfo.currentUrl}<br>
            错误次数: ${diagnosticInfo.errorCount}<br>
            时间: ${diagnosticInfo.timestamp}<br>
            <small>请检查网络连接和服务器状态</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('main .container') || document.querySelector('main');
        if (container) {
            container.insertAdjacentHTML('afterbegin', diagnosticDiv.outerHTML);
        }
    }

    // 检查API端点是否可用
    async checkApiHealth() {
        try {
            const response = await fetch('/api/system/health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('API健康检查:', data);
                return true;
            } else {
                console.warn('API健康检查失败:', response.status);
                return false;
            }
        } catch (error) {
            console.error('API健康检查错误:', error);
            return false;
        }
    }

    // 重置错误计数
    resetErrorCount() {
        this.errorCount = 0;
    }

    // 检查用户是否已登录
    async checkAuthentication() {
        try {
            const response = await fetch('/api/auth/profile', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                redirect: 'manual'
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    authenticated: true,
                    user: data.user
                };
            } else if (response.status === 302 || response.status === 303) {
                return {
                    authenticated: false,
                    redirectUrl: response.headers.get('location')
                };
            } else {
                return {
                    authenticated: false
                };
            }
        } catch (error) {
            console.error('认证检查失败:', error);
            return {
                authenticated: false
            };
        }
    }

    // 显示登录提示
    showLoginPrompt() {
        const loginDiv = document.createElement('div');
        loginDiv.className = 'alert alert-warning alert-dismissible fade show';
        loginDiv.innerHTML = `
            <strong>需要登录</strong><br>
            您需要登录才能访问此功能。<br>
            <a href="/auth/login" class="btn btn-primary btn-sm mt-2">立即登录</a>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('main .container') || document.querySelector('main');
        if (container) {
            container.insertAdjacentHTML('afterbegin', loginDiv.outerHTML);
        }
    }

    // 预检查认证状态
    async preCheckAuth() {
        const authStatus = await this.checkAuthentication();
        if (!authStatus.authenticated) {
            this.showLoginPrompt();
            return false;
        }
        return true;
    }
}

// 创建全局实例
window.apiErrorHandler = new ApiErrorHandler();

// 页面加载时检查API健康状态
document.addEventListener('DOMContentLoaded', function() {
    // 延迟检查，避免影响页面加载
    setTimeout(() => {
        window.apiErrorHandler.checkApiHealth();
    }, 2000);
});

// 导出类
window.ApiErrorHandler = ApiErrorHandler;

