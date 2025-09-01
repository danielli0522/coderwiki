/**
 * 浮层清理修复脚本
 * 立即解决页面覆盖层阻塞交互的问题
 */

(function() {
    'use strict';
    
    // 立即执行清理函数
    function forceCleanupOverlays() {
        console.log('🧹 开始强制清理页面覆盖层...');
        
        // 1. 清理UI增强系统的初始化进度条
        const uiInitProgress = document.getElementById('ui-init-progress');
        if (uiInitProgress) {
            console.log('🗑️ 移除UI初始化进度条');
            uiInitProgress.remove();
        }
        
        // 2. 清理所有模态框背景层
        const modalBackdrops = document.querySelectorAll('.modal-backdrop, .modal-backdrop-lite, #modal-backdrop-lite');
        modalBackdrops.forEach((backdrop, index) => {
            console.log(`🗑️ 移除模态框背景层 ${index + 1}`);
            backdrop.remove();
        });
        
        // 3. 清理加载覆盖层和用户反馈覆盖层
        const loadingOverlays = document.querySelectorAll('#loading-overlay, .loading-overlay, .user-feedback-overlay');
        loadingOverlays.forEach((overlay, index) => {
            console.log(`🗑️ 移除加载覆盖层 ${index + 1}`);
            overlay.style.display = 'none';
            overlay.remove();
        });
        
        // 4. 清理移动导航覆盖层
        const mobileOverlays = document.querySelectorAll('.mobile-nav-overlay, .mobile-search-overlay');
        mobileOverlays.forEach((overlay, index) => {
            console.log(`🗑️ 移除移动端覆盖层 ${index + 1}`);
            overlay.remove();
        });
        
        // 5. 清理任何具有高z-index的全屏覆盖层
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const zIndex = parseInt(computedStyle.zIndex);
            const position = computedStyle.position;
            
            // 检查是否为阻塞性覆盖层
            if (zIndex > 9999 && 
                (position === 'fixed' || position === 'absolute') &&
                element.offsetWidth >= window.innerWidth * 0.8 &&
                element.offsetHeight >= window.innerHeight * 0.8) {
                
                console.log('🗑️ 移除可疑的全屏覆盖层:', element.id || element.className);
                element.style.display = 'none';
                element.remove();
            }
        });
        
        // 6. 重置body样式，确保可以滚动和交互
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');
        
        // 7. 移除任何阻止交互的样式
        document.documentElement.style.pointerEvents = '';
        document.body.style.pointerEvents = '';
        
        console.log('✅ 覆盖层清理完成，页面应该可以正常交互了');
    }
    
    // 立即执行清理
    forceCleanupOverlays();
    
    // DOM加载完成后再次执行清理（防止延迟加载的覆盖层）
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceCleanupOverlays);
    }
    
    // 页面完全加载后执行最终清理
    window.addEventListener('load', function() {
        setTimeout(forceCleanupOverlays, 1000);
    });
    
    // 提供手动清理函数给控制台使用
    window.forceCleanupOverlays = forceCleanupOverlays;
    
    // 监听并阻止新的阻塞性覆盖层创建
    const originalAppendChild = Element.prototype.appendChild;
    Element.prototype.appendChild = function(child) {
        // 检查是否为可能的阻塞覆盖层
        if (child.nodeType === Node.ELEMENT_NODE) {
            const style = child.style;
            if (style && 
                (style.position === 'fixed' || style.position === 'absolute') &&
                (style.zIndex > 9999 || parseInt(style.zIndex) > 9999) &&
                (style.width === '100%' || style.width === '100vw') &&
                (style.height === '100%' || style.height === '100vh')) {
                
                console.warn('🚫 阻止创建可能阻塞交互的覆盖层:', child);
                return child;
            }
        }
        
        return originalAppendChild.call(this, child);
    };
    
})();

console.log('🛠️ 覆盖层清理修复脚本已加载');