/**
 * 导航链接修复脚本 - 重构版本
 * 解决顶部导航按钮点击无响应的问题
 */

// 全局变量防止重复初始化
let navigationFixInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Navigation fix script loaded');
    
    if (!navigationFixInitialized) {
        navigationFixInitialized = true;
        
        // 仅修复CSS样式，不破坏现有事件绑定
        forceFixNavigationStyles();
        
        // 添加调试功能（可选）
        addNavigationDebugInfo();
        
        console.log('Navigation fix completed - preserving original event handlers');
    }
});

// 移除危险的DOM操作，仅通过CSS修复
function fixNavigationLinks() {
    // 仅确保链接样式正确，不修改DOM或事件
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    console.log('Found navigation links:', navLinks.length);

    navLinks.forEach(function(link, index) {
        console.log(`Link ${index + 1}:`, link.textContent.trim(), link.href);

        // 仅修复CSS样式，保留原始事件处理
        link.style.pointerEvents = 'auto';
        link.style.cursor = 'pointer';
        link.style.visibility = 'visible';
        link.style.opacity = '1';
    });
}

function addNavigationDebugInfo() {
    // 添加调试信息到页面
    const debugInfo = document.createElement('div');
    debugInfo.id = 'navigation-debug';
    debugInfo.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 10000;
        display: none;
    `;

    debugInfo.innerHTML = `
        <strong>导航调试信息</strong><br>
        <span id="debug-nav-links">正在检查导航链接...</span>
    `;

    document.body.appendChild(debugInfo);

    // 按F12显示调试信息
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12') {
            e.preventDefault();
            const debugDiv = document.getElementById('navigation-debug');
            debugDiv.style.display = debugDiv.style.display === 'none' ? 'block' : 'none';

            // 更新调试信息
            updateDebugInfo();
        }
    });
}

function updateDebugInfo() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const debugSpan = document.getElementById('debug-nav-links');

    if (debugSpan) {
        let info = `找到 ${navLinks.length} 个导航链接:<br>`;
        navLinks.forEach(function(link, index) {
            info += `${index + 1}. ${link.textContent.trim()} - ${link.href}<br>`;
        });
        debugSpan.innerHTML = info;
    }
}

// 强制修复导航链接的CSS样式
function forceFixNavigationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* 强制修复导航链接样式 */
        .navbar-nav .nav-link {
            pointer-events: auto !important;
            cursor: pointer !important;
            user-select: auto !important;
            opacity: 1 !important;
            visibility: visible !important;
            display: block !important;
            position: relative !important;
            z-index: 1000 !important;
        }

        .navbar-nav .nav-link:hover {
            opacity: 0.8 !important;
            text-decoration: none !important;
        }

        .navbar-nav .nav-link:active {
            opacity: 0.6 !important;
        }

        /* 确保导航容器不会阻止点击 */
        .navbar-nav {
            pointer-events: auto !important;
        }

        .navbar-nav li {
            pointer-events: auto !important;
        }
    `;

    document.head.appendChild(style);
}

// 页面加载完成后执行修复 - 已整合到主初始化函数中

