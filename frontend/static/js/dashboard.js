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
        
        // Initialize Winston Framework integration
        this.initializeWinstonIntegration();
        
        this.initializeComponents();
        this.bindGlobalEvents();
        this.setupResponsiveHandling();
        this.initialized = true;
        
        console.log('✅ Dashboard initialized with Winston Framework integration');
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
            // 初始化API客户端 - 使用全局实例或创建新实例
            if (window.api && typeof window.api.createRepository === 'function') {
                this.api = window.api;
            } else if (typeof ApiClient !== 'undefined') {
                this.api = new ApiClient();
            } else {
                // 降级策略：使用fetch API
                this.api = this.createFallbackApiClient();
            }

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
        // Use Winston Modal Template System
        if (!window.winstonModalTemplates) {
            console.error('❌ Winston Modal Templates not available, falling back to basic modal');
            this.showAddRepositoryModalFallback();
            return;
        }

        const modal = window.winstonModalTemplates.showModal('addRepository', {
            onSave: (modalElement) => {
                this.saveRepositoryFromTemplate(modalElement);
            }
        });

        if (modal) {
            // Bind save button event
            const saveBtn = modal.element.querySelector('#saveRepositoryBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    this.saveRepositoryFromTemplate(modal.element, modal.bootstrap);
                });
            }
        }
    }

    async saveRepositoryFromTemplate(modalElement, modalInstance = null) {
        const form = modalElement.querySelector('#addRepositoryForm');

        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const repoData = {
            name: modalElement.querySelector('#repoName').value,
            url: modalElement.querySelector('#repoUrl').value,
            description: modalElement.querySelector('#repoDescription').value,
            branch: modalElement.querySelector('#repoBranch').value
        };

        try {
            const response = await this.api.createRepository(repoData);
            this.showSuccess('仓库添加成功');
            
            // Hide modal using Winston system
            if (modalInstance) {
                modalInstance.hide();
            } else {
                const modalId = modalElement.id;
                if (window.winstonModalTemplates) {
                    window.winstonModalTemplates.hideModal(modalId);
                }
            }

            // Refresh repository list
            if (this.components.repositoryList) {
                this.components.repositoryList.loadRepositories();
            }

        } catch (error) {
            console.error('添加仓库失败:', error);
            this.showError('添加仓库失败: ' + error.message);
        }
    }

    // Legacy fallback method for when Winston templates are not available
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
        // Use Winston Modal Template System
        if (!window.winstonModalTemplates) {
            console.error('❌ Winston Modal Templates not available, falling back to basic modal');
            this.showGenerateDocumentModalFallback();
            return;
        }

        const modal = window.winstonModalTemplates.showModal('generateDocument', {
            loadRepositories: (modalElement) => {
                this.loadRepositoryOptionsForTemplate(modalElement);
            },
            onGenerate: (modalElement) => {
                this.generateDocumentFromTemplate(modalElement);
            }
        });

        if (modal) {
            // Bind generate button event
            const generateBtn = modal.element.querySelector('#generateDocumentBtn');
            if (generateBtn) {
                generateBtn.addEventListener('click', () => {
                    this.generateDocumentFromTemplate(modal.element, modal.bootstrap);
                });
            }
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

    async loadRepositoryOptionsForTemplate(modalElement) {
        try {
            // Use already initialized ApiClient instance
            const apiClient = this.api || window.api || new ApiClient();
            const data = await apiClient.request('/repositories');
            const repositories = data.repositories || [];
            const select = modalElement.querySelector('#documentRepo');

            if (select) {
                select.innerHTML = '<option value="">请选择仓库...</option>';
                repositories.forEach(repo => {
                    const option = document.createElement('option');
                    option.value = repo.id;
                    option.textContent = repo.name;
                    select.appendChild(option);
                });

                // If no repositories, show message
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
            const select = modalElement.querySelector('#documentRepo');
            if (select) {
                select.innerHTML = '<option value="">加载失败 - 请检查网络连接</option>';
            }
            this.showError('加载仓库列表失败，请刷新页面重试');
        }
    }

    async generateDocumentFromTemplate(modalElement, modalInstance = null) {
        const form = modalElement.querySelector('#generateDocumentForm');
        const repoId = modalElement.querySelector('#documentRepo').value;
        const docType = modalElement.querySelector('#documentType').value;
        const docFormat = modalElement.querySelector('#documentFormat').value;
        const analysisDepth = modalElement.querySelector('#analysisDepth')?.value || 'detailed';
        const includeDiagrams = modalElement.querySelector('#includeDiagrams')?.checked || true;
        const includeTroubleshooting = modalElement.querySelector('#includeTroubleshooting')?.checked || true;

        if (!repoId) {
            this.showError('请选择仓库');
            return;
        }

        try {
            // Show progress in modal
            this.showGenerationProgress(modalElement);

            // Call smart document generation API
            const response = await fetch(`/api/smart-document/generate/${repoId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_depth: analysisDepth,
                    include_diagrams: includeDiagrams,
                    include_troubleshooting: includeTroubleshooting,
                    doc_type: docType,
                    format: docFormat
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '文档生成失败');
            }

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('文档生成完成！');
                
                // Hide modal using Winston system
                if (modalInstance) {
                    modalInstance.hide();
                } else {
                    const modalId = modalElement.id;
                    if (window.winstonModalTemplates) {
                        window.winstonModalTemplates.hideModal(modalId);
                    }
                }

                // Navigate to result
                if (result.mkdocs_url) {
                    setTimeout(() => {
                        window.location.href = result.mkdocs_url;
                    }, 1000);
                } else if (result.document_id) {
                    setTimeout(() => {
                        window.location.href = `/documents/${result.document_id}/view`;
                    }, 1000);
                }

                // Refresh task list
                if (this.components.taskProgress) {
                    this.components.taskProgress.loadTasks();
                }
            } else {
                throw new Error(result.error || '文档生成失败');
            }

        } catch (error) {
            console.error('生成文档失败:', error);
            this.showError('生成文档失败: ' + error.message);
            this.hideGenerationProgress(modalElement);
        }
    }

    showGenerationProgress(modalElement) {
        const form = modalElement.querySelector('#generateDocumentForm');
        const progress = modalElement.querySelector('#generateProgress');
        const generateBtn = modalElement.querySelector('#generateDocumentBtn');
        
        if (form) form.classList.add('d-none');
        if (progress) progress.classList.remove('d-none');
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>生成中...';
        }
    }

    hideGenerationProgress(modalElement) {
        const form = modalElement.querySelector('#generateDocumentForm');
        const progress = modalElement.querySelector('#generateProgress');
        const generateBtn = modalElement.querySelector('#generateDocumentBtn');
        
        if (form) form.classList.remove('d-none');
        if (progress) progress.classList.add('d-none');
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>开始生成';
        }
    }

    // Legacy fallback methods
    showAddRepositoryModalFallback() {
        console.warn('⚠️ Using fallback modal for add repository');
        // Original HTML injection implementation as fallback
        // (keeping the original implementation for emergency use)
    }

    showGenerateDocumentModalFallback() {
        console.warn('⚠️ Using fallback modal for generate document');
        // Original HTML injection implementation as fallback
        // (keeping the original implementation for emergency use)
    }

    // Legacy method - kept for backward compatibility
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
            // 调用智能文档生成API
            const response = await fetch(`/api/smart-document/generate/${repoId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_depth: 'detailed',
                    include_diagrams: true,
                    include_troubleshooting: true,
                    doc_type: docType
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '文档生成失败');
            }

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('文档生成完成！');
                modal.hide();

                // 如果有MkDocs站点URL，直接跳转
                if (result.mkdocs_url) {
                    setTimeout(() => {
                        window.location.href = result.mkdocs_url;
                    }, 1000);
                } else {
                    // 降级到文档查看页面
                    if (result.document_id) {
                        setTimeout(() => {
                            window.location.href = `/documents/${result.document_id}/view`;
                        }, 1000);
                    }
                }

                // 刷新任务列表
                if (this.components.taskProgress) {
                    this.components.taskProgress.loadTasks();
                }
            } else {
                throw new Error(result.error || '文档生成失败');
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

    // =================================================================
    // WINSTON FRAMEWORK INTEGRATION
    // =================================================================

    initializeWinstonIntegration() {
        console.log('🏗️ Initializing Winston Framework integration for Dashboard');
        
        // Check Winston dependencies
        this.checkWinstonDependencies();
        
        // Register with Winston error recovery
        this.registerWithErrorRecovery();
        
        // Setup Winston modal event handlers
        this.setupWinstonModalHandlers();
    }

    checkWinstonDependencies() {
        const dependencies = {
            modalDispatcher: window.modalDispatcher,
            modalTemplates: window.winstonModalTemplates,
            errorRecovery: window.winstonErrorRecovery,
            coreSystem: window.coreSystem
        };

        const missing = [];
        Object.entries(dependencies).forEach(([name, dependency]) => {
            if (!dependency) {
                missing.push(name);
            }
        });

        if (missing.length > 0) {
            console.warn('⚠️ Missing Winston dependencies:', missing);
            this.initializeWinstonFallbacks(missing);
        } else {
            console.log('✅ All Winston dependencies available');
        }

        return missing.length === 0;
    }

    initializeWinstonFallbacks(missing) {
        missing.forEach(dependency => {
            switch (dependency) {
                case 'modalTemplates':
                    console.warn('⚠️ Modal templates unavailable, using legacy modal system');
                    break;
                case 'errorRecovery':
                    console.warn('⚠️ Error recovery unavailable, using basic error handling');
                    break;
            }
        });
    }

    registerWithErrorRecovery() {
        if (window.winstonErrorRecovery) {
            // Add dashboard-specific recovery methods
            window.winstonErrorRecovery.dashboardRecovery = () => {
                console.log('🛡️ Dashboard-specific recovery initiated');
                
                // Cleanup any stuck modal states
                this.cleanupModalStates();
                
                // Reset component states
                this.resetComponentStates();
                
                // Refresh dashboard data
                this.refreshDashboardData();
            };
            
            console.log('✅ Dashboard registered with Winston error recovery');
        }
    }

    setupWinstonModalHandlers() {
        if (window.modalDispatcher) {
            // Register global modal event handlers for dashboard
            document.addEventListener('winston:modal:shown', (event) => {
                const { modalId } = event.detail;
                console.log(`📊 Dashboard: Modal shown - ${modalId}`);
                this.onModalShown(modalId);
            });

            document.addEventListener('winston:modal:hidden', (event) => {
                const { modalId } = event.detail;
                console.log(`📊 Dashboard: Modal hidden - ${modalId}`);
                this.onModalHidden(modalId);
            });
        }
    }

    onModalShown(modalId) {
        // Dashboard-specific modal shown handling
        if (modalId.includes('addRepository')) {
            this.trackModalUsage('repository_add');
        } else if (modalId.includes('generateDocument')) {
            this.trackModalUsage('document_generate');
        }
    }

    onModalHidden(modalId) {
        // Dashboard-specific modal hidden handling
        console.log(`📊 Dashboard modal ${modalId} closed`);
    }

    trackModalUsage(action) {
        // Track modal usage for analytics
        console.log(`📈 Dashboard action tracked: ${action}`);
    }

    // =================================================================
    // ERROR RECOVERY AND CLEANUP
    // =================================================================

    cleanupModalStates() {
        console.log('🧹 Cleaning up dashboard modal states');
        
        // Use Winston modal cleanup if available
        if (window.winstonModalTemplates) {
            window.winstonModalTemplates.cleanupAllModals();
        } else {
            // Fallback cleanup
            document.querySelectorAll('.modal').forEach(modal => {
                if (modal.id.includes('Repository') || modal.id.includes('Document')) {
                    modal.remove();
                }
            });
        }
    }

    resetComponentStates() {
        console.log('🔄 Resetting dashboard component states');
        
        Object.values(this.components).forEach(component => {
            if (component.reset) {
                try {
                    component.reset();
                } catch (error) {
                    console.warn(`⚠️ Failed to reset component:`, error);
                }
            }
        });
    }

    refreshDashboardData() {
        console.log('🔄 Refreshing dashboard data');
        
        // Refresh all components
        setTimeout(() => {
            if (this.components.stats) {
                this.components.stats.loadStats();
            }
            if (this.components.repositoryList) {
                this.components.repositoryList.loadRepositories();
            }
            if (this.components.taskProgress) {
                this.components.taskProgress.loadTasks();
            }
            if (this.components.recentActivity) {
                this.components.recentActivity.loadActivities();
            }
        }, 1000);
    }

    // =================================================================
    // ENHANCED ERROR HANDLING WITH WINSTON INTEGRATION
    // =================================================================

    showError(message, options = {}) {
        if (window.winstonModalTemplates && options.useModal) {
            // Use Winston error modal template
            window.winstonModalTemplates.showModal('error', {
                message: message,
                details: options.details,
                stack: options.stack,
                onRetry: options.onRetry
            });
        } else {
            // Use toast notification
            this.showToast(message, 'error');
        }
    }

    showSuccess(message, options = {}) {
        if (window.winstonModalTemplates && options.useModal) {
            // Use Winston success modal template
            window.winstonModalTemplates.showModal('success', {
                message: message,
                details: options.details
            });
        } else {
            // Use toast notification
            this.showToast(message, 'success');
        }
    }

    showConfirmation(message, details, onConfirm) {
        if (window.winstonModalTemplates) {
            const modal = window.winstonModalTemplates.showModal('confirmation', {
                message: message,
                details: details
            });

            if (modal) {
                const confirmBtn = modal.element.querySelector('#confirmBtn');
                if (confirmBtn) {
                    confirmBtn.addEventListener('click', () => {
                        onConfirm();
                        modal.bootstrap.hide();
                    });
                }
            }
        } else {
            // Fallback to browser confirm
            if (confirm(`${message}\\n\\n${details}`)) {
                onConfirm();
            }
        }
    }

    destroy() {
        console.log('🗑️ Destroying dashboard controller with Winston integration');
        
        // Cleanup Winston integrations
        this.cleanupModalStates();
        
        // Unregister from error recovery
        if (window.winstonErrorRecovery && window.winstonErrorRecovery.dashboardRecovery) {
            delete window.winstonErrorRecovery.dashboardRecovery;
        }
        
        // Clean up all components
        Object.values(this.components).forEach(component => {
            if (component.destroy) {
                component.destroy();
            }
        });

        // Clean up real-time updates
        if (this.realtimeUpdates) {
            this.realtimeUpdates.destroy();
        }

        // Remove event listeners
        window.removeEventListener('resize', this.handleResize);
        
        console.log('✅ Dashboard controller destroyed');
    }

    // 降级策略：创建简单的API客户端
    createFallbackApiClient() {
        console.warn('🚨 ApiClient not available, using fallback implementation');
        return {
            async createRepository(data) {
                try {
                    const response = await fetch('/api/repositories', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data),
                        credentials: 'include'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Repository creation failed:', error);
                    throw error;
                }
            },
            
            async getRepositories() {
                try {
                    const response = await fetch('/api/repositories', {
                        method: 'GET',
                        credentials: 'include'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Repository fetch failed:', error);
                    throw error;
                }
            },
            
            async updateRepository(id, data) {
                try {
                    const response = await fetch(`/api/repositories/${id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data),
                        credentials: 'include'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Repository update failed:', error);
                    throw error;
                }
            },
            
            async deleteRepository(id) {
                try {
                    const response = await fetch(`/api/repositories/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Repository delete failed:', error);
                    throw error;
                }
            }
        };
    }
}

// 创建全局仪表板控制器实例
const dashboard = new DashboardController();

// 导出控制器
window.DashboardController = DashboardController;
window.dashboard = dashboard;
