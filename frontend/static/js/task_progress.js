/**
 * Task Progress Monitoring JavaScript
 * Handles real-time task progress monitoring, charts, and system performance
 */

class TaskProgressMonitor {
    constructor() {
        this.apiClient = new ApiClient();
        this.updateInterval = null;
        this.refreshInterval = 180000; // 3 minutes default
        this.charts = {};
        this.settings = {
            autoRefresh: true,
            refreshInterval: 180000,
            maxTasksDisplay: 50,
            enableNotifications: true,
            enableSound: true
        };
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSettings();
        this.initializeCharts();
        this.startMonitoring();
    }

    bindEvents() {
        // Auto refresh toggle
        document.getElementById('autoRefreshToggle')?.addEventListener('change', (e) => {
            this.settings.autoRefresh = e.target.checked;
            this.saveSettings();
            if (this.settings.autoRefresh) {
                this.startMonitoring();
            } else {
                this.stopMonitoring();
            }
        });

        // Refresh button
        document.getElementById('refreshAllBtn')?.addEventListener('click', () => {
            this.refreshAllData();
        });

        // Settings button
        document.getElementById('settingsBtn')?.addEventListener('click', () => {
            this.showSettingsModal();
        });

        // Filters
        document.getElementById('taskTypeFilter')?.addEventListener('change', () => {
            this.loadActiveTasks();
        });

        document.getElementById('sortBy')?.addEventListener('change', () => {
            this.loadActiveTasks();
        });

        // Save settings
        document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
            this.saveSettingsFromModal();
        });
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('taskProgressSettings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
            this.applySettings();
        }
    }

    saveSettings() {
        localStorage.setItem('taskProgressSettings', JSON.stringify(this.settings));
    }

    applySettings() {
        const autoRefreshToggle = document.getElementById('autoRefreshToggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.checked = this.settings.autoRefresh;
        }
    }

    saveSettingsFromModal() {
        const refreshInterval = document.getElementById('refreshInterval')?.value;
        const maxTasksDisplay = document.getElementById('maxTasksDisplay')?.value;
        const enableNotifications = document.getElementById('enableNotifications')?.checked;
        const enableSound = document.getElementById('enableSound')?.checked;

        this.settings.refreshInterval = parseInt(refreshInterval) || 3000;
        this.settings.maxTasksDisplay = parseInt(maxTasksDisplay) || 50;
        this.settings.enableNotifications = enableNotifications;
        this.settings.enableSound = enableSound;

        this.saveSettings();

        // Restart monitoring with new settings
        this.stopMonitoring();
        if (this.settings.autoRefresh) {
            this.startMonitoring();
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        if (modal) {
            modal.hide();
        }

        this.showSuccess('设置已保存');
    }

    showSettingsModal() {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));

        // Set current values
        document.getElementById('refreshInterval').value = this.settings.refreshInterval;
        document.getElementById('maxTasksDisplay').value = this.settings.maxTasksDisplay;
        document.getElementById('enableNotifications').checked = this.settings.enableNotifications;
        document.getElementById('enableSound').checked = this.settings.enableSound;

        modal.show();
    }

    initializeCharts() {
        // Progress trend chart
        const progressCtx = document.getElementById('progressChart');
        if (progressCtx) {
            this.charts.progress = new Chart(progressCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '平均进度',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        // Task type distribution chart
        const taskTypeCtx = document.getElementById('taskTypeChart');
        if (taskTypeCtx) {
            this.charts.taskType = new Chart(taskTypeCtx, {
                type: 'doughnut',
                data: {
                    labels: ['代码分析', '文档生成', '数据处理', '系统维护'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 205, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }

    startMonitoring() {
        this.refreshAllData();
        this.updateInterval = setInterval(() => {
            this.refreshAllData();
        }, this.settings.refreshInterval);
    }

    stopMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async refreshAllData() {
        try {
            await Promise.all([
                this.loadTaskStatistics(),
                this.loadActiveTasks(),
                this.loadQueueStatus(),
                this.loadSystemPerformance()
            ]);
        } catch (error) {
            console.error('Error refreshing data:', error);
        }
    }

    async loadTaskStatistics() {
        try {
            const response = await this.apiClient.get('/tasks/statistics');
            if (response.success) {
                this.updateStatistics(response.statistics);
                this.updateCharts(response.statistics);
            }
        } catch (error) {
            console.error('Error loading task statistics:', error);
        }
    }

    updateStatistics(statistics) {
        // Update total tasks count
        const totalTasksCount = document.getElementById('totalTasksCount');
        if (totalTasksCount) {
            totalTasksCount.textContent = statistics.total || 0;
        }

        // Update running tasks count
        const runningTasksCount = document.getElementById('runningTasksCount');
        if (runningTasksCount) {
            runningTasksCount.textContent = statistics.running || 0;
        }

        // Update average progress
        const averageProgress = document.getElementById('averageProgress');
        if (averageProgress) {
            averageProgress.textContent = `${Math.round(statistics.average_progress || 0)}%`;
        }

        // Update success rate
        const successRate = document.getElementById('successRate');
        if (successRate) {
            successRate.textContent = `${Math.round(statistics.success_rate || 0)}%`;
        }
    }

    updateCharts(statistics) {
        // Update progress trend chart
        if (this.charts.progress && statistics.progress_history) {
            const now = new Date().toLocaleTimeString('zh-CN');
            this.charts.progress.data.labels.push(now);
            this.charts.progress.data.datasets[0].data.push(statistics.average_progress || 0);

            // Keep only last 20 data points
            if (this.charts.progress.data.labels.length > 20) {
                this.charts.progress.data.labels.shift();
                this.charts.progress.data.datasets[0].data.shift();
            }

            this.charts.progress.update('none');
        }

        // Update task type distribution chart
        if (this.charts.taskType && statistics.task_types) {
            this.charts.taskType.data.datasets[0].data = [
                statistics.task_types.analysis || 0,
                statistics.task_types.generation || 0,
                statistics.task_types.processing || 0,
                statistics.task_types.maintenance || 0
            ];
            this.charts.taskType.update('none');
        }
    }

    async loadActiveTasks() {
        try {
            const filter = document.getElementById('taskTypeFilter')?.value || '';
            const sortBy = document.getElementById('sortBy')?.value || 'progress';

            const response = await this.apiClient.get('/tasks/active', {
                filter: filter,
                sort: sortBy,
                limit: this.settings.maxTasksDisplay
            });

            if (response.success) {
                this.updateActiveTasksList(response.tasks);
            }
        } catch (error) {
            console.error('Error loading active tasks:', error);
        }
    }

    updateActiveTasksList(tasks) {
        const container = document.getElementById('activeTasksList');
        if (!container) return;

        if (!tasks || tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2"></i>
                    <p>暂无活跃任务</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>任务名称</th>
                            <th>类型</th>
                            <th>进度</th>
                            <th>状态</th>
                            <th>运行时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tasks.map(task => this.createTaskRow(task)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    createTaskRow(task) {
        const progressClass = task.progress >= 80 ? 'bg-success' :
                           task.progress >= 50 ? 'bg-warning' : 'bg-info';

        return `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="task-status-indicator ${task.status} me-2"></div>
                        <div>
                            <div class="fw-bold">${this.escapeHtml(task.name)}</div>
                            <small class="text-muted">${this.escapeHtml(task.description || '')}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-secondary">${this.getTaskTypeText(task.task_type)}</span>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress me-2" style="width: 60px; height: 8px;">
                            <div class="progress-bar ${progressClass}"
                                 role="progressbar"
                                 style="width: ${task.progress || 0}%"
                                 aria-valuenow="${task.progress || 0}"
                                 aria-valuemin="0"
                                 aria-valuemax="100">
                            </div>
                        </div>
                        <span class="small">${task.progress || 0}%</span>
                    </div>
                </td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(task.status)}">
                        ${this.getStatusText(task.status)}
                    </span>
                </td>
                <td>
                    <small class="text-muted">${this.formatDuration(task.execution_time)}</small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary"
                                onclick="taskProgressMonitor.showTaskDetail('${task.id}')"
                                title="查看详情">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${task.status === 'running' ? `
                            <button class="btn btn-outline-warning"
                                    onclick="taskProgressMonitor.cancelTask('${task.id}')"
                                    title="取消任务">
                                <i class="fas fa-stop"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }

    async loadQueueStatus() {
        try {
            const response = await this.apiClient.get('/tasks/queue/status');
            if (response.success) {
                this.updateQueueStatus(response.queue_status);
            }
        } catch (error) {
            console.error('Error loading queue status:', error);
        }
    }

    updateQueueStatus(queueStatus) {
        const pendingCount = document.getElementById('pendingQueueCount');
        const runningCount = document.getElementById('runningQueueCount');
        const completedCount = document.getElementById('completedQueueCount');
        const failedCount = document.getElementById('failedQueueCount');

        if (pendingCount) pendingCount.textContent = queueStatus.pending || 0;
        if (runningCount) runningCount.textContent = queueStatus.running || 0;
        if (completedCount) completedCount.textContent = queueStatus.completed || 0;
        if (failedCount) failedCount.textContent = queueStatus.failed || 0;
    }

    async loadSystemPerformance() {
        try {
            const response = await this.apiClient.get('/system/performance');
            if (response.success) {
                this.updateSystemPerformance(response.performance);
            }
        } catch (error) {
            console.error('Error loading system performance:', error);
        }
    }

    updateSystemPerformance(performance) {
        // Update CPU usage
        const cpuUsage = document.getElementById('cpuUsage');
        const cpuProgressBar = document.getElementById('cpuProgressBar');
        if (cpuUsage && cpuProgressBar) {
            cpuUsage.textContent = `${Math.round(performance.cpu || 0)}%`;
            cpuProgressBar.style.width = `${performance.cpu || 0}%`;
        }

        // Update memory usage
        const memoryUsage = document.getElementById('memoryUsage');
        const memoryProgressBar = document.getElementById('memoryProgressBar');
        if (memoryUsage && memoryProgressBar) {
            memoryUsage.textContent = `${Math.round(performance.memory || 0)}%`;
            memoryProgressBar.style.width = `${performance.memory || 0}%`;
        }

        // Update disk usage
        const diskUsage = document.getElementById('diskUsage');
        const diskProgressBar = document.getElementById('diskProgressBar');
        if (diskUsage && diskProgressBar) {
            diskUsage.textContent = `${Math.round(performance.disk || 0)}%`;
            diskProgressBar.style.width = `${performance.disk || 0}%`;
        }
    }

    async showTaskDetail(taskId) {
        try {
            const response = await this.apiClient.get(`/tasks/${taskId}`);
            if (response.success) {
                this.showTaskDetailModal(response.task);
            }
        } catch (error) {
            console.error('Error loading task detail:', error);
            this.showError('加载任务详情失败');
        }
    }

    showTaskDetailModal(task) {
        const modalBody = document.getElementById('taskDetailModalBody');
        if (!modalBody) return;

        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label fw-bold">任务名称</label>
                        <p class="form-control-plaintext">${this.escapeHtml(task.name)}</p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">状态</label>
                        <p>
                            <span class="badge ${this.getStatusBadgeClass(task.status)}">
                                ${this.getStatusText(task.status)}
                            </span>
                        </p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">进度</label>
                        <div class="progress">
                            <div class="progress-bar bg-success"
                                 role="progressbar"
                                 style="width: ${task.progress || 0}%"
                                 aria-valuenow="${task.progress || 0}"
                                 aria-valuemin="0"
                                 aria-valuemax="100">
                                ${task.progress || 0}%
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label fw-bold">创建时间</label>
                        <p class="form-control-plaintext">${this.formatDateTime(task.created_at)}</p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">运行时间</label>
                        <p class="form-control-plaintext">${this.formatDuration(task.execution_time)}</p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">重试次数</label>
                        <p class="form-control-plaintext">${task.retry_count || 0}</p>
                    </div>
                </div>
            </div>
            ${task.description ? `
                <div class="mb-3">
                    <label class="form-label fw-bold">描述</label>
                    <p class="form-control-plaintext">${this.escapeHtml(task.description)}</p>
                </div>
            ` : ''}
        `;

        const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
        modal.show();
    }

    async cancelTask(taskId) {
        if (!confirm('确定要取消这个任务吗？')) return;

        try {
            const response = await this.apiClient.post(`/tasks/${taskId}/cancel`);
            if (response.success) {
                this.showSuccess('任务已取消');
                this.loadActiveTasks();
            } else {
                this.showError('取消任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error canceling task:', error);
            this.showError('取消任务失败: ' + error.message);
        }
    }

    // Utility methods
    getStatusBadgeClass(status) {
        const classes = {
            'pending': 'bg-secondary',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        };
        return classes[status] || 'bg-secondary';
    }

    getStatusText(status) {
        const texts = {
            'pending': '待处理',
            'running': '进行中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        };
        return texts[status] || status;
    }

    getTaskTypeText(type) {
        const texts = {
            'analysis': '代码分析',
            'generation': '文档生成',
            'processing': '数据处理',
            'maintenance': '系统维护'
        };
        return texts[type] || type;
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    formatDuration(seconds) {
        if (!seconds) return '-';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showToast(message, type = 'info') {
        if (!this.settings.enableNotifications) return;

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.appendChild(toast);
        document.body.appendChild(container);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(container);
        });
    }

    // Cleanup when page is unloaded
    destroy() {
        this.stopMonitoring();
        if (this.charts.progress) {
            this.charts.progress.destroy();
        }
        if (this.charts.taskType) {
            this.charts.taskType.destroy();
        }
    }
}

// Initialize task progress monitor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.taskProgressMonitor = new TaskProgressMonitor();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.taskProgressMonitor) {
        window.taskProgressMonitor.destroy();
    }
});
