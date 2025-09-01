/**
 * CoderWiki 导航管理器 - 解决导航失效问题
 * 
 * 功能：
 * 1. 防护性导航处理，确保导航链接始终有效
 * 2. 自动清理可能阻塞导航的元素（浮层、模态框等）
 * 3. 智能监控和自动修复机制
 * 4. 紧急导航降级处理
 */

class NavigationManager {
    constructor() {
        this.initialized = false;
        this.routes = new Map();
        this.currentRoute = null;
        this.isNavigating = false;
        this.healthCheckInterval = null;
        
        console.log('🧭 NavigationManager: 正在初始化...');
        this.init();
    }
    
    init() {
        if (this.initialized) {
            console.warn('NavigationManager already initialized');
            return;
        }
        
        // 等待DOM完全加载
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupNavigation());
        } else {
            this.setupNavigation();
        }
        
        // 确保在所有脚本加载后再次设置
        window.addEventListener('load', () => this.reinforceNavigation());
        
        // 页面显示时重新检查
        window.addEventListener('pageshow', () => this.reinforceNavigation());
        
        this.initialized = true;
        console.log('✅ NavigationManager: 初始化完成');
    }
    
    setupNavigation() {
        console.log('🔧 NavigationManager: 设置导航系统...');
        
        // 清理现有的事件监听器，避免重复绑定
        this.cleanupExistingListeners();
        
        // 设置防护性事件监听器
        this.attachNavigationListeners();
        
        // 设置监控和自动修复机制
        this.startNavigationMonitoring();
        
        // 添加DOM变化监听器
        this.addMutationObserver();
        
        console.log('✅ NavigationManager: 导航系统设置完成');
    }
    
    cleanupExistingListeners() {
        // 标记导航链接，防止其他脚本干扰
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            if (link.onclick) {
                link.onclick = null;
            }
            link.removeAttribute('onclick');
            // 添加标记，表示这是由NavigationManager管理的链接
            link.setAttribute('data-navigation-managed', 'true');
        });
    }
    
    attachNavigationListeners() {
        // 仅针对导航栏中的链接进行特殊处理
        document.addEventListener('click', (e) => {
            // 只处理导航栏中的链接
            const navLink = e.target.closest('.navbar-nav .nav-link, .navbar .nav-link');
            
            if (navLink && this.isValidNavigationLink(navLink)) {
                console.log('🔗 NavigationManager: 监控导航点击', navLink.href);
                
                // 仅在必要时清理阻塞元素，不干扰正常导航
                // this.clearNavigationBlockers(); // 暂时禁用自动清理
                
                // 标记导航状态但不阻止正常行为
                this.isNavigating = true;
                setTimeout(() => {
                    this.isNavigating = false;
                }, 1000);
            }
        }, false); // 使用冒泡阶段，不干扰正常点击
        
        console.log('✅ NavigationManager: 事件监听器已添加');
    }
    
    isValidNavigationLink(link) {
        const href = link.getAttribute('href');
        
        // 必须有有效的href属性
        if (!href) {
            return false;
        }
        
        // 排除空链接和JavaScript链接
        if (href === '#' || href === 'javascript:void(0)' || href.startsWith('javascript:')) {
            return false;
        }
        
        // 排除下载链接
        if (link.hasAttribute('download')) {
            return false;
        }
        
        // 排除模态框触发器
        if (link.hasAttribute('data-bs-toggle') || link.hasAttribute('data-toggle')) {
            return false;
        }
        
        // 允许相对路径、绝对路径和同域链接
        if (href.startsWith('/') || href.startsWith('./') || href.startsWith('../')) {
            return true;
        }
        
        // 允许同域的完整URL
        if (href.startsWith('http') && href.includes(window.location.hostname)) {
            return true;
        }
        
        // 允许相对路径（没有协议和域名的路径）
        if (!href.startsWith('http') && !href.includes('//')) {
            return true;
        }
        
        return false;
    }
    
    handleNavigation(link) {
        if (this.isNavigating) {
            console.warn('NavigationManager: 导航正在进行中，忽略点击');
            return;
        }
        
        this.isNavigating = true;
        
        try {
            const href = link.getAttribute('href');
            const target = link.getAttribute('target');
            
            console.log('🚀 NavigationManager: 执行导航', href);
            
            // 清理可能阻止导航的元素
            this.clearNavigationBlockers();
            
            // 执行导航
            if (target === '_blank') {
                window.open(href, '_blank');
                this.isNavigating = false; // 新窗口打开不影响当前页面
            } else {
                // 添加加载指示器
                this.showNavigationLoading();
                
                // 执行页面跳转
                window.location.href = href;
            }
            
        } catch (error) {
            console.error('NavigationManager: 导航错误', error);
            // 降级处理：强制页面跳转
            this.emergencyNavigate(link.href);
        }
    }
    
    clearNavigationBlockers() {
        console.log('🧹 NavigationManager: 清理导航阻塞元素...');
        
        // 移除可能阻止导航的浮层
        const blockers = document.querySelectorAll([
            '.modal-backdrop:not(.show)',
            '.overlay:not(.active)', 
            '.loading-overlay:not(.active)',
            '.user-feedback-overlay:not(.active)',
            '[style*="z-index: 999"]:not(.dropdown-menu):not(.modal.show)'
        ].join(', '));
        
        let removedCount = 0;
        blockers.forEach(blocker => {
            const style = window.getComputedStyle(blocker);
            if (style.display !== 'none' && style.visibility !== 'hidden') {
                blocker.style.display = 'none';
                removedCount++;
            }
        });
        
        if (removedCount > 0) {
            console.log(`🧹 NavigationManager: 移除了 ${removedCount} 个阻塞元素`);
        }
        
        // 重置body状态
        document.body.style.overflow = '';
        document.body.style.pointerEvents = '';
        document.body.classList.remove('modal-open');
        
        // 重置documentElement状态
        document.documentElement.style.overflow = '';
        document.documentElement.style.pointerEvents = '';
    }
    
    showNavigationLoading() {
        // 在导航链接上显示加载状态
        const activeLinks = document.querySelectorAll('.nav-link.active, .nav-link[aria-current="page"]');
        activeLinks.forEach(link => {
            const originalText = link.textContent;
            link.textContent = '加载中...';
            link.style.opacity = '0.6';
            
            // 3秒后恢复（防止卡住）
            setTimeout(() => {
                link.textContent = originalText;
                link.style.opacity = '';
            }, 3000);
        });
    }
    
    startNavigationMonitoring() {
        // 清理之前的监控
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        
        // 每5秒检查导航系统状态
        this.healthCheckInterval = setInterval(() => {
            this.healthCheck();
        }, 5000);
        
        console.log('👁️ NavigationManager: 导航监控已启动');
    }
    
    healthCheck() {
        const navLinks = document.querySelectorAll('.nav-link, .navbar-nav a');
        const validLinks = Array.from(navLinks).filter(link => 
            this.isValidNavigationLink(link)
        );
        
        if (validLinks.length === 0 && navLinks.length > 0) {
            console.warn('⚠️ NavigationManager: 检测到导航系统异常，尝试修复...');
            this.emergencyRepair();
        }
        
        // 检查是否有阻塞元素
        const blockers = document.querySelectorAll([
            '.modal-backdrop:not(.show)',
            '[style*="pointer-events: none"]:not(.d-none)'
        ].join(', '));
        
        if (blockers.length > 0) {
            console.log('🧹 NavigationManager: 发现阻塞元素，自动清理');
            this.clearNavigationBlockers();
        }
    }
    
    emergencyRepair() {
        console.log('🚨 NavigationManager: 执行紧急修复...');
        
        // 重新设置导航系统
        this.setupNavigation();
        
        // 1秒后检查修复结果
        setTimeout(() => {
            if (this.isNavigationBroken()) {
                console.error('❌ NavigationManager: 修复失败，显示紧急导航');
                this.showEmergencyNavigation();
            } else {
                console.log('✅ NavigationManager: 修复成功');
            }
        }, 1000);
    }
    
    isNavigationBroken() {
        const navLinks = document.querySelectorAll('.nav-link[href]:not([href="#"])');
        return navLinks.length === 0;
    }
    
    showEmergencyNavigation() {
        // 移除之前的紧急导航
        const existingEmergency = document.querySelector('.emergency-navigation');
        if (existingEmergency) {
            existingEmergency.remove();
        }
        
        const emergencyNav = document.createElement('div');
        emergencyNav.className = 'emergency-navigation';
        emergencyNav.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10001;
            background: #dc3545;
            color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        emergencyNav.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 10px;">
                ⚠️ 导航系统故障
            </div>
            <div style="margin-bottom: 10px; font-size: 12px;">
                使用下方按钮继续导航：
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button onclick="window.emergencyNavigate('/')" 
                        style="background: white; color: #dc3545; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    首页
                </button>
                <button onclick="window.emergencyNavigate('/dashboard')" 
                        style="background: white; color: #dc3545; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    仪表盘
                </button>
                <button onclick="window.emergencyNavigate('/repositories')" 
                        style="background: white; color: #dc3545; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    仓库管理
                </button>
                <button onclick="location.reload()" 
                        style="background: #ffc107; color: #000; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    刷新页面
                </button>
            </div>
            <button onclick="this.parentElement.remove()" 
                    style="position: absolute; top: 5px; right: 8px; background: none; border: none; color: white; cursor: pointer; font-size: 16px;">
                ×
            </button>
        `;
        
        document.body.appendChild(emergencyNav);
        
        // 15秒后自动移除
        setTimeout(() => {
            if (emergencyNav.parentElement) {
                emergencyNav.remove();
            }
        }, 15000);
    }
    
    reinforceNavigation() {
        console.log('💪 NavigationManager: 强化导航系统...');
        
        // 清理导航阻塞元素
        this.clearNavigationBlockers();
        
        // 重新标记导航链接
        this.cleanupExistingListeners();
        
        // 修复可能的样式问题
        this.fixNavigationStyles();
        
        // 重新设置导航监听器
        this.attachNavigationListeners();
        
        // 确保监控正在运行
        if (!this.healthCheckInterval) {
            this.startNavigationMonitoring();
        }
    }
    
    fixNavigationStyles() {
        // 确保所有导航链接都有正确的样式
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            // 确保链接可点击
            link.style.pointerEvents = 'auto';
            link.style.cursor = 'pointer';
            link.style.position = 'relative';
            link.style.zIndex = '1000';
            
            // 移除可能的阻塞样式
            link.style.removeProperty('opacity');
            link.style.removeProperty('visibility');
        });
        
        console.log('✅ NavigationManager: 导航样式已修复');
    }
    
    addMutationObserver() {
        // 监控DOM变化，当导航元素被修改时重新设置
        const observer = new MutationObserver((mutations) => {
            let needsReinforcement = false;
            
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1 && 
                            (node.classList?.contains('nav-link') || 
                             node.classList?.contains('navbar') ||
                             node.querySelector?.('.nav-link, .navbar'))) {
                            needsReinforcement = true;
                        }
                    });
                }
                
                // 监控属性变化（如href被修改）
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'href' || mutation.attributeName === 'onclick')) {
                    needsReinforcement = true;
                }
            });
            
            if (needsReinforcement) {
                console.log('🔄 NavigationManager: 检测到导航元素变化，重新强化...');
                setTimeout(() => this.reinforceNavigation(), 100);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['href', 'onclick']
        });
        
        console.log('👁️ NavigationManager: DOM变化监听器已添加');
    }
    
    // 紧急导航方法
    emergencyNavigate(url) {
        console.log('🚨 NavigationManager: 执行紧急导航', url);
        try {
            window.location.href = url;
        } catch (error) {
            console.error('紧急导航也失败了:', error);
            // 最后的降级方案
            window.location.replace(url);
        }
    }
    
    // 获取诊断信息
    getDiagnostics() {
        const navLinks = document.querySelectorAll('.nav-link, .navbar-nav a');
        const validLinks = [];
        const brokenLinks = [];
        
        Array.from(navLinks).forEach(link => {
            const isValid = this.isValidNavigationLink(link);
            const linkInfo = {
                element: link,
                text: link.textContent.trim(),
                href: link.getAttribute('href'),
                isValid: isValid
            };
            
            if (isValid) {
                validLinks.push(linkInfo);
            } else {
                brokenLinks.push(linkInfo);
            }
        });
        
        const overlays = document.querySelectorAll(
            '.modal-backdrop, .overlay, [style*="z-index: 999"]'
        );
        const blockingOverlays = Array.from(overlays).filter(el => {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden';
        });
        
        // 输出详细的损坏链接信息
        if (brokenLinks.length > 0) {
            console.warn('🔍 NavigationManager: 发现损坏的导航链接:');
            brokenLinks.forEach((link, index) => {
                console.warn(`  ${index + 1}. "${link.text}" -> ${link.href}`);
            });
        }
        
        return {
            totalLinks: navLinks.length,
            validLinks: validLinks.length,
            brokenLinks: brokenLinks.length,
            totalOverlays: overlays.length,
            blockingOverlays: blockingOverlays.length,
            isNavigating: this.isNavigating,
            monitoringActive: !!this.healthCheckInterval,
            brokenLinkDetails: brokenLinks,
            validLinkDetails: validLinks
        };
    }
    
    // 销毁方法（用于清理）
    destroy() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
        
        console.log('🔥 NavigationManager: 已销毁');
    }
}

// 创建全局导航管理器实例
let navigationManager;

// 确保只创建一个实例
if (!window.navigationManager) {
    navigationManager = new NavigationManager();
    window.navigationManager = navigationManager;
} else {
    navigationManager = window.navigationManager;
}

// 紧急导航全局函数
window.emergencyNavigate = (url) => {
    console.log('🚨 紧急导航:', url);
    navigationManager.emergencyNavigate(url);
};

// 导航诊断全局函数
window.getNavigationDiagnostics = () => {
    return navigationManager.getDiagnostics();
};

// 导航系统重置全局函数
window.resetNavigation = () => {
    console.log('🔄 重置导航系统');
    navigationManager.reinforceNavigation();
};

// 紧急导航功能
window.emergencyNavigate = (url) => {
    console.log('🆘 执行紧急导航:', url);
    navigationManager.emergencyNavigate(url);
};

// 导出供模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationManager;
}

console.log('✅ NavigationManager 脚本加载完成');