/**
 * 文档管理页面JavaScript
 */
class DocumentManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDocuments();
        this.loadRepositories();
    }

    bindEvents() {
        // 新建文档按钮
        document.getElementById('addDocumentBtn')?.addEventListener('click', () => {
            this.showAddDocumentModal();
        });

        // 创建文档按钮
        document.getElementById('createDocumentBtn')?.addEventListener('click', () => {
            this.createDocument();
        });

        // 搜索功能
        document.getElementById('searchDocuments')?.addEventListener('input', (e) => {
            this.debounce(() => this.loadDocuments(), 300)();
        });

        // 状态过滤
        document.getElementById('statusFilter')?.addEventListener('change', () => {
            this.loadDocuments();
        });
    }

    async loadDocuments() {
        const tbody = document.getElementById('documentsTableBody');
        if (!tbody) return;

        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="fas fa-spinner fa-spin"></i> 加载中...
                </td>
            </tr>
        `;

        try {
            const search = document.getElementById('searchDocuments')?.value || '';
            const status = document.getElementById('statusFilter')?.value || '';

            // 使用ApiClient进行请求
            const apiClient = window.apiClient || new ApiClient();
            const data = await apiClient.request(`/documents?page=${this.currentPage}&limit=${this.pageSize}&search=${search}&status=${status}`);

            this.renderDocuments(data.documents || []);
            this.updateStats(data.stats || {});
        } catch (error) {
            console.error('加载文档失败:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle"></i> 加载失败
                    </td>
                </tr>
            `;
        }
    }

    renderDocuments(documents) {
        const tbody = document.getElementById('documentsTableBody');
        if (!tbody) return;

        if (documents.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        暂无文档
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = documents.map(doc => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <i class="fas fa-file-alt text-primary me-2"></i>
                        <div>
                            <div class="fw-bold">${doc.title}</div>
                            <small class="text-muted">${doc.description || '无描述'}</small>
                        </div>
                    </div>
                </td>
                <td>${doc.repository_name || '未知仓库'}</td>
                <td>
                    <span class="badge bg-${this.getStatusBadgeClass(doc.status)}">
                        ${this.getStatusText(doc.status)}
                    </span>
                </td>
                <td>${this.formatDate(doc.created_at)}</td>
                <td>${this.formatDate(doc.updated_at)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="documentManager.viewDocument(${doc.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="documentManager.editDocument(${doc.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="documentManager.deleteDocument(${doc.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    updateStats(stats) {
        document.getElementById('totalDocuments').textContent = stats.total || 0;
        document.getElementById('processingDocuments').textContent = stats.processing || 0;
        document.getElementById('completedDocuments').textContent = stats.completed || 0;
        document.getElementById('errorDocuments').textContent = stats.error || 0;
    }

    async loadRepositories() {
        const select = document.getElementById('repositorySelect');
        if (!select) return;

        try {
            // 使用ApiClient进行请求
            const apiClient = window.apiClient || new ApiClient();
            const data = await apiClient.request('/repositories');
            const repositories = data.repositories || [];

            select.innerHTML = '<option value="">请选择仓库</option>';
            repositories.forEach(repo => {
                const option = document.createElement('option');
                option.value = repo.id;
                option.textContent = repo.name;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('加载仓库失败:', error);
            select.innerHTML = '<option value="">加载仓库失败</option>';
        }
    }

    showAddDocumentModal() {
        const modal = new bootstrap.Modal(document.getElementById('addDocumentModal'));
        modal.show();

        // 重新加载仓库列表
        this.loadRepositories();

        // 确保模态框可以正常交互
        setTimeout(() => {
            if (window.fixModalInteractions) {
                window.fixModalInteractions();
            }
        }, 100);
    }

    async createDocument() {
        const form = document.getElementById('addDocumentForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = {
            title: document.getElementById('documentName').value,
            repository_id: document.getElementById('repositorySelect').value,
            document_type: document.getElementById('documentType').value,
            description: document.getElementById('documentDescription').value
        };

        const submitBtn = document.getElementById('createDocumentBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 创建中...';

        try {
            // 使用ApiClient进行请求
            const apiClient = window.apiClient || new ApiClient();
            await apiClient.request('/documents', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            this.showToast('文档创建成功', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addDocumentModal')).hide();
            form.reset();
            this.loadDocuments();
        } catch (error) {
            console.error('创建文档失败:', error);
            this.showToast(error.message || '创建文档失败', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '创建文档';
        }
    }

    async viewDocument(id) {
        try {
            // 直接跳转到文档查看器页面
            window.location.href = `/documents/${id}/view`;
        } catch (error) {
            console.error('查看文档失败:', error);
            this.showToast(error.message, 'error');
        }
    }

    async editDocument(id) {
        this.showToast('文档编辑功能开发中', 'info');
    }

    async deleteDocument(id) {
        if (!confirm('确定要删除这个文档吗？')) {
            return;
        }

        try {
            // 使用ApiClient进行请求
            const apiClient = window.apiClient || new ApiClient();
            await apiClient.request(`/documents/${id}`, {
                method: 'DELETE'
            });

            this.showToast('文档删除成功', 'success');
            this.loadDocuments();
        } catch (error) {
            console.error('删除文档失败:', error);
            this.showToast(error.message || '删除文档失败', 'error');
        }
    }

    getStatusBadgeClass(status) {
        const statusMap = {
            'processing': 'warning',
            'completed': 'success',
            'error': 'danger',
            'pending': 'secondary'
        };
        return statusMap[status] || 'secondary';
    }

    getStatusText(status) {
        const statusMap = {
            'processing': '处理中',
            'completed': '已完成',
            'error': '错误',
            'pending': '等待中'
        };
        return statusMap[status] || '未知';
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    showToast(message, type = 'info') {
        // 使用现有的toast系统
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            alert(message);
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
}

// 初始化文档管理器
const documentManager = new DocumentManager();

