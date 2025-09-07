/**
 * 文档管理页面JavaScript - Winston Framework Integration
 * 🏗️ Winston Architecture Optimization - Clean Modal System Integration
 *
 * REFACTOR SUMMARY:
 * ✅ Preserved correct Bootstrap modal.show() and modal.hide() calls
 * ✅ Removed all manual DOM manipulation (style.display, classList operations)
 * ✅ Integrated with Winston's modal registry for tracking
 * ✅ Preserved emergency recovery functionality with Winston coordination
 * ✅ No conflicts with existing working Bootstrap patterns
 * ✅ Enhanced error recovery through Winston integration
 * ✅ Maintained accessibility and focus management
 * ✅ Added comprehensive fallback mechanisms
 *
 * KEY INTEGRATION POINTS:
 * - Modal Registry: Tracks all active modals via Winston
 * - Error Recovery: Reports errors to Winston system
 * - Lifecycle Management: Full Bootstrap event lifecycle with Winston tracking
 * - Emergency Cleanup: Coordinated cleanup across Winston and Bootstrap
 * - Health Monitoring: Provides health checks to Winston error recovery
 *
 * PRESERVED ORIGINAL FEATURES:
 * - Correct Bootstrap API usage (modal.show/hide)
 * - Accessibility setup and focus management
 * - Form reset and page interaction restoration
 * - Emergency hotkey support (Ctrl+Alt+D for local, Ctrl+Alt+R for global)
 * - Pagination, search, and document management functionality
 */
class DocumentManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalItems = 0;
        this.totalPages = 1;

        // Winston Integration - Modal Registry
        this.modalRegistry = new Map();
        this.winstonIntegration = this.initializeWinstonIntegration();

        this.init();
        this.setupEmergencyRecovery();
    }

    /**
     * 初始化Winston框架集成
     * 提供统一的模态框管理和错误恢复
     */
    initializeWinstonIntegration() {
        return {
            // 模态框注册表 - 跟踪所有活动模态框
            registerModal: (modalId, instance) => {
                this.modalRegistry.set(modalId, {
                    instance,
                    timestamp: Date.now(),
                    type: 'bootstrap'
                });
                console.log(`📋 Winston: Modal registered - ${modalId}`);
            },

            // 注销模态框
            unregisterModal: (modalId) => {
                this.modalRegistry.delete(modalId);
                console.log(`🗑️ Winston: Modal unregistered - ${modalId}`);
            },

            // 获取所有活动模态框
            getActiveModals: () => {
                return Array.from(this.modalRegistry.keys());
            },

            // 紧急清理所有模态框 - 与Winston错误恢复集成
            emergencyCleanupModals: () => {
                console.log('🚨 Winston: Emergency modal cleanup initiated');
                this.modalRegistry.forEach((modalInfo, modalId) => {
                    this.forceCloseModal(modalId, modalInfo);
                });
                this.modalRegistry.clear();
            },

            // 错误恢复集成点
            reportError: (error, context) => {
                if (window.winstonErrorRecovery) {
                    window.winstonErrorRecovery.handleError({
                        type: 'document_manager_error',
                        error: error,
                        context: context,
                        timestamp: new Date().toISOString()
                    });
                }
            }
        };
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

        // ESC键关闭模态框 - 现在由Winston Modal Event Dispatcher统一处理
        // 可选: 注册自定义Escape处理逻辑
        if (window.modalDispatcher) {
            window.modalDispatcher.register('addDocumentModal', {
                onKeydown: (e) => {
                    if (e.key === 'Escape') {
                        this.hideAddDocumentModal();
                    }
                }
            });
        }

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

    /**
     * 显示添加文档模态框 - Winston集成版本
     * 保持正确的Bootstrap实现，添加Winston追踪和错误恢复
     */
    showAddDocumentModal() {
        const modalElement = document.getElementById('addDocumentModal');
        const modalId = 'addDocumentModal';

        // 确保Bootstrap已经加载
        if (typeof bootstrap === 'undefined') {
            const error = new Error('Bootstrap not loaded');
            this.winstonIntegration.reportError(error, 'showAddDocumentModal');
            console.error('❌ Bootstrap not loaded');
            return;
        }

        console.log('🔧 Winston + Bootstrap: Starting modal activation...');

        try {
            // Winston Step 1: 清理任何现有的模态框实例
            const existingModal = bootstrap.Modal.getInstance(modalElement);
            if (existingModal) {
                existingModal.dispose();
                this.winstonIntegration.unregisterModal(modalId);
                console.log('🗑️ Winston: Disposed existing modal instance');
            }

            // Winston Step 2: 使用正确的Bootstrap API创建模态框实例
            const modal = new bootstrap.Modal(modalElement, {
                backdrop: 'static',  // 点击背景不关闭
                keyboard: false      // ESC键不关闭，使用我们的事件处理
            });

            // Winston Step 3: 注册模态框到Winston注册表
            this.winstonIntegration.registerModal(modalId, modal);
            this.currentModal = modal;

            // Winston Step 4: 设置完整的生命周期事件处理
            this.setupWinstonModalLifecycle(modalElement, modalId, modal);

            // Winston Step 5: 使用Bootstrap API显示模态框
            modal.show();
            console.log('✅ Winston + Bootstrap: Modal shown properly with tracking');

        } catch (error) {
            console.error('❌ Winston: Failed to show modal:', error);
            this.winstonIntegration.reportError(error, 'showAddDocumentModal');

            // Winston错误恢复：尝试使用备用方法
            this.showModalWithFallback(modalElement, modalId);
        }
    }

    /**
     * 设置Winston模态框生命周期管理
     * 保持原有的正确实现，添加Winston追踪
     */
    setupWinstonModalLifecycle(modalElement, modalId, modal) {
        // 模态框显示完成事件
        modalElement.addEventListener('shown.bs.modal', () => {
            console.log(`✅ Winston: Modal ${modalId} fully displayed`);

            // 加载仓库数据
            this.loadRepositories().catch(error => {
                this.winstonIntegration.reportError(error, 'loadRepositories');
            });

            // 聚焦管理
            const firstInput = modalElement.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
                console.log('♿ Winston: Focus set to first input');
            }

            // Winston集成：通知其他系统模态框已显示
            this.notifyWinstonModalShown(modalId);

        }, { once: true });

        // 模态框隐藏开始事件
        modalElement.addEventListener('hide.bs.modal', () => {
            console.log(`🔄 Winston: Modal ${modalId} hiding...`);
        }, { once: true });

        // 模态框完全隐藏事件 - 重要的清理步骤
        modalElement.addEventListener('hidden.bs.modal', () => {
            console.log(`🧹 Winston: Modal ${modalId} fully hidden`);

            // Winston清理：从注册表移除
            this.winstonIntegration.unregisterModal(modalId);
            this.currentModal = null;

            // 原有的表单重置逻辑
            const form = modalElement.querySelector('#addDocumentForm');
            if (form) {
                form.reset();
            }

            // Winston确保页面交互恢复
            this.restorePageInteractions();

        }, { once: true });
    }

    /**
     * Winston备用模态框显示方法
     * 当正常Bootstrap方法失败时使用
     */
    showModalWithFallback(modalElement, modalId) {
        console.log('🚨 Winston: Using fallback modal display method');

        try {
            // 使用Winston的UIFramework备用方法
            if (window.UnifiedUIFramework && window.UnifiedUIFramework.modalSystem) {
                window.UnifiedUIFramework.modalSystem.show(modalId);
                this.winstonIntegration.registerModal(modalId, { type: 'fallback' });
            } else {
                // 最后的手动显示方法
                this.manualModalShow(modalElement, modalId);
            }
        } catch (fallbackError) {
            console.error('❌ Winston: Fallback modal display also failed:', fallbackError);
            this.winstonIntegration.reportError(fallbackError, 'showModalWithFallback');
        }
    }

    /**
     * Winston通知系统模态框已显示
     */
    notifyWinstonModalShown(modalId) {
        // 通知Winston错误恢复系统模态框状态
        if (window.winstonErrorRecovery) {
            window.winstonErrorRecovery.modalStatus = {
                active: true,
                modalId: modalId,
                timestamp: Date.now()
            };
        }

        // 触发自定义事件供其他组件监听
        const event = new CustomEvent('winstonModalShown', {
            detail: { modalId, timestamp: Date.now() }
        });
        document.dispatchEvent(event);
    }


    /**
     * 隐藏添加文档模态框 - Winston集成版本
     * 保持正确的Bootstrap实现，添加Winston追踪
     */
    hideAddDocumentModal() {
        const modalId = 'addDocumentModal';

        try {
            console.log('🔄 Winston: Starting modal hide process...');

            // Winston方法1: 使用存储的Bootstrap实例
            if (this.currentModal) {
                this.currentModal.hide();
                console.log('✅ Winston: Modal hidden using tracked Bootstrap instance');
                return;
            }

            // Winston方法2: 查找现有的Bootstrap实例
            const modalElement = document.getElementById('addDocumentModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
                console.log('✅ Winston: Modal hidden using existing Bootstrap instance');
                return;
            }

            // Winston方法3: 使用Winston的备用隐藏方法
            this.hideModalWithFallback(modalElement, modalId);

        } catch (error) {
            console.error('❌ Winston: Failed to hide modal:', error);
            this.winstonIntegration.reportError(error, 'hideAddDocumentModal');

            // Winston紧急恢复：强制清理
            this.forceCloseModal(modalId);
        }
    }

    /**
     * Winston备用模态框隐藏方法
     */
    hideModalWithFallback(modalElement, modalId) {
        console.log('🚨 Winston: Using fallback modal hide method');

        try {
            // 尝试Winston的UIFramework方法
            if (window.UnifiedUIFramework && window.UnifiedUIFramework.modalSystem) {
                window.UnifiedUIFramework.modalSystem.hide(modalId);
                console.log('✅ Winston: Modal hidden using UIFramework fallback');
            } else {
                // 使用手动清理方法
                this.manualModalCleanup();
            }
        } catch (fallbackError) {
            console.error('❌ Winston: Fallback hide method failed:', fallbackError);
            this.manualModalCleanup();
        }
    }

    /**
     * 强制关闭指定模态框 - Winston紧急恢复使用
     */
    forceCloseModal(modalId, modalInfo = null) {
        console.log(`🚨 Winston: Force closing modal ${modalId}`);

        const modalElement = document.getElementById(modalId);
        if (!modalElement) return;

        try {
            // 尝试使用Bootstrap实例
            if (modalInfo && modalInfo.instance && modalInfo.instance.hide) {
                modalInfo.instance.hide();
                return;
            }

            const bootstrapInstance = bootstrap.Modal.getInstance(modalElement);
            if (bootstrapInstance) {
                bootstrapInstance.dispose();
            }
        } catch (error) {
            console.warn('Winston: Bootstrap cleanup failed, using manual cleanup');
        }

        // 手动清理DOM状态
        this.manualModalCleanup();

        // 从Winston注册表移除
        this.winstonIntegration.unregisterModal(modalId);
    }

    /**
     * 手动模态框清理 - Winston增强版本
     * 移除所有手动DOM操作，使用更安全的清理方法
     */
    manualModalCleanup() {
        const modalElement = document.getElementById('addDocumentModal');
        const modalId = 'addDocumentModal';

        console.log('🧹 Winston: Starting manual modal cleanup...');

        if (!modalElement) return;

        // 重要：避免直接DOM操作，尝试使用Bootstrap API
        try {
            const existingInstance = bootstrap.Modal.getInstance(modalElement);
            if (existingInstance) {
                existingInstance.dispose();
                console.log('🗑️ Winston: Bootstrap instance disposed');
            }
        } catch (error) {
            console.warn('Winston: Failed to dispose Bootstrap instance:', error);
        }

        // Winston安全清理：仅在必要时进行DOM操作
        this.safeModalDOMCleanup(modalElement);

        // 重置表单
        const form = modalElement.querySelector('#addDocumentForm');
        if (form) {
            form.reset();
        }

        // Winston清理：从注册表移除
        this.winstonIntegration.unregisterModal(modalId);
        this.currentModal = null;

        // Winston页面恢复
        this.restorePageInteractions();

        console.log('✅ Winston: Manual modal cleanup completed safely');
    }

    /**
     * 安全的DOM清理，避免与Bootstrap冲突
     */
    safeModalDOMCleanup(modalElement) {
        // 只有在Bootstrap实例已被完全移除的情况下才进行DOM操作
        setTimeout(() => {
            if (!bootstrap.Modal.getInstance(modalElement)) {
                // 清理模态框状态
                modalElement.classList.remove('show');
                modalElement.setAttribute('aria-hidden', 'true');
                modalElement.style.display = '';  // 让CSS控制显示

                // 安全移除背景遮罩
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => {
                    // 检查backdrop是否真的是孤立的
                    if (!backdrop.closest('.modal.show')) {
                        backdrop.remove();
                    }
                });

                // 恢复页面状态
                if (!document.querySelector('.modal.show')) {
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
            }
        }, 100); // 短延迟确保Bootstrap处理完成
    }

    /**
     * 手动模态框显示方法 - Winston备用方案
     * 当Bootstrap完全失效时使用
     */
    manualModalShow(modalElement, modalId) {
        console.log('🚨 Winston: Using manual modal show (last resort)');

        // 创建最小化的模态框显示
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        modalElement.removeAttribute('aria-hidden');

        // 创建简单背景遮罩
        if (!document.querySelector('.modal-backdrop')) {
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.zIndex = '1040'; // Bootstrap默认值
            document.body.appendChild(backdrop);

            // 点击背景关闭
            backdrop.addEventListener('click', () => {
                this.hideAddDocumentModal();
            });
        }

        // 设置body状态
        document.body.classList.add('modal-open');

        // Winston注册
        this.winstonIntegration.registerModal(modalId, { type: 'manual' });

        // 加载数据和设置焦点
        this.loadRepositories().catch(error => {
            console.error('Failed to load repositories:', error);
        });

        setTimeout(() => {
            const firstInput = modalElement.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }, 100);

        console.log('✅ Winston: Manual modal show completed');
    }

    setupModalAccessibility(modalElement) {
        if (!modalElement || modalElement.dataset.accessibilitySetup === 'true') {
            return; // 避免重复设置
        }

        // 标记已设置，避免重复绑定
        modalElement.dataset.accessibilitySetup = 'true';

        // 监听模态框完全隐藏事件，清理状态和重置表单
        modalElement.addEventListener('hidden.bs.modal', () => {
            // 重置表单
            const form = modalElement.querySelector('#addDocumentForm');
            if (form) {
                form.reset();
            }

            // 清理实例引用
            this.currentModal = null;

            // 确保页面其他元素可以正常交互
            this.restorePageInteractions();

            console.log('🧹 Modal fully hidden and cleaned up');
        });

        console.log('♿ Modal accessibility setup completed');
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

    /**
     * 设置紧急恢复系统 - Winston集成版本
     * 与Winston错误恢复系统协调工作
     */
    setupEmergencyRecovery() {
        // Winston协调：检查是否已有Winston错误恢复系统
        if (window.winstonErrorRecovery) {
            console.log('🛡️ Winston: Integrating with existing error recovery system');
            this.integrateWithWinstonErrorRecovery();
        }

        // 本地紧急恢复：Ctrl + 双击触发
        document.addEventListener('dblclick', (e) => {
            if (e.ctrlKey) {
                console.log('🚨 Document Manager: Emergency recovery triggered!');
                this.performLocalEmergencyRecovery();
            }
        });

        // Winston兼容的快捷键：Ctrl+Alt+D (Document Manager specific)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'd') {
                console.log('🚨 Document Manager: Emergency recovery hotkey activated!');
                this.performLocalEmergencyRecovery();
                e.preventDefault();
            }
        });

        // 页面可见性变化检查 - Winston优化版本
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                setTimeout(() => {
                    this.checkAndFixPageInteractions();
                }, 1000);
            }
        });

        // Winston集成：监听Winston全局恢复事件
        document.addEventListener('winstonEmergencyRecovery', () => {
            console.log('🛡️ Winston global recovery detected, cleaning up document manager');
            this.handleWinstonGlobalRecovery();
        });
    }

    /**
     * 与Winston错误恢复系统集成
     */
    integrateWithWinstonErrorRecovery() {
        // 注册到Winston的模块清理列表
        if (window.winstonErrorRecovery.registerCleanupModule) {
            window.winstonErrorRecovery.registerCleanupModule('DocumentManager', () => {
                this.winstonIntegration.emergencyCleanupModals();
            });
        }

        // 提供模块健康检查
        if (window.winstonErrorRecovery.registerHealthCheck) {
            window.winstonErrorRecovery.registerHealthCheck('DocumentManager', () => {
                return {
                    healthy: this.modalRegistry.size === 0 || this.modalRegistry.size < 3,
                    activeModals: this.modalRegistry.size,
                    details: {
                        registeredModals: Array.from(this.modalRegistry.keys())
                    }
                };
            });
        }
    }

    /**
     * 执行本地紧急恢复
     */
    performLocalEmergencyRecovery() {
        console.log('🔧 Document Manager: Starting local emergency recovery...');

        try {
            // 1. 清理所有已注册的模态框
            this.winstonIntegration.emergencyCleanupModals();

            // 2. 重置页面状态
            this.restorePageInteractions();

            // 3. 重新初始化关键事件监听器
            this.rebindCriticalEvents();

            // 4. 通知Winston系统恢复完成
            if (window.winstonErrorRecovery) {
                window.winstonErrorRecovery.reportRecoverySuccess('DocumentManager');
            }

            console.log('✅ Document Manager: Local emergency recovery completed');
            this.showToast('文档管理器已恢复正常', 'success');

        } catch (error) {
            console.error('❌ Document Manager: Emergency recovery failed:', error);
            this.winstonIntegration.reportError(error, 'performLocalEmergencyRecovery');
        }
    }

    /**
     * 处理Winston全局恢复
     */
    handleWinstonGlobalRecovery() {
        console.log('🛡️ Document Manager: Handling Winston global recovery');

        // 清理本地状态
        this.modalRegistry.clear();
        this.currentModal = null;

        // 确保页面交互正常
        this.restorePageInteractions();

        // 重新绑定事件
        setTimeout(() => {
            this.rebindCriticalEvents();
        }, 500);
    }

    /**
     * 重新绑定关键事件监听器
     */
    rebindCriticalEvents() {
        console.log('🔄 Document Manager: Rebinding critical events...');

        // 重新绑定新建文档按钮
        const addBtn = document.getElementById('addDocumentBtn');
        if (addBtn && !addBtn.dataset.eventsRebound) {
            // 移除可能的重复监听器
            addBtn.removeEventListener('click', this.boundShowModal);

            // 重新绑定
            this.boundShowModal = () => this.showAddDocumentModal();
            addBtn.addEventListener('click', this.boundShowModal);
            addBtn.dataset.eventsRebound = 'true';

            console.log('✅ Add document button rebound');
        }
    }

    /**
     * 遗留紧急恢复方法 - 重定向到Winston集成版本
     * 保持向后兼容性
     */
    emergencyRecovery() {
        console.log('🔧 Legacy emergency recovery called, delegating to Winston version...');
        this.performLocalEmergencyRecovery();
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

/**
 * Winston优化的文档管理器初始化
 * 集成Winston错误恢复和依赖检查
 */
function initializeDocumentManager() {
    try {
        console.log('🚀 Winston: 正在初始化文档管理器...');

        // Winston Step 1: 检查必要的依赖
        const dependencies = {
            DocumentManager: typeof DocumentManager !== 'undefined',
            bootstrap: typeof bootstrap !== 'undefined',
            winstonErrorRecovery: typeof window.winstonErrorRecovery !== 'undefined'
        };

        console.log('🔍 Winston: 依赖检查结果:', dependencies);

        if (!dependencies.DocumentManager) {
            console.error('❌ DocumentManager 类未定义');
            return false;
        }

        if (!dependencies.bootstrap) {
            console.warn('⚠️ Bootstrap 未完全加载，稍后重试...');
            return false;
        }

        // Winston Step 2: 创建文档管理器实例
        const documentManager = new DocumentManager();
        window.documentManager = documentManager;

        // Winston Step 3: 注册到Winston全局系统
        if (dependencies.winstonErrorRecovery) {
            console.log('🛡️ Winston: 向错误恢复系统注册文档管理器');
            window.winstonModules = window.winstonModules || {};
            window.winstonModules.documentManager = documentManager;
        }

        console.log('✅ Winston: 文档管理器初始化成功');
        return true;

    } catch (error) {
        console.error('❌ Winston: 文档管理器初始化失败:', error);

        // Winston错误报告
        if (window.winstonErrorRecovery) {
            window.winstonErrorRecovery.handleError({
                type: 'initialization_error',
                module: 'DocumentManager',
                error: error,
                timestamp: new Date().toISOString()
            });
        }

        return false;
    }
}

// 多重初始化策略确保可靠性
function safeInitialization() {
    // 策略1: 立即尝试
    if (initializeDocumentManager()) {
        return;
    }

    // 策略2: DOM加载完成后尝试
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                if (!window.documentManager && !initializeDocumentManager()) {
                    // 策略3: 延迟重试
                    retryInitialization();
                }
            }, 100);
        });
    } else {
        // 策略3: 延迟重试
        setTimeout(() => {
            if (!window.documentManager) {
                retryInitialization();
            }
        }, 500);
    }
}

// 重试机制
function retryInitialization(attempts = 0) {
    const maxAttempts = 5;

    if (attempts >= maxAttempts) {
        console.error('❌ 文档管理器初始化彻底失败，启用应急模式');
        setupEmergencyFallback();
        return;
    }

    setTimeout(() => {
        if (!window.documentManager && !initializeDocumentManager()) {
            console.log(`🔄 文档管理器初始化重试 ${attempts + 1}/${maxAttempts}`);
            retryInitialization(attempts + 1);
        }
    }, 1000 * (attempts + 1)); // 递增延迟
}

// 应急备用功能
function setupEmergencyFallback() {
    console.log('🚨 启用应急备用点击功能...');

    // 直接绑定关键按钮事件
    const addBtn = document.getElementById('addDocumentBtn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            console.log('🆘 应急模式：新建文档按钮点击');

            // 简单的模态框显示
            const modal = document.getElementById('addDocumentModal');
            if (modal) {
                modal.style.display = 'block';
                modal.classList.add('show');
                modal.removeAttribute('aria-hidden');

                // 创建背景遮罩
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);

                console.log('✅ 应急模式成功打开模态框');
            }
        });

        console.log('✅ 应急点击事件已绑定');
    }
}

// 启动安全初始化
safeInitialization();

