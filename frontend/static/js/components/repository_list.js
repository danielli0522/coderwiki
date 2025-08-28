/**
 * 仓库列表组件
 * 负责仓库数据的获取、展示和操作
 */
class RepositoryListComponent {
    constructor() {
        this.repositories = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.filters = {
            search: '',
            status: ''
        };
        this.selectedRepositories = new Set();
        this.bulkMode = false;
        this.isAuthenticated = false;
        this.init();
    }

    async init() {
        await this.checkAuthentication();
        if (this.isAuthenticated) {
            this.bindEvents();
            this.loadRepositories();
        } else {
            console.log('用户未登录，跳过仓库列表组件初始化');
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
        // 搜索功能
        const searchInput = document.getElementById('repoSearchInput');
        const searchBtn = document.getElementById('repoSearchBtn');

        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.filters.search = searchInput.value;
                this.currentPage = 1;
                this.loadRepositories();
            }, 300));
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.filters.search = searchInput.value;
                this.currentPage = 1;
                this.loadRepositories();
            });
        }

        // 状态筛选
        const statusFilter = document.getElementById('repoStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.currentPage = 1;
                this.loadRepositories();
            });
        }

        // 添加仓库按钮
        const addRepoBtn = document.getElementById('addRepoBtn');
        if (addRepoBtn) {
            addRepoBtn.addEventListener('click', () => {
                this.showAddRepositoryModal();
            });
        }

        // 批量操作按钮
        const bulkModeBtn = document.getElementById('bulkModeBtn');
        if (bulkModeBtn) {
            bulkModeBtn.addEventListener('click', () => {
                this.toggleBulkMode();
            });
        }

        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        if (bulkDeleteBtn) {
            bulkDeleteBtn.addEventListener('click', () => {
                this.bulkDeleteRepositories();
            });
        }

        const selectAllBtn = document.getElementById('selectAllBtn');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                this.selectAll();
            });
        }

        const cancelBulkBtn = document.getElementById('cancelBulkBtn');
        if (cancelBulkBtn) {
            cancelBulkBtn.addEventListener('click', () => {
                this.toggleBulkMode();
            });
        }

        // 仓库操作按钮（事件委托）
        const container = document.getElementById('repositoryListContainer');
        if (container) {
            container.addEventListener('click', (e) => {
                const repoItem = e.target.closest('.repository-item');
                if (!repoItem) return;

                const repoId = repoItem.dataset.repoId;

                // 处理批量选择模式下的复选框点击
                if (e.target.closest('.repo-checkbox')) {
                    this.toggleRepositorySelection(repoId);
                    return;
                }

                // 非批量模式下的操作
                if (!this.bulkMode) {
                    if (e.target.closest('.generate-doc-btn')) {
                        this.generateDocument(repoId);
                    } else if (e.target.closest('.view-repo-btn')) {
                        this.viewRepository(repoId);
                    } else if (e.target.closest('.edit-repo-btn')) {
                        this.editRepository(repoId);
                    } else if (e.target.closest('.delete-repo-btn')) {
                        this.deleteRepository(repoId);
                    }
                }
            });
        }
    }

    async loadRepositories() {
        if (!this.isAuthenticated) {
            console.log('用户未登录，跳过仓库数据加载');
            return;
        }

        try {
            console.log('开始加载仓库列表...');

            const params = new URLSearchParams({
                page: this.currentPage,
                limit: this.itemsPerPage,
                ...this.filters
            });

            console.log('API请求参数:', params.toString());

            const response = await fetch(`/api/repositories?${params}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                redirect: 'manual'
            });

            console.log('API响应状态:', response.status);

            if (response.status === 302 || response.status === 303) {
                throw new Error('需要登录');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('API响应数据:', data);

            this.repositories = data.repositories || [];
            this.totalItems = data.total || 0;

            console.log(`加载到 ${this.repositories.length} 个仓库`);

            this.renderRepositories();
            this.renderPagination();
        } catch (error) {
            console.error('加载仓库列表失败:', error);
            this.showError('加载仓库列表失败: ' + error.message);
        }
    }

    renderRepositories() {
        const container = document.getElementById('repositoryListContainer');
        const emptyState = document.getElementById('emptyRepoState');

        if (!container) return;

        if (this.repositories.length === 0) {
            container.innerHTML = '';
            if (emptyState) {
                container.appendChild(emptyState.cloneNode(true));
            }
            return;
        }

        const template = document.getElementById('repositoryItemTemplate');
        if (!template) return;

        container.innerHTML = '';

        this.repositories.forEach(repo => {
            const repoElement = this.createRepositoryElement(repo, template);
            container.appendChild(repoElement);
        });
    }

    createRepositoryElement(repo, template) {
        const element = template.content.cloneNode(true);
        const repoItem = element.querySelector('.repository-item');

        repoItem.dataset.repoId = repo.id;

        // 设置仓库名称和描述
        const nameElement = element.querySelector('.repository-name');
        const descElement = element.querySelector('.repository-description');

        if (nameElement) nameElement.textContent = repo.name;
        if (descElement) descElement.textContent = repo.description || '暂无描述';

        // 设置状态徽章
        const statusBadge = element.querySelector('.repository-meta .badge');
        if (statusBadge) {
            statusBadge.textContent = this.getStatusText(repo.status);
            statusBadge.className = `badge ${this.getStatusClass(repo.status)}`;
        }

        // 设置元数据
        const metaElements = element.querySelectorAll('.repository-meta small');
        if (metaElements[0]) metaElements[0].textContent = this.formatDate(repo.created_at);
        if (metaElements[1]) metaElements[1].textContent = repo.language || 'Unknown';

        // 设置统计信息
        const branchCount = element.querySelector('.branch-count');
        const fileCount = element.querySelector('.file-count');
        const docCount = element.querySelector('.doc-count');

        if (branchCount) branchCount.textContent = repo.branch_count || 0;
        if (fileCount) fileCount.textContent = repo.file_count || 0;
        if (docCount) docCount.textContent = repo.document_count || 0;

        // 在批量操作模式下添加复选框
        if (this.bulkMode) {
            const checkbox = element.querySelector('.repo-checkbox');
            if (checkbox) {
                checkbox.style.display = 'block';
                const input = checkbox.querySelector('input');
                if (input) {
                    input.checked = this.selectedRepositories.has(repo.id.toString());
                }
            }

            // 隐藏操作按钮
            const actionButtons = element.querySelector('.repository-actions');
            if (actionButtons) {
                actionButtons.style.display = 'none';
            }
        } else {
            // 隐藏复选框
            const checkbox = element.querySelector('.repo-checkbox');
            if (checkbox) {
                checkbox.style.display = 'none';
            }

            // 显示操作按钮
            const actionButtons = element.querySelector('.repository-actions');
            if (actionButtons) {
                actionButtons.style.display = 'block';
            }
        }

        return element;
    }

    renderPagination() {
        const container = document.getElementById('repoPaginationContainer');
        const pagination = document.getElementById('repoPagination');

        if (!container || !pagination) return;

        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);

        if (totalPages <= 1) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        pagination.innerHTML = '';

        // 上一页按钮
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage - 1}">上一页</a>`;
        pagination.appendChild(prevLi);

        // 页码按钮
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            pagination.appendChild(li);
        }

        // 下一页按钮
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage + 1}">下一页</a>`;
        pagination.appendChild(nextLi);

        // 绑定分页事件
        pagination.addEventListener('click', (e) => {
            e.preventDefault();
            const pageLink = e.target.closest('.page-link');
            if (pageLink && !pageLink.closest('.disabled')) {
                const page = parseInt(pageLink.dataset.page);
                this.currentPage = page;
                this.loadRepositories();
            }
        });
    }

    async generateDocument(repoId) {
        try {
            // 临时禁用API调用
            // const response = await fetch(`/api/repositories/${repoId}/generate`, {
            //     method: 'POST'
            // });

            // if (!response.ok) {
            //     throw new Error(`HTTP error! status: ${response.status}`);
            // }

            // const data = await response.json();
            // this.showSuccess('文档生成任务已创建');

            // 触发任务列表刷新
            // window.dispatchEvent(new CustomEvent('task:refresh'));

            // 临时显示成功消息
            this.showSuccess('文档生成功能已禁用（开发模式）');
        } catch (error) {
            console.error('生成文档失败:', error);
            this.showError('生成文档失败');
        }
    }

    async viewRepository(repoId) {
        try {
            // 获取仓库信息以构建MkDocs站点URL
            const response = await fetch(`/api/repositories/${repoId}`);
            if (response.ok) {
                const repo = await response.json();
                // 构建MkDocs站点URL
                const sanitizedName = repo.name.replace(/[^\w\-_]/g, '_');
                const mkdocsUrl = `/sites/${sanitizedName}_${repoId}/`;
                
                // 检查MkDocs站点是否存在
                const checkResponse = await fetch(mkdocsUrl, { method: 'HEAD' });
                if (checkResponse.ok) {
                    // 站点存在，直接跳转
                    window.location.href = mkdocsUrl;
                } else {
                    // 站点不存在，降级到仓库详情页
                    window.location.href = `/repositories/${repoId}`;
                }
            } else {
                // 获取仓库信息失败，降级到仓库详情页
                window.location.href = `/repositories/${repoId}`;
            }
        } catch (error) {
            console.error('查看仓库失败:', error);
            // 发生错误，降级到仓库详情页
            window.location.href = `/repositories/${repoId}`;
        }
    }

    editRepository(repoId) {
        // 实现编辑仓库逻辑
        console.log('编辑仓库:', repoId);
    }

    // 删除仓库功能已禁用
    /*
    async deleteRepository(repoId) {
        if (!confirm('确定要删除这个仓库吗？此操作不可撤销。')) {
            return;
        }

        try {
            const response = await fetch(`/api/repositories/${repoId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showSuccess('仓库删除成功');
            this.loadRepositories();
        } catch (error) {
            console.error('删除仓库失败:', error);
            this.showError('删除仓库失败');
        }
    }
    */

    showAddRepositoryModal() {
        // 实现添加仓库模态框
        console.log('显示添加仓库模态框');
    }

    getStatusText(status) {
        const statusMap = {
            'active': '活跃',
            'inactive': '非活跃',
            'error': '错误',
            'cloning': '克隆中',
            'analyzing': '分析中'
        };
        return statusMap[status] || status;
    }

    getStatusClass(status) {
        const classMap = {
            'active': 'bg-success',
            'inactive': 'bg-secondary',
            'error': 'bg-danger',
            'cloning': 'bg-warning',
            'analyzing': 'bg-info'
        };
        return classMap[status] || 'bg-primary';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
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
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('.repository-list-container');
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

    // 批量操作方法
    toggleBulkMode() {
        this.bulkMode = !this.bulkMode;
        this.selectedRepositories.clear();

        // 更新界面显示
        this.updateBulkModeUI();
        this.renderRepositories();
    }

    updateBulkModeUI() {
        const bulkModeBtn = document.getElementById('bulkModeBtn');
        const bulkToolbar = document.getElementById('bulkToolbar');
        const normalToolbar = document.getElementById('normalToolbar');

        if (this.bulkMode) {
            bulkModeBtn.textContent = '取消选择';
            bulkModeBtn.className = 'btn btn-secondary';
            if (bulkToolbar) bulkToolbar.style.display = 'flex';
            if (normalToolbar) normalToolbar.style.display = 'none';
        } else {
            bulkModeBtn.textContent = '批量操作';
            bulkModeBtn.className = 'btn btn-outline-primary';
            if (bulkToolbar) bulkToolbar.style.display = 'none';
            if (normalToolbar) normalToolbar.style.display = 'flex';
        }

        this.updateBulkSelectionUI();
    }

    updateBulkSelectionUI() {
        const selectedCount = this.selectedRepositories.size;
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        const selectedCountElement = document.getElementById('selectedCount');

        if (selectedCountElement) {
            selectedCountElement.textContent = `已选择 ${selectedCount} 个仓库`;
        }

        if (bulkDeleteBtn) {
            bulkDeleteBtn.disabled = selectedCount === 0;
        }
    }

    toggleRepositorySelection(repoId) {
        if (this.selectedRepositories.has(repoId)) {
            this.selectedRepositories.delete(repoId);
        } else {
            this.selectedRepositories.add(repoId);
        }

        // 更新复选框状态
        const checkbox = document.querySelector(`[data-repo-id="${repoId}"] .repo-checkbox input`);
        if (checkbox) {
            checkbox.checked = this.selectedRepositories.has(repoId);
        }

        this.updateBulkSelectionUI();
    }

    selectAll() {
        const allSelected = this.selectedRepositories.size === this.repositories.length;

        if (allSelected) {
            // 取消全选
            this.selectedRepositories.clear();
        } else {
            // 全选
            this.repositories.forEach(repo => {
                this.selectedRepositories.add(repo.id.toString());
            });
        }

        // 更新所有复选框
        document.querySelectorAll('.repo-checkbox input').forEach(checkbox => {
            const repoId = checkbox.closest('.repository-item').dataset.repoId;
            checkbox.checked = this.selectedRepositories.has(repoId);
        });

        this.updateBulkSelectionUI();
    }

    async bulkDeleteRepositories() {
        const selectedCount = this.selectedRepositories.size;

        if (selectedCount === 0) {
            this.showError('请至少选择一个仓库');
            return;
        }

        const confirmed = confirm(`确定要删除选中的 ${selectedCount} 个仓库吗？此操作不可撤销。`);
        if (!confirmed) return;

        try {
            // 临时禁用API调用
            // const repositoryIds = Array.from(this.selectedRepositories).map(id => parseInt(id));

            // const response = await fetch('/api/repositories/bulk-delete', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json'
            //     },
            //     body: JSON.stringify({ repository_ids: repositoryIds })
            // });

            // if (!response.ok) {
            //     throw new Error(`HTTP error! status: ${response.status}`);
            // }

            // const data = await response.json();

            // if (data.success) {
            //     this.showSuccess(`成功删除 ${data.deleted_count} 个仓库`);
            //     this.selectedRepositories.clear();
            //     this.toggleBulkMode();
            //     this.loadRepositories();
            // } else {
            //     throw new Error(data.message || '批量删除失败');
            // }

            // 临时显示成功消息
            this.showSuccess(`批量删除功能已禁用（开发模式）`);
            this.selectedRepositories.clear();
            this.toggleBulkMode();

        } catch (error) {
            console.error('批量删除仓库失败:', error);
            this.showError('批量删除失败: ' + error.message);
        }
    }
}

// 导出组件
window.RepositoryListComponent = RepositoryListComponent;
