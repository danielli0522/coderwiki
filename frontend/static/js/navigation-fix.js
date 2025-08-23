/**
 * 导航链接修复脚本
 * 解决顶部导航按钮点击无响应的问题
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Navigation fix script loaded');

    // 修复导航链接点击问题
    fixNavigationLinks();

    // 添加调试信息
    addNavigationDebugInfo();
});

function fixNavigationLinks() {
    // 获取所有导航链接
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    console.log('Found navigation links:', navLinks.length);

    navLinks.forEach(function(link, index) {
        console.log(`Link ${index + 1}:`, link.textContent.trim(), link.href);

        // 确保链接可以点击
        link.style.pointerEvents = 'auto';
        link.style.cursor = 'pointer';
        link.style.userSelect = 'auto';

        // 移除可能的事件监听器
        const newLink = link.cloneNode(true);
        link.parentNode.replaceChild(newLink, link);

        // 添加点击事件监听器
        newLink.addEventListener('click', function(e) {
            console.log('Navigation link clicked:', this.textContent.trim(), this.href);

            // 确保链接正常工作
            if (this.href && this.href !== '#' && this.href !== window.location.href) {
                console.log('Navigating to:', this.href);
                window.location.href = this.href;
            }
        });

        // 添加鼠标悬停效果
        newLink.addEventListener('mouseenter', function() {
            this.style.opacity = '0.8';
        });

        newLink.addEventListener('mouseleave', function() {
            this.style.opacity = '1';
        });
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

// 页面加载完成后执行修复
document.addEventListener('DOMContentLoaded', function() {
    forceFixNavigationStyles();
    console.log('Navigation styles fixed');
});

