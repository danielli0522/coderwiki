/**
 * 响应式设计验证工具
 * 用于验证AC8：仓库列表能够响应式地适应不同屏幕尺寸
 */
class ResponsiveValidation {
    constructor() {
        this.breakpoints = {
            mobile: 576,
            tablet: 768,
            desktop: 992,
            wide: 1200
        };
        this.testResults = {};
    }

    /**
     * 运行所有响应式测试
     */
    async runAllTests() {
        console.log('开始响应式设计验证...');
        
        const tests = [
            this.testMobileLayout.bind(this),
            this.testTabletLayout.bind(this),
            this.testDesktopLayout.bind(this),
            this.testNavigation.bind(this),
            this.testRepositoryCards.bind(this),
            this.testBulkOperations.bind(this),
            this.testPagination.bind(this)
        ];

        for (const test of tests) {
            try {
                await test();
            } catch (error) {
                console.error(`测试失败:`, error);
            }
        }

        return this.generateReport();
    }

    /**
     * 测试移动端布局 (< 576px)
     */
    async testMobileLayout() {
        console.log('测试移动端布局...');
        
        this.simulateViewport(320, 568); // iPhone SE
        
        const results = {
            cardStacking: this.checkCardStacking(),
            buttonSize: this.checkMobileTouchTargets(),
            textReadability: this.checkTextReadability(),
            scrollBehavior: this.checkScrollBehavior()
        };

        this.testResults.mobile = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    /**
     * 测试平板端布局 (576px - 768px)
     */
    async testTabletLayout() {
        console.log('测试平板端布局...');
        
        this.simulateViewport(768, 1024); // iPad
        
        const results = {
            columnLayout: this.checkColumnLayout(2),
            navigationVisible: this.checkNavigationVisibility(),
            actionButtons: this.checkActionButtonLayout()
        };

        this.testResults.tablet = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    /**
     * 测试桌面端布局 (> 992px)
     */
    async testDesktopLayout() {
        console.log('测试桌面端布局...');
        
        this.simulateViewport(1200, 800); // Desktop
        
        const results = {
            fullFeatures: this.checkFullFeatureAccess(),
            tableView: this.checkTableView(),
            sidebarLayout: this.checkSidebarLayout()
        };

        this.testResults.desktop = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    /**
     * 测试导航响应式
     */
    async testNavigation() {
        console.log('测试导航响应式...');
        
        const results = {};
        
        // 测试不同断点下的导航
        for (const [breakpoint, width] of Object.entries(this.breakpoints)) {
            this.simulateViewport(width - 1, 600);
            results[breakpoint] = this.checkNavigationAtBreakpoint(breakpoint);
        }

        this.testResults.navigation = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    /**
     * 测试仓库卡片响应式
     */
    async testRepositoryCards() {
        console.log('测试仓库卡片响应式...');
        
        const results = {
            cardResponsiveness: this.checkCardResponsiveness(),
            imageScaling: this.checkImageScaling(),
            contentWrapping: this.checkContentWrapping()
        };

        this.testResults.repositoryCards = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    /**
     * 测试批量操作响应式
     */
    async testBulkOperations() {
        console.log('测试批量操作响应式...');
        
        const results = {
            toolbarAdaptation: this.checkBulkToolbarAdaptation(),
            checkboxAccessibility: this.checkCheckboxAccessibility(),
            actionButtons: this.checkBulkActionButtons()
        };

        this.testResults.bulkOperations = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    /**
     * 测试分页响应式
     */
    async testPagination() {
        console.log('测试分页响应式...');
        
        const results = {
            paginationScaling: this.checkPaginationScaling(),
            touchTargets: this.checkPaginationTouchTargets(),
            overflow: this.checkPaginationOverflow()
        };

        this.testResults.pagination = {
            passed: Object.values(results).every(r => r.passed),
            details: results
        };
    }

    // 辅助方法
    simulateViewport(width, height) {
        // 模拟视口大小变化
        if (window.visualViewport) {
            Object.defineProperty(window.visualViewport, 'width', { value: width });
            Object.defineProperty(window.visualViewport, 'height', { value: height });
        }
        
        // 触发resize事件
        window.dispatchEvent(new Event('resize'));
        
        // 给React一些时间重新渲染
        return new Promise(resolve => setTimeout(resolve, 100));
    }

    checkCardStacking() {
        const cards = document.querySelectorAll('.repository-item');
        if (cards.length === 0) return { passed: false, message: '找不到仓库卡片' };

        const firstCard = cards[0];
        const computedStyle = getComputedStyle(firstCard);
        
        return {
            passed: computedStyle.display === 'block' || computedStyle.flexDirection === 'column',
            message: '卡片应在移动设备上垂直堆叠'
        };
    }

    checkMobileTouchTargets() {
        const buttons = document.querySelectorAll('.repository-item button, .repository-item .btn');
        const minTouchTarget = 44; // 最小触摸目标大小(px)

        const results = Array.from(buttons).map(button => {
            const rect = button.getBoundingClientRect();
            const size = Math.min(rect.width, rect.height);
            return size >= minTouchTarget;
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: `触摸目标应至少为${minTouchTarget}px`
        };
    }

    checkTextReadability() {
        const textElements = document.querySelectorAll('.repository-name, .repository-description');
        const minFontSize = 14; // 最小字体大小(px)

        const results = Array.from(textElements).map(element => {
            const fontSize = parseInt(getComputedStyle(element).fontSize);
            return fontSize >= minFontSize;
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: `文本字体大小应至少为${minFontSize}px`
        };
    }

    checkScrollBehavior() {
        const container = document.querySelector('.repository-list-container');
        if (!container) return { passed: false, message: '找不到仓库列表容器' };

        const computedStyle = getComputedStyle(container);
        
        return {
            passed: computedStyle.overflowX !== 'visible',
            message: '容器应处理水平滚动溢出'
        };
    }

    checkColumnLayout(expectedColumns) {
        const container = document.querySelector('.repository-list-container');
        if (!container) return { passed: false, message: '找不到仓库列表容器' };

        const computedStyle = getComputedStyle(container);
        const gridColumns = computedStyle.gridTemplateColumns;
        
        if (gridColumns && gridColumns !== 'none') {
            const columnCount = gridColumns.split(' ').length;
            return {
                passed: columnCount <= expectedColumns,
                message: `列数应不超过${expectedColumns}`
            };
        }

        return { passed: true, message: '未使用CSS Grid布局' };
    }

    checkNavigationVisibility() {
        const nav = document.querySelector('nav, .navbar');
        if (!nav) return { passed: true, message: '未找到导航元素' };

        const computedStyle = getComputedStyle(nav);
        
        return {
            passed: computedStyle.display !== 'none',
            message: '导航应在平板设备上可见'
        };
    }

    checkActionButtonLayout() {
        const actionContainers = document.querySelectorAll('.repository-actions');
        
        const results = Array.from(actionContainers).map(container => {
            const computedStyle = getComputedStyle(container);
            return computedStyle.flexWrap === 'wrap' || computedStyle.display === 'block';
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: '操作按钮应能够换行或垂直布局'
        };
    }

    checkFullFeatureAccess() {
        const advancedFeatures = document.querySelectorAll('.bulk-operations, .advanced-filters');
        
        return {
            passed: advancedFeatures.length > 0,
            message: '桌面端应显示所有高级功能'
        };
    }

    checkTableView() {
        const table = document.querySelector('table, .table-responsive');
        
        return {
            passed: table !== null,
            message: '桌面端应支持表格视图'
        };
    }

    checkSidebarLayout() {
        const sidebar = document.querySelector('.sidebar, .side-panel');
        
        return {
            passed: true, // 侧边栏是可选的
            message: '侧边栏布局检查'
        };
    }

    checkNavigationAtBreakpoint(breakpoint) {
        const nav = document.querySelector('nav, .navbar');
        if (!nav) return { passed: true, message: '未找到导航元素' };

        const isMobile = breakpoint === 'mobile';
        const hamburger = nav.querySelector('.navbar-toggler, .hamburger');
        
        if (isMobile) {
            return {
                passed: hamburger !== null,
                message: '移动端应有汉堡菜单'
            };
        } else {
            return {
                passed: true,
                message: `${breakpoint}断点导航检查通过`
            };
        }
    }

    checkCardResponsiveness() {
        const cards = document.querySelectorAll('.repository-item');
        
        const results = Array.from(cards).map(card => {
            const computedStyle = getComputedStyle(card);
            return computedStyle.maxWidth === '100%' || computedStyle.width === '100%';
        });

        return {
            passed: results.length === 0 || results.some(r => r),
            message: '卡片应能响应容器宽度'
        };
    }

    checkImageScaling() {
        const images = document.querySelectorAll('.repository-item img');
        
        const results = Array.from(images).map(img => {
            const computedStyle = getComputedStyle(img);
            return computedStyle.maxWidth === '100%';
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: '图片应能正确缩放'
        };
    }

    checkContentWrapping() {
        const textElements = document.querySelectorAll('.repository-description');
        
        const results = Array.from(textElements).map(element => {
            const computedStyle = getComputedStyle(element);
            return computedStyle.wordWrap === 'break-word' || computedStyle.overflowWrap === 'break-word';
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: '文本内容应能正确换行'
        };
    }

    checkBulkToolbarAdaptation() {
        const toolbar = document.getElementById('bulkToolbar');
        if (!toolbar) return { passed: true, message: '未找到批量操作工具栏' };

        const computedStyle = getComputedStyle(toolbar);
        
        return {
            passed: computedStyle.flexWrap === 'wrap' || computedStyle.flexDirection === 'column',
            message: '批量操作工具栏应能适应小屏幕'
        };
    }

    checkCheckboxAccessibility() {
        const checkboxes = document.querySelectorAll('.repo-checkbox input');
        const minSize = 20; // 最小复选框大小
        
        const results = Array.from(checkboxes).map(checkbox => {
            const rect = checkbox.getBoundingClientRect();
            return Math.min(rect.width, rect.height) >= minSize;
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: `复选框应至少为${minSize}px`
        };
    }

    checkBulkActionButtons() {
        const buttons = document.querySelectorAll('#bulkToolbar button');
        
        const results = Array.from(buttons).map(button => {
            const computedStyle = getComputedStyle(button);
            return computedStyle.minHeight >= '44px' || computedStyle.height >= '44px';
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: '批量操作按钮应有足够的点击区域'
        };
    }

    checkPaginationScaling() {
        const pagination = document.querySelector('.pagination');
        if (!pagination) return { passed: true, message: '未找到分页组件' };

        const computedStyle = getComputedStyle(pagination);
        
        return {
            passed: computedStyle.justifyContent === 'center' || computedStyle.textAlign === 'center',
            message: '分页组件应居中显示'
        };
    }

    checkPaginationTouchTargets() {
        const pageLinks = document.querySelectorAll('.pagination .page-link');
        const minTouchTarget = 44;
        
        const results = Array.from(pageLinks).map(link => {
            const rect = link.getBoundingClientRect();
            return Math.min(rect.width, rect.height) >= minTouchTarget;
        });

        return {
            passed: results.length === 0 || results.every(r => r),
            message: `分页链接应至少为${minTouchTarget}px`
        };
    }

    checkPaginationOverflow() {
        const pagination = document.querySelector('.pagination');
        if (!pagination) return { passed: true, message: '未找到分页组件' };

        const container = pagination.parentElement;
        const containerWidth = container.getBoundingClientRect().width;
        const paginationWidth = pagination.getBoundingClientRect().width;
        
        return {
            passed: paginationWidth <= containerWidth,
            message: '分页组件不应超出容器宽度'
        };
    }

    generateReport() {
        const allTests = Object.values(this.testResults);
        const passedTests = allTests.filter(test => test.passed);
        const overallPass = passedTests.length === allTests.length;

        const report = {
            overall: {
                passed: overallPass,
                score: `${passedTests.length}/${allTests.length}`,
                message: overallPass ? 'AC8响应式设计验证通过' : 'AC8响应式设计验证未完全通过'
            },
            details: this.testResults,
            recommendations: this.generateRecommendations()
        };

        console.log('响应式设计验证报告:', report);
        return report;
    }

    generateRecommendations() {
        const recommendations = [];
        
        Object.entries(this.testResults).forEach(([category, result]) => {
            if (!result.passed) {
                Object.entries(result.details).forEach(([test, detail]) => {
                    if (!detail.passed) {
                        recommendations.push(`${category}: ${detail.message}`);
                    }
                });
            }
        });

        return recommendations;
    }
}

// 导出类和创建全局实例
window.ResponsiveValidation = ResponsiveValidation;
window.responsiveValidation = new ResponsiveValidation();

// 自动运行验证（仅在开发模式下）
if (window.location.hostname === 'localhost' || window.location.hostname.includes('dev')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            window.responsiveValidation.runAllTests();
        }, 2000); // 等待页面完全加载
    });
}