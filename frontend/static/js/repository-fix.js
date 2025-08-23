/**
 * Repository.js API路径修复脚本
 * 修复所有重复的/api前缀问题
 */

// 修复repository.js中的API路径
function fixRepositoryApiPaths() {
    console.log('开始修复repository.js中的API路径...');

    // 获取所有使用fetch的代码
    const fetchCalls = [
        { old: '/api/repositories/validate-url', new: '/repositories/validate-url' },
        { old: '/api/repositories', new: '/repositories' },
        { old: '/api/repositories/', new: '/repositories/' },
        { old: '/api/repositories/statistics', new: '/repositories/statistics' },
        { old: '/api/repositories/sync', new: '/repositories/sync' },
        { old: '/api/repositories/confirm-delete', new: '/repositories/confirm-delete' }
    ];

    // 修复fetch调用
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        let fixedUrl = url;

        // 修复API路径
        fetchCalls.forEach(fix => {
            if (typeof url === 'string' && url.includes(fix.old)) {
                fixedUrl = url.replace(fix.old, fix.new);
                console.log(`修复API路径: ${url} -> ${fixedUrl}`);
            }
        });

        return originalFetch(fixedUrl, options);
    };

    console.log('repository.js API路径修复完成');
}

// 页面加载时执行修复
document.addEventListener('DOMContentLoaded', function() {
    fixRepositoryApiPaths();
});

// 导出修复函数
window.RepositoryApiFixer = {
    fixRepositoryApiPaths: fixRepositoryApiPaths
};

