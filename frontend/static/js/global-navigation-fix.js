/**
 * Global Navigation Fix
 * 确保顶部导航在所有页面都能正常工作
 */

class GlobalNavigationFix {
    constructor() {
        this.init();
    }

    init() {
        console.log('GlobalNavigationFix: 初始化全局导航修复...');
        
        // 页面加载完成后立即执行修复
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.fixNavigation());
        } else {
            this.fixNavigation();
        }

        // 监听页面状态变化
        this.setupPageChangeListeners();
        
        // 定期检查导航状态
        this.setupNavigationMonitor();
    }

    fixNavigation() {
        console.log('GlobalNavigationFix: 修复导航功能...');
        
        // 清理可能阻止导航的样式
        this.cleanupBlockingStyles();
        
        // 确保导航链接可点击
        this.ensureNavigationClickable();
        
        // 移除模态框残留效果
        this.cleanupModalEffects();
        
        console.log('GlobalNavigationFix: 导航修复完成');
    }

    cleanupBlockingStyles() {
        // 清理body样式
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');
        
        // 移除可能的覆盖层
        const overlays = document.querySelectorAll('.modal-backdrop, .overlay');
        overlays.forEach(overlay => overlay.remove());
    }

    ensureNavigationClickable() {
        // 修复所有导航链接
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link, .navbar-brand, .nav-item a');
        
        navLinks.forEach(link => {
            // 确保链接样式正确
            link.style.pointerEvents = 'auto';
            link.style.cursor = 'pointer';
            link.style.zIndex = 'auto';
            link.style.position = 'relative';
            
            // 移除可能的事件阻止
            link.style.userSelect = 'auto';
            
            // 确保链接可见
            link.style.visibility = 'visible';
            link.style.opacity = '1';
        });

        // 确保导航容器可点击
        const navbars = document.querySelectorAll('.navbar, .navbar-nav, .navbar-collapse');
        navbars.forEach(navbar => {
            navbar.style.pointerEvents = 'auto';
            navbar.style.zIndex = 'auto';
        });
    }

    cleanupModalEffects() {
        // 移除所有模态框背景
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // 确保所有模态框都是隐藏状态
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
        });
    }

    setupPageChangeListeners() {
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                // 页面变为可见时修复导航
                setTimeout(() => this.fixNavigation(), 100);
            }
        });

        // 监听窗口焦点变化
        window.addEventListener('focus', () => {
            setTimeout(() => this.fixNavigation(), 100);
        });

        // 监听history变化（SPA应用）
        window.addEventListener('popstate', () => {
            setTimeout(() => this.fixNavigation(), 100);
        });
    }

    setupNavigationMonitor() {
        // 每隔5秒检查一次导航状态
        setInterval(() => {
            this.checkNavigationHealth();
        }, 5000);
    }

    checkNavigationHealth() {
        // 检查body是否有问题样式
        if (document.body.style.overflow === 'hidden' && 
            !document.querySelector('.modal.show')) {
            console.log('GlobalNavigationFix: 检测到异常的body overflow，正在修复...');
            this.fixNavigation();
        }

        // 检查是否有残留的modal-backdrop
        const backdrops = document.querySelectorAll('.modal-backdrop');
        if (backdrops.length > 0 && !document.querySelector('.modal.show')) {
            console.log('GlobalNavigationFix: 检测到残留的modal背景，正在清理...');
            backdrops.forEach(backdrop => backdrop.remove());
        }
    }

    // 公共方法：强制修复导航（可被其他脚本调用）
    forceFixNavigation() {
        console.log('GlobalNavigationFix: 强制修复导航...');
        this.fixNavigation();
    }
}

// 立即初始化
const globalNavigationFix = new GlobalNavigationFix();

// 导出到全局，供其他脚本使用
window.GlobalNavigationFix = globalNavigationFix;

// 为其他脚本提供便捷的修复函数
window.fixNavigation = () => globalNavigationFix.forceFixNavigation();

console.log('GlobalNavigationFix: 全局导航修复脚本已加载');