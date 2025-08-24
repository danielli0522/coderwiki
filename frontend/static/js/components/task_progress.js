/**
 * 任务进度组件
 * 负责任务列表的获取、展示和状态监控
 */

// 使用组件注册表防止重复声明
// 使用立即执行函数表达式避免全局作用域污染
(function() {
    // 检查组件是否已注册
    if (window.ComponentRegistry && window.ComponentRegistry.isRegistered('TaskProgressComponent')) {
        console.log('TaskProgressComponent already registered, reusing existing component');
        return;
    }

    class TaskProgressComponent {
    constructor() {
        this.tasks = [];
        this.filters = {
            status: ''
        };
        this.refreshInterval = null;
        this.isAuthenticated = false;
        this.init();
    }

    async init() {
        await this.checkAuthentication();
        if (this.isAuthenticated) {
            this.bindEvents();
            this.loadTasks();
            this.startAutoRefresh();
        } else {
            console.log('用户未登录，跳过任务进度组件初始化');
        }
    }

    async checkAuthentication() {
        try {
            const response = await fetch('/api/auth/status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                redirect: 'manual'
            });

            if (response.ok) {
                const data = await response.json();
                this.isAuthenticated = data.logged_in || false;
            } else if (response.status === 302 || response.status === 303) {
                this.isAuthenticated = false;
            } else {
                this.isAuthenticated = false;
            }
        } catch (error) {
            console.error('认证检查失败:', error);
            this.isAuthenticated = false;
        }
    }

    bindEvents() {
        // 状态筛选
        const statusFilter = document.getElementById('taskStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.loadTasks();
            });
        }

        // 刷新按钮
        const refreshBtn = document.getElementById('refreshTasksBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadTasks(true);
            });
        }

        // 任务操作按钮（事件委托）
        const container = document.getElementById('taskListContainer');
        if (container) {
            container.addEventListener('click', (e) => {
                const taskItem = e.target.closest('.task-item');
                if (!taskItem) return;

                const taskId = taskItem.dataset.taskId;

                if (e.target.closest('.view-task-btn')) {
                    this.viewTask(taskId);
                } else if (e.target.closest('.cancel-task-btn')) {
                    this.cancelTask(taskId);
                } else if (e.target.closest('.retry-task-btn')) {
                    this.retryTask(taskId);
                }
            });
        }

        // 监听任务刷新事件
        window.addEventListener('task:refresh', () => {
            this.loadTasks(true);
        });
    }

    async loadTasks(forceRefresh = false) {
        if (!this.isAuthenticated) {
            console.log('用户未登录，跳过任务数据加载');
            return;
        }

        try {
            const params = new URLSearchParams(this.filters);
            const response = await fetch(`/api/tasks?${params}`, {
                redirect: 'manual'
            });

            if (response.status === 302 || response.status === 303) {
                throw new Error('需要登录');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.tasks = data.tasks || [];

            this.renderTasks();
        } catch (error) {
            console.error('加载任务列表失败:', error);
            this.showError('加载任务列表失败');
        }
    }

    renderTasks() {
        const container = document.getElementById('taskListContainer');
        const emptyState = document.getElementById('emptyTaskState');

        if (!container) return;

        if (this.tasks.length === 0) {
            container.innerHTML = '';
            if (emptyState) {
                container.appendChild(emptyState.cloneNode(true));
            }
            return;
        }

        const template = document.getElementById('taskItemTemplate');
        if (!template) return;

        container.innerHTML = '';

        this.tasks.forEach(task => {
            const taskElement = this.createTaskElement(task, template);
            container.appendChild(taskElement);
        });
    }

    createTaskElement(task, template) {
        const element = template.content.cloneNode(true);
        const taskItem = element.querySelector('.task-item');

        taskItem.dataset.taskId = task.id;

        // 设置任务标题和描述
        const titleElement = element.querySelector('.task-title');
        const descElement = element.querySelector('.task-description');

        if (titleElement) titleElement.textContent = task.title;
        if (descElement) descElement.textContent = task.description || '暂无描述';

        // 设置状态徽章
        const statusBadge = element.querySelector('.task-status-badge');
        if (statusBadge) {
            statusBadge.textContent = this.getStatusText(task.status);
            statusBadge.className = `badge ${this.getStatusClass(task.status)}`;
        }

        // 设置元数据
        const metaElements = element.querySelectorAll('.task-meta small');
        if (metaElements[0]) metaElements[0].textContent = `创建时间: ${this.formatDate(task.created_at)}`;
        if (metaElements[1]) metaElements[1].textContent = `类型: ${this.getTaskTypeText(task.type)}`;

        // 设置进度条
        const progressBar = element.querySelector('.task-progress-bar');
        const percentage = element.querySelector('.task-percentage');

        if (progressBar) {
            progressBar.style.width = `${task.progress || 0}%`;
            progressBar.className = `progress-bar ${this.getProgressClass(task.status)}`;
        }
        if (percentage) percentage.textContent = `${task.progress || 0}%`;

        // 设置任务图标
        const taskIcon = element.querySelector('.task-icon i');
        if (taskIcon) {
            taskIcon.className = this.getTaskIcon(task.status);
            if (task.status === 'running') {
                taskIcon.classList.add('fa-spin');
            }
        }

        // 设置操作按钮可见性
        this.updateActionButtons(element, task);

        return element;
    }

    updateActionButtons(element, task) {
        const cancelBtn = element.querySelector('.cancel-task-btn');
        const retryBtn = element.querySelector('.retry-task-btn');

        if (cancelBtn) {
            cancelBtn.style.display = (task.status === 'running' || task.status === 'pending') ? 'inline-block' : 'none';
        }

        if (retryBtn) {
            retryBtn.style.display = (task.status === 'failed' || task.status === 'cancelled') ? 'inline-block' : 'none';
        }
    }

    async cancelTask(taskId) {
        if (!confirm('确定要取消这个任务吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/tasks/${taskId}/cancel`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showSuccess('任务已取消');
            this.loadTasks();
        } catch (error) {
            console.error('取消任务失败:', error);
            this.showError('取消任务失败');
        }
    }

    async retryTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}/retry`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showSuccess('任务已重新开始');
            this.loadTasks();
        } catch (error) {
            console.error('重试任务失败:', error);
            this.showError('重试任务失败');
        }
    }

    viewTask(taskId) {
        // 实现查看任务详情逻辑
        console.log('查看任务详情:', taskId);
    }

    startAutoRefresh() {
        // 每3分钟自动刷新一次任务列表
        this.refreshInterval = setInterval(() => {
            this.loadTasks();
        }, 180000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    getStatusText(status) {
        const statusMap = {
            'pending': '待处理',
            'running': '运行中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
    }

    getStatusClass(status) {
        const classMap = {
            'pending': 'bg-secondary',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        };
        return classMap[status] || 'bg-primary';
    }

    getProgressClass(status) {
        const classMap = {
            'pending': 'bg-secondary',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        };
        return classMap[status] || 'bg-primary';
    }

    getTaskIcon(status) {
        const iconMap = {
            'pending': 'fas fa-clock',
            'running': 'fas fa-cog',
            'completed': 'fas fa-check-circle',
            'failed': 'fas fa-times-circle',
            'cancelled': 'fas fa-ban'
        };
        return iconMap[status] || 'fas fa-tasks';
    }

    getTaskTypeText(type) {
        const typeMap = {
            'document_generation': '文档生成',
            'repository_analysis': '仓库分析',
            'code_analysis': '代码分析',
            'system_maintenance': '系统维护'
        };
        return typeMap[type] || type;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('.task-progress-container');
        if (container) {
            container.insertAdjacentHTML('afterbegin', alertHtml);

            setTimeout(() => {
                const alert = container.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }

    destroy() {
        this.stopAutoRefresh();
    }
}

    // 注册组件到注册表
    if (window.ComponentRegistry) {
        window.ComponentRegistry.register('TaskProgressComponent', TaskProgressComponent);
    } else {
        // 降级方案
        window.TaskProgressComponent = TaskProgressComponent;
    }

    // 确保组件实例被创建
    if (typeof window.taskProgressComponent === 'undefined') {
        window.taskProgressComponent = new TaskProgressComponent();
        console.log('TaskProgressComponent instance created');
    } else {
        console.log('TaskProgressComponent instance already exists, reusing');
    }
})();
