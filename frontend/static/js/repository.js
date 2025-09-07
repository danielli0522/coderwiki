/**
 * 仓库管理页面JavaScript
 * 处理表格形式的仓库列表显示和操作
 */

class RepositoryManager {
    constructor() {
        this.repositories = [];
        this.statistics = {};
        this.isAuthenticated = false;
        this.currentPage = 1;
        this.perPage = 10;
        this.totalPages = 1;
        this.totalItems = 0;
        this.init();
    }

    async init() {
        await this.checkAuthentication();
        if (this.isAuthenticated) {
            this.bindEvents();
            this.setupRealtimeUpdates();
            this.loadRepositories();
            this.loadStatistics();
        } else {
            console.log('用户未登录，跳过仓库管理初始化');
        }
    }

    setupRealtimeUpdates() {
        // WebSocket-based real-time updates (QA Fix for PERF-001)
        document.addEventListener('repositoryStatusUpdate', (event) => {
            console.log('🔄 Received real-time repository update:', event.detail);
            this.handleRepositoryUpdate(event.detail);
        });

        document.addEventListener('taskUpdate', (event) => {
            console.log('⚙️ Received real-time task update:', event.detail);
            this.handleTaskUpdate(event.detail);
        });

        // Connection status monitoring
        document.addEventListener('connectionStatus', (event) => {
            this.updateConnectionStatus(event.detail.status);
        });

        console.log('✅ Real-time updates configured for repository management');
    }

    handleRepositoryUpdate(updateData) {
        const { repositoryId, status, progress, name, error, lastUpdated } = updateData;
        
        // Update local repository data
        const repoIndex = this.repositories.findIndex(repo => repo.id === repositoryId);
        if (repoIndex !== -1) {
            this.repositories[repoIndex].status = status;
            this.repositories[repoIndex].progress = progress;
            if (lastUpdated) {
                this.repositories[repoIndex].updated_at = lastUpdated;
            }
            
            // Update UI for this specific repository
            this.updateRepositoryRowUI(repositoryId, {
                status,
                progress,
                error,
                lastUpdated
            });
            
            // Update statistics if status changed to completed/failed
            if (status === 'completed' || status === 'failed') {
                this.loadStatistics();
            }
            
            console.log(`✅ Updated repository ${name} (${repositoryId}) status to: ${status}`);
        }
    }

    handleTaskUpdate(updateData) {
        const { taskId, status, progress, repositoryId } = updateData;
        
        if (repositoryId) {
            // Update repository progress based on task progress
            this.updateRepositoryRowUI(repositoryId, {
                status: status === 'completed' ? 'completed' : 'analyzing',
                progress: progress
            });
            
            console.log(`⚙️ Updated task ${taskId} affecting repository ${repositoryId}: ${status} (${progress}%)`);
        }
    }

    updateRepositoryRowUI(repositoryId, updateData) {
        const row = document.querySelector(`tr[data-repo-id="${repositoryId}"]`);
        if (!row) return;

        const { status, progress, error, lastUpdated } = updateData;

        // Update status badge
        const statusBadge = row.querySelector('.status-badge');
        if (statusBadge && status) {
            statusBadge.className = `badge status-badge status-${status}`;
            statusBadge.textContent = this.getStatusDisplayText(status);
            
            // Add visual feedback for status changes
            statusBadge.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                statusBadge.style.animation = '';
            }, 500);
        }

        // Update progress bar (if analyzing)
        let progressBar = row.querySelector('.progress-bar');
        if (status === 'analyzing' && progress !== undefined) {
            if (!progressBar) {
                // Create progress bar if it doesn't exist
                const statusCell = row.querySelector('.status-cell');
                if (statusCell) {
                    const progressContainer = document.createElement('div');
                    progressContainer.className = 'progress mt-1';
                    progressContainer.style.height = '4px';
                    
                    progressBar = document.createElement('div');
                    progressBar.className = 'progress-bar bg-info';
                    progressBar.setAttribute('role', 'progressbar');
                    
                    progressContainer.appendChild(progressBar);
                    statusCell.appendChild(progressContainer);
                }
            }
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.setAttribute('aria-valuemin', '0');
                progressBar.setAttribute('aria-valuemax', '100');
            }
        } else {
            // Remove progress bar if not analyzing
            const progressContainer = row.querySelector('.progress');
            if (progressContainer) {
                progressContainer.remove();
            }
        }

        // Update last updated timestamp
        const timestampCell = row.querySelector('.timestamp-cell');
        if (timestampCell && lastUpdated) {
            timestampCell.textContent = this.formatTimestamp(lastUpdated);
        }

        // Show error state if applicable
        if (error && status === 'failed') {
            const statusCell = row.querySelector('.status-cell');
            if (statusCell && !statusCell.querySelector('.error-indicator')) {
                const errorIcon = document.createElement('i');
                errorIcon.className = 'fas fa-exclamation-triangle text-warning ms-1 error-indicator';
                errorIcon.title = error;
                statusCell.appendChild(errorIcon);
            }
        }
    }

    updateConnectionStatus(status) {
        const connectionIndicator = document.getElementById('realtime-status');
        if (connectionIndicator) {
            connectionIndicator.className = `badge ms-2 ${this.getConnectionStatusClass(status)}`;
            connectionIndicator.textContent = this.getConnectionStatusText(status);
        }
    }

    getConnectionStatusClass(status) {
        const statusClasses = {
            'connected': 'bg-success',
            'polling': 'bg-warning',
            'disconnected': 'bg-secondary',
            'error': 'bg-danger',
            'failed': 'bg-danger'
        };
        return statusClasses[status] || 'bg-secondary';
    }

    getConnectionStatusText(status) {
        const statusTexts = {
            'connected': '实时',
            'polling': '轮询',
            'disconnected': '离线',
            'error': '错误',
            'failed': '失败'
        };
        return statusTexts[status] || '未知';
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
            } else {
                this.isAuthenticated = false;
            }
        } catch (error) {
            console.error('认证检查失败:', error);
            this.isAuthenticated = false;
        }
    }

    bindEvents() {
        // 添加仓库按钮 - 修复缺失的事件绑定
        const addRepoBtn = document.getElementById('addRepoBtn');
        if (addRepoBtn) {
            addRepoBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleAddRepository();
            });
            console.log('✅ Add repository button event bound');
        }

        // 验证URL按钮事件绑定
        const validateUrlBtn = document.getElementById('validateUrlBtn');
        if (validateUrlBtn) {
            validateUrlBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleValidateUrl();
            });
            console.log('✅ Validate URL button event bound');
        }

        // 搜索功能
        const searchInput = document.getElementById('searchRepo');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.currentPage = 1; // 重置到第一页
                this.loadRepositories();
            }, 300));
        }

        // 状态筛选
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                this.currentPage = 1; // 重置到第一页
                this.loadRepositories();
            });
        }

        // 分页控件事件委托
        const paginationControls = document.getElementById('paginationControls');
        if (paginationControls) {
            paginationControls.addEventListener('click', (e) => {
                const button = e.target.closest('button');
                if (!button) return;
                
                e.preventDefault();
                const page = parseInt(button.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    this.loadRepositories();
                }
            });
        }

        // 表格事件委托 - 处理所有按钮点击
        const tableContainer = document.getElementById('repositoriesTable');
        if (tableContainer) {
            tableContainer.addEventListener('click', (e) => {
                this.handleTableClick(e);
            });
        }

        console.log('✅ Repository events bound');
    }

    handleTableClick(e) {
        const button = e.target.closest('button, a');
        if (!button) return;

        // 获取仓库ID
        const row = button.closest('tr');
        const repoId = this.getRepositoryIdFromRow(row);
        
        if (!repoId) {
            console.warn('无法获取仓库ID');
            return;
        }

        // 阻止默认行为
        e.preventDefault();
        e.stopPropagation();

        // 根据按钮类型执行操作
        if (button.classList.contains('btn-view') || button.querySelector('.fa-eye')) {
            this.viewRepository(repoId);
        } else if (button.classList.contains('btn-edit') || button.querySelector('.fa-edit')) {
            this.editRepository(repoId);
        } else if (button.classList.contains('btn-delete') || button.querySelector('.fa-trash')) {
            this.deleteRepository(repoId);
        } else if (button.classList.contains('btn-generate') || button.querySelector('.fa-cog')) {
            this.generateDocument(repoId);
        }
    }

    getRepositoryIdFromRow(row) {
        // 尝试从多个位置获取仓库ID
        let repoId = row.dataset.repoId || row.dataset.repositoryId;
        
        if (!repoId) {
            // 尝试从行中的隐藏字段或数据属性获取
            const hiddenInput = row.querySelector('input[data-repo-id], [data-repository-id]');
            if (hiddenInput) {
                repoId = hiddenInput.dataset.repoId || hiddenInput.dataset.repositoryId;
            }
        }

        if (!repoId) {
            // 尝试从URL链接中提取
            const link = row.querySelector('a[href*="/repositories/"]');
            if (link) {
                const match = link.href.match(/\/repositories\/(\d+)/);
                if (match) {
                    repoId = match[1];
                }
            }
        }

        return repoId;
    }

    async loadRepositories() {
        if (!this.isAuthenticated) {
            console.log('用户未登录，跳过仓库数据加载');
            return;
        }

        const loadingState = document.getElementById('loadingState');
        const tableContainer = document.querySelector('.table-responsive');
        const emptyState = document.getElementById('emptyState');

        try {
            // 显示加载状态
            if (loadingState) loadingState.style.display = 'block';
            if (tableContainer) tableContainer.style.display = 'none';
            if (emptyState) emptyState.style.display = 'none';

            // 获取搜索和筛选参数
            const searchInput = document.getElementById('searchRepo');
            const statusFilter = document.getElementById('statusFilter');
            
            const params = new URLSearchParams();
            params.append('page', this.currentPage);
            params.append('per_page', this.perPage);
            
            if (searchInput && searchInput.value) {
                params.append('search', searchInput.value);
            }
            if (statusFilter && statusFilter.value) {
                params.append('status', statusFilter.value);
            }

            const response = await fetch(`/api/repositories?${params}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                redirect: 'manual'
            });

            if (response.status === 302 || response.status === 303) {
                throw new Error('需要登录');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.repositories = data.repositories || [];
            this.totalPages = data.pages || 1;
            this.totalItems = data.total || 0;
            this.currentPage = data.page || 1;

            // 渲染仓库列表
            this.renderRepositories();
            
            // 渲染分页控件
            this.renderPagination();

        } catch (error) {
            console.error('加载仓库列表失败:', error);
            this.showError('加载仓库列表失败: ' + error.message);
        } finally {
            // 隐藏加载状态
            if (loadingState) loadingState.style.display = 'none';
        }
    }

    renderRepositories() {
        const tbody = document.getElementById('repositoriesTable');
        const tableContainer = document.querySelector('.table-responsive');
        const emptyState = document.getElementById('emptyState');

        if (!tbody) {
            console.error('找不到表格tbody元素');
            return;
        }

        if (this.repositories.length === 0) {
            if (tableContainer) tableContainer.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        if (tableContainer) tableContainer.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';

        // 清空现有内容
        tbody.innerHTML = '';

        // 渲染每个仓库
        this.repositories.forEach(repo => {
            const row = this.createRepositoryRow(repo);
            tbody.appendChild(row);
        });

        console.log(`✅ 渲染了 ${this.repositories.length} 个仓库`);
    }

    renderPagination() {
        const paginationContainer = document.getElementById('paginationContainer');
        const paginationInfo = document.getElementById('paginationInfo');
        const paginationControls = document.getElementById('paginationControls');

        if (!paginationContainer || !paginationInfo || !paginationControls) {
            return;
        }

        // 如果只有一页或没有数据，隐藏分页控件
        if (this.totalPages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }

        // 显示分页容器
        paginationContainer.style.display = 'flex';

        // 更新分页信息
        const startItem = (this.currentPage - 1) * this.perPage + 1;
        const endItem = Math.min(this.currentPage * this.perPage, this.totalItems);
        paginationInfo.textContent = `显示 ${startItem}-${endItem} 项，共 ${this.totalItems} 项`;

        // 清空现有的分页控件
        paginationControls.innerHTML = '';

        // 生成分页按钮
        const createPageButton = (page, text, disabled = false, active = false) => {
            const li = document.createElement('li');
            li.className = `page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}`;
            
            const button = document.createElement('button');
            button.className = 'page-link';
            button.textContent = text;
            button.dataset.page = page;
            button.disabled = disabled;
            
            li.appendChild(button);
            return li;
        };

        // 上一页按钮
        paginationControls.appendChild(
            createPageButton(this.currentPage - 1, '上一页', this.currentPage <= 1)
        );

        // 计算显示的页码范围
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(this.totalPages, this.currentPage + 2);

        // 如果在开头，显示更多后面的页
        if (this.currentPage <= 3) {
            endPage = Math.min(this.totalPages, 5);
        }

        // 如果在末尾，显示更多前面的页
        if (this.currentPage > this.totalPages - 3) {
            startPage = Math.max(1, this.totalPages - 4);
        }

        // 如果起始页不是1，添加第一页和省略号
        if (startPage > 1) {
            paginationControls.appendChild(createPageButton(1, '1'));
            if (startPage > 2) {
                const li = document.createElement('li');
                li.className = 'page-item disabled';
                li.innerHTML = '<span class="page-link">...</span>';
                paginationControls.appendChild(li);
            }
        }

        // 添加页码按钮
        for (let page = startPage; page <= endPage; page++) {
            paginationControls.appendChild(
                createPageButton(page, page.toString(), false, page === this.currentPage)
            );
        }

        // 如果结束页不是最后一页，添加省略号和最后一页
        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                const li = document.createElement('li');
                li.className = 'page-item disabled';
                li.innerHTML = '<span class="page-link">...</span>';
                paginationControls.appendChild(li);
            }
            paginationControls.appendChild(createPageButton(this.totalPages, this.totalPages.toString()));
        }

        // 下一页按钮
        paginationControls.appendChild(
            createPageButton(this.currentPage + 1, '下一页', this.currentPage >= this.totalPages)
        );
    }

    createRepositoryRow(repo) {
        const row = document.createElement('tr');
        row.dataset.repoId = repo.id;

        // 状态徽章样式
        const getStatusBadge = (repo) => {
            const status = repo.status;
            if (status === 'error') {
                // 显示错误原因
                let errorInfo = '错误';
                if (repo.clone_error) {
                    if (repo.clone_error.includes('not-a-git-url') || repo.clone_error.includes('Invalid URL')) {
                        errorInfo = '错误(URL无效)';
                    } else if (repo.clone_error.includes('Permission denied')) {
                        errorInfo = '错误(权限不足)';
                    } else if (repo.clone_error.includes('Repository not found')) {
                        errorInfo = '错误(仓库不存在)';
                    } else if (repo.clone_error.includes('Network')) {
                        errorInfo = '错误(网络问题)';
                    } else {
                        errorInfo = '错误(克隆失败)';
                    }
                }
                return `<span class="badge bg-danger" title="${this.escapeHtml(repo.clone_error || '未知错误')}">${errorInfo}</span>`;
            }
            
            const statusMap = {
                'active': '<span class="badge bg-success">活跃</span>',
                'inactive': '<span class="badge bg-secondary">非活跃</span>',
                'cloning': '<span class="badge bg-warning">克隆中</span>',
                'analyzing': '<span class="badge bg-info">分析中</span>'
            };
            return statusMap[status] || `<span class="badge bg-primary">${status}</span>`;
        };

        // 格式化文件大小
        const formatSize = (bytes) => {
            if (!bytes) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        };

        // 格式化日期
        const formatDate = (dateString) => {
            if (!dateString) return '-';
            return new Date(dateString).toLocaleDateString('zh-CN');
        };

        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-folder text-primary me-2"></i>
                    <div>
                        <div class="fw-bold">${this.escapeHtml(repo.name || '')}</div>
                        <small class="text-muted">${this.escapeHtml(repo.description || '暂无描述')}</small>
                    </div>
                </div>
            </td>
            <td>
                <div class="text-truncate" style="max-width: 200px;">
                    <a href="${this.escapeHtml(repo.url || '#')}" target="_blank" class="text-decoration-none">
                        ${this.escapeHtml(repo.url || '')}
                    </a>
                </div>
            </td>
            <td>${getStatusBadge(repo)}</td>
            <td>
                ${this.getCloneStatusDisplay(repo)}
            </td>
            <td>${repo.file_count || 0}</td>
            <td>${formatSize(repo.size)}</td>
            <td>${formatDate(repo.created_at)}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-primary btn-view" title="查看仓库">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-edit" title="编辑仓库">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-outline-info btn-generate" title="生成文档">
                        <i class="fas fa-cog"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger btn-delete" title="删除仓库">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        return row;
    }

    async viewRepository(repoId) {
        try {
            console.log('查看仓库:', repoId);
            
            // 获取仓库详细信息
            const response = await fetch(`/api/repositories/${repoId}`);
            
            if (response.ok) {
                const repo = await response.json();
                
                // 尝试打开MkDocs站点
                const sanitizedName = repo.name.replace(/[^\w\-_]/g, '_');
                const mkdocsUrl = `/sites/${sanitizedName}_${repoId}/`;
                
                // 检查MkDocs站点是否存在
                const checkResponse = await fetch(mkdocsUrl, { method: 'HEAD' });
                
                if (checkResponse.ok) {
                    // 站点存在，在新窗口打开
                    window.open(mkdocsUrl, '_blank');
                } else {
                    // 站点不存在，跳转到仓库详情页
                    window.location.href = `/repositories/${repoId}`;
                }
            } else {
                // 获取仓库信息失败，跳转到仓库详情页
                window.location.href = `/repositories/${repoId}`;
            }
            
        } catch (error) {
            console.error('查看仓库失败:', error);
            // 发生错误，跳转到仓库详情页
            window.location.href = `/repositories/${repoId}`;
        }
    }

    editRepository(repoId) {
        console.log('编辑仓库:', repoId);
        // TODO: 实现编辑仓库功能
        this.showError('编辑功能正在开发中');
    }

    async generateDocument(repoId) {
        try {
            console.log('生成文档:', repoId);
            
            const response = await fetch(`/api/repositories/${repoId}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.showSuccess('文档生成任务已创建');
            } else {
                throw new Error('生成文档失败');
            }
        } catch (error) {
            console.error('生成文档失败:', error);
            this.showError('生成文档失败');
        }
    }

    async deleteRepository(repoId) {
        if (!confirm('确定要删除这个仓库吗？此操作不可撤销。')) {
            return;
        }

        try {
            console.log('删除仓库:', repoId);
            
            const response = await fetch(`/api/repositories/${repoId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.showSuccess('仓库删除成功');
                this.loadRepositories(); // 重新加载列表
            } else {
                throw new Error('删除仓库失败');
            }
        } catch (error) {
            console.error('删除仓库失败:', error);
            this.showError('删除仓库失败');
        }
    }

    handleAddRepository() {
        console.log('🔄 Opening add repository modal...');
        
        // 尝试使用Winston模态框系统
        if (window.winstonModalTemplates) {
            this.showAddRepositoryWithWinston();
        } else {
            // 降级到Bootstrap模态框
            this.showAddRepositoryWithBootstrap();
        }
    }

    showAddRepositoryWithWinston() {
        const modal = window.winstonModalTemplates.showModal('addRepository', {
            onSave: (modalElement) => {
                this.saveRepositoryFromModal(modalElement);
            }
        });

        if (modal) {
            // 绑定保存按钮事件
            const saveBtn = modal.element.querySelector('#saveRepositoryBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    this.saveRepositoryFromModal(modal.element, modal.bootstrap);
                });
            }
            console.log('✅ Winston add repository modal opened');
        } else {
            console.warn('⚠️ Failed to open Winston modal, falling back to Bootstrap');
            this.showAddRepositoryWithBootstrap();
        }
    }

    showAddRepositoryWithBootstrap() {
        const modalElement = document.getElementById('addRepositoryModal');
        if (modalElement) {
            // 清理之前的事件监听器
            const existingBtn = modalElement.querySelector('#addRepoBtn');
            if (existingBtn) {
                // 克隆按钮以清理事件监听器
                const newBtn = existingBtn.cloneNode(true);
                existingBtn.parentNode.replaceChild(newBtn, existingBtn);
                
                // 添加新的事件监听器
                newBtn.addEventListener('click', () => {
                    this.saveRepositoryFromModal(modalElement);
                });
            }

            // 显示模态框
            const bsModal = new bootstrap.Modal(modalElement);
            bsModal.show();
            console.log('✅ Bootstrap add repository modal opened');
        } else {
            console.error('❌ Add repository modal not found in DOM');
            this.showError('无法打开添加仓库对话框');
        }
    }

    async saveRepositoryFromModal(modalElement, modalInstance = null) {
        const form = modalElement.querySelector('#addRepositoryForm');
        
        // 验证表单
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const repoData = {
            name: modalElement.querySelector('#repoName')?.value || '',
            url: modalElement.querySelector('#repoUrl')?.value || '',
            description: modalElement.querySelector('#repoDescription')?.value || ''
        };

        // 如果名称为空，从URL中提取
        if (!repoData.name && repoData.url) {
            const urlParts = repoData.url.split('/');
            const repoName = urlParts[urlParts.length - 1].replace('.git', '');
            repoData.name = repoName;
        }

        if (!repoData.url) {
            this.showError('请输入仓库URL');
            return;
        }

        try {
            // 检查认证状态
            const authResponse = await fetch('/api/auth/status', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });

            let isAuthenticated = false;
            if (authResponse.ok) {
                const authData = await authResponse.json();
                isAuthenticated = authData.logged_in || false;
            }

            if (!isAuthenticated) {
                const message = '请先登录后再添加仓库。系统将为您跳转到登录页面。';
                if (confirm(`${message}\n\n点击确定跳转到登录页面。`)) {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                }
                return;
            }

            // 调用API添加仓库
            const response = await fetch('/api/repositories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(repoData),
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.showSuccess('仓库添加成功');

            // 关闭模态框
            if (modalInstance) {
                modalInstance.hide();
            } else if (window.winstonModalTemplates) {
                window.winstonModalTemplates.hideModal(modalElement.id);
            } else {
                const bsModal = bootstrap.Modal.getInstance(modalElement);
                if (bsModal) {
                    bsModal.hide();
                }
            }

            // 重新加载仓库列表
            this.loadRepositories();
            this.loadStatistics();

        } catch (error) {
            console.error('添加仓库失败:', error);
            
            // 检查是否是认证错误
            if (error.message.includes('401') || error.message.includes('login') || error.message.includes('登录')) {
                const message = '登录会话已过期，请重新登录后再试。';
                if (confirm(`${message}\n\n点击确定跳转到登录页面。`)) {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                }
            } else {
                this.showError('添加仓库失败: ' + error.message);
            }
        }
    }

    async handleValidateUrl() {
        console.log('🔍 Validating repository URL...');
        
        const urlInput = document.getElementById('repoUrl');
        const resultSpan = document.getElementById('validationResult');
        const validateBtn = document.getElementById('validateUrlBtn');
        
        if (!urlInput || !resultSpan) {
            console.error('❌ URL validation elements not found');
            return;
        }

        const url = urlInput.value.trim();
        
        if (!url) {
            resultSpan.innerHTML = '<span class="text-warning"><i class="fas fa-exclamation-triangle"></i> 请输入URL</span>';
            return;
        }

        // 基本URL格式验证
        try {
            new URL(url);
        } catch (error) {
            resultSpan.innerHTML = '<span class="text-danger"><i class="fas fa-times-circle"></i> URL格式无效</span>';
            return;
        }

        // 检查是否是Git仓库URL
        if (!this.isValidGitUrl(url)) {
            resultSpan.innerHTML = '<span class="text-warning"><i class="fas fa-exclamation-triangle"></i> 请输入Git仓库URL</span>';
            return;
        }

        // 显示验证中状态
        if (validateBtn) {
            validateBtn.disabled = true;
            validateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 验证中...';
        }
        resultSpan.innerHTML = '<span class="text-info"><i class="fas fa-spinner fa-spin"></i> 验证中...</span>';

        try {
            // 调用后端验证API
            const response = await fetch('/api/repositories/validate-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url }),
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                
                if (result.valid) {
                    resultSpan.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> 仓库URL有效</span>';
                    
                    // 自动填充仓库名称（如果为空）
                    const nameInput = document.getElementById('repoName');
                    if (nameInput && !nameInput.value.trim() && result.name) {
                        nameInput.value = result.name;
                    }
                } else {
                    resultSpan.innerHTML = `<span class="text-danger"><i class="fas fa-times-circle"></i> ${result.error || '仓库不可访问'}</span>`;
                }
            } else {
                resultSpan.innerHTML = '<span class="text-danger"><i class="fas fa-times-circle"></i> 验证失败，请稍后重试</span>';
            }
        } catch (error) {
            console.error('URL验证失败:', error);
            resultSpan.innerHTML = '<span class="text-danger"><i class="fas fa-times-circle"></i> 验证失败，网络错误</span>';
        } finally {
            // 恢复按钮状态
            if (validateBtn) {
                validateBtn.disabled = false;
                validateBtn.innerHTML = '<i class="fas fa-check-circle"></i> 验证 URL';
            }
        }
    }

    isValidGitUrl(url) {
        // 检查是否是Git仓库URL格式
        const gitPatterns = [
            /^https?:\/\/[^\/]+\/.*\.git$/,  // https://domain/path/repo.git
            /^https?:\/\/github\.com\/[^\/]+\/[^\/]+$/,  // https://github.com/user/repo
            /^https?:\/\/gitlab\.com\/[^\/]+\/[^\/]+$/,  // https://gitlab.com/user/repo
            /^https?:\/\/bitbucket\.org\/[^\/]+\/[^\/]+$/,  // https://bitbucket.org/user/repo
            /^git@[^:]+:[^\/]+\/.*\.git$/,  // git@domain:user/repo.git
            /^ssh:\/\/git@[^\/]+\/.*\.git$/  // ssh://git@domain/user/repo.git
        ];
        
        return gitPatterns.some(pattern => pattern.test(url));
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/repositories/statistics');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatistics(stats);
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }

    updateStatistics(stats) {
        const totalRepos = document.getElementById('totalRepos');
        const activeRepos = document.getElementById('activeRepos');
        const clonedRepos = document.getElementById('clonedRepos');
        const totalFiles = document.getElementById('totalFiles');

        if (totalRepos) totalRepos.textContent = stats.total || 0;
        if (activeRepos) activeRepos.textContent = stats.active || 0;
        if (clonedRepos) clonedRepos.textContent = stats.cloned || 0;
        if (totalFiles) totalFiles.textContent = stats.total_files || 0;
    }

    // 工具函数
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCloneStatusDisplay(repo) {
        const status = repo.clone_status;
        const error = repo.clone_error;
        
        if (status === 'completed') {
            return '<span class="badge bg-success">已完成</span>';
        } else if (status === 'pending') {
            return '<span class="badge bg-secondary">待处理</span>';
        } else if (status === 'cloning') {
            return '<span class="badge bg-primary">克隆中</span>';
        } else if (status === 'failed') {
            // 显示失败原因
            let errorMessage = '失败';
            if (error) {
                // 提取关键错误信息
                if (error.includes('not-a-git-url') || error.includes('Invalid URL')) {
                    errorMessage = '失败(URL无效)';
                } else if (error.includes('Permission denied') || error.includes('Authentication failed')) {
                    errorMessage = '失败(权限不足)';
                } else if (error.includes('Repository not found') || error.includes('404')) {
                    errorMessage = '失败(仓库不存在)';
                } else if (error.includes('Network') || error.includes('timeout')) {
                    errorMessage = '失败(网络错误)';
                } else if (error.includes('No space left') || error.includes('disk')) {
                    errorMessage = '失败(磁盘空间不足)';
                } else if (error.length > 50) {
                    // 如果错误信息太长，显示简化版本
                    errorMessage = '失败(点击查看详情)';
                } else {
                    errorMessage = `失败(${error.substring(0, 20)}...)`;
                }
            }
            return `<span class="badge bg-danger" title="${this.escapeHtml(error || '未知错误')}">${errorMessage}</span>`;
        } else {
            // 处理未知状态的情况
            return `<span class="badge bg-warning" title="数据状态异常，请联系管理员">未知(${status || '状态异常'})</span>`;
        }
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

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type) {
        // 查找或创建alert容器
        let alertContainer = document.querySelector('.alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
            alertContainer.style.zIndex = '9999';
            document.body.appendChild(alertContainer);
        }

        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        alertContainer.insertAdjacentHTML('beforeend', alertHtml);

        // 5秒后自动移除
        setTimeout(() => {
            const alerts = alertContainer.querySelectorAll('.alert');
            if (alerts.length > 0) {
                alerts[0].remove();
            }
        }, 5000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.repositoryManager = new RepositoryManager();
});

// 导出给全局使用
window.RepositoryManager = RepositoryManager;