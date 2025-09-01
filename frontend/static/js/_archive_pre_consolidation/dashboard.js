/**
 * 仪表板主控制器
 * 负责初始化和协调所有组件
 */
class DashboardController {
    constructor() {
        this.components = {};
        this.initialized = false;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.waitForComponentsAndInitialize();
        });
    }

    async waitForComponentsAndInitialize() {
        // Wait for components to be loaded before initializing
        await this.waitForComponents();
        this.initializeComponents();
        this.bindGlobalEvents();
        this.setupResponsiveHandling();
        this.initialized = true;
    }

    async waitForComponents() {
        const requiredComponents = [
            'StatsComponent',
            'RepositoryListComponent', 
            'TaskProgressComponent',
            'RecentActivityComponent',
            'SystemStatusComponent'
        ];

        const maxWaitTime = 10000; // 10 seconds maximum wait
        const checkInterval = 100; // Check every 100ms
        let elapsed = 0;

        return new Promise((resolve) => {
            const checkComponents = () => {
                const allLoaded = requiredComponents.every(componentName => 
                    typeof window[componentName] !== 'undefined'
                );

                if (allLoaded) {
                    console.log('All dashboard components loaded successfully');
                    resolve();
                } else if (elapsed >= maxWaitTime) {
                    console.warn('Component loading timeout, proceeding anyway');
                    resolve();
                } else {
                    elapsed += checkInterval;
                    setTimeout(checkComponents, checkInterval);
                }
            };

            checkComponents();
        });
    }

    initializeComponents() {
        try {
            // 初始化API客户端
            this.api = new ApiClient();

            // 初始化实时更新
            this.realtimeUpdates = new RealtimeUpdates();

            // 初始化统计组件
            if (document.querySelector('.stats-container') && typeof StatsComponent !== 'undefined') {
                this.components.stats = new StatsComponent();
                window.statsComponent = this.components.stats;
            } else if (document.querySelector('.stats-container')) {
                console.warn('StatsComponent not available, skipping stats initialization');
            }

            // 初始化仓库列表组件
            if (document.querySelector('.repository-list-container') && typeof RepositoryListComponent !== 'undefined') {
                this.components.repositoryList = new RepositoryListComponent();
                window.repositoryListComponent = this.components.repositoryList;
            } else if (document.querySelector('.repository-list-container')) {
                console.warn('RepositoryListComponent not available, skipping repository list initialization');
            }

            // 初始化任务进度组件
            if (document.querySelector('.task-progress-container') && typeof TaskProgressComponent !== 'undefined') {
                this.components.taskProgress = new TaskProgressComponent();
                window.taskProgressComponent = this.components.taskProgress;
            } else if (document.querySelector('.task-progress-container')) {
                console.warn('TaskProgressComponent not available, skipping task progress initialization');
            }

            // 初始化最近活动组件
            if (document.querySelector('.recent-activity-container') && typeof RecentActivityComponent !== 'undefined') {
                this.components.recentActivity = new RecentActivityComponent();
                window.recentActivityComponent = this.components.recentActivity;
            } else if (document.querySelector('.recent-activity-container')) {
                console.warn('RecentActivityComponent not available, skipping recent activity initialization');
            }

            // 初始化系统状态组件
            if (document.querySelector('.system-status-container') && typeof SystemStatusComponent !== 'undefined') {
                this.components.systemStatus = new SystemStatusComponent();
                window.systemStatusComponent = this.components.systemStatus;
            } else if (document.querySelector('.system-status-container')) {
                console.warn('SystemStatusComponent not available, skipping system status initialization');
            }

            console.log('所有组件初始化完成');

        } catch (error) {
            console.error('组件初始化失败:', error);
            this.showError('组件初始化失败，请刷新页面重试');
        }
    }

    bindGlobalEvents() {
        // 快速操作按钮
        const quickAddRepoBtn = document.getElementById('quickAddRepoBtn');
        if (quickAddRepoBtn) {
            quickAddRepoBtn.addEventListener('click', () => {
                this.showAddRepositoryModal();
            });
        }

        const quickGenerateDocBtn = document.getElementById('quickGenerateDocBtn');
        if (quickGenerateDocBtn) {
            quickGenerateDocBtn.addEventListener('click', () => {
                this.showGenerateDocumentModal();
            });
        }

        // 添加仓库按钮
        const addRepoBtn = document.getElementById('addRepoBtn');
        if (addRepoBtn) {
            addRepoBtn.addEventListener('click', () => {
                this.showAddRepositoryModal();
            });
        }

        // 通知下拉菜单
        const notificationDropdown = document.getElementById('notificationDropdown');
        if (notificationDropdown) {
            notificationDropdown.addEventListener('shown.bs.dropdown', () => {
                this.markNotificationsAsRead();
            });
        }

        // 用户菜单
        const userDropdown = document.getElementById('userDropdown');
        if (userDropdown) {
            userDropdown.addEventListener('click', (e) => {
                if (e.target.closest('a[href="/logout"]')) {
                    this.handleLogout();
                }
            });
        }

        // 监听实时更新事件
        this.setupRealtimeEventHandlers();
    }

    setupRealtimeEventHandlers() {
        if (!this.realtimeUpdates) return;

        // 任务更新事件
        this.realtimeUpdates.on('task_update', (data) => {
            console.log('收到任务更新:', data);
            this.showTaskNotification(data);
        });

        // 系统状态事件
        this.realtimeUpdates.on('system_status', (data) => {
            console.log('收到系统状态更新:', data);
            this.updateSystemStatusIndicator(data);
        });

        // 通知事件
        this.realtimeUpdates.on('notification', (data) => {
            console.log('收到通知:', data);
            this.showNotification(data);
        });

        // 活动事件
        this.realtimeUpdates.on('activity', (data) => {
            console.log('收到活动更新:', data);
            this.showActivityToast(data);
        });
    }

    setupResponsiveHandling() {
        // 处理响应式布局
        const handleResize = () => {
            this.updateResponsiveLayout();
        };

        window.addEventListener('resize', this.debounce(handleResize, 250));
        this.updateResponsiveLayout();
    }

    updateResponsiveLayout() {
        const width = window.innerWidth;
        const sidebar = document.querySelector('.dashboard-sidebar');
        const mainContent = document.querySelector('.dashboard-container > .row > div:last-child');

        if (width < 768) {
            // 移动端布局
            if (sidebar) {
                sidebar.classList.add('mobile-sidebar');
            }
            if (mainContent) {
                mainContent.classList.add('mobile-main');
            }
        } else {
            // 桌面端布局
            if (sidebar) {
                sidebar.classList.remove('mobile-sidebar');
            }
            if (mainContent) {
                mainContent.classList.remove('mobile-main');
            }
        }
    }

    showAddRepositoryModal() {
        // 创建添加仓库模态框
        const modalHtml = `
            <div class="modal fade" id="addRepositoryModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">添加仓库</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addRepositoryForm">
                                <div class="mb-3">
                                    <label for="repoName" class="form-label">仓库名称</label>
                                    <input type="text" class="form-control" id="repoName" name="repoName" required>
                                </div>
                                <div class="mb-3">
                                    <label for="repoUrl" class="form-label">仓库URL</label>
                                    <input type="url" class="form-control" id="repoUrl" name="repoUrl" required>
                                    <div class="form-text">支持GitHub、GitLab等Git仓库地址</div>
                                </div>
                                <div class="mb-3">
                                    <label for="repoDescription" class="form-label">描述</label>
                                    <textarea class="form-control" id="repoDescription" name="repoDescription" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="repoBranch" class="form-label">分支</label>
                                    <input type="text" class="form-control" id="repoBranch" name="repoBranch" value="main">
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="saveRepositoryBtn">保存</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除现有模态框
        const existingModal = document.getElementById('addRepositoryModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新模态框
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('addRepositoryModal'));
        modal.show();

        // 绑定保存按钮事件
        const saveBtn = document.getElementById('saveRepositoryBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveRepository(modal);
            });
        }
    }

    async saveRepository(modal) {
        const form = document.getElementById('addRepositoryForm');

        // 验证表单
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const repoData = {
            name: document.getElementById('repoName').value,
            url: document.getElementById('repoUrl').value,
            description: document.getElementById('repoDescription').value,
            branch: document.getElementById('repoBranch').value
        };

        try {
            const response = await this.api.createRepository(repoData);
            this.showSuccess('仓库添加成功');
            modal.hide();

            // 刷新仓库列表
            if (this.components.repositoryList) {
                this.components.repositoryList.loadRepositories();
            }

        } catch (error) {
            console.error('添加仓库失败:', error);
            this.showError('添加仓库失败: ' + error.message);
        }
    }

    showGenerateDocumentModal() {
        // 显示生成文档模态框
        const modalHtml = `
            <div class="modal fade" id="generateDocumentModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">生成文档</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="generateDocumentForm">
                                <div class="mb-3">
                                    <label for="documentRepo" class="form-label">选择仓库</label>
                                    <select class="form-select" id="documentRepo" required>
                                        <option value="">请选择仓库</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="documentType" class="form-label">文档类型</label>
                                    <select class="form-select" id="documentType" required>
                                        <option value="readme">README文档</option>
                                        <option value="api">API文档</option>
                                        <option value="architecture">架构文档</option>
                                        <option value="user_guide">用户指南</option>
                                        <option value="developer_guide">开发指南</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="documentFormat" class="form-label">输出格式</label>
                                    <select class="form-select" id="documentFormat" required>
                                        <option value="markdown">Markdown</option>
                                        <option value="html">HTML</option>
                                        <option value="pdf">PDF</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="generateDocumentBtn">生成</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除现有模态框
        const existingModal = document.getElementById('generateDocumentModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新模态框
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 加载仓库列表
        this.loadRepositoryOptions();

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('generateDocumentModal'));
        modal.show();

        // 绑定生成按钮事件
        const generateBtn = document.getElementById('generateDocumentBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateDocument(modal);
            });
        }
    }

    async loadRepositoryOptions() {
        try {
            // 使用已初始化的ApiClient实例
            const apiClient = this.api || window.api || new ApiClient();
            const data = await apiClient.request('/repositories');
            const repositories = data.repositories || [];
            const select = document.getElementById('documentRepo');

            if (select) {
                select.innerHTML = '<option value="">请选择仓库</option>';
                repositories.forEach(repo => {
                    const option = document.createElement('option');
                    option.value = repo.id;
                    option.textContent = repo.name;
                    select.appendChild(option);
                });

                // 如果没有仓库，显示提示
                if (repositories.length === 0) {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = '暂无可用仓库';
                    option.disabled = true;
                    select.appendChild(option);
                }
            }
        } catch (error) {
            console.error('加载仓库列表失败:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                apiClient: typeof apiClient,
                windowApi: typeof window.api,
                windowApiClient: typeof window.ApiClient
            });
            const select = document.getElementById('documentRepo');
            if (select) {
                select.innerHTML = '<option value="">加载失败 - 请检查网络连接</option>';
            }
            // 显示用户友好的错误提示
            this.showError('加载仓库列表失败，请刷新页面重试');
        }
    }

    async generateDocument(modal) {
        const form = document.getElementById('generateDocumentForm');
        const repoId = document.getElementById('documentRepo').value;
        const docType = document.getElementById('documentType').value;
        const docFormat = document.getElementById('documentFormat').value;

        if (!repoId) {
            this.showError('请选择仓库');
            return;
        }

        try {
            const response = await this.api.generateDocument(repoId, {
                document_type: docType,  // 修复：将 'type' 改为 'document_type'
                output_format: docFormat  // 修复：将 'format' 改为 'output_format'
            });

            this.showSuccess('文档生成任务已创建');
            modal.hide();

            // 刷新任务列表
            if (this.components.taskProgress) {
                this.components.taskProgress.loadTasks();
            }

        } catch (error) {
            console.error('生成文档失败:', error);
            this.showError('生成文档失败: ' + error.message);
        }
    }

    showTaskNotification(taskData) {
        const message = `任务 "${taskData.title}" 状态已更新为: ${this.getStatusText(taskData.status)}`;
        this.showToast(message, taskData.status === 'completed' ? 'success' : 'info');
    }

    updateSystemStatusIndicator(systemData) {
        const statusDot = document.getElementById('systemStatusDot');
        const statusText = document.getElementById('systemStatusText');

        if (statusDot && statusText) {
            const status = systemData.overall_status || 'unknown';
            const statusInfo = this.getStatusInfo(status);

            statusDot.className = `status-dot ${statusInfo.dotClass}`;
            statusText.textContent = statusInfo.text;
        }
    }

    showNotification(notificationData) {
        this.showToast(notificationData.message, notificationData.type);
    }

    showActivityToast(activityData) {
        this.showToast(activityData.title, 'info');
    }

    markNotificationsAsRead() {
        // 标记通知为已读
        const notificationCount = document.getElementById('notificationCount');
        if (notificationCount) {
            notificationCount.style.display = 'none';
        }
    }

    handleLogout() {
        if (confirm('确定要退出登录吗？')) {
            // 清理本地存储
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_id');

            // 断开实时连接
            if (this.realtimeUpdates) {
                this.realtimeUpdates.destroy();
            }

            // 清理组件
            Object.values(this.components).forEach(component => {
                if (component.destroy) {
                    component.destroy();
                }
            });
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

    getStatusInfo(status) {
        const statusMap = {
            'healthy': { text: '正常', dotClass: 'status-dot-success' },
            'warning': { text: '警告', dotClass: 'status-dot-warning' },
            'error': { text: '错误', dotClass: 'status-dot-error' },
            'unknown': { text: '未知', dotClass: 'status-dot-unknown' }
        };
        return statusMap[status] || statusMap.unknown;
    }

    showToast(message, type = 'info') {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        const toastElement = document.createElement('div');
        toastElement.innerHTML = toastHtml;
        toastContainer.appendChild(toastElement);

        const toast = new bootstrap.Toast(toastElement.querySelector('.toast'));
        toast.show();

        // 自动移除
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    debounce(func, wait) {
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

    destroy() {
        // 清理所有组件
        Object.values(this.components).forEach(component => {
            if (component.destroy) {
                component.destroy();
            }
        });

        // 清理实时更新
        if (this.realtimeUpdates) {
            this.realtimeUpdates.destroy();
        }

        // 移除事件监听器
        window.removeEventListener('resize', this.handleResize);
    }
}

// 创建全局仪表板控制器实例
const dashboard = new DashboardController();

// 导出控制器
window.DashboardController = DashboardController;
window.dashboard = dashboard;
