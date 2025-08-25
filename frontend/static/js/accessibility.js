/**
 * CoderWiki 可访问性增强 JavaScript 模块
 * 提供键盘导航、屏幕阅读器支持和焦点管理
 */

class AccessibilityManager {
    constructor() {
        this.currentFocusIndex = -1;
        this.focusableElements = [];
        this.announceRegion = null;
        this.focusTrap = null;
        this.preferences = this.loadPreferences();
        
        this.init();
    }
    
    init() {
        this.createLiveRegions();
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupSkipLinks();
        this.detectFocusVisible();
        this.setupModalAccessibility();
        this.setupTableAccessibility();
        this.setupFormAccessibility();
        this.applyUserPreferences();
        
        console.log('AccessibilityManager initialized');
    }
    
    // 创建 ARIA Live Regions
    createLiveRegions() {
        // 状态更新区域
        const statusRegion = document.createElement('div');
        statusRegion.id = 'status-region';
        statusRegion.className = 'live-region';
        statusRegion.setAttribute('aria-live', 'polite');
        statusRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(statusRegion);
        
        // 错误消息区域
        const errorRegion = document.createElement('div');
        errorRegion.id = 'error-region';
        errorRegion.className = 'live-region';
        errorRegion.setAttribute('aria-live', 'assertive');
        errorRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(errorRegion);
        
        // 进度更新区域
        const progressRegion = document.createElement('div');
        progressRegion.id = 'progress-region';
        progressRegion.className = 'live-region';
        progressRegion.setAttribute('aria-live', 'polite');
        progressRegion.setAttribute('aria-atomic', 'false');
        document.body.appendChild(progressRegion);
        
        this.announceRegion = statusRegion;
    }
    
    // 语音播报消息
    announce(message, priority = 'polite') {
        const region = priority === 'assertive' ? 
            document.getElementById('error-region') : 
            document.getElementById('status-region');
            
        if (region) {
            region.textContent = '';
            setTimeout(() => {
                region.textContent = message;
            }, 100);
        }
        
        console.log(`Announced (${priority}): ${message}`);
    }
    
    // 设置键盘导航
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // ESC 键关闭模态框
            if (e.key === 'Escape') {
                this.handleEscapeKey(e);
            }
            
            // Tab 键焦点管理
            if (e.key === 'Tab') {
                this.handleTabKey(e);
            }
            
            // 方向键导航
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                this.handleArrowKeys(e);
            }
            
            // Enter 键激活
            if (e.key === 'Enter') {
                this.handleEnterKey(e);
            }
            
            // Space 键激活
            if (e.key === ' ') {
                this.handleSpaceKey(e);
            }
        });
        
        // 为可交互的卡片添加键盘支持
        document.querySelectorAll('.card.interactive').forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
        });
    }
    
    // 处理 ESC 键
    handleEscapeKey(e) {
        // 关闭打开的模态框
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const bsModal = bootstrap.Modal.getInstance(openModal);
            if (bsModal) {
                bsModal.hide();
            }
            return;
        }
        
        // 关闭打开的下拉菜单
        const openDropdown = document.querySelector('.dropdown-menu.show');
        if (openDropdown) {
            const bsDropdown = bootstrap.Dropdown.getInstance(openDropdown.parentElement.querySelector('[data-bs-toggle="dropdown"]'));
            if (bsDropdown) {
                bsDropdown.hide();
            }
            return;
        }
        
        // 清除搜索
        const searchInput = document.querySelector('input[type="search"]:focus');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            return;
        }
    }
    
    // 处理 Tab 键
    handleTabKey(e) {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            this.trapFocusInModal(e, modal);
        }
    }
    
    // 在模态框中捕获焦点
    trapFocusInModal(e, modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const focusableArray = Array.from(focusableElements);
        const firstElement = focusableArray[0];
        const lastElement = focusableArray[focusableArray.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
    
    // 处理方向键
    handleArrowKeys(e) {
        const target = e.target;
        
        // 在表格中导航
        if (target.tagName === 'TD' || target.tagName === 'TH') {
            this.navigateTable(e, target);
        }
        
        // 在网格布局中导航
        if (target.closest('.grid-navigation')) {
            this.navigateGrid(e, target);
        }
        
        // 在列表中导航
        if (target.closest('.list-group')) {
            this.navigateList(e, target);
        }
    }
    
    // 表格导航
    navigateTable(e, cell) {
        e.preventDefault();
        const table = cell.closest('table');
        const rows = Array.from(table.querySelectorAll('tr'));
        const currentRow = cell.closest('tr');
        const currentRowIndex = rows.indexOf(currentRow);
        const cells = Array.from(currentRow.querySelectorAll('td, th'));
        const currentCellIndex = cells.indexOf(cell);
        
        let targetCell;
        
        switch (e.key) {
            case 'ArrowUp':
                if (currentRowIndex > 0) {
                    const targetRow = rows[currentRowIndex - 1];
                    const targetCells = targetRow.querySelectorAll('td, th');
                    targetCell = targetCells[Math.min(currentCellIndex, targetCells.length - 1)];
                }
                break;
            case 'ArrowDown':
                if (currentRowIndex < rows.length - 1) {
                    const targetRow = rows[currentRowIndex + 1];
                    const targetCells = targetRow.querySelectorAll('td, th');
                    targetCell = targetCells[Math.min(currentCellIndex, targetCells.length - 1)];
                }
                break;
            case 'ArrowLeft':
                if (currentCellIndex > 0) {
                    targetCell = cells[currentCellIndex - 1];
                }
                break;
            case 'ArrowRight':
                if (currentCellIndex < cells.length - 1) {
                    targetCell = cells[currentCellIndex + 1];
                }
                break;
        }
        
        if (targetCell) {
            targetCell.focus();
        }
    }
    
    // 处理 Enter 键
    handleEnterKey(e) {
        const target = e.target;
        
        // 激活可点击元素
        if (target.getAttribute('role') === 'button' && !target.matches('button, a, input')) {
            e.preventDefault();
            target.click();
        }
    }
    
    // 处理空格键
    handleSpaceKey(e) {
        const target = e.target;
        
        // 激活按钮角色的元素
        if (target.getAttribute('role') === 'button' && !target.matches('button, input')) {
            e.preventDefault();
            target.click();
        }
    }
    
    // 焦点管理
    setupFocusManagement() {
        // 记录上一个聚焦的元素
        let lastFocusedElement = null;
        
        document.addEventListener('focusin', (e) => {
            lastFocusedElement = e.target;
        });
        
        // 模态框显示时管理焦点
        document.addEventListener('shown.bs.modal', (e) => {
            const modal = e.target;
            const firstFocusable = modal.querySelector(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            if (firstFocusable) {
                firstFocusable.focus();
            }
        });
        
        // 模态框隐藏时恢复焦点
        document.addEventListener('hidden.bs.modal', (e) => {
            if (lastFocusedElement && lastFocusedElement !== e.target) {
                lastFocusedElement.focus();
            }
        });
    }
    
    // 设置跳转链接
    setupSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-navigation';
        skipLink.textContent = '跳转到主要内容';
        
        // 在body开头插入跳转链接
        document.body.insertAdjacentElement('afterbegin', skipLink);
        
        // 确保主要内容区域有ID
        const mainContent = document.querySelector('main') || 
                           document.querySelector('[role="main"]') ||
                           document.querySelector('#main-content');
        
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }
        
        // 添加标志性区域的跳转链接
        this.addLandmarkSkipLinks();
    }
    
    // 添加标志性区域跳转链接
    addLandmarkSkipLinks() {
        const landmarks = [
            { selector: 'nav, [role="navigation"]', text: '跳转到导航' },
            { selector: '.search, [role="search"]', text: '跳转到搜索' },
            { selector: 'aside, [role="complementary"]', text: '跳转到侧边栏' },
            { selector: 'footer, [role="contentinfo"]', text: '跳转到页脚' }
        ];
        
        landmarks.forEach((landmark, index) => {
            const element = document.querySelector(landmark.selector);
            if (element) {
                const skipId = `skip-to-${index}`;
                if (!element.id) {
                    element.id = skipId;
                }
                
                const skipLink = document.createElement('a');
                skipLink.href = `#${element.id}`;
                skipLink.className = 'skip-navigation';
                skipLink.textContent = landmark.text;
                
                document.body.insertAdjacentElement('afterbegin', skipLink);
            }
        });
    }
    
    // 检测和应用 focus-visible
    detectFocusVisible() {
        let hadKeyboardEvent = true;
        const keyboardThrottleTimeout = 100;
        
        const pointerTypes = ['mouse', 'pointer', 'touch'];
        
        function onPointerDown(e) {
            hadKeyboardEvent = false;
        }
        
        function onKeyDown(e) {
            if (e.metaKey || e.altKey || e.ctrlKey) {
                return;
            }
            hadKeyboardEvent = true;
        }
        
        function onFocus(e) {
            if (hadKeyboardEvent || e.target.matches(':focus-visible')) {
                e.target.classList.add('focus-visible');
            }
        }
        
        function onBlur(e) {
            e.target.classList.remove('focus-visible');
        }
        
        document.addEventListener('keydown', onKeyDown, true);
        document.addEventListener('mousedown', onPointerDown, true);
        document.addEventListener('pointerdown', onPointerDown, true);
        document.addEventListener('touchstart', onPointerDown, true);
        document.addEventListener('focus', onFocus, true);
        document.addEventListener('blur', onBlur, true);
        
        document.body.classList.add('js-focus-visible');
    }
    
    // 模态框可访问性
    setupModalAccessibility() {
        // 为模态框添加适当的ARIA属性
        document.querySelectorAll('.modal').forEach(modal => {
            const modalTitle = modal.querySelector('.modal-title');
            if (modalTitle && !modal.hasAttribute('aria-labelledby')) {
                if (!modalTitle.id) {
                    modalTitle.id = `modal-title-${Date.now()}`;
                }
                modal.setAttribute('aria-labelledby', modalTitle.id);
            }
            
            if (!modal.hasAttribute('aria-hidden')) {
                modal.setAttribute('aria-hidden', 'true');
            }
        });
        
        // 监听模态框状态变化
        document.addEventListener('show.bs.modal', (e) => {
            e.target.setAttribute('aria-hidden', 'false');
            this.announce('对话框已打开');
        });
        
        document.addEventListener('hide.bs.modal', (e) => {
            e.target.setAttribute('aria-hidden', 'true');
            this.announce('对话框已关闭');
        });
    }
    
    // 表格可访问性
    setupTableAccessibility() {
        document.querySelectorAll('table').forEach(table => {
            // 添加标题
            if (!table.querySelector('caption') && table.dataset.caption) {
                const caption = document.createElement('caption');
                caption.textContent = table.dataset.caption;
                table.insertAdjacentElement('afterbegin', caption);
            }
            
            // 为表头添加scope属性
            table.querySelectorAll('th').forEach(th => {
                if (!th.hasAttribute('scope')) {
                    const isRowHeader = th.parentElement.querySelector('th') === th;
                    th.setAttribute('scope', isRowHeader ? 'row' : 'col');
                }
            });
            
            // 可排序表格
            table.querySelectorAll('th.sortable').forEach(th => {
                th.setAttribute('tabindex', '0');
                th.setAttribute('role', 'button');
                th.setAttribute('aria-sort', 'none');
                
                th.addEventListener('click', () => {
                    this.handleTableSort(th);
                });
                
                th.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        th.click();
                    }
                });
            });
        });
    }
    
    // 处理表格排序
    handleTableSort(th) {
        const table = th.closest('table');
        const column = Array.from(th.parentElement.children).indexOf(th);
        const currentSort = th.getAttribute('aria-sort');
        
        // 重置其他列的排序状态
        table.querySelectorAll('th').forEach(header => {
            header.setAttribute('aria-sort', 'none');
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        // 设置当前列的排序状态
        let newSort;
        if (currentSort === 'none' || currentSort === 'descending') {
            newSort = 'ascending';
            th.classList.add('sort-asc');
        } else {
            newSort = 'descending';
            th.classList.add('sort-desc');
        }
        
        th.setAttribute('aria-sort', newSort);
        
        this.announce(`表格按第${column + 1}列${newSort === 'ascending' ? '升序' : '降序'}排序`);
    }
    
    // 表单可访问性
    setupFormAccessibility() {
        // 为所有表单控件添加适当的标签关联
        document.querySelectorAll('input, select, textarea').forEach(control => {
            const label = document.querySelector(`label[for="${control.id}"]`) ||
                         control.closest('.form-group')?.querySelector('label') ||
                         control.parentElement?.querySelector('label');
            
            if (label && !control.hasAttribute('aria-labelledby')) {
                if (!label.id) {
                    label.id = `label-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                }
                control.setAttribute('aria-labelledby', label.id);
            }
            
            // 为必填字段添加aria-required
            if (control.hasAttribute('required') && !control.hasAttribute('aria-required')) {
                control.setAttribute('aria-required', 'true');
            }
        });
        
        // 表单验证反馈
        document.addEventListener('invalid', (e) => {
            const control = e.target;
            const message = control.validationMessage;
            this.announce(`表单验证错误: ${message}`, 'assertive');
        }, true);
    }
    
    // 加载用户偏好设置
    loadPreferences() {
        const preferences = localStorage.getItem('accessibility-preferences');
        return preferences ? JSON.parse(preferences) : {
            reducedMotion: false,
            highContrast: false,
            fontSize: 'normal'
        };
    }
    
    // 保存用户偏好设置
    savePreferences() {
        localStorage.setItem('accessibility-preferences', JSON.stringify(this.preferences));
    }
    
    // 应用用户偏好设置
    applyUserPreferences() {
        if (this.preferences.reducedMotion) {
            document.body.classList.add('reduce-motion');
        }
        
        if (this.preferences.highContrast) {
            document.body.classList.add('high-contrast');
        }
        
        if (this.preferences.fontSize !== 'normal') {
            document.body.classList.add(`font-size-${this.preferences.fontSize}`);
        }
    }
    
    // 切换减少动效
    toggleReducedMotion() {
        this.preferences.reducedMotion = !this.preferences.reducedMotion;
        document.body.classList.toggle('reduce-motion', this.preferences.reducedMotion);
        this.savePreferences();
        this.announce(this.preferences.reducedMotion ? '已启用减少动效' : '已禁用减少动效');
    }
    
    // 切换高对比度
    toggleHighContrast() {
        this.preferences.highContrast = !this.preferences.highContrast;
        document.body.classList.toggle('high-contrast', this.preferences.highContrast);
        this.savePreferences();
        this.announce(this.preferences.highContrast ? '已启用高对比度' : '已禁用高对比度');
    }
    
    // 更改字体大小
    changeFontSize(size) {
        // 移除旧的字体大小类
        document.body.classList.remove('font-size-small', 'font-size-large', 'font-size-xlarge');
        
        if (size !== 'normal') {
            document.body.classList.add(`font-size-${size}`);
        }
        
        this.preferences.fontSize = size;
        this.savePreferences();
        this.announce(`字体大小已更改为${size}`);
    }
    
    // 创建可访问性控制面板
    createAccessibilityControls() {
        const panel = document.createElement('div');
        panel.className = 'accessibility-controls';
        panel.innerHTML = `
            <button class="btn btn-sm btn-outline-secondary" aria-label="可访问性设置" data-bs-toggle="modal" data-bs-target="#accessibilityModal">
                <i class="fas fa-universal-access" aria-hidden="true"></i>
            </button>
        `;
        
        // 在导航栏添加控制面板
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.appendChild(panel);
        }
        
        this.createAccessibilityModal();
    }
    
    // 创建可访问性设置模态框
    createAccessibilityModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'accessibilityModal';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-labelledby', 'accessibilityModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="accessibilityModalLabel">可访问性设置</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
                    </div>
                    <div class="modal-body">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="reducedMotionToggle" ${this.preferences.reducedMotion ? 'checked' : ''}>
                            <label class="form-check-label" for="reducedMotionToggle">
                                减少动画效果
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="highContrastToggle" ${this.preferences.highContrast ? 'checked' : ''}>
                            <label class="form-check-label" for="highContrastToggle">
                                高对比度模式
                            </label>
                        </div>
                        <div class="mb-3">
                            <label for="fontSizeSelect" class="form-label">字体大小</label>
                            <select class="form-select" id="fontSizeSelect">
                                <option value="small" ${this.preferences.fontSize === 'small' ? 'selected' : ''}>小</option>
                                <option value="normal" ${this.preferences.fontSize === 'normal' ? 'selected' : ''}>正常</option>
                                <option value="large" ${this.preferences.fontSize === 'large' ? 'selected' : ''}>大</option>
                                <option value="xlarge" ${this.preferences.fontSize === 'xlarge' ? 'selected' : ''}>特大</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 绑定事件
        modal.querySelector('#reducedMotionToggle').addEventListener('change', () => {
            this.toggleReducedMotion();
        });
        
        modal.querySelector('#highContrastToggle').addEventListener('change', () => {
            this.toggleHighContrast();
        });
        
        modal.querySelector('#fontSizeSelect').addEventListener('change', (e) => {
            this.changeFontSize(e.target.value);
        });
    }
}

// 初始化可访问性管理器
const accessibilityManager = new AccessibilityManager();

// 导出到全局
window.AccessibilityManager = AccessibilityManager;
window.accessibilityManager = accessibilityManager;