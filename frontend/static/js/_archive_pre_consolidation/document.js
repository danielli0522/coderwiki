/**
 * 文档管理页面JavaScript
 */
class DocumentManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalItems = 0;
        this.totalPages = 1;
        this.init();
        this.setupEmergencyRecovery();
    }

    init() {
        this.bindEvents();
        this.setupModalAccessibility(document.getElementById('addDocumentModal'));
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

        // 模态框关闭按钮
        document.querySelectorAll('#addDocumentModal .btn-close, #addDocumentModal [data-bs-dismiss="modal"]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideAddDocumentModal();
            });
        });

        // 模态框背景点击关闭
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.hideAddDocumentModal();
            }
        });

        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('addDocumentModal');
                if (modal && modal.classList.contains('show')) {
                    this.hideAddDocumentModal();
                }
            }
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
            const apiClient = window.api || new ApiClient();
            const data = await apiClient.request(`/documents?page=${this.currentPage}&limit=${this.pageSize}&search=${search}&status=${status}`);

            this.renderDocuments(data.documents || []);
            this.updateStats(data.stats || {});
            this.updatePagination(data.pagination || {});
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

        updatePagination(pagination) {
        this.totalItems = pagination.total || 0;
        this.totalPages = Math.ceil(this.totalItems / this.pageSize);

        // 更新分页信息显示
        document.getElementById('currentPageInfo').textContent = this.currentPage;
        document.getElementById('totalPagesInfo').textContent = this.totalPages;
        document.getElementById('totalItemsInfo').textContent = this.totalItems;

        // 渲染分页按钮
        this.renderPagination();
        this.bindPaginationEvents();
    }

    renderPagination() {
        const pagination = document.getElementById('documentPagination');
        if (!pagination) return;

        pagination.innerHTML = '';

        if (this.totalPages <= 1) {
            return;
        }

        // 上一页按钮
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage - 1}">上一页</a>`;
        pagination.appendChild(prevLi);

        // 页码按钮
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(this.totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            pagination.appendChild(li);
        }

        // 下一页按钮
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === this.totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage + 1}">下一页</a>`;
        pagination.appendChild(nextLi);
    }

        bindPaginationEvents() {
        const pagination = document.getElementById('documentPagination');
        if (!pagination) return;

        // 移除之前的事件监听器（如果存在）
        if (this.paginationClickHandler) {
            pagination.removeEventListener('click', this.paginationClickHandler);
        }

        // 创建新的事件处理函数并保存引用
        this.paginationClickHandler = this.handlePaginationClick.bind(this);
        pagination.addEventListener('click', this.paginationClickHandler);
    }

    handlePaginationClick(e) {
        e.preventDefault();
        const pageLink = e.target.closest('.page-link');

        if (pageLink && !pageLink.closest('.disabled')) {
            const page = parseInt(pageLink.dataset.page);

            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
                this.loadDocuments();
            }
        }
    }

    async loadRepositories() {
        const select = document.getElementById('repositorySelect');
        if (!select) return;

        try {
            // 使用ApiClient进行请求
            const apiClient = window.api || new ApiClient();
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
        const modalElement = document.getElementById('addDocumentModal');
        
        // 确保Bootstrap已经加载
        if (typeof bootstrap === 'undefined') {
            console.error('Bootstrap not loaded');
            return;
        }
        
        console.log('🔧 Starting modal activation process...');
        
        try {
            // 激进方式 1: 立即强制移除 aria-hidden
            modalElement.removeAttribute('aria-hidden');
            console.log('✅ Immediately removed aria-hidden');
            
            // 激进方式 2: 设置 inert 属性管理
            document.body.style.overflow = 'hidden';
            
            // 先清理任何现有的模态框实例
            const existingModal = bootstrap.Modal.getInstance(modalElement);
            if (existingModal) {
                existingModal.dispose();
                console.log('🗑️ Disposed existing modal instance');
            }
            
            // 激进方式 3: 直接操作DOM显示
            modalElement.style.display = 'block';
            modalElement.classList.add('show');
            
            // 创建背景遮罩
            if (!document.querySelector('.modal-backdrop')) {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                console.log('🎭 Created modal backdrop');
            }
            
            // 激进方式 4: 强制焦点管理
            setTimeout(() => {
                const firstInput = modalElement.querySelector('input, select, textarea');
                if (firstInput) {
                    firstInput.focus();
                    console.log('🎯 Set focus to first input');
                }
            }, 100);
            
            // 激进方式 5: 属性监控器
            this.setupAriaHiddenMonitor(modalElement);
            
            // 重新加载仓库列表
            this.loadRepositories();
            console.log('📋 Loaded repositories');
            
        } catch (error) {
            console.error('❌ Failed to show modal:', error);
        }
    }

    setupAriaHiddenMonitor(modalElement) {
        // 创建属性监控器，防止 aria-hidden 被重新设置
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'aria-hidden') {
                    if (modalElement.getAttribute('aria-hidden') === 'true' && modalElement.classList.contains('show')) {
                        console.warn('⚠️ Detected aria-hidden=true on visible modal, fixing...');
                        modalElement.removeAttribute('aria-hidden');
                    }
                }
            });
        });
        
        observer.observe(modalElement, {
            attributes: true,
            attributeFilter: ['aria-hidden']
        });
        
        // 5秒后停止监控
        setTimeout(() => {
            observer.disconnect();
            console.log('🔍 Aria-hidden monitor disconnected');
        }, 5000);
    }

    hideAddDocumentModal() {
        const modalElement = document.getElementById('addDocumentModal');
        
        // 隐藏模态框
        modalElement.style.display = 'none';
        modalElement.classList.remove('show');
        modalElement.setAttribute('aria-hidden', 'true');
        
        // 移除背景遮罩
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // 恢复页面滚动
        document.body.style.overflow = '';
        
        // 重置表单
        const form = modalElement.querySelector('#addDocumentForm');
        if (form) {
            form.reset();
        }
        
        console.log('✅ Modal hidden and page interactions restored');
    }

    setupModalAccessibility(modalElement) {
        if (!modalElement || modalElement.dataset.accessibilitySetup === 'true') {
            return; // 避免重复设置
        }
        
        // 标记已设置，避免重复绑定
        modalElement.dataset.accessibilitySetup = 'true';
        
        // 监听模态框显示事件，确保正确处理aria-hidden
        modalElement.addEventListener('show.bs.modal', () => {
            // 移除aria-hidden属性，避免与焦点冲突
            modalElement.removeAttribute('aria-hidden');
        });

        // 监听模态框隐藏事件，恢复aria-hidden
        modalElement.addEventListener('hide.bs.modal', () => {
            modalElement.setAttribute('aria-hidden', 'true');
        });

        // 监听模态框完全显示事件，确保焦点正确设置
        modalElement.addEventListener('shown.bs.modal', () => {
            // 确保焦点在模态框内的第一个可交互元素
            const firstFocusable = modalElement.querySelector('input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])');
            if (firstFocusable) {
                setTimeout(() => {
                    firstFocusable.focus();
                }, 100);
            }
        });

        // 监听模态框完全隐藏事件，清理状态
        modalElement.addEventListener('hidden.bs.modal', () => {
            // 重置表单
            const form = modalElement.querySelector('#addDocumentForm');
            if (form) {
                form.reset();
            }
            
            // 确保页面其他元素可以正常交互
            this.restorePageInteractions();
        });
    }

    restorePageInteractions() {
        // 移除可能阻止交互的样式或属性
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');
        
        // 移除模态框背景遮罩可能的干扰
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            if (backdrop.parentNode) {
                backdrop.parentNode.removeChild(backdrop);
            }
        });
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
            const apiClient = window.api || new ApiClient();
            await apiClient.request('/documents', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            this.showToast('文档创建成功', 'success');
            this.hideAddDocumentModal();
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
            const apiClient = window.api || new ApiClient();
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

    setupEmergencyRecovery() {
        // 紧急恢复：双击页面任意位置恢复交互
        document.addEventListener('dblclick', (e) => {
            if (e.ctrlKey) { // Ctrl + 双击触发紧急恢复
                console.log('🚨 Emergency page interaction recovery triggered!');
                this.emergencyRecovery();
            }
        });

        // 紧急恢复：Ctrl+Alt+R
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.altKey && e.key === 'r') {
                console.log('🚨 Emergency recovery hotkey activated!');
                this.emergencyRecovery();
                e.preventDefault();
            }
        });

        // 页面可见性变化时检查
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                setTimeout(() => {
                    this.checkAndFixPageInteractions();
                }, 1000);
            }
        });
    }

    emergencyRecovery() {
        console.log('🔧 Starting emergency page recovery...');
        
        // 1. 关闭所有模态框
        const allModals = document.querySelectorAll('.modal');
        allModals.forEach(modal => {
            modal.style.display = 'none';
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
        });

        // 2. 移除所有背景遮罩
        const allBackdrops = document.querySelectorAll('.modal-backdrop');
        allBackdrops.forEach(backdrop => backdrop.remove());

        // 3. 恢复页面滚动
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');

        // 4. 移除所有可能阻塞的样式
        document.body.style.pointerEvents = '';
        document.documentElement.style.overflow = '';

        // 5. 重新启用所有按钮
        const allButtons = document.querySelectorAll('button[disabled]');
        allButtons.forEach(btn => {
            if (!btn.dataset.permanentlyDisabled) {
                btn.disabled = false;
            }
        });

        // 6. 重新初始化关键事件监听器（如果需要）
        setTimeout(() => {
            // 重新绑定主要的事件监听器
            const addBtn = document.getElementById('addDocumentBtn');
            if (addBtn && !addBtn.hasAttribute('data-events-bound')) {
                addBtn.addEventListener('click', () => this.showAddDocumentModal());
                addBtn.setAttribute('data-events-bound', 'true');
            }
        }, 100);

        console.log('✅ Emergency recovery completed - page should be interactive now');
        
        // 显示恢复成功消息
        this.showToast('页面交互已恢复', 'success');
    }

    checkAndFixPageInteractions() {
        // 检查页面是否存在交互问题
        const hasModalBackdrop = document.querySelector('.modal-backdrop');
        const hasVisibleModal = document.querySelector('.modal.show');
        const bodyHasModalOpen = document.body.classList.contains('modal-open');

        if (hasModalBackdrop && !hasVisibleModal) {
            console.warn('⚠️ Found orphaned modal backdrop, cleaning up...');
            hasModalBackdrop.remove();
        }

        if (bodyHasModalOpen && !hasVisibleModal) {
            console.warn('⚠️ Found modal-open class without visible modal, cleaning up...');
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
        }

        // 检查是否有元素设置了 aria-hidden 但具有焦点
        const focusedElement = document.activeElement;
        if (focusedElement && focusedElement.closest('[aria-hidden="true"]')) {
            console.warn('⚠️ Found focused element with aria-hidden, fixing...');
            const ariaHiddenParent = focusedElement.closest('[aria-hidden="true"]');
            ariaHiddenParent.removeAttribute('aria-hidden');
        }
    }
}

// 全局紧急恢复函数
window.emergencyRecovery = function() {
    if (window.documentManager) {
        window.documentManager.emergencyRecovery();
    }
};

// 初始化文档管理器
const documentManager = new DocumentManager();
window.documentManager = documentManager; // 全局访问

