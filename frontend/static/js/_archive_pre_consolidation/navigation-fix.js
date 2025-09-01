/**
 * 统一导航系统
 * 解决顶部导航按钮点击无响应的问题
 */

class UnifiedNavigation {
    constructor() {
        this.initialized = false;
        this.currentPage = window.location.pathname;
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        // 等待DOM完全加载
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        console.log('🚀 Unified Navigation System - Initializing...');
        
        // 清除现有的导航事件监听器
        this.clearExistingHandlers();
        
        // 修复导航链接
        this.fixNavigationLinks();
        
        // 设置响应式导航
        this.setupResponsiveNavigation();
        
        // 添加调试信息
        this.addDebugInfo();
        
        this.initialized = true;
        console.log('✅ Unified Navigation System - Ready!');
    }

    clearExistingHandlers() {
        // 获取所有导航链接并移除克隆以清除事件
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            const newLink = link.cloneNode(true);
            link.parentNode.replaceChild(newLink, link);
        });
    }

    fixNavigationLinks() {
        // 获取所有导航链接
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        console.log(`🔗 Found ${navLinks.length} navigation links`);

        navLinks.forEach((link, index) => {
            const linkText = link.textContent.trim();
            const linkHref = link.href;
            
            console.log(`Link ${index + 1}: "${linkText}" -> ${linkHref}`);

            // 确保链接样式正确
            this.ensureLinkStyles(link);
            
            // 添加统一的点击处理
            this.attachClickHandler(link, linkText, linkHref);
            
            // 添加视觉反馈
            this.addVisualFeedback(link);
            
            // 标记当前页面
            this.markCurrentPage(link);
        });
    }

    ensureLinkStyles(link) {
        // 强制确保链接可点击
        link.style.pointerEvents = 'auto';
        link.style.cursor = 'pointer';
        link.style.userSelect = 'auto';
        link.style.display = 'block';
        link.style.position = 'relative';
        link.style.zIndex = '1000';
        
        // 移除可能的干扰属性
        link.style.removeProperty('pointer-events');
        link.style.removeProperty('opacity');
        link.style.removeProperty('visibility');
    }

    attachClickHandler(link, linkText, linkHref) {
        // 移除现有的点击事件
        link.onclick = null;
        
        // 添加新的点击事件
        link.addEventListener('click', (e) => {
            console.log(`🖱️ Navigation clicked: "${linkText}" -> ${linkHref}`);
            
            // 确保链接有效
            if (!linkHref || linkHref === '#' || linkHref.includes('javascript:')) {
                console.warn('⚠️ Invalid link detected:', linkHref);
                e.preventDefault();
                return;
            }
            
            // 添加视觉反馈
            this.showClickFeedback(link);
            
            // 允许正常导航
            console.log('✅ Allowing navigation to:', linkHref);
            // 不阻止默认行为，让链接正常工作
        }, { passive: false });
    }

    addVisualFeedback(link) {
        // 鼠标悬停效果
        link.addEventListener('mouseenter', () => {
            link.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            link.style.transform = 'scale(1.02)';
            link.style.transition = 'all 0.2s ease';
        });

        link.addEventListener('mouseleave', () => {
            if (!link.classList.contains('active')) {
                link.style.backgroundColor = '';
            }
            link.style.transform = '';
        });
    }

    showClickFeedback(link) {
        // 点击动画效果
        link.style.transform = 'scale(0.98)';
        link.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        
        setTimeout(() => {
            link.style.transform = '';
            if (!link.classList.contains('active')) {
                link.style.backgroundColor = '';
            }
        }, 150);
    }

    markCurrentPage(link) {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === this.currentPage) {
            link.classList.add('active');
            link.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
            link.style.fontWeight = 'bold';
        }
    }

    setupResponsiveNavigation() {
        // 处理移动设备导航
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', () => {
                navbarCollapse.classList.toggle('show');
            });
        }
    }

    addDebugInfo() {
        // 创建调试面板
        const debugInfo = document.createElement('div');
        debugInfo.id = 'unified-nav-debug';
        debugInfo.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.9);
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            z-index: 10000;
            max-width: 350px;
            display: none;
            border: 1px solid #00ff00;
        `;

        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        let debugHtml = `
            <div style="color: #00ffff; font-weight: bold; margin-bottom: 10px;">
                🔧 Unified Navigation Debug Panel
            </div>
            <div style="color: #ffff00;">Current Page: ${this.currentPage}</div>
            <div style="color: #ffff00;">Links Found: ${navLinks.length}</div>
            <div style="margin-top: 10px; color: #ffffff;">Navigation Links:</div>
        `;

        navLinks.forEach((link, index) => {
            const status = link.style.pointerEvents === 'none' ? '❌' : '✅';
            debugHtml += `
                <div style="margin: 2px 0; color: #cccccc;">
                    ${status} ${index + 1}. ${link.textContent.trim()}
                </div>
            `;
        });

        debugHtml += `
            <div style="margin-top: 10px; color: #00ff00; font-size: 10px;">
                Press Ctrl+Shift+N to toggle this panel
            </div>
        `;

        debugInfo.innerHTML = debugHtml;
        document.body.appendChild(debugInfo);

        // 键盘快捷键显示调试信息
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'N') {
                e.preventDefault();
                const debugPanel = document.getElementById('unified-nav-debug');
                debugPanel.style.display = debugPanel.style.display === 'none' ? 'block' : 'none';
            }
        });
    }

    // 强制应用导航样式修复
    applyStyleFixes() {
        const style = document.createElement('style');
        style.id = 'unified-nav-fixes';
        style.textContent = `
            /* 统一导航系统样式修复 */
            .navbar-nav .nav-link {
                pointer-events: auto !important;
                cursor: pointer !important;
                user-select: auto !important;
                opacity: 1 !important;
                visibility: visible !important;
                display: flex !important;
                align-items: center !important;
                position: relative !important;
                z-index: 1000 !important;
                color: rgba(255, 255, 255, 0.85) !important;
                transition: all 0.2s ease !important;
            }

            .navbar-nav .nav-link:hover {
                color: #ffffff !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
                text-decoration: none !important;
                transform: scale(1.02) !important;
            }

            .navbar-nav .nav-link.active {
                color: #ffffff !important;
                background-color: rgba(255, 255, 255, 0.15) !important;
                font-weight: bold !important;
            }

            .navbar-nav .nav-link:active {
                transform: scale(0.98) !important;
            }

            /* 确保导航容器可交互 */
            .navbar-nav,
            .navbar-nav li,
            .navbar-collapse {
                pointer-events: auto !important;
            }

            /* 移除可能干扰的覆盖层 */
            .navbar::before,
            .navbar::after {
                display: none !important;
            }
        `;

        // 移除旧的样式
        const oldStyle = document.getElementById('unified-nav-fixes');
        if (oldStyle) {
            oldStyle.remove();
        }

        document.head.appendChild(style);
        console.log('📝 Navigation style fixes applied');
    }
}

// 立即初始化统一导航系统
const unifiedNavigation = new UnifiedNavigation();

// 确保样式立即应用
document.addEventListener('DOMContentLoaded', () => {
    unifiedNavigation.applyStyleFixes();
});

// 如果DOM已经加载完成，立即应用样式
if (document.readyState !== 'loading') {
    unifiedNavigation.applyStyleFixes();
}

// 导出全局访问
window.UnifiedNavigation = UnifiedNavigation;
window.unifiedNavigation = unifiedNavigation;

