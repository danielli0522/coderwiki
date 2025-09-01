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
            this.loadRepositories();
            this.loadStatistics();
        } else {
            console.log('用户未登录，跳过仓库管理初始化');
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
        const getStatusBadge = (status) => {
            const statusMap = {
                'active': '<span class="badge bg-success">活跃</span>',
                'inactive': '<span class="badge bg-secondary">非活跃</span>',
                'error': '<span class="badge bg-danger">错误</span>',
                'cloning': '<span class="badge bg-warning">克隆中</span>',
                'completed': '<span class="badge bg-success">已完成</span>'
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
            <td>${getStatusBadge(repo.status)}</td>
            <td>
                ${repo.clone_status === 'completed' ? 
                    '<span class="badge bg-success">已完成</span>' : 
                    repo.clone_status === 'failed' ? 
                    '<span class="badge bg-danger">失败</span>' :
                    '<span class="badge bg-warning">未知</span>'
                }
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