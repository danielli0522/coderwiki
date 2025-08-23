/**
 * Task Detail Page JavaScript
 * Handles task detail display, real-time updates, and interactions
 */

class TaskDetailManager {
    constructor(taskId) {
        this.taskId = taskId;
        this.apiClient = new ApiClient();
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.startRealtimeUpdates();
        this.loadRelatedTasks();
        this.loadTaskLogs();
    }

    bindEvents() {
        // Auto-refresh controls
        document.getElementById('autoRefreshToggle')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startRealtimeUpdates();
            } else {
                this.stopRealtimeUpdates();
            }
        });

        // Refresh buttons
        document.getElementById('refreshTaskBtn')?.addEventListener('click', () => {
            this.loadTaskDetails();
        });

        document.getElementById('refreshLogsBtn')?.addEventListener('click', () => {
            this.loadTaskLogs();
        });

        // Copy result functionality
        document.getElementById('copyResultBtn')?.addEventListener('click', () => {
            this.copyResult();
        });

        // Download result functionality
        document.getElementById('downloadResultBtn')?.addEventListener('click', () => {
            this.downloadResult();
        });

        // View full result modal
        document.getElementById('viewFullResultBtn')?.addEventListener('click', () => {
            this.showFullResultModal();
        });

        // Task action buttons
        document.getElementById('cancelTaskBtn')?.addEventListener('click', () => {
            this.cancelTask();
        });

        document.getElementById('retryTaskBtn')?.addEventListener('click', () => {
            this.retryTask();
        });

        document.getElementById('deleteTaskBtn')?.addEventListener('click', () => {
            this.deleteTask();
        });
    }

    async loadTaskDetails() {
        try {
            const response = await this.apiClient.get(`/api/tasks/${this.taskId}`);
            if (response.success) {
                this.updateTaskDisplay(response.task);
            } else {
                this.showError('加载任务详情失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error loading task details:', error);
            this.showError('加载任务详情失败: ' + error.message);
        }
    }

    updateTaskDisplay(task) {
        // Update status badge
        const statusBadge = document.getElementById('taskStatusBadge');
        if (statusBadge) {
            statusBadge.className = `badge ${this.getStatusBadgeClass(task.status)}`;
            statusBadge.innerHTML = `<i class="fas fa-circle me-1"></i>${this.getStatusText(task.status)}`;
        }

        // Update progress bar
        const progressBar = document.getElementById('taskProgressBar');
        const progressText = document.getElementById('taskProgressText');
        if (progressBar && progressText) {
            progressBar.style.width = `${task.progress || 0}%`;
            progressBar.setAttribute('aria-valuenow', task.progress || 0);
            progressText.textContent = `${task.progress || 0}%`;
        }

        // Update execution time
        const executionTime = document.getElementById('executionTime');
        if (executionTime) {
            executionTime.textContent = `${task.execution_time || 0} 秒`;
        }

        // Update retry count
        const retryCount = document.getElementById('retryCount');
        if (retryCount) {
            retryCount.textContent = task.retry_count || 0;
        }

        // Update status indicator for running tasks
        if (task.status === 'running') {
            this.showRunningIndicator();
        } else {
            this.hideRunningIndicator();
        }

        // Update action buttons based on status
        this.updateActionButtons(task.status);

        // Show result if task is completed
        if (task.status === 'completed' && task.result) {
            this.showTaskResult(task.result);
        }

        // Show error if task failed
        if (task.status === 'failed' && task.error_message) {
            this.showTaskError(task.error_message, task.error_stacktrace);
        }
    }

    async loadTaskLogs() {
        try {
            const response = await this.apiClient.get(`/api/tasks/${this.taskId}/logs`);
            if (response.success) {
                this.updateLogsDisplay(response.logs);
            }
        } catch (error) {
            console.error('Error loading task logs:', error);
        }
    }

    updateLogsDisplay(logs) {
        const logsContainer = document.getElementById('taskLogs');
        if (!logsContainer) return;

        if (!logs || logs.length === 0) {
            logsContainer.innerHTML = '<div class="text-muted">暂无日志</div>';
            return;
        }

        logsContainer.innerHTML = logs.map(log => `
            <div class="log-entry mb-1">
                <span class="text-muted">[${this.formatDateTime(log.timestamp)}]</span>
                <span class="text-${this.getLogLevelClass(log.level)}">${log.level}</span>
                <span>${this.escapeHtml(log.message)}</span>
            </div>
        `).join('');

        // Auto-scroll to bottom for new logs
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    async loadRelatedTasks() {
        try {
            const response = await this.apiClient.get(`/api/tasks/${this.taskId}/related`);
            if (response.success) {
                this.updateRelatedTasksDisplay(response.related_tasks);
            }
        } catch (error) {
            console.error('Error loading related tasks:', error);
            const relatedContainer = document.getElementById('relatedTasks');
            if (relatedContainer) {
                relatedContainer.innerHTML = '<div class="text-muted">无法加载相关任务</div>';
            }
        }
    }

    updateRelatedTasksDisplay(relatedTasks) {
        const relatedContainer = document.getElementById('relatedTasks');
        if (!relatedContainer) return;

        if (!relatedTasks || relatedTasks.length === 0) {
            relatedContainer.innerHTML = '<div class="text-muted">暂无相关任务</div>';
            return;
        }

        relatedContainer.innerHTML = `
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>任务名称</th>
                            <th>状态</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${relatedTasks.map(task => `
                            <tr>
                                <td>
                                    <a href="/tasks/${task.id}" class="text-decoration-none">
                                        ${this.escapeHtml(task.name)}
                                    </a>
                                </td>
                                <td>
                                    <span class="badge ${this.getStatusBadgeClass(task.status)}">
                                        ${this.getStatusText(task.status)}
                                    </span>
                                </td>
                                <td>${this.formatDateTime(task.created_at)}</td>
                                <td>
                                    <a href="/tasks/${task.id}" class="btn btn-sm btn-outline-primary">
                                        查看详情
                                    </a>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    startRealtimeUpdates() {
        // Update task details every 3 seconds if running
        this.updateInterval = setInterval(() => {
            this.loadTaskDetails();
            this.loadTaskLogs();
        }, 3000);
    }

    stopRealtimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    showRunningIndicator() {
        const indicator = document.getElementById('runningIndicator');
        if (indicator) {
            indicator.style.display = 'inline-block';
        }
    }

    hideRunningIndicator() {
        const indicator = document.getElementById('runningIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    updateActionButtons(status) {
        const cancelBtn = document.getElementById('cancelTaskBtn');
        const retryBtn = document.getElementById('retryTaskBtn');
        const deleteBtn = document.getElementById('deleteTaskBtn');

        // Hide all buttons first
        if (cancelBtn) cancelBtn.style.display = 'none';
        if (retryBtn) retryBtn.style.display = 'none';
        if (deleteBtn) deleteBtn.style.display = 'none';

        // Show buttons based on status
        if (status === 'running' && cancelBtn) {
            cancelBtn.style.display = 'inline-block';
        } else if (status === 'failed' && retryBtn) {
            retryBtn.style.display = 'inline-block';
        }

        if (status === 'completed' || status === 'failed') {
            if (deleteBtn) deleteBtn.style.display = 'inline-block';
        }
    }

    showTaskResult(result) {
        const resultContainer = document.getElementById('taskResultContainer');
        const resultContent = document.getElementById('taskResult');
        
        if (resultContainer && resultContent) {
            resultContainer.style.display = 'block';
            resultContent.textContent = JSON.stringify(result, null, 2);
        }
    }

    showTaskError(errorMessage, errorStacktrace) {
        const errorContainer = document.getElementById('taskErrorContainer');
        const errorMessageElement = document.getElementById('taskErrorMessage');
        const errorStacktraceElement = document.getElementById('taskErrorStacktrace');
        
        if (errorContainer && errorMessageElement) {
            errorContainer.style.display = 'block';
            errorMessageElement.textContent = errorMessage;
            
            if (errorStacktrace && errorStacktraceElement) {
                errorStacktraceElement.textContent = errorStacktrace;
            }
        }
    }

    showFullResultModal() {
        const resultContent = document.getElementById('taskResult');
        const modalResultContent = document.getElementById('modalResultContent');
        
        if (resultContent && modalResultContent) {
            modalResultContent.textContent = resultContent.textContent;
            const modal = new bootstrap.Modal(document.getElementById('resultModal'));
            modal.show();
        }
    }

    async cancelTask() {
        if (!confirm('确定要取消这个任务吗？')) return;

        try {
            const response = await this.apiClient.post(`/api/tasks/${this.taskId}/cancel`);
            if (response.success) {
                this.showSuccess('任务已取消');
                this.loadTaskDetails();
            } else {
                this.showError('取消任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error canceling task:', error);
            this.showError('取消任务失败: ' + error.message);
        }
    }

    async retryTask() {
        try {
            const response = await this.apiClient.post(`/api/tasks/${this.taskId}/retry`);
            if (response.success) {
                this.showSuccess('任务已重新启动');
                this.loadTaskDetails();
            } else {
                this.showError('重试任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error retrying task:', error);
            this.showError('重试任务失败: ' + error.message);
        }
    }

    async deleteTask() {
        if (!confirm('确定要删除这个任务吗？此操作不可恢复。')) return;

        try {
            const response = await this.apiClient.delete(`/api/tasks/${this.taskId}`);
            if (response.success) {
                this.showSuccess('任务已删除');
                window.location.href = '/tasks';
            } else {
                this.showError('删除任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showError('删除任务失败: ' + error.message);
        }
    }

    copyResult() {
        const resultContent = document.getElementById('taskResult');
        if (!resultContent) return;

        navigator.clipboard.writeText(resultContent.textContent).then(() => {
            this.showSuccess('结果已复制到剪贴板');
        }).catch(error => {
            this.showError('复制失败: ' + error.message);
        });
    }

    downloadResult() {
        const resultContent = document.getElementById('taskResult');
        if (!resultContent) return;

        const blob = new Blob([resultContent.textContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `task_${this.taskId}_result.json`;
        a.click();
        URL.revokeObjectURL(url);
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

    getLogLevelClass(level) {
        const classes = {
            'DEBUG': 'info',
            'INFO': 'success',
            'WARNING': 'warning',
            'ERROR': 'danger',
            'CRITICAL': 'danger'
        };
        return classes[level] || 'info';
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
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
        this.stopRealtimeUpdates();
    }
}

// Initialize task detail manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Get task ID from URL or data attribute
    const taskId = document.body.dataset.taskId || 
                   window.location.pathname.split('/').pop() || 
                   new URLSearchParams(window.location.search).get('id');
    
    if (taskId) {
        window.taskDetailManager = new TaskDetailManager(taskId);
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.taskDetailManager) {
        window.taskDetailManager.destroy();
    }
});