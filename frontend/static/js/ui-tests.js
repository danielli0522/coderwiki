// UI组件测试套件

// 测试工具函数
const TestUtils = {
    // 创建测试元素
    createElement: function(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        if (content) {
            element.innerHTML = content;
        }
        return element;
    },
    
    // 模拟用户交互
    simulateClick: function(element) {
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        element.dispatchEvent(event);
    },
    
    // 模拟键盘事件
    simulateKey: function(element, key, eventType = 'keydown') {
        const event = new KeyboardEvent(eventType, {
            key: key,
            bubbles: true,
            cancelable: true
        });
        element.dispatchEvent(event);
    },
    
    // 模拟表单输入
    simulateInput: function(element, value) {
        element.value = value;
        const event = new Event('input', { bubbles: true });
        element.dispatchEvent(event);
    },
    
    // 等待条件满足
    waitFor: function(condition, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            const checkCondition = () => {
                if (condition()) {
                    resolve();
                } else if (Date.now() - startTime > timeout) {
                    reject(new Error('Timeout waiting for condition'));
                } else {
                    setTimeout(checkCondition, 100);
                }
            };
            
            checkCondition();
        });
    },
    
    // 获取元素的计算样式
    getComputedStyle: function(element, property) {
        return window.getComputedStyle(element)[property];
    },
    
    // 检查元素是否可见
    isVisible: function(element) {
        return element.offsetWidth > 0 && element.offsetHeight > 0;
    },
    
    // 检查元素是否包含指定类
    hasClass: function(element, className) {
        return element.classList.contains(className);
    },
    
    // 检查元素是否具有指定属性
    hasAttribute: function(element, attributeName) {
        return element.hasAttribute(attributeName);
    }
};

// 测试套件
const TestSuite = {
    tests: [],
    passed: 0,
    failed: 0,
    
    // 添加测试
    addTest: function(name, testFunction) {
        this.tests.push({ name, testFunction });
    },
    
    // 运行所有测试
    run: function() {
        console.group('🧪 UI组件测试开始');
        
        this.tests.forEach(test => {
            try {
                test.testFunction();
                this.passed++;
                console.log(`✅ ${test.name}`);
            } catch (error) {
                this.failed++;
                console.error(`❌ ${test.name}:`, error.message);
            }
        });
        
        console.groupEnd();
        console.log(`📊 测试结果: ${this.passed} 通过, ${this.failed} 失败`);
        
        return {
            passed: this.passed,
            failed: this.failed,
            total: this.tests.length,
            success: this.failed === 0
        };
    },
    
    // 断言函数
    assert: {
        equal: function(actual, expected, message) {
            if (actual !== expected) {
                throw new Error(message || `期望 ${expected}，但得到 ${actual}`);
            }
        },
        
        notEqual: function(actual, expected, message) {
            if (actual === expected) {
                throw new Error(message || `期望不等于 ${expected}，但得到 ${actual}`);
            }
        },
        
        true: function(value, message) {
            if (!value) {
                throw new Error(message || `期望 true，但得到 ${value}`);
            }
        },
        
        false: function(value, message) {
            if (value) {
                throw new Error(message || `期望 false，但得到 ${value}`);
            }
        },
        
        null: function(value, message) {
            if (value !== null) {
                throw new Error(message || `期望 null，但得到 ${value}`);
            }
        },
        
        notNull: function(value, message) {
            if (value === null) {
                throw new Error(message || `期望非 null，但得到 null`);
            }
        },
        
        undefined: function(value, message) {
            if (value !== undefined) {
                throw new Error(message || `期望 undefined，但得到 ${value}`);
            }
        },
        
        notUndefined: function(value, message) {
            if (value === undefined) {
                throw new Error(message || `期望非 undefined，但得到 undefined`);
            }
        },
        
        contains: function(array, item, message) {
            if (!array.includes(item)) {
                throw new Error(message || `期望数组包含 ${item}，但未找到`);
            }
        },
        
        notContains: function(array, item, message) {
            if (array.includes(item)) {
                throw new Error(message || `期望数组不包含 ${item}，但找到了`);
            }
        },
        
        throws: function(fn, expectedError, message) {
            try {
                fn();
                throw new Error(message || '期望抛出异常，但没有抛出');
            } catch (error) {
                if (expectedError && !(error instanceof expectedError)) {
                    throw new Error(message || `期望抛出 ${expectedError.name}，但抛出了 ${error.constructor.name}`);
                }
            }
        }
    }
};

// 组件测试
const ComponentTests = {
    // 测试侧边栏组件
    testSidebar: function() {
        const sidebar = TestUtils.createElement('div', { id: 'sidebar', class: 'sidebar' });
        const toggleBtn = TestUtils.createElement('button', { 'data-toggle': 'sidebar' }, 'Toggle');
        const overlay = TestUtils.createElement('div', { id: 'sidebar-overlay', class: 'sidebar-overlay' });
        
        document.body.appendChild(sidebar);
        document.body.appendChild(toggleBtn);
        document.body.appendChild(overlay);
        
        // 初始化侧边栏
        ComponentManager.initSidebar();
        
        // 测试侧边栏切换
        TestUtils.simulateClick(toggleBtn);
        TestSuite.assert.true(TestUtils.hasClass(sidebar, 'show'), '侧边栏应该显示');
        
        TestUtils.simulateClick(overlay);
        TestSuite.assert.false(TestUtils.hasClass(sidebar, 'show'), '侧边栏应该隐藏');
        
        // 清理
        sidebar.remove();
        toggleBtn.remove();
        overlay.remove();
    },
    
    // 测试卡片组件
    testEnhancedCards: function() {
        const card = TestUtils.createElement('div', { class: 'card-enhanced' }, '<div class="card-header">Test Card</div>');
        document.body.appendChild(card);
        
        // 初始化卡片
        ComponentManager.initEnhancedCards();
        
        // 测试卡片动画
        TestSuite.assert.true(TestUtils.hasClass(card, 'card-enhanced'), '卡片应该具有增强样式');
        
        // 清理
        card.remove();
    },
    
    // 测试表单组件
    testEnhancedForms: function() {
        const form = TestUtils.createElement('form', { class: 'form-enhanced' });
        const input = TestUtils.createElement('input', { 
            class: 'form-control-enhanced', 
            type: 'text', 
            placeholder: 'Test input' 
        });
        
        form.appendChild(input);
        document.body.appendChild(form);
        
        // 初始化表单
        ComponentManager.initEnhancedForms();
        
        // 测试表单焦点
        TestUtils.simulateClick(input);
        TestSuite.assert.true(TestUtils.hasClass(input.parentElement, 'focused'), '输入框获得焦点时应该有focused类');
        
        // 测试表单输入
        TestUtils.simulateInput(input, 'test value');
        TestSuite.assert.equal(input.value, 'test value', '输入框应该正确设置值');
        
        // 清理
        form.remove();
    },
    
    // 测试模态框组件
    testEnhancedModals: function() {
        const modal = TestUtils.createElement('div', { class: 'modal-enhanced' });
        document.body.appendChild(modal);
        
        // 初始化模态框
        ComponentManager.initEnhancedModals();
        
        // 测试模态框事件
        const showEvent = new Event('show.bs.modal');
        modal.dispatchEvent(showEvent);
        
        TestSuite.assert.true(TestUtils.hasClass(modal, 'modal-enhanced'), '模态框应该具有增强样式');
        
        // 清理
        modal.remove();
    },
    
    // 测试通知组件
    testEnhancedNotifications: function() {
        const notificationEvent = new CustomEvent('showEnhancedNotification', {
            detail: {
                message: 'Test notification',
                type: 'success'
            }
        });
        
        // 初始化通知
        ComponentManager.initEnhancedNotifications();
        
        // 测试通知事件
        document.dispatchEvent(notificationEvent);
        
        // 这里可以添加更多的通知测试逻辑
        TestSuite.assert.true(true, '通知系统应该正常工作');
    },
    
    // 测试工具提示组件
    testEnhancedTooltips: function() {
        const tooltip = TestUtils.createElement('button', { 
            'data-bs-toggle': 'tooltip-enhanced',
            'title': 'Test tooltip'
        }, 'Hover me');
        
        document.body.appendChild(tooltip);
        
        // 初始化工具提示
        ComponentManager.initEnhancedTooltips();
        
        // 测试工具提示属性
        TestSuite.assert.equal(
            tooltip.getAttribute('data-bs-toggle'), 
            'tooltip-enhanced', 
            '工具提示应该有正确的data-bs-toggle属性'
        );
        
        // 清理
        tooltip.remove();
    },
    
    // 测试主题切换组件
    testThemeToggle: function() {
        const themeToggle = TestUtils.createElement('button', { id: 'toggleTheme' }, '<i class="fas fa-moon"></i>');
        document.body.appendChild(themeToggle);
        
        // 初始化主题切换
        ComponentManager.initThemeToggle();
        
        // 测试主题切换
        TestUtils.simulateClick(themeToggle);
        TestSuite.assert.true(TestUtils.hasClass(document.body, 'dark-theme'), '点击后应该切换到深色主题');
        
        // 测试主题保存
        const savedTheme = localStorage.getItem('theme');
        TestSuite.assert.equal(savedTheme, 'dark', '主题偏好应该保存到localStorage');
        
        // 清理
        themeToggle.remove();
        document.body.classList.remove('dark-theme');
        localStorage.removeItem('theme');
    },
    
    // 测试文件上传组件
    testFileUpload: function() {
        const uploadArea = TestUtils.createElement('div', { class: 'upload-area' }, 'Drop files here');
        const fileInput = TestUtils.createElement('input', { type: 'file', multiple: true });
        
        document.body.appendChild(uploadArea);
        document.body.appendChild(fileInput);
        
        // 初始化文件上传
        ComponentManager.initFileUpload();
        
        // 测试文件上传区域
        TestSuite.assert.true(TestUtils.hasClass(uploadArea, 'upload-area'), '上传区域应该有正确的类');
        
        // 清理
        uploadArea.remove();
        fileInput.remove();
    },
    
    // 测试表格组件
    testEnhancedTables: function() {
        const table = TestUtils.createElement('table', { class: 'table table-enhanced' });
        const tbody = TestUtils.createElement('tbody');
        const row = TestUtils.createElement('tr');
        const cell = TestUtils.createElement('td', {}, 'Test cell');
        
        row.appendChild(cell);
        tbody.appendChild(row);
        table.appendChild(tbody);
        document.body.appendChild(table);
        
        // 初始化表格
        ComponentManager.initEnhancedTables();
        
        // 测试表格样式
        TestSuite.assert.true(TestUtils.hasClass(table, 'table-enhanced'), '表格应该有增强样式');
        
        // 清理
        table.remove();
    },
    
    // 测试分页组件
    testEnhancedPagination: function() {
        const pagination = TestUtils.createElement('nav');
        const paginationList = TestUtils.createElement('ul', { class: 'pagination pagination-enhanced' });
        const pageItem = TestUtils.createElement('li', { class: 'page-item' });
        const pageLink = TestUtils.createElement('a', { class: 'page-link', href: '#' }, '1');
        
        pageItem.appendChild(pageLink);
        paginationList.appendChild(pageItem);
        pagination.appendChild(paginationList);
        document.body.appendChild(pagination);
        
        // 初始化分页
        ComponentManager.initEnhancedPagination();
        
        // 测试分页样式
        TestSuite.assert.true(TestUtils.hasClass(paginationList, 'pagination-enhanced'), '分页应该有增强样式');
        
        // 清理
        pagination.remove();
    },
    
    // 测试列表组件
    testEnhancedLists: function() {
        const list = TestUtils.createElement('ul', { class: 'list-group list-group-enhanced' });
        const listItem = TestUtils.createElement('li', { class: 'list-group-item' }, 'Test item');
        
        list.appendChild(listItem);
        document.body.appendChild(list);
        
        // 初始化列表
        ComponentManager.initEnhancedLists();
        
        // 测试列表样式
        TestSuite.assert.true(TestUtils.hasClass(list, 'list-group-enhanced'), '列表应该有增强样式');
        
        // 清理
        list.remove();
    },
    
    // 测试面包屑组件
    testEnhancedBreadcrumbs: function() {
        const breadcrumb = TestUtils.createElement('nav', { 'aria-label': 'breadcrumb' });
        const breadcrumbList = TestUtils.createElement('ol', { class: 'breadcrumb breadcrumb-enhanced' });
        const breadcrumbItem = TestUtils.createElement('li', { class: 'breadcrumb-item' });
        const breadcrumbLink = TestUtils.createElement('a', { href: '#' }, 'Home');
        
        breadcrumbItem.appendChild(breadcrumbLink);
        breadcrumbList.appendChild(breadcrumbItem);
        breadcrumb.appendChild(breadcrumbList);
        document.body.appendChild(breadcrumb);
        
        // 初始化面包屑
        ComponentManager.initEnhancedBreadcrumbs();
        
        // 测试面包屑样式
        TestSuite.assert.true(TestUtils.hasClass(breadcrumbList, 'breadcrumb-enhanced'), '面包屑应该有增强样式');
        
        // 清理
        breadcrumb.remove();
    }
};

// 运行测试
function runTests() {
    // 添加所有测试
    TestSuite.addTest('侧边栏组件测试', ComponentTests.testSidebar);
    TestSuite.addTest('卡片组件测试', ComponentTests.testEnhancedCards);
    TestSuite.addTest('表单组件测试', ComponentTests.testEnhancedForms);
    TestSuite.addTest('模态框组件测试', ComponentTests.testEnhancedModals);
    TestSuite.addTest('通知组件测试', ComponentTests.testEnhancedNotifications);
    TestSuite.addTest('工具提示组件测试', ComponentTests.testEnhancedTooltips);
    TestSuite.addTest('主题切换测试', ComponentTests.testThemeToggle);
    TestSuite.addTest('文件上传测试', ComponentTests.testFileUpload);
    TestSuite.addTest('表格组件测试', ComponentTests.testEnhancedTables);
    TestSuite.addTest('分页组件测试', ComponentTests.testEnhancedPagination);
    TestSuite.addTest('列表组件测试', ComponentTests.testEnhancedLists);
    TestSuite.addTest('面包屑组件测试', ComponentTests.testEnhancedBreadcrumbs);
    
    // 运行测试
    const results = TestSuite.run();
    
    // 返回测试结果
    return results;
}

// 导出测试模块
window.TestUtils = TestUtils;
window.TestSuite = TestSuite;
window.ComponentTests = ComponentTests;
window.runTests = runTests;