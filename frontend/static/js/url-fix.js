/**
 * URL修复脚本
 * 修复所有API路径问题，避免重复的/api前缀
 */

// 全局URL修复函数
window.fixApiUrls = function() {
    console.log('开始修复API URL...');

    // 修复fetch调用中的API路径
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        // 如果URL以/auth/、/repositories/等开头但不以/api/开头，添加/api前缀
        if (typeof url === 'string') {
            const needsApiPrefix = ['/auth/', '/repositories/', '/tasks/', '/documents/', '/system/', '/users/', '/analysis/'];
            const shouldAddApiPrefix = needsApiPrefix.some(prefix => url.startsWith(prefix)) && !url.startsWith('/api/');
            
            if (shouldAddApiPrefix) {
                const fixedUrl = '/api' + url;
                console.log(`修复API URL: ${url} -> ${fixedUrl}`);
                return originalFetch(fixedUrl, options);
            }
        }
        return originalFetch(url, options);
    };

    console.log('API URL修复完成');
};

// 修复URLSearchParams构造问题
window.fixUrlSearchParams = function() {
    console.log('开始修复URLSearchParams...');

    // 重写URLSearchParams构造函数
    const OriginalURLSearchParams = window.URLSearchParams;
    window.URLSearchParams = function(init) {
        try {
            return new OriginalURLSearchParams(init);
        } catch (error) {
            console.error('URLSearchParams构造失败:', error);
            // 回退到空对象
            return new OriginalURLSearchParams();
        }
    };

    console.log('URLSearchParams修复完成');
};

// 修复URL构造函数问题
window.fixUrlConstructor = function() {
    console.log('开始修复URL构造函数...');

    const OriginalURL = window.URL;
    window.URL = function(url, base) {
        try {
            // 如果URL是相对路径且没有base，使用当前域名
            if (typeof url === 'string' && url.startsWith('/') && !base) {
                return new OriginalURL(url, window.location.origin);
            }
            return new OriginalURL(url, base);
        } catch (error) {
            console.error('URL构造失败:', error);
            // 回退到当前页面URL
            return new OriginalURL(window.location.href);
        }
    };

    // 保持静态方法
    window.URL.createObjectURL = OriginalURL.createObjectURL;
    window.URL.revokeObjectURL = OriginalURL.revokeObjectURL;

    console.log('URL构造函数修复完成');
};

// 页面加载时执行修复
document.addEventListener('DOMContentLoaded', function() {
    console.log('URL修复脚本加载');

    // 执行所有修复
    window.fixApiUrls();
    window.fixUrlSearchParams();
    window.fixUrlConstructor();

    console.log('所有URL修复完成');
});

// 导出修复函数供其他脚本使用
window.UrlFixer = {
    fixApiUrls: window.fixApiUrls,
    fixUrlSearchParams: window.fixUrlSearchParams,
    fixUrlConstructor: window.fixUrlConstructor
};

