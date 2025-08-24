// UI组件JavaScript功能 - 性能优化

// 性能优化 - 使用 requestAnimationFrame 和防抖
// Prevent duplicate declaration
if (typeof ComponentManager !== 'undefined') {
    console.warn('ComponentManager already declared, skipping...');
} else {
    const ComponentManager = {
    // 性能优化 - 缓存DOM元素
    cache: {},

    // 性能优化 - 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 性能优化 - 节流函数
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // 性能优化 - 懒加载初始化
    init: function() {
        // 使用 requestAnimationFrame 优化初始化
        requestAnimationFrame(() => {
            this.initSidebar();
            this.initEnhancedCards();
            this.initEnhancedForms();
            this.initEnhancedModals();
            this.initEnhancedNotifications();
            this.initThemeToggle();
            this.initEnhancedTooltips();
            this.initFileUpload();
            this.initEnhancedTables();
            this.initEnhancedPagination();
            this.initEnhancedLists();
            this.initEnhancedBreadcrumbs();
        });
    },

    // 性能优化 - 初始化侧边栏
    initSidebar: function() {
        // 性能优化 - 缓存DOM元素
        this.cache.sidebar = document.getElementById('sidebar');
        this.cache.sidebarToggle = document.getElementById('sidebarToggle');
        this.cache.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.cache.sidebarToggleBtn = document.querySelector('[data-toggle="sidebar"]');

        if (this.cache.sidebarToggle && this.cache.sidebar && this.cache.sidebarOverlay) {
            this.cache.sidebarToggle.addEventListener('click', () => {
                this.cache.sidebar.classList.remove('show');
                this.cache.sidebarOverlay.classList.remove('show');
            });
        }

        if (this.cache.sidebarToggleBtn && this.cache.sidebar && this.cache.sidebarOverlay) {
            this.cache.sidebarToggleBtn.addEventListener('click', () => {
                this.cache.sidebar.classList.toggle('show');
                this.cache.sidebarOverlay.classList.toggle('show');
            });
        }

        if (this.cache.sidebarOverlay && this.cache.sidebar) {
            this.cache.sidebarOverlay.addEventListener('click', () => {
                this.cache.sidebar.classList.remove('show');
                this.cache.sidebarOverlay.classList.remove('show');
            });
        }

        // 性能优化 - 使用节流处理响应式
        this.handleResponsiveSidebar();
        window.addEventListener('resize', this.throttle(this.handleResponsiveSidebar.bind(this), 250));
    },

    // 性能优化 - 处理响应式侧边栏
    handleResponsiveSidebar: function() {
        if (window.innerWidth > 992) {
            if (this.cache.sidebar) {
                this.cache.sidebar.classList.remove('show');
            }
            if (this.cache.sidebarOverlay) {
                this.cache.sidebarOverlay.classList.remove('show');
            }
        }
    },

    // 性能优化 - 初始化增强卡片
    initEnhancedCards: function() {
        const cards = document.querySelectorAll('.card-enhanced');

        // 性能优化 - 使用 Intersection Observer 实现懒加载
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const card = entry.target;
                    this.animateCard(card);
                    observer.unobserve(card);
                }
            });
        }, { threshold: 0.1 });

        cards.forEach(card => observer.observe(card));
    },

    // 性能优化 - 动画卡片
    animateCard: function(card) {
        requestAnimationFrame(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';

            requestAnimationFrame(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            });
        });

        // 性能优化 - 使用事件委托
        card.addEventListener('click', (e) => {
            this.createRipple(e, card);
        });
    },

    // 性能优化 - 初始化增强表单
    initEnhancedForms: function() {
        const forms = document.querySelectorAll('.form-enhanced');

        forms.forEach(form => {
            const inputs = form.querySelectorAll('.form-control-enhanced');

            inputs.forEach(input => {
                // 性能优化 - 使用事件委托
                input.addEventListener('focus', () => {
                    input.parentElement.classList.add('focused');
                });

                input.addEventListener('blur', () => {
                    input.parentElement.classList.remove('focused');
                });

                // 性能优化 - 防抖实时验证
                input.addEventListener('input', this.debounce(() => {
                    this.validateField(input);
                }, 300));
            });

            // 性能优化 - 表单提交处理
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitEnhancedForm(form);
            });
        });
    },

    // 性能优化 - 初始化增强模态框
    initEnhancedModals: function() {
        const modals = document.querySelectorAll('.modal-enhanced');

        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', () => {
                this.addModalAnimation(modal);
            });

            modal.addEventListener('hidden.bs.modal', () => {
                this.resetModalAnimation(modal);
            });
        });
    },

    // 初始化增强通知
    initEnhancedNotifications: function() {
        // 监听自定义通知事件
        document.addEventListener('showEnhancedNotification', function(e) {
            this.showEnhancedNotification(e.detail.message, e.detail.type);
        }.bind(this));

        // 自动关闭现有通知
        this.autoCloseNotifications();
    },

    // 初始化主题切换
    initThemeToggle: function() {
        const themeToggle = document.getElementById('toggleTheme');
        const body = document.body;

        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                body.classList.toggle('dark-theme');
                const isDark = body.classList.contains('dark-theme');

                // 更新按钮图标
                const icon = themeToggle.querySelector('i');
                icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';

                // 保存主题偏好
                localStorage.setItem('theme', isDark ? 'dark' : 'light');

                // 显示切换通知
                this.showEnhancedNotification(
                    isDark ? '已切换到深色模式' : '已切换到浅色模式',
                    'success'
                );
            }.bind(this));

            // 加载保存的主题
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                body.classList.add('dark-theme');
                themeToggle.querySelector('i').className = 'fas fa-sun';
            }
        }
    },

    // 初始化增强工具提示
    initEnhancedTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip-enhanced"]'));

        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                template: '<div class="tooltip tooltip-enhanced" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>'
            });
        });
    },

    // 初始化文件上传
    initFileUpload: function() {
        const uploadAreas = document.querySelectorAll('.upload-area');

        uploadAreas.forEach(function(area) {
            const input = area.querySelector('input[type="file"]');

            if (input) {
                // 拖拽上传
                area.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    area.classList.add('dragover');
                });

                area.addEventListener('dragleave', function() {
                    area.classList.remove('dragover');
                });

                area.addEventListener('drop', function(e) {
                    e.preventDefault();
                    area.classList.remove('dragover');

                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        input.files = files;
                        this.handleFileUpload(files[0], area);
                    }
                }.bind(this));

                // 点击上传
                area.addEventListener('click', function() {
                    input.click();
                });

                input.addEventListener('change', function() {
                    if (input.files.length > 0) {
                        this.handleFileUpload(input.files[0], area);
                    }
                }.bind(this));
            }
        }.bind(this));
    },

    // 初始化增强表格
    initEnhancedTables: function() {
        const tables = document.querySelectorAll('.table-enhanced');

        tables.forEach(function(table) {
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                row.addEventListener('click', function() {
                    // 移除其他行的选中状态
                    rows.forEach(r => r.classList.remove('selected'));
                    // 添加当前行的选中状态
                    row.classList.add('selected');
                });
            });

            // 添加排序功能
            this.addTableSorting(table);
        }.bind(this));
    },

    // 初始化增强分页
    initEnhancedPagination: function() {
        const paginations = document.querySelectorAll('.pagination-enhanced');

        paginations.forEach(function(pagination) {
            const links = pagination.querySelectorAll('.page-link');

            links.forEach(function(link) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    // 移除其他页面的活动状态
                    links.forEach(l => l.parentElement.classList.remove('active'));
                    // 添加当前页面的活动状态
                    link.parentElement.classList.add('active');

                    // 加载对应页面数据
                    const page = link.getAttribute('data-page');
                    if (page) {
                        this.loadPageData(page);
                    }
                }.bind(this));
            }.bind(this));
        }.bind(this));
    },

    // 初始化增强列表
    initEnhancedLists: function() {
        const lists = document.querySelectorAll('.list-group-enhanced');

        lists.forEach(function(list) {
            const items = list.querySelectorAll('.list-group-item');

            items.forEach(function(item) {
                item.addEventListener('click', function() {
                    // 移除其他项目的选中状态
                    items.forEach(i => i.classList.remove('active'));
                    // 添加当前项目的选中状态
                    item.classList.add('active');
                });
            });
        });
    },

    // 初始化增强面包屑
    initEnhancedBreadcrumbs: function() {
        const breadcrumbs = document.querySelectorAll('.breadcrumb-enhanced');

        breadcrumbs.forEach(function(breadcrumb) {
            const items = breadcrumb.querySelectorAll('.breadcrumb-item');

            items.forEach(function(item) {
                const link = item.querySelector('a');
                if (link) {
                    link.addEventListener('click', function(e) {
                        // 添加点击效果
                        this.addBreadcrumbClickEffect(item);
                    }.bind(this));
                }
            }.bind(this));
        });
    },

    // 创建波纹效果
    createRipple: function(e, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
        `;

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    },

    // 验证字段
    validateField: function(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        let isValid = true;
        let errorMessage = '';

        // 基本验证
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = '此字段为必填项';
        }

        // 类型特定验证
        if (value && isValid) {
            switch (fieldType) {
                case 'email':
                    if (!this.isValidEmail(value)) {
                        isValid = false;
                        errorMessage = '请输入有效的邮箱地址';
                    }
                    break;
                case 'url':
                    if (!this.isValidUrl(value)) {
                        isValid = false;
                        errorMessage = '请输入有效的URL';
                    }
                    break;
            }
        }

        // 显示验证结果
        this.showFieldValidation(field, isValid, errorMessage);
    },

    // 显示字段验证结果
    showFieldValidation: function(field, isValid, errorMessage) {
        const feedback = field.parentElement.querySelector('.invalid-feedback');

        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedback) feedback.remove();
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');

            if (!feedback) {
                const feedbackElement = document.createElement('div');
                feedbackElement.className = 'invalid-feedback';
                feedbackElement.textContent = errorMessage;
                field.parentElement.appendChild(feedbackElement);
            } else {
                feedback.textContent = errorMessage;
            }
        }
    },

    // 提交增强表单
    submitEnhancedForm: function(form) {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;

        // 显示加载状态
        submitBtn.innerHTML = '<span class="loading-enhanced"></span> 提交中...';
        submitBtn.disabled = true;

        // 模拟API调用
        setTimeout(() => {
            this.showEnhancedNotification('表单提交成功！', 'success');
            form.reset();
            submitBtn.innerHTML = originalContent;
            submitBtn.disabled = false;
        }, 2000);
    },

    // 显示增强通知
    showEnhancedNotification: function(message, type = 'info') {
        const alertClass = `alert-enhanced alert-enhanced-${type}`;
        const notification = document.createElement('div');
        notification.className = alertClass;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;

        // 插入到页面顶部
        const container = document.querySelector('main .container') || document.querySelector('main');
        container.insertAdjacentHTML('afterbegin', notification.outerHTML);

        // 自动关闭
        setTimeout(() => {
            const alert = container.querySelector('.alert-enhanced');
            if (alert) alert.remove();
        }, 5000);
    },

    // 获取通知图标
    getNotificationIcon: function(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    },

    // 自动关闭通知
    autoCloseNotifications: function() {
        setInterval(() => {
            const alerts = document.querySelectorAll('.alert-enhanced');
            alerts.forEach(alert => {
                if (alert.style.display !== 'none') {
                    alert.style.opacity = '0';
                    setTimeout(() => alert.remove(), 300);
                }
            });
        }, 10000);
    },

    // 添加模态框动画
    addModalAnimation: function(modal) {
        const content = modal.querySelector('.modal-content');
        content.style.transform = 'scale(0.7)';
        content.style.opacity = '0';

        setTimeout(() => {
            content.style.transition = 'all 0.3s ease';
            content.style.transform = 'scale(1)';
            content.style.opacity = '1';
        }, 50);
    },

    // 重置模态框动画
    resetModalAnimation: function(modal) {
        const content = modal.querySelector('.modal-content');
        content.style.transform = 'scale(1)';
        content.style.opacity = '1';
    },

    // 处理文件上传
    handleFileUpload: function(file, area) {
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (file.size > maxSize) {
            this.showEnhancedNotification('文件大小超过10MB限制', 'danger');
            return;
        }

        // 显示文件信息
        area.innerHTML = `
            <div class="text-center">
                <i class="fas fa-file fa-3x mb-3"></i>
                <h6>${file.name}</h6>
                <p class="text-muted">${this.formatFileSize(file.size)}</p>
                <div class="progress mt-3">
                    <div class="progress-bar progress-bar-enhanced" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
        `;

        // 模拟上传进度
        this.simulateUploadProgress(area);
    },

    // 模拟上传进度
    simulateUploadProgress: function(area) {
        const progressBar = area.querySelector('.progress-bar');
        let progress = 0;

        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                this.showEnhancedNotification('文件上传成功！', 'success');
            }
            progressBar.style.width = progress + '%';
        }, 200);
    },

    // 添加表格排序功能
    addTableSorting: function(table) {
        const headers = table.querySelectorAll('thead th');

        headers.forEach(function(header, index) {
            if (header.hasAttribute('data-sortable')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    this.sortTable(table, index);
                }.bind(this));
            }
        }.bind(this));
    },

    // 排序表格
    sortTable: function(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort(function(a, b) {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();

            // 数字排序
            if (!isNaN(aValue) && !isNaN(bValue)) {
                return parseFloat(aValue) - parseFloat(bValue);
            }

            // 字符串排序
            return aValue.localeCompare(bValue);
        });

        // 重新排列行
        rows.forEach(row => tbody.appendChild(row));
    },

    // 加载页面数据
    loadPageData: function(page) {
        this.showEnhancedNotification(`正在加载第 ${page} 页数据...`, 'info');

        // 模拟数据加载
        setTimeout(() => {
            this.showEnhancedNotification(`第 ${page} 页数据加载完成`, 'success');
        }, 1000);
    },

    // 添加面包屑点击效果
    addBreadcrumbClickEffect: function(item) {
        item.style.transform = 'scale(0.95)';
        setTimeout(() => {
            item.style.transform = 'scale(1)';
        }, 150);
    },

    // 工具函数
    isValidEmail: function(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    isValidUrl: function(url) {
        if (!url || typeof url !== 'string') {
            return false;
        }

        try {
            // 如果URL是相对路径，添加当前域名
            if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
                new URL(url, window.location.origin);
            } else {
                new URL(url);
            }
            return true;
        } catch {
            return false;
        }
    },

    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// 性能监控 - 已移至独立的 performance.js 文件

// 键盘导航增强
// Prevent duplicate declaration
if (typeof KeyboardNavigation !== 'undefined') {
    console.warn('KeyboardNavigation already declared, skipping...');
} else {
    const KeyboardNavigation = {
    init: function() {
        this.setupKeyboardShortcuts();
        this.setupFocusManagement();
        this.setupAriaLabels();
    },

    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + K 打开搜索
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openSearch();
            }

            // Ctrl/Cmd + B 切换侧边栏
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }

            // Escape 关闭模态框和侧边栏
            if (e.key === 'Escape') {
                this.closeModals();
                this.closeSidebar();
            }

            // 方向键导航
            if (e.key === 'ArrowLeft' && e.ctrlKey) {
                e.preventDefault();
                this.navigateBack();
            }

            if (e.key === 'ArrowRight' && e.ctrlKey) {
                e.preventDefault();
                this.navigateForward();
            }
        }.bind(this));
    },

    setupFocusManagement: function() {
        // 为模态框设置焦点陷阱
        document.addEventListener('shown.bs.modal', function(e) {
            const modal = e.target;
            const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            const firstFocusableElement = focusableElements[0];
            const lastFocusableElement = focusableElements[focusableElements.length - 1];

            modal.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstFocusableElement) {
                            lastFocusableElement.focus();
                            e.preventDefault();
                        }
                    } else {
                        if (document.activeElement === lastFocusableElement) {
                            firstFocusableElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });

            firstFocusableElement.focus();
        });
    },

    setupAriaLabels: function() {
        // 为动态内容添加ARIA标签
        this.updateAriaLiveRegions();
    },

    updateAriaLiveRegions: function() {
        // 创建屏幕阅读器友好的通知区域
        let liveRegion = document.getElementById('aria-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'aria-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
    },

    openSearch: function() {
        const searchModal = document.getElementById('searchModal');
        if (searchModal) {
            const modal = new bootstrap.Modal(searchModal);
            modal.show();
        }
    },

    toggleSidebar: function() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    },

    closeModals: function() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    },

    closeSidebar: function() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.remove('show');
        }
    },

    navigateBack: function() {
        if (window.history.length > 1) {
            window.history.back();
        }
    },

    navigateForward: function() {
        if (window.history.length < window.history.length) {
            window.history.forward();
        }
    }
};

// 导出 KeyboardNavigation
window.KeyboardNavigation = KeyboardNavigation;
}

// 拖拽功能增强
// Prevent duplicate declaration
if (typeof DragDropManager !== 'undefined') {
    console.warn('DragDropManager already declared, skipping...');
} else {
    const DragDropManager = {
    init: function() {
        this.setupFileDragDrop();
        this.setupElementDragDrop();
    },

    setupFileDragDrop: function() {
        const dropZones = document.querySelectorAll('.upload-area');

        dropZones.forEach(zone => {
            zone.addEventListener('dragover', this.handleDragOver.bind(this));
            zone.addEventListener('dragleave', this.handleDragLeave.bind(this));
            zone.addEventListener('drop', this.handleDrop.bind(this));
        });
    },

    setupElementDragDrop: function() {
        const draggableElements = document.querySelectorAll('[draggable="true"]');

        draggableElements.forEach(element => {
            element.addEventListener('dragstart', this.handleDragStart.bind(this));
            element.addEventListener('dragend', this.handleDragEnd.bind(this));
        });

        const dropTargets = document.querySelectorAll('.drop-target');
        dropTargets.forEach(target => {
            target.addEventListener('dragover', this.handleDragOver.bind(this));
            target.addEventListener('drop', this.handleElementDrop.bind(this));
        });
    },

    handleDragOver: function(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    },

    handleDragLeave: function(e) {
        e.currentTarget.classList.remove('dragover');
    },

    handleDrop: function(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFiles(files, e.currentTarget);
        }
    },

    handleDragStart: function(e) {
        e.dataTransfer.setData('text/plain', e.target.id);
        e.target.classList.add('dragging');
    },

    handleDragEnd: function(e) {
        e.target.classList.remove('dragging');
    },

    handleElementDrop: function(e) {
        e.preventDefault();
        const draggedElementId = e.dataTransfer.getData('text/plain');
        const draggedElement = document.getElementById(draggedElementId);

        if (draggedElement) {
            e.currentTarget.appendChild(draggedElement);
            this.showDropSuccess(e.currentTarget);
        }
    },

    processFiles: function(files, dropZone) {
        Array.from(files).forEach(file => {
            this.validateAndProcessFile(file, dropZone);
        });
    },

    validateAndProcessFile: function(file, dropZone) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf', 'text/plain'];

        if (file.size > maxSize) {
            this.showFileError('文件大小超过10MB限制', dropZone);
            return;
        }

        if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
            this.showFileError('文件类型不支持', dropZone);
            return;
        }

        this.showFileSuccess(file, dropZone);
    },

    showFileSuccess: function(file, dropZone) {
        dropZone.innerHTML = `
            <div class="text-center">
                <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                <h6>${file.name}</h6>
                <p class="text-muted">${this.formatFileSize(file.size)}</p>
                <div class="progress mt-3">
                    <div class="progress-bar progress-bar-enhanced" style="width: 100%"></div>
                </div>
            </div>
        `;
    },

    showFileError: function(message, dropZone) {
        dropZone.innerHTML = `
            <div class="text-center">
                <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                <h6>上传失败</h6>
                <p class="text-muted">${message}</p>
                <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">重试</button>
            </div>
        `;
    },

    showDropSuccess: function(target) {
        target.classList.add('drop-success');
        setTimeout(() => {
            target.classList.remove('drop-success');
        }, 2000);
    },

    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// 导出 DragDropManager
window.DragDropManager = DragDropManager;
}

// 本地存储管理
// StorageManager - 本地存储管理
// Only declare if not already defined
if (typeof StorageManager === 'undefined') {
    const StorageManager = {
    init: function() {
        this.setupAutoSave();
        this.setupThemePersistence();
        this.setupUserPreferences();
    },

    setupAutoSave: function() {
        const forms = document.querySelectorAll('form[data-auto-save]');

        forms.forEach(form => {
            const formKey = `form_${form.id || form.action}`;
            const savedData = this.get(formKey);

            if (savedData) {
                this.restoreFormData(form, savedData);
            }

            form.addEventListener('input', this.debounce(function() {
                const formData = this.serializeForm(form);
                this.set(formKey, formData);
            }.bind(this), 1000));

            form.addEventListener('submit', function() {
                this.remove(formKey);
            }.bind(this));
        });
    },

    setupThemePersistence: function() {
        const savedTheme = this.get('theme');
        if (savedTheme) {
            document.body.classList.toggle('dark-theme', savedTheme === 'dark');
        }
    },

    setupUserPreferences: function() {
        const preferences = this.get('userPreferences') || {};

        // 应用用户偏好
        if (preferences.fontSize) {
            document.body.style.fontSize = preferences.fontSize;
        }

        if (preferences.language) {
            document.documentElement.lang = preferences.language;
        }
    },

    serializeForm: function(form) {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    },

    restoreFormData: function(form, data) {
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key];
            }
        });
    },

    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('本地存储失败:', e);
        }
    },

    get: function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.warn('读取本地存储失败:', e);
            return null;
        }
    },

    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('删除本地存储失败:', e);
        }
    },

    clear: function() {
        try {
            localStorage.clear();
        } catch (e) {
            console.warn('清空本地存储失败:', e);
        }
    },

    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// 导出 StorageManager
window.StorageManager = StorageManager;
}

// 应用初始化
// Prevent duplicate declaration
if (typeof AppInitializer !== 'undefined') {
    console.warn('AppInitializer already declared, skipping...');
} else {
    const AppInitializer = {
    init: function() {
        // 性能监控已移至独立的 performance.js 文件

        // 初始化键盘导航
        KeyboardNavigation.init();

        // 初始化拖拽功能
        DragDropManager.init();

        // 初始化本地存储
        StorageManager.init();

        // 初始化组件管理器
        ComponentManager.init();

        // 设置全局错误处理
        this.setupGlobalErrorHandling();

        // 检查浏览器兼容性
        this.checkBrowserCompatibility();

        // 初始化服务工作线程（如果支持）
        this.initServiceWorker();

        console.log('CoderWiki 应用初始化完成');
    },

    setupGlobalErrorHandling: function() {
        window.addEventListener('error', function(e) {
            console.error('全局错误:', e.error);

            // 显示用户友好的错误消息
            ComponentManager.showEnhancedNotification(
                '应用遇到错误，请刷新页面重试',
                'danger'
            );

            // 发送错误报告（如果配置了错误监控）
            this.reportError(e.error);
        }.bind(this));

        window.addEventListener('unhandledrejection', function(e) {
            console.error('未处理的Promise拒绝:', e.reason);

            ComponentManager.showEnhancedNotification(
                '网络请求失败，请检查网络连接',
                'warning'
            );
        });
    },

    checkBrowserCompatibility: function() {
        const incompatible = [];

        // 检查必要的API支持
        if (!window.fetch) {
            incompatible.push('Fetch API');
        }

        if (!window.Promise) {
            incompatible.push('Promise');
        }

        if (!window.localStorage) {
            incompatible.push('Local Storage');
        }

        if (incompatible.length > 0) {
            console.warn('浏览器兼容性警告:', incompatible);

            // 显示兼容性警告
            const warningMessage = `您的浏览器可能不完全支持某些功能：${incompatible.join(', ')}`;
            ComponentManager.showEnhancedNotification(warningMessage, 'warning');
        }
    },

    initServiceWorker: function() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(function(registration) {
                    console.log('Service Worker 注册成功:', registration);
                })
                .catch(function(error) {
                    console.log('Service Worker 注册失败:', error);
                });
        }
    },

    reportError: function(error) {
        // 这里可以集成错误监控服务
        if (window.ga) {
            window.ga('send', 'exception', {
                exDescription: error.message,
                exFatal: false
            });
        }
    }
};

// 导出 AppInitializer
window.AppInitializer = AppInitializer;
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', function() {
    AppInitializer.init();
});

    // 导出 ComponentManager
    window.ComponentManager = ComponentManager;
    // PerformanceMonitor 已移至独立的 performance.js 文件
}
