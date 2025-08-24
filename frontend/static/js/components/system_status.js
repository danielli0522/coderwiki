/**
 * 系统状态组件
 * 负责系统监控和状态展示
 */
class SystemStatusComponent {
    constructor() {
        this.systemData = {};
        this.refreshInterval = null;
        this.isAuthenticated = false;
        this.init();
    }

    async init() {
        // 系统状态是公开的，不需要认证
        this.isAuthenticated = true;
        this.bindEvents();
        this.loadSystemStatus();
        this.startAutoRefresh();
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
        // 刷新按钮
        const refreshBtn = document.getElementById('refreshSystemStatusBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadSystemStatus(true);
            });
        }
    }

    async loadSystemStatus(forceRefresh = false) {
        // 系统状态是公开的，不需要认证检查

        try {
            const response = await fetch('/api/system/health', {
                redirect: 'manual'
            });

            if (response.status === 302 || response.status === 303) {
                throw new Error('需要登录');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.systemData = data;

            this.updateSystemStatus();
            this.updateServiceStatus();
            this.updateSystemAlerts();
        } catch (error) {
            console.error('加载系统状态失败:', error);
            this.showError('加载系统状态失败');
        }
    }

    updateSystemStatus() {
        // 更新系统概览状态
        this.updateOverallStatus();
        this.updateUptime();
        this.updateResourceUsage();
    }

    updateOverallStatus() {
        const statusElement = document.getElementById('systemOverallStatus');
        const statusDot = document.getElementById('systemStatusDot');

        if (!statusElement || !this.systemData.overall_status) return;

        const status = this.systemData.overall_status;
        const statusInfo = this.getStatusInfo(status);

        if (statusElement) {
            statusElement.textContent = statusInfo.text;
            statusElement.className = `badge ${statusInfo.class}`;
        }

        if (statusDot) {
            statusDot.className = `status-dot ${statusInfo.dotClass}`;
        }
    }

    updateUptime() {
        const uptimeElement = document.getElementById('systemUptime');
        if (!uptimeElement || !this.systemData.uptime) return;

        const uptime = this.systemData.uptime;
        const days = Math.floor(uptime / 86400);
        const hours = Math.floor((uptime % 86400) / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);

        uptimeElement.textContent = `${days}天 ${hours}小时 ${minutes}分钟`;
    }

    updateResourceUsage() {
        // 更新CPU使用率
        this.updateResourceMetric('cpu', this.systemData.cpu_usage);

        // 更新内存使用率
        this.updateResourceMetric('memory', this.systemData.memory_usage);

        // 更新磁盘使用率
        this.updateResourceMetric('disk', this.systemData.disk_usage);
    }

    updateResourceMetric(type, value) {
        const valueElement = document.getElementById(`${type}Usage`);
        const progressBar = document.getElementById(`${type}ProgressBar`);

        if (!valueElement || !progressBar || value === undefined) return;

        valueElement.textContent = `${value}%`;
        progressBar.style.width = `${value}%`;

        // 根据使用率设置进度条颜色
        progressBar.className = 'progress-bar';
        if (value >= 90) {
            progressBar.classList.add('bg-danger');
        } else if (value >= 70) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-success');
        }
    }

    updateServiceStatus() {
        const serviceList = document.getElementById('serviceList');
        if (!serviceList || !this.systemData.services) return;

        serviceList.innerHTML = '';

        this.systemData.services.forEach(service => {
            const serviceElement = this.createServiceElement(service);
            serviceList.appendChild(serviceElement);
        });
    }

    createServiceElement(service) {
        const template = document.getElementById('serviceItemTemplate');
        if (!template) return document.createElement('div');

        const element = template.content.cloneNode(true);

        // 设置服务图标
        const iconElement = element.querySelector('.service-icon');
        if (iconElement) {
            iconElement.className = this.getServiceIcon(service.type);
        }

        // 设置服务名称
        const nameElement = element.querySelector('.service-name');
        if (nameElement) {
            nameElement.textContent = service.name;
        }

        // 设置服务状态
        const statusBadge = element.querySelector('.service-status-badge');
        if (statusBadge) {
            const statusInfo = this.getStatusInfo(service.status);
            statusBadge.textContent = statusInfo.text;
            statusBadge.className = `badge ${statusInfo.class}`;
        }

        // 设置响应时间
        const responseTimeElement = element.querySelector('.service-response-time');
        if (responseTimeElement && service.response_time) {
            responseTimeElement.textContent = `${service.response_time}ms`;
        }

        return element;
    }

    updateSystemAlerts() {
        const alertsContainer = document.getElementById('systemAlerts');
        if (!alertsContainer || !this.systemData.alerts) return;

        alertsContainer.innerHTML = '';

        if (this.systemData.alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <i class="fas fa-info-circle me-2"></i>
                    系统运行正常，暂无告警信息
                </div>
            `;
            return;
        }

        this.systemData.alerts.forEach(alert => {
            const alertElement = this.createAlertElement(alert);
            alertsContainer.appendChild(alertElement);
        });
    }

    createAlertElement(alert) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${alert.level} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');

        const icon = this.getAlertIcon(alert.level);
        alertDiv.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            <strong>${alert.title}</strong>
            <p class="mb-0">${alert.message}</p>
            <small class="text-muted">${this.formatTime(alert.timestamp)}</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        return alertDiv;
    }

    getStatusInfo(status) {
        const statusMap = {
            'healthy': {
                text: '正常',
                class: 'bg-success',
                dotClass: 'status-dot-success'
            },
            'warning': {
                text: '警告',
                class: 'bg-warning',
                dotClass: 'status-dot-warning'
            },
            'error': {
                text: '错误',
                class: 'bg-danger',
                dotClass: 'status-dot-error'
            },
            'unknown': {
                text: '未知',
                class: 'bg-secondary',
                dotClass: 'status-dot-unknown'
            }
        };

        return statusMap[status] || statusMap.unknown;
    }

    getServiceIcon(type) {
        const iconMap = {
            'database': 'fas fa-database',
            'api': 'fas fa-server',
            'cache': 'fas fa-memory',
            'queue': 'fas fa-tasks',
            'storage': 'fas fa-hdd',
            'network': 'fas fa-network-wired',
            'security': 'fas fa-shield-alt',
            'monitoring': 'fas fa-chart-line'
        };
        return iconMap[type] || 'fas fa-cog';
    }

    getAlertIcon(level) {
        const iconMap = {
            'info': 'info-circle',
            'warning': 'exclamation-triangle',
            'error': 'exclamation-circle',
            'success': 'check-circle'
        };
        return iconMap[level] || 'info-circle';
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    startAutoRefresh() {
        // 每3分钟自动刷新一次系统状态
        this.refreshInterval = setInterval(() => {
            this.loadSystemStatus();
        }, 180000);
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

        const container = document.querySelector('.system-status-container');
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
window.SystemStatusComponent = SystemStatusComponent;
