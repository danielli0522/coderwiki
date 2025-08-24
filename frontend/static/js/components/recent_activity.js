/**
 * 最近活动组件
 * 负责活动时间轴的展示和数据获取
 */
class RecentActivityComponent {
    constructor() {
        this.activities = [];
        this.filters = {
            type: ''
        };
        this.refreshInterval = null;
        this.isAuthenticated = false;
        this.init();
    }

    async init() {
        await this.checkAuthentication();
        if (this.isAuthenticated) {
            this.bindEvents();
            this.loadActivities();
            this.startAutoRefresh();
        } else {
            console.log('用户未登录，跳过活动组件初始化');
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
        // 活动类型筛选
        const activityFilter = document.getElementById('activityFilter');
        if (activityFilter) {
            activityFilter.addEventListener('change', (e) => {
                this.filters.type = e.target.value;
                this.loadActivities();
            });
        }

        // 刷新按钮
        const refreshBtn = document.getElementById('refreshActivityBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadActivities(true);
            });
        }
    }

    async loadActivities(forceRefresh = false) {
        if (!this.isAuthenticated) {
            console.log('用户未登录，跳过活动数据加载');
            return;
        }

        try {
            const params = new URLSearchParams(this.filters);
            const response = await fetch(`/api/activities?${params}`, {
                redirect: 'manual'
            });

            if (response.status === 302 || response.status === 303) {
                throw new Error('需要登录');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.activities = data.activities || [];

            this.renderActivities();
        } catch (error) {
            console.error('加载活动列表失败:', error);
            this.showError('加载活动列表失败');
        }
    }

    renderActivities() {
        const timeline = document.getElementById('activityTimeline');
        const emptyState = document.getElementById('emptyActivityState');

        if (!timeline) return;

        if (this.activities.length === 0) {
            timeline.innerHTML = '';
            if (emptyState) {
                timeline.appendChild(emptyState.cloneNode(true));
            }
            return;
        }

        const template = document.getElementById('activityItemTemplate');
        if (!template) return;

        timeline.innerHTML = '';

        this.activities.forEach((activity, index) => {
            const activityElement = this.createActivityElement(activity, template);
            timeline.appendChild(activityElement);
        });
    }

    createActivityElement(activity, template) {
        const element = template.content.cloneNode(true);
        const timelineItem = element.querySelector('.timeline-item');

        // 设置活动图标
        const iconElement = element.querySelector('.activity-icon');
        if (iconElement) {
            iconElement.className = this.getActivityIcon(activity.type);
        }

        // 设置活动标题和描述
        const titleElement = element.querySelector('.activity-title');
        const descElement = element.querySelector('.activity-description');

        if (titleElement) titleElement.textContent = activity.title;
        if (descElement) descElement.textContent = activity.description || '';

        // 设置活动类型徽章
        const typeBadge = element.querySelector('.activity-type-badge');
        if (typeBadge) {
            typeBadge.textContent = this.getActivityTypeText(activity.type);
            typeBadge.className = `badge ${this.getActivityTypeClass(activity.type)}`;
        }

        // 设置时间和元数据
        const timeElement = element.querySelector('.activity-time');
        const metaElement = element.querySelector('.activity-meta small');

        if (timeElement) timeElement.textContent = this.formatTime(activity.timestamp || activity.created_at);
        if (metaElement) metaElement.textContent = `用户: ${activity.user_name || '系统'}`;

        return element;
    }

    getActivityIcon(type) {
        const iconMap = {
            'repository': 'fas fa-folder',
            'document': 'fas fa-file-alt',
            'task': 'fas fa-tasks',
            'system': 'fas fa-cog',
            'user': 'fas fa-user',
            'login': 'fas fa-sign-in-alt',
            'logout': 'fas fa-sign-out-alt',
            'error': 'fas fa-exclamation-triangle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        return iconMap[type] || 'fas fa-circle';
    }

    getActivityTypeText(type) {
        const typeMap = {
            'repository': '仓库',
            'document': '文档',
            'task': '任务',
            'system': '系统',
            'user': '用户',
            'login': '登录',
            'logout': '登出',
            'error': '错误',
            'success': '成功',
            'warning': '警告',
            'info': '信息'
        };
        return typeMap[type] || type;
    }

    getActivityTypeClass(type) {
        const classMap = {
            'repository': 'bg-primary',
            'document': 'bg-success',
            'task': 'bg-warning',
            'system': 'bg-info',
            'user': 'bg-secondary',
            'login': 'bg-success',
            'logout': 'bg-secondary',
            'error': 'bg-danger',
            'success': 'bg-success',
            'warning': 'bg-warning',
            'info': 'bg-info'
        };
        return classMap[type] || 'bg-primary';
    }

    formatTime(dateString) {
        // 处理空值或无效值
        if (!dateString) {
            return '未知时间';
        }

        const date = new Date(dateString);

        // 检查日期是否有效
        if (isNaN(date.getTime())) {
            console.warn('Invalid date string:', dateString);
            return '时间格式错误';
        }

        const now = new Date();
        const diff = now - date;

        // 小于1分钟
        if (diff < 60000) {
            return '刚刚';
        }

        // 小于1小时
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}分钟前`;
        }

        // 小于1天
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}小时前`;
        }

        // 小于7天
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days}天前`;
        }

        // 超过7天显示具体日期
        try {
            return date.toLocaleDateString('zh-CN');
        } catch (error) {
            console.warn('Error formatting date:', error);
            return '日期显示错误';
        }
    }

    startAutoRefresh() {
        // 每30秒自动刷新一次活动列表
        this.refreshInterval = setInterval(() => {
            this.loadActivities();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('.recent-activity-container');
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

// 导出组件
window.RecentActivityComponent = RecentActivityComponent;
