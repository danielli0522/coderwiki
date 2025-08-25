/**
 * CoderWiki 响应式导航系统
 * 提供移动设备友好的导航体验
 */

class ResponsiveNavigation {
    constructor() {
        this.breakpoints = {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400
        };
        
        this.currentBreakpoint = this.getCurrentBreakpoint();
        this.isMenuOpen = false;
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.createMobileMenuToggle();
        this.enhanceNavigation();
        this.setupSwipeGestures();
        this.setupResizeHandler();
        this.setupKeyboardNavigation();
        this.setupMobileSearch();
        this.initBreadcrumbs();
        this.setupScrollingHeader();
        
        this.isInitialized = true;
        console.log('Responsive navigation initialized');
    }
    
    // 获取当前断点
    getCurrentBreakpoint() {
        const width = window.innerWidth;
        
        if (width >= this.breakpoints.xxl) return 'xxl';
        if (width >= this.breakpoints.xl) return 'xl';
        if (width >= this.breakpoints.lg) return 'lg';
        if (width >= this.breakpoints.md) return 'md';
        if (width >= this.breakpoints.sm) return 'sm';
        return 'xs';
    }
    
    // 创建移动菜单切换按钮
    createMobileMenuToggle() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        // 检查是否已有切换按钮
        let existingToggle = navbar.querySelector('.mobile-menu-toggle');
        if (existingToggle) {
            existingToggle.remove();
        }
        
        // 创建新的切换按钮
        const toggle = document.createElement('button');
        toggle.className = 'mobile-menu-toggle btn btn-outline-light d-lg-none';
        toggle.setAttribute('type', 'button');
        toggle.setAttribute('aria-label', '切换导航菜单');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-controls', 'navbarNav');
        
        toggle.innerHTML = `
            <span class="hamburger">
                <span class="hamburger-line"></span>
                <span class="hamburger-line"></span>
                <span class="hamburger-line"></span>
            </span>
        `;
        
        // 插入到navbar-brand之后
        const brand = navbar.querySelector('.navbar-brand');
        if (brand) {
            brand.insertAdjacentElement('afterend', toggle);
        } else {
            navbar.insertAdjacentElement('afterbegin', toggle);
        }
        
        // 绑定点击事件
        toggle.addEventListener('click', () => {
            this.toggleMobileMenu();
        });
    }
    
    // 增强导航功能
    enhanceNavigation() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        // 添加响应式类
        navbar.classList.add('navbar-responsive');
        
        // 增强导航项
        const navItems = navbar.querySelectorAll('.nav-item');
        navItems.forEach((item, index) => {
            this.enhanceNavItem(item, index);
        });
        
        // 添加导航背景
        this.addNavigationBackground();
        
        // 设置移动端导航样式
        this.setupMobileNavStyles();
    }
    
    // 增强导航项
    enhanceNavItem(item, index) {
        const link = item.querySelector('.nav-link');
        if (!link) return;
        
        // 添加动画延迟
        item.style.setProperty('--nav-item-delay', `${index * 0.1}s`);
        
        // 添加触摸友好的类
        link.classList.add('touch-friendly');
        
        // 为下拉菜单添加特殊处理
        const dropdown = item.querySelector('.dropdown-menu');
        if (dropdown) {
            this.enhanceDropdown(item, dropdown);
        }
        
        // 添加活动状态指示器
        this.addActiveIndicator(item, link);
    }
    
    // 增强下拉菜单
    enhanceDropdown(item, dropdown) {
        const toggle = item.querySelector('.dropdown-toggle');
        if (!toggle) return;
        
        // 移动端点击行为
        toggle.addEventListener('click', (e) => {
            if (this.currentBreakpoint === 'xs' || this.currentBreakpoint === 'sm') {
                e.preventDefault();
                this.toggleMobileDropdown(item, dropdown);
            }
        });
        
        // 添加下拉箭头
        if (!toggle.querySelector('.dropdown-arrow')) {
            const arrow = document.createElement('i');
            arrow.className = 'fas fa-chevron-down dropdown-arrow ms-1';
            toggle.appendChild(arrow);
        }
    }
    
    // 切换移动端下拉菜单
    toggleMobileDropdown(item, dropdown) {
        const isOpen = dropdown.classList.contains('show');
        const arrow = item.querySelector('.dropdown-arrow');
        
        // 关闭其他下拉菜单
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            if (menu !== dropdown) {
                menu.classList.remove('show');
                menu.previousElementSibling.querySelector('.dropdown-arrow')?.classList.remove('rotated');
            }
        });
        
        if (isOpen) {
            dropdown.classList.remove('show');
            arrow?.classList.remove('rotated');
        } else {
            dropdown.classList.add('show');
            arrow?.classList.add('rotated');
        }
    }
    
    // 添加活动状态指示器
    addActiveIndicator(item, link) {
        if (link.classList.contains('active')) {
            const indicator = document.createElement('div');
            indicator.className = 'nav-active-indicator';
            item.appendChild(indicator);
        }
    }
    
    // 添加导航背景
    addNavigationBackground() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        const background = document.createElement('div');
        background.className = 'navbar-background';
        navbar.insertAdjacentElement('afterbegin', background);
    }
    
    // 设置移动端导航样式
    setupMobileNavStyles() {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (!navbarCollapse) return;
        
        navbarCollapse.classList.add('mobile-nav-menu');
        
        // 添加移动端覆盖层
        const overlay = document.createElement('div');
        overlay.className = 'mobile-nav-overlay';
        overlay.addEventListener('click', () => {
            this.closeMobileMenu();
        });
        document.body.appendChild(overlay);
    }
    
    // 切换移动菜单
    toggleMobileMenu() {
        const navbar = document.querySelector('.navbar');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const toggle = navbar?.querySelector('.mobile-menu-toggle');
        const overlay = document.querySelector('.mobile-nav-overlay');
        
        if (!navbarCollapse || !toggle) return;
        
        this.isMenuOpen = !this.isMenuOpen;
        
        // 更新ARIA属性
        toggle.setAttribute('aria-expanded', this.isMenuOpen.toString());
        
        if (this.isMenuOpen) {
            this.openMobileMenu(navbarCollapse, toggle, overlay);
        } else {
            this.closeMobileMenu(navbarCollapse, toggle, overlay);
        }
    }
    
    // 打开移动菜单
    openMobileMenu(navbarCollapse, toggle, overlay) {
        document.body.classList.add('mobile-menu-open');
        navbarCollapse.classList.add('show', 'mobile-menu-active');
        toggle.classList.add('active');
        overlay?.classList.add('show');
        
        // 禁用背景滚动
        document.body.style.overflow = 'hidden';
        
        // 聚焦到第一个导航链接
        const firstLink = navbarCollapse.querySelector('.nav-link');
        if (firstLink) {
            setTimeout(() => firstLink.focus(), 300);
        }
        
        // 通知屏幕阅读器
        if (window.accessibilityManager) {
            window.accessibilityManager.announce('导航菜单已打开');
        }
    }
    
    // 关闭移动菜单
    closeMobileMenu(navbarCollapse, toggle, overlay) {
        document.body.classList.remove('mobile-menu-open');
        navbarCollapse?.classList.remove('show', 'mobile-menu-active');
        toggle?.classList.remove('active');
        overlay?.classList.remove('show');
        
        // 恢复背景滚动
        document.body.style.overflow = '';
        
        // 关闭所有下拉菜单
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
            menu.previousElementSibling.querySelector('.dropdown-arrow')?.classList.remove('rotated');
        });
        
        // 通知屏幕阅读器
        if (window.accessibilityManager) {
            window.accessibilityManager.announce('导航菜单已关闭');
        }
    }
    
    // 设置滑动手势
    setupSwipeGestures() {
        if (!('ontouchstart' in window)) return;
        
        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        });
        
        document.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipeGesture();
        });
    }
    
    // 处理滑动手势
    handleSwipeGesture() {
        const swipeThreshold = 100;
        const swipeDistance = this.touchEndX - this.touchStartX;
        
        // 从左边缘向右滑动打开菜单
        if (swipeDistance > swipeThreshold && this.touchStartX < 50 && !this.isMenuOpen) {
            if (this.currentBreakpoint === 'xs' || this.currentBreakpoint === 'sm') {
                this.toggleMobileMenu();
            }
        }
        
        // 向左滑动关闭菜单
        if (swipeDistance < -swipeThreshold && this.isMenuOpen) {
            this.closeMobileMenu();
        }
    }
    
    // 设置窗口大小改变处理
    setupResizeHandler() {
        let resizeTimer;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    }
    
    // 处理窗口大小改变
    handleResize() {
        const newBreakpoint = this.getCurrentBreakpoint();
        
        if (newBreakpoint !== this.currentBreakpoint) {
            this.currentBreakpoint = newBreakpoint;
            
            // 在大屏幕上自动关闭移动菜单
            if (newBreakpoint === 'lg' || newBreakpoint === 'xl' || newBreakpoint === 'xxl') {
                if (this.isMenuOpen) {
                    this.isMenuOpen = false;
                    this.closeMobileMenu();
                }
            }
            
            // 更新导航样式
            this.updateNavigationForBreakpoint();
        }
    }
    
    // 根据断点更新导航
    updateNavigationForBreakpoint() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        // 移除旧的断点类
        Object.keys(this.breakpoints).forEach(bp => {
            navbar.classList.remove(`navbar-${bp}`);
        });
        
        // 添加新的断点类
        navbar.classList.add(`navbar-${this.currentBreakpoint}`);
    }
    
    // 设置键盘导航
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMenuOpen) {
                this.closeMobileMenu();
                
                // 将焦点返回到切换按钮
                const toggle = document.querySelector('.mobile-menu-toggle');
                if (toggle) {
                    toggle.focus();
                }
            }
            
            // Alt + M 切换菜单
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                if (this.currentBreakpoint === 'xs' || this.currentBreakpoint === 'sm') {
                    this.toggleMobileMenu();
                }
            }
        });
        
        // 导航项键盘导航
        this.setupNavItemKeyboardNavigation();
    }
    
    // 设置导航项键盘导航
    setupNavItemKeyboardNavigation() {
        const navItems = document.querySelectorAll('.nav-item .nav-link');
        
        navItems.forEach((link, index) => {
            link.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                    e.preventDefault();
                    const nextIndex = (index + 1) % navItems.length;
                    navItems[nextIndex].focus();
                }
                
                if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prevIndex = index === 0 ? navItems.length - 1 : index - 1;
                    navItems[prevIndex].focus();
                }
                
                if (e.key === 'Home') {
                    e.preventDefault();
                    navItems[0].focus();
                }
                
                if (e.key === 'End') {
                    e.preventDefault();
                    navItems[navItems.length - 1].focus();
                }
            });
        });
    }
    
    // 设置移动端搜索
    setupMobileSearch() {
        this.createMobileSearch();
        this.setupSearchToggle();
    }
    
    // 创建移动端搜索
    createMobileSearch() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        const searchToggle = document.createElement('button');
        searchToggle.className = 'mobile-search-toggle btn btn-outline-light d-lg-none me-2';
        searchToggle.setAttribute('type', 'button');
        searchToggle.setAttribute('aria-label', '打开搜索');
        searchToggle.innerHTML = '<i class="fas fa-search"></i>';
        
        // 插入到菜单切换按钮之前
        const menuToggle = navbar.querySelector('.mobile-menu-toggle');
        if (menuToggle) {
            menuToggle.insertAdjacentElement('beforebegin', searchToggle);
        }
        
        // 创建移动端搜索面板
        this.createMobileSearchPanel();
    }
    
    // 创建移动端搜索面板
    createMobileSearchPanel() {
        const searchPanel = document.createElement('div');
        searchPanel.className = 'mobile-search-panel';
        searchPanel.innerHTML = `
            <div class="mobile-search-header">
                <h5 class="mobile-search-title">搜索</h5>
                <button type="button" class="btn-close mobile-search-close" aria-label="关闭搜索"></button>
            </div>
            <div class="mobile-search-body">
                <form class="mobile-search-form">
                    <div class="input-group">
                        <input type="search" class="form-control form-control-lg" placeholder="搜索..." aria-label="搜索">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </form>
                <div class="mobile-search-suggestions">
                    <!-- 搜索建议将在这里显示 -->
                </div>
            </div>
        `;
        
        document.body.appendChild(searchPanel);
        
        // 创建搜索覆盖层
        const overlay = document.createElement('div');
        overlay.className = 'mobile-search-overlay';
        document.body.appendChild(overlay);
    }
    
    // 设置搜索切换
    setupSearchToggle() {
        const searchToggle = document.querySelector('.mobile-search-toggle');
        const searchPanel = document.querySelector('.mobile-search-panel');
        const searchClose = document.querySelector('.mobile-search-close');
        const searchOverlay = document.querySelector('.mobile-search-overlay');
        
        if (!searchToggle || !searchPanel) return;
        
        // 打开搜索
        searchToggle.addEventListener('click', () => {
            this.openMobileSearch();
        });
        
        // 关闭搜索
        searchClose?.addEventListener('click', () => {
            this.closeMobileSearch();
        });
        
        searchOverlay?.addEventListener('click', () => {
            this.closeMobileSearch();
        });
        
        // ESC 键关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchPanel.classList.contains('show')) {
                this.closeMobileSearch();
            }
        });
    }
    
    // 打开移动端搜索
    openMobileSearch() {
        const searchPanel = document.querySelector('.mobile-search-panel');
        const searchOverlay = document.querySelector('.mobile-search-overlay');
        const searchInput = searchPanel?.querySelector('input[type="search"]');
        
        if (!searchPanel) return;
        
        searchPanel.classList.add('show');
        searchOverlay?.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // 聚焦到搜索输入框
        setTimeout(() => {
            searchInput?.focus();
        }, 300);
        
        if (window.accessibilityManager) {
            window.accessibilityManager.announce('搜索面板已打开');
        }
    }
    
    // 关闭移动端搜索
    closeMobileSearch() {
        const searchPanel = document.querySelector('.mobile-search-panel');
        const searchOverlay = document.querySelector('.mobile-search-overlay');
        
        if (!searchPanel) return;
        
        searchPanel.classList.remove('show');
        searchOverlay?.classList.remove('show');
        document.body.style.overflow = '';
        
        if (window.accessibilityManager) {
            window.accessibilityManager.announce('搜索面板已关闭');
        }
    }
    
    // 初始化面包屑导航
    initBreadcrumbs() {
        this.createBreadcrumbs();
        this.updateBreadcrumbs();
    }
    
    // 创建面包屑导航
    createBreadcrumbs() {
        const main = document.querySelector('main');
        if (!main) return;
        
        const breadcrumbContainer = document.createElement('nav');
        breadcrumbContainer.className = 'breadcrumb-container';
        breadcrumbContainer.setAttribute('aria-label', '面包屑导航');
        
        breadcrumbContainer.innerHTML = `
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="/" class="breadcrumb-link">
                        <i class="fas fa-home" aria-hidden="true"></i>
                        <span class="sr-only">首页</span>
                    </a>
                </li>
            </ol>
        `;
        
        main.insertAdjacentElement('afterbegin', breadcrumbContainer);
    }
    
    // 更新面包屑导航
    updateBreadcrumbs() {
        const breadcrumb = document.querySelector('.breadcrumb');
        if (!breadcrumb) return;
        
        const path = window.location.pathname;
        const pathSegments = path.split('/').filter(segment => segment);
        
        // 清除现有的面包屑项（除了首页）
        const existingItems = breadcrumb.querySelectorAll('.breadcrumb-item:not(:first-child)');
        existingItems.forEach(item => item.remove());
        
        // 添加路径段
        pathSegments.forEach((segment, index) => {
            const item = document.createElement('li');
            item.className = 'breadcrumb-item';
            
            const isLast = index === pathSegments.length - 1;
            const href = '/' + pathSegments.slice(0, index + 1).join('/');
            const text = this.formatBreadcrumbText(segment);
            
            if (isLast) {
                item.className += ' active';
                item.setAttribute('aria-current', 'page');
                item.textContent = text;
            } else {
                item.innerHTML = `<a href="${href}" class="breadcrumb-link">${text}</a>`;
            }
            
            breadcrumb.appendChild(item);
        });
    }
    
    // 格式化面包屑文本
    formatBreadcrumbText(segment) {
        const textMap = {
            'dashboard': '仪表板',
            'repositories': '仓库管理',
            'documents': '文档管理',
            'analysis': '代码分析',
            'tasks': '任务管理',
            'settings': '系统设置',
            'profile': '个人设置'
        };
        
        return textMap[segment] || segment.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // 设置滚动头部
    setupScrollingHeader() {
        let lastScrollY = window.scrollY;
        let ticking = false;
        
        const updateHeader = () => {
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;
            
            const scrollY = window.scrollY;
            const scrollDirection = scrollY > lastScrollY ? 'down' : 'up';
            
            if (scrollY > 100) {
                navbar.classList.add('navbar-scrolled');
                
                if (scrollDirection === 'down' && scrollY > lastScrollY + 10) {
                    navbar.classList.add('navbar-hidden');
                } else if (scrollDirection === 'up') {
                    navbar.classList.remove('navbar-hidden');
                }
            } else {
                navbar.classList.remove('navbar-scrolled', 'navbar-hidden');
            }
            
            lastScrollY = scrollY;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        });
    }
    
    // 公共API方法
    openMenu() {
        if (!this.isMenuOpen) {
            this.toggleMobileMenu();
        }
    }
    
    closeMenu() {
        if (this.isMenuOpen) {
            this.toggleMobileMenu();
        }
    }
    
    isMenuOpen() {
        return this.isMenuOpen;
    }
    
    getCurrentBreakpoint() {
        return this.currentBreakpoint;
    }
}

// 创建全局实例
const responsiveNavigation = new ResponsiveNavigation();

// 导出到全局
window.ResponsiveNavigation = ResponsiveNavigation;
window.responsiveNavigation = responsiveNavigation;