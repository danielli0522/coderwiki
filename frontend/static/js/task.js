/**
 * Task Management JavaScript
 * Handles task list display, filtering, and management
 */

class TaskManager {
    constructor() {
        this.tasks = [];
        this.filteredTasks = [];
        this.currentFilter = '';
        this.currentSearch = '';
        this.apiClient = window.api || new ApiClient();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTasks();
        this.startRealtimeUpdates();
    }

    bindEvents() {
        // Search functionality
        document.getElementById('taskSearch')?.addEventListener('input', (e) => {
            this.currentSearch = e.target.value.toLowerCase();
            this.filterTasks();
        });

        // Status filter
        document.getElementById('taskStatusFilter')?.addEventListener('change', (e) => {
            this.currentFilter = e.target.value;
            this.filterTasks();
        });

        // Add task button
        document.getElementById('addTaskBtn')?.addEventListener('click', () => {
            this.showAddTaskModal();
        });

        // Refresh button
        document.getElementById('refreshTasksBtn')?.addEventListener('click', () => {
            this.loadTasks();
        });

        // Task action buttons (delegated)
        document.getElementById('taskTableBody')?.addEventListener('click', (e) => {
            const target = e.target.closest('button');
            if (!target) return;

            const taskId = target.dataset.taskId;
            const action = target.dataset.action;

            if (action === 'view') {
                this.viewTask(taskId);
            } else if (action === 'cancel') {
                this.cancelTask(taskId);
            } else if (action === 'retry') {
                this.retryTask(taskId);
            } else if (action === 'delete') {
                this.deleteTask(taskId);
            }
        });

        // Bulk operations
        document.getElementById('bulkDeleteBtn')?.addEventListener('click', () => {
            this.bulkDeleteTasks();
        });

        document.getElementById('clearSelectionBtn')?.addEventListener('click', () => {
            this.clearSelection();
        });

        // Select all checkbox
        document.getElementById('selectAllTasks')?.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.task-checkbox');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            this.updateBulkActionsVisibility();
        });
    }

    async loadTasks() {
        try {
            // 清除任务相关的缓存，确保获取最新数据
            this.apiClient.clearCache();

            const response = await this.apiClient.get('/tasks', {}, { skipCache: true });
            if (response.success) {
                this.tasks = response.tasks || [];
                this.updateTaskStats();
                this.filterTasks();
                this.renderTasks();
            } else {
                this.showError('加载任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showError('加载任务失败: ' + error.message);
        }
    }

    filterTasks() {
        this.filteredTasks = this.tasks.filter(task => {
            const matchesSearch = !this.currentSearch ||
                task.name.toLowerCase().includes(this.currentSearch) ||
                task.description.toLowerCase().includes(this.currentSearch);

            const matchesFilter = !this.currentFilter || task.status === this.currentFilter;

            return matchesSearch && matchesFilter;
        });

        this.renderTasks();
    }

    renderTasks() {
        const tbody = document.getElementById('taskTableBody');
        if (!tbody) return;

        if (this.filteredTasks.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        <div class="task-empty-state">
                            <i class="fas fa-inbox fa-2x mb-2"></i>
                            <p>${this.currentSearch || this.currentFilter ? '没有找到匹配的任务' : '暂无任务'}</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.filteredTasks.map(task => `
            <tr class="task-row" data-task-id="${task.id}">
                <td>
                    <div class="form-check">
                        <input class="form-check-input task-checkbox"
                               type="checkbox"
                               value="${task.id}"
                               onchange="taskManager.updateBulkActionsVisibility()">
                    </div>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="task-status-indicator ${task.status} me-2"></div>
                        <div>
                            <div class="fw-bold">${this.escapeHtml(task.name)}</div>
                            <small class="text-muted task-description-truncate">${this.escapeHtml(task.description || '')}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(task.status)}">
                        ${this.getStatusText(task.status)}
                    </span>
                </td>
                <td>
                    <span class="badge ${this.getPriorityBadgeClass(task.priority)}">
                        ${this.getPriorityText(task.priority)}
                    </span>
                </td>
                <td>
                    <div class="task-time">
                        <div class="task-time-relative">${this.getTimeAgo(task.created_at)}</div>
                        <small>${this.formatDate(task.created_at)}</small>
                    </div>
                </td>
                <td>
                    <div class="task-actions btn-group btn-group-sm">
                        <button class="btn btn-outline-primary"
                                data-action="view"
                                data-task-id="${task.id}"
                                title="查看详情">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${this.getActionButtons(task)}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getActionButtons(task) {
        let buttons = '';

        if (task.status === 'running') {
            buttons += `
                <button class="btn btn-outline-warning"
                        data-action="cancel"
                        data-task-id="${task.id}"
                        title="取消任务">
                    <i class="fas fa-stop"></i>
                </button>
            `;
        } else if (task.status === 'failed') {
            buttons += `
                <button class="btn btn-outline-warning"
                        data-action="retry"
                        data-task-id="${task.id}"
                        title="重试任务">
                    <i class="fas fa-redo"></i>
                </button>
            `;
        }

        if (task.status === 'completed' || task.status === 'failed') {
            buttons += `
                <button class="btn btn-outline-danger"
                        data-action="delete"
                        data-task-id="${task.id}"
                        title="删除任务">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }

        return buttons;
    }

    updateTaskStats() {
        const stats = {
            total: this.tasks.length,
            running: this.tasks.filter(t => t.status === 'running').length,
            completed: this.tasks.filter(t => t.status === 'completed').length,
            failed: this.tasks.filter(t => t.status === 'failed').length
        };

        // Update stat cards
        this.updateStatCard('总任务', stats.total, 'fas fa-tasks', 'bg-primary');
        this.updateStatCard('进行中', stats.running, 'fas fa-clock', 'bg-warning');
        this.updateStatCard('已完成', stats.completed, 'fas fa-check-circle', 'bg-success');
        this.updateStatCard('失败', stats.failed, 'fas fa-exclamation-triangle', 'bg-danger');
    }

    updateStatCard(title, value, icon, bgClass) {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const titleElement = card.querySelector('.card-title');
            if (titleElement && titleElement.textContent === title) {
                const valueElement = card.querySelector('h2');
                if (valueElement) {
                    valueElement.textContent = value;
                }
            }
        });
    }

    async viewTask(taskId) {
        try {
            const response = await this.apiClient.get(`/tasks/${taskId}`);
            if (response.success) {
                this.showTaskDetail(response.task);
            } else {
                this.showError('加载任务详情失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error loading task details:', error);
            this.showError('加载任务详情失败: ' + error.message);
        }
    }

    async cancelTask(taskId) {
        if (!confirm('确定要取消这个任务吗？')) return;

        try {
            const response = await this.apiClient.post(`/tasks/${taskId}/cancel`);
            if (response.success) {
                this.showSuccess('任务已取消');
                this.loadTasks();
            } else {
                this.showError('取消任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error canceling task:', error);
            this.showError('取消任务失败: ' + error.message);
        }
    }

    async retryTask(taskId) {
        try {
            const response = await this.apiClient.post(`/tasks/${taskId}/retry`);
            if (response.success) {
                this.showSuccess('任务已重新启动');
                this.loadTasks();
            } else {
                this.showError('重试任务失败: ' + (response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error retrying task:', error);
            this.showError('重试任务失败: ' + error.message);
        }
    }

    async deleteTask(taskId, showNotification = true) {
        if (showNotification && !confirm('确定要删除这个任务吗？此操作不可恢复。')) return;

        try {
            const response = await this.apiClient.delete(`/tasks/${taskId}`);
            if (response.success) {
                if (showNotification) {
                    this.showSuccess('任务已删除');
                    this.loadTasks();
                }
                return Promise.resolve();
            } else {
                if (showNotification) {
                    this.showError('删除任务失败: ' + (response.error || '未知错误'));
                }
                return Promise.reject(new Error(response.error || '未知错误'));
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            if (showNotification) {
                this.showError('删除任务失败: ' + error.message);
            }
            return Promise.reject(error);
        }
    }

    showAddTaskModal() {
        // For now, redirect to the main dashboard to create analysis tasks
        window.location.href = '/dashboard';
    }

    showTaskDetail(task) {
        // Create modal for task details
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">任务详情</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <strong>任务名称:</strong> ${this.escapeHtml(task.name)}<br>
                                <strong>状态:</strong>
                                <span class="badge ${this.getStatusBadgeClass(task.status)}">
                                    ${this.getStatusText(task.status)}
                                </span><br>
                                <strong>优先级:</strong>
                                <span class="badge ${this.getPriorityBadgeClass(task.priority)}">
                                    ${this.getPriorityText(task.priority)}
                                </span><br>
                                <strong>创建时间:</strong> ${this.formatDate(task.created_at)}<br>
                                <strong>更新时间:</strong> ${this.formatDate(task.updated_at)}<br>
                            </div>
                            <div class="col-md-6">
                                <strong>进度:</strong> ${task.progress || 0}%<br>
                                <strong>执行时间:</strong> ${task.execution_time || 0}秒<br>
                                <strong>重试次数:</strong> ${task.retry_count || 0}<br>
                            </div>
                        </div>
                        ${task.description ? `
                            <div class="mt-3">
                                <strong>描述:</strong><br>
                                <p>${this.escapeHtml(task.description)}</p>
                            </div>
                        ` : ''}
                        ${task.result ? `
                            <div class="mt-3">
                                <strong>结果:</strong><br>
                                <pre class="bg-light p-3 rounded">${this.escapeHtml(JSON.stringify(task.result, null, 2))}</pre>
                            </div>
                        ` : ''}
                        ${task.error_message ? `
                            <div class="mt-3">
                                <strong>错误信息:</strong><br>
                                <div class="alert alert-danger">${this.escapeHtml(task.error_message)}</div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        ${this.getTaskDetailActions(task)}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    getTaskDetailActions(task) {
        let actions = '';

        if (task.status === 'running') {
            actions += `
                <button type="button" class="btn btn-warning" onclick="taskManager.cancelTask('${task.id}')">
                    <i class="fas fa-stop"></i> 取消任务
                </button>
            `;
        } else if (task.status === 'failed') {
            actions += `
                <button type="button" class="btn btn-warning" onclick="taskManager.retryTask('${task.id}')">
                    <i class="fas fa-redo"></i> 重试任务
                </button>
            `;
        }

        if (task.status === 'completed' || task.status === 'failed') {
            actions += `
                <button type="button" class="btn btn-danger" onclick="taskManager.deleteTask('${task.id}')">
                    <i class="fas fa-trash"></i> 删除任务
                </button>
            `;
        }

        return actions;
    }

    startRealtimeUpdates() {
        // Poll for task updates every 30 seconds for better responsiveness
        setInterval(() => {
            this.loadTasks();
        }, 30000);
    }

    // Bulk operations
    bulkDeleteTasks() {
        const selectedTasks = this.getSelectedTasks();
        if (selectedTasks.length === 0) {
            this.showError('请先选择要删除的任务');
            return;
        }

        if (!confirm(`确定要删除选中的 ${selectedTasks.length} 个任务吗？此操作不可恢复。`)) {
            return;
        }

        Promise.all(selectedTasks.map(taskId => this.deleteTask(taskId, false)))
            .then(() => {
                this.showSuccess(`成功删除 ${selectedTasks.length} 个任务`);
                this.clearSelection();
                this.loadTasks();
            })
            .catch(error => {
                this.showError('批量删除任务时出错: ' + error.message);
            });
    }

    getSelectedTasks() {
        const checkboxes = document.querySelectorAll('.task-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    clearSelection() {
        const checkboxes = document.querySelectorAll('.task-checkbox');
        checkboxes.forEach(cb => cb.checked = false);
        this.updateBulkActionsVisibility();
    }

    updateBulkActionsVisibility() {
        const selectedCount = this.getSelectedTasks().length;
        const bulkActions = document.getElementById('bulkActions');
        const selectedCountSpan = document.getElementById('selectedCount');

        if (bulkActions) {
            bulkActions.style.display = selectedCount > 0 ? 'block' : 'none';
        }

        if (selectedCountSpan) {
            selectedCountSpan.textContent = selectedCount;
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

    getPriorityBadgeClass(priority) {
        const classes = {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger',
            'urgent': 'bg-danger'
        };
        return classes[priority] || classes['normal'] || 'bg-secondary';
    }

    getPriorityText(priority) {
        const texts = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '紧急'
        };
        return texts[priority] || (priority || 'normal');
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    getTimeAgo(dateString) {
        if (!dateString) return '-';

        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMinutes < 1) {
            return '刚刚';
        } else if (diffMinutes < 60) {
            return `${diffMinutes}分钟前`;
        } else if (diffHours < 24) {
            return `${diffHours}小时前`;
        } else if (diffDays < 7) {
            return `${diffDays}天前`;
        } else {
            return this.formatDate(dateString);
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
}

// Initialize task manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.taskManager = new TaskManager();
});
