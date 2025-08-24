/**
 * Repository management JavaScript
 */

class RepositoryManager {
    constructor() {
        this.repositories = [];
        this.statistics = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadRepositories();
        this.loadStatistics();
        this.fixModalInteractions(); // 添加模态框修复
    }

    // 添加模态框修复方法 - 现在由RepositoryModalFix处理
    fixModalInteractions() {
        // 检查是否有RepositoryModalFix可用
        if (window.RepositoryModalFix) {
            console.log('RepositoryModalFix已可用，跳过本地修复');
            return;
        }

        // 备用修复方法
        console.log('使用备用模态框修复方法...');

        // 监听模态框显示事件
        document.addEventListener('shown.bs.modal', (event) => {
            if (event.target.id === 'addRepositoryModal') {
                this.fixRepositoryModal();
            }
        });

        // 页面加载时也尝试修复
        setTimeout(() => {
            this.fixRepositoryModal();
        }, 1000);
    }

    fixRepositoryModal() {
        const modal = document.getElementById('addRepositoryModal');
        if (!modal) return;

        // 修复所有输入元素
        const inputs = modal.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.style.pointerEvents = 'auto';
            input.style.zIndex = '10000';
            input.style.position = 'relative';
            input.disabled = false;
            input.readOnly = false;

            // 确保输入框可以获得焦点
            input.addEventListener('focus', function() {
                this.style.zIndex = '10001';
                this.style.outline = '2px solid #007bff';
                this.style.outlineOffset = '2px';
            });

            input.addEventListener('blur', function() {
                this.style.outline = '';
                this.style.outlineOffset = '';
            });
        });

        // 修复所有按钮
        const buttons = modal.querySelectorAll('button, .btn');
        buttons.forEach(button => {
            button.style.pointerEvents = 'auto';
            button.style.zIndex = '10000';
            button.style.position = 'relative';
            button.style.cursor = 'pointer';
            button.disabled = false;
        });

        // 修复表单
        const form = modal.querySelector('form');
        if (form) {
            form.style.pointerEvents = 'auto';
            form.style.zIndex = '10000';
            form.style.position = 'relative';
        }

        // 修复模态框本身
        modal.style.pointerEvents = 'auto';
        modal.style.zIndex = '9999';

        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.pointerEvents = 'auto';
            modalContent.style.zIndex = '9999';
        }

        const modalDialog = modal.querySelector('.modal-dialog');
        if (modalDialog) {
            modalDialog.style.pointerEvents = 'auto';
            modalDialog.style.zIndex = '9999';
        }

        console.log('仓库模态框交互已修复');
    }

    bindEvents() {
        // 添加仓库表单提交
        document.getElementById('addRepoBtn')?.addEventListener('click', () => this.addRepository());

        // URL 验证
        document.getElementById('validateUrlBtn')?.addEventListener('click', () => this.validateUrl());
        document.getElementById('repoUrl')?.addEventListener('input', () => this.clearValidation());

        // 搜索和筛选
        document.getElementById('searchRepo')?.addEventListener('input', () => this.filterRepositories());
        document.getElementById('statusFilter')?.addEventListener('change', () => this.filterRepositories());

        // 表单回车提交
        document.getElementById('addRepositoryForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addRepository();
        });
    }

    async loadRepositories() {
        try {
            console.log('开始加载仓库列表...');

            const response = await fetch('/api/repositories', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            console.log('API响应状态:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('API返回数据结构:', data);

            this.repositories = data.repositories || data.data || [];
            console.log(`加载到 ${this.repositories.length} 个仓库`);

            this.renderRepositories();

            // 隐藏加载状态
            const loadingState = document.getElementById('loadingState');
            if (loadingState) {
                loadingState.style.display = 'none';
            }

            // 显示空状态（如果没有仓库）
            if (this.repositories.length === 0) {
                const emptyState = document.getElementById('emptyState');
                if (emptyState) {
                    emptyState.style.display = 'block';
                }
            }

        } catch (error) {
            console.error('Error loading repositories:', error);
            this.showError('加载仓库列表失败: ' + error.message);
        }
    }

    async loadStatistics() {
        try {
            console.log('开始加载统计数据...');

            const response = await fetch('/api/repositories/statistics', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            console.log('统计API响应状态:', response.status);

            if (!response.ok) {
                throw new Error('加载统计数据失败');
            }

            const data = await response.json();
            console.log('统计API返回数据结构:', data);

            this.statistics = data.statistics || data;
            this.renderStatistics();

        } catch (error) {
            console.error('Error loading statistics:', error);
            console.error('加载统计数据失败:', error);
        }
    }

    renderStatistics() {
        document.getElementById('totalRepos').textContent = this.statistics.total_repositories || 0;
        document.getElementById('activeRepos').textContent = this.statistics.active_repositories || 0;
        document.getElementById('clonedRepos').textContent = this.statistics.cloned_repositories || 0;
        document.getElementById('totalFiles').textContent = this.formatNumber(this.statistics.total_files || 0);
    }

    renderRepositories() {
        const tbody = document.getElementById('repositoriesTable');
        tbody.innerHTML = '';

        this.repositories.forEach(repo => {
            const row = this.createRepositoryRow(repo);
            tbody.appendChild(row);
        });
    }

    createRepositoryRow(repo) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-folder text-primary me-2"></i>
                    <div>
                        <div class="fw-bold">${this.escapeHtml(repo.name)}</div>
                        ${repo.description ? `<small class="text-muted">${this.escapeHtml(repo.description)}</small>` : ''}
                    </div>
                </div>
            </td>
            <td>
                <a href="${this.escapeHtml(repo.url)}" target="_blank" class="text-decoration-none">
                    ${this.truncateUrl(this.escapeHtml(repo.url))}
                </a>
            </td>
            <td>
                ${this.getStatusBadge(repo.status)}
            </td>
            <td>
                ${this.getCloneStatusBadge(repo.clone_status)}
            </td>
            <td>${this.formatNumber(repo.file_count || 0)}</td>
            <td>${this.formatFileSize(repo.repo_size || 0)}</td>
            <td>${this.formatDate(repo.created_at)}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary" onclick="repositoryManager.showRepositoryDetail(${repo.id})" title="查看详情">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${repo.clone_status === 'completed' ? `
                        <button class="btn btn-sm btn-outline-info" onclick="repositoryManager.viewAnalysisResults(${repo.id})" title="查看分析结果">
                            <i class="fas fa-chart-line"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-primary" onclick="repositoryManager.analyzeRepository(${repo.id})" title="分析仓库">
                            <i class="fas fa-chart-bar"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="repositoryManager.syncRepository(${repo.id})" title="同步仓库">
                            <i class="fas fa-sync"></i>
                        </button>
                    ` : ''}
                    <!-- 删除仓库功能已禁用 -->
                    <!--
                    <button class="btn btn-sm btn-outline-danger" onclick="repositoryManager.deleteRepository(${repo.id})" title="删除仓库">
                        <i class="fas fa-trash"></i>
                    </button>
                    -->
                </div>
            </td>
        `;
        return row;
    }

    getStatusBadge(status) {
        const badges = {
            'active': '<span class="badge bg-success">活跃</span>',
            'inactive': '<span class="badge bg-secondary">非活跃</span>',
            'error': '<span class="badge bg-danger">错误</span>',
            'cloning': '<span class="badge bg-warning">克隆中</span>',
            'analyzing': '<span class="badge bg-info">分析中</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">未知</span>';
    }

    getCloneStatusBadge(status) {
        const badges = {
            'pending': '<span class="badge bg-secondary">待处理</span>',
            'cloning': '<span class="badge bg-warning text-dark">克隆中</span>',
            'completed': '<span class="badge bg-success">已完成</span>',
            'failed': '<span class="badge bg-danger">失败</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">未知</span>';
    }

    async validateUrl() {
        const url = document.getElementById('repoUrl').value.trim();
        const validateBtn = document.getElementById('validateUrlBtn');
        const resultSpan = document.getElementById('validationResult');

        if (!url) {
            this.showUrlError('请输入仓库 URL');
            return;
        }

        // 显示加载状态
        validateBtn.disabled = true;
        validateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 验证中...';
        resultSpan.innerHTML = '';

        try {
            // 临时禁用API调用，使用模拟验证
            // const response = await fetch('/api/repositories/validate-url', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json'
            //     },
            //     body: JSON.stringify({ url: url })
            // });

            // const data = await response.json();

            // if (data.success) {
            //     if (data.valid) {
            //         resultSpan.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> URL 有效且可访问</span>';
            //         this.clearUrlError();

            //         // 自动提取仓库名称
            //         if (!document.getElementById('repoName').value) {
            //             const repoName = this.extractRepoName(url);
            //             document.getElementById('repoName').value = repoName;
            //         }
            //     } else {
            //         resultSpan.innerHTML = '<span class="text-warning"><i class="fas fa-exclamation-triangle"></i> URL 格式正确但无法访问</span>';
            //     }
            // } else {
            //     this.showUrlError(data.message);
            // }

            // 临时模拟验证成功
            resultSpan.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> URL 验证功能已禁用（开发模式）</span>';
            this.clearUrlError();

            // 自动提取仓库名称
            if (!document.getElementById('repoName').value) {
                const repoName = this.extractRepoName(url);
                document.getElementById('repoName').value = repoName;
            }

        } catch (error) {
            console.error('Error validating URL:', error);
            this.showUrlError('验证 URL 时发生错误');
        } finally {
            validateBtn.disabled = false;
            validateBtn.innerHTML = '<i class="fas fa-check-circle"></i> 验证 URL';
        }
    }

    async addRepository() {
        const url = document.getElementById('repoUrl').value.trim();
        const name = document.getElementById('repoName').value.trim();
        const description = document.getElementById('repoDescription').value.trim();

        if (!url) {
            this.showUrlError('请输入仓库 URL');
            return;
        }

        const addBtn = document.getElementById('addRepoBtn');
        addBtn.disabled = true;
        addBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 添加中...';

        try {
            // 临时禁用API调用
            // const response = await fetch('/api/repositories', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json'
            //     },
            //     body: JSON.stringify({
            //         url: url,
            //         name: name || undefined,
            //         description: description || undefined
            //     })
            // });

            // const data = await response.json();

            // if (data.success) {
            //     // 关闭模态框
            //     const modal = bootstrap.Modal.getInstance(document.getElementById('addRepositoryModal'));
            //     modal.hide();

            //     // 重置表单
            //     document.getElementById('addRepositoryForm').reset();
            //     document.getElementById('validationResult').innerHTML = '';

            //     // 重新加载仓库列表和统计数据
            //     this.loadRepositories();
            //     this.loadStatistics();

            //     this.showSuccess('仓库添加成功，正在克隆中...');

            //     // 开始轮询克隆状态
            //     this.pollCloneStatus(data.repository.id);

            // } else {
            //     this.showUrlError(data.error);
            // }

            // 临时模拟成功
            // 关闭模态框 - 使用安全的关闭方法
            this.closeAddRepositoryModal();

            // 重置表单
            document.getElementById('addRepositoryForm').reset();
            document.getElementById('validationResult').innerHTML = '';

            this.showSuccess('仓库添加功能已禁用（开发模式）');

        } catch (error) {
            console.error('Error adding repository:', error);
            this.showUrlError('添加仓库时发生错误');
        } finally {
            addBtn.disabled = false;
            addBtn.innerHTML = '<i class="fas fa-plus"></i> 添加仓库';
        }
    }

    // 安全的模态框关闭方法
    closeAddRepositoryModal() {
        const modal = document.getElementById('addRepositoryModal');
        if (!modal) {
            console.warn('找不到添加仓库模态框');
            return;
        }

        // 优先使用RepositoryModalFix
        if (window.RepositoryModalFix) {
            window.RepositoryModalFix.closeModal(modal);
            return;
        }

        // 备用方法：使用Bootstrap API
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            } else {
                // 手动关闭
                modal.style.display = 'none';
                modal.classList.remove('show');
                document.body.classList.remove('modal-open');

                // 移除背景
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());
            }
        } else {
            // 手动关闭
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.classList.remove('modal-open');

            // 移除背景
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
        }
    }

    async pollCloneStatus(repositoryId, maxAttempts = 30) {
        // Use WebSocket for real-time status updates instead of polling
        if (window.realtimeUpdates) {
            // Subscribe to repository-specific updates
            window.realtimeUpdates.subscribe(`repository:${repositoryId}`);

            // Listen for repository status updates
            const handleRepositoryUpdate = (event) => {
                if (event.detail.repositoryId === repositoryId) {
                    const { status, name, error } = event.detail;

                    if (status === 'completed') {
                        this.loadRepositories();
                        this.loadStatistics();
                        this.showSuccess(`仓库 "${name}" 克隆完成！`);
                        document.removeEventListener('repositoryStatusUpdate', handleRepositoryUpdate);
                    } else if (status === 'failed') {
                        this.loadRepositories();
                        this.loadStatistics();
                        this.showError(`仓库 "${name}" 克隆失败: ${error}`);
                        document.removeEventListener('repositoryStatusUpdate', handleRepositoryUpdate);
                    }
                }
            };

            document.addEventListener('repositoryStatusUpdate', handleRepositoryUpdate);

            // Fallback timeout
            setTimeout(() => {
                document.removeEventListener('repositoryStatusUpdate', handleRepositoryUpdate);
                this.loadRepositories();
            }, 60000);
        } else {
            // Fallback to polling if WebSocket is not available
            this.pollCloneStatusFallback(repositoryId, maxAttempts);
        }
    }

    async pollCloneStatusFallback(repositoryId, maxAttempts = 30) {
        let attempts = 0;

        const poll = async () => {
            try {
                const response = await fetch(`/api/repositories/${repositoryId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) return;

                const data = await response.json();
                const repo = data.repository;

                if (repo.clone_status === 'completed' || repo.clone_status === 'failed') {
                    // 克隆完成或失败，重新加载列表
                    this.loadRepositories();
                    this.loadStatistics();

                    if (repo.clone_status === 'completed') {
                        this.showSuccess(`仓库 "${repo.name}" 克隆完成！`);
                    } else {
                        this.showError(`仓库 "${repo.name}" 克隆失败: ${repo.clone_error}`);
                    }
                    return;
                }

                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, 2000); // 2秒后再次检查
                }

            } catch (error) {
                console.error('Error polling clone status:', error);
            }
        };

        setTimeout(poll, 2000);
    }

    async showRepositoryDetail(repositoryId) {
        try {
            const response = await fetch(`/api/repositories/${repositoryId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('获取仓库详情失败');
            }

            const data = await response.json();
            const repo = data.repository;

            const detailContent = document.getElementById('repositoryDetailContent');
            detailContent.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>基本信息</h6>
                        <table class="table table-sm">
                            <tr><td><strong>名称:</strong></td><td>${this.escapeHtml(repo.name)}</td></tr>
                            <tr><td><strong>URL:</strong></td><td><a href="${this.escapeHtml(repo.url)}" target="_blank">${this.escapeHtml(repo.url)}</a></td></tr>
                            <tr><td><strong>描述:</strong></td><td>${repo.description ? this.escapeHtml(repo.description) : '无'}</td></tr>
                            <tr><td><strong>状态:</strong></td><td>${this.getStatusBadge(repo.status)}</td></tr>
                            <tr><td><strong>克隆状态:</strong></td><td>${this.getCloneStatusBadge(repo.clone_status)}</td></tr>
                            <tr><td><strong>创建时间:</strong></td><td>${this.formatDate(repo.created_at)}</td></tr>
                            <tr><td><strong>更新时间:</strong></td><td>${this.formatDate(repo.updated_at)}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>仓库信息</h6>
                        <table class="table table-sm">
                            <tr><td><strong>本地路径:</strong></td><td>${repo.local_path ? this.escapeHtml(repo.local_path) : '未克隆'}</td></tr>
                            <tr><td><strong>分支:</strong></td><td>${this.escapeHtml(repo.branch || 'main')}</td></tr>
                            <tr><td><strong>最新提交:</strong></td><td>${repo.commit_hash ? this.escapeHtml(repo.commit_hash.substring(0, 7)) : '未知'}</td></tr>
                            <tr><td><strong>文件数量:</strong></td><td>${this.formatNumber(repo.file_count || 0)}</td></tr>
                            <tr><td><strong>仓库大小:</strong></td><td>${this.formatFileSize(repo.repo_size || 0)}</td></tr>
                            <tr><td><strong>私有仓库:</strong></td><td>${repo.is_private ? '是' : '否'}</td></tr>
                        </table>
                    </div>
                </div>
                ${repo.clone_error ? `
                    <div class="alert alert-danger">
                        <h6>错误信息</h6>
                        <p class="mb-0">${this.escapeHtml(repo.clone_error)}</p>
                    </div>
                ` : ''}
            `;

            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('repositoryDetailModal'));
            modal.show();

        } catch (error) {
            console.error('Error showing repository detail:', error);
            this.showError('获取仓库详情失败');
        }
    }

    async analyzeRepository(repositoryId) {
        // 跳转到分析页面
        window.location.href = `/analysis/${repositoryId}`;
    }

    async viewAnalysisResults(repositoryId) {
        // 跳转到分析结果页面
        window.location.href = `/analysis/${repositoryId}`;
    }

    renderAnalysisResult(analysis) {
        const content = document.getElementById('analysisResultContent');

        let html = '<div class="row">';

        // 基本信息
        html += `
            <div class="col-md-4">
                <h6>基本信息</h6>
                <table class="table table-sm">
                    <tr><td><strong>文件总数:</strong></td><td>${this.formatNumber(analysis.structure?.total_files || 0)}</td></tr>
                    <tr><td><strong>目录总数:</strong></td><td>${this.formatNumber(analysis.structure?.total_directories || 0)}</td></tr>
                    <tr><td><strong>估计复杂度:</strong></td><td><span class="badge bg-${this.getComplexityBadgeClass(analysis.metadata?.estimated_complexity)}">${this.escapeHtml(analysis.metadata?.estimated_complexity || 'low')}</span></td></tr>
                    <tr><td><strong>维护分数:</strong></td><td>${Math.round(analysis.metadata?.maintenance_score || 0)}%</td></tr>
                </table>
            </div>
        `;

        // 编程语言
        if (analysis.languages && analysis.languages.length > 0) {
            html += `
                <div class="col-md-4">
                    <h6>编程语言</h6>
                    <div class="list-group list-group-flush">
            `;

            analysis.languages.slice(0, 5).forEach(lang => {
                html += `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <span>${this.escapeHtml(lang.name)}</span>
                        <span class="badge bg-primary rounded-pill">${lang.file_count}</span>
                    </div>
                `;
            });

            html += '</div></div>';
        }

        // 配置
        if (analysis.configuration) {
            html += `
                <div class="col-md-4">
                    <h6>技术栈</h6>
                    <div class="mb-2">
                        <strong>框架:</strong> ${this.formatTags(analysis.configuration.frameworks)}
                    </div>
                    <div class="mb-2">
                        <strong>数据库:</strong> ${this.formatTags(analysis.configuration.databases)}
                    </div>
                    <div class="mb-2">
                        <strong>测试:</strong> ${this.formatTags(analysis.configuration.testing)}
                    </div>
                    <div class="mb-2">
                        <strong>部署:</strong> ${this.formatTags(analysis.configuration.deployment)}
                    </div>
                </div>
            `;
        }

        html += '</div>';

        // 文档信息
        if (analysis.documentation) {
            html += `
                <div class="mt-4">
                    <h6>文档信息</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr><td><strong>README:</strong></td><td>${analysis.documentation.readme ? '✓ 存在' : '✗ 不存在'}</td></tr>
                                <tr><td><strong>API 文档:</strong></td><td>${analysis.documentation.api_docs.length} 个文件</td></tr>
                                <tr><td><strong>指南:</strong></td><td>${analysis.documentation.guides.length} 个文件</td></tr>
                                <tr><td><strong>示例:</strong></td><td>${analysis.documentation.examples.length} 个文件</td></tr>
                                <tr><td><strong>总文档文件:</strong></td><td>${analysis.documentation.total_doc_files} 个</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6>推荐文档</h6>
                            <ul class="list-unstyled">
            `;

            if (analysis.metadata?.recommended_documentation) {
                analysis.metadata.recommended_documentation.forEach(doc => {
                    html += `<li><i class="fas fa-plus-circle text-success"></i> ${this.escapeHtml(doc)}</li>`;
                });
            }

            html += '</ul></div></div>';
        }

        // 依赖信息
        if (analysis.dependencies && analysis.dependencies.package_managers.length > 0) {
            html += `
                <div class="mt-4">
                    <h6>依赖管理</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <strong>包管理器:</strong> ${this.formatTags(analysis.dependencies.package_managers)}
                        </div>
                        <div class="col-md-6">
                            <strong>依赖数量:</strong> ${Object.keys(analysis.dependencies.dependencies).length}
                        </div>
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
    }

    async syncRepository(repositoryId) {
        if (!confirm('确定要同步此仓库吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/repositories/${repositoryId}/sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('仓库同步任务已启动');
                this.loadRepositories();
                this.loadStatistics();
            } else {
                this.showError(data.error);
            }

        } catch (error) {
            console.error('Error syncing repository:', error);
            this.showError('同步仓库失败');
        }
    }

    // 删除仓库功能已禁用
    /*
    async deleteRepository(repositoryId) {
        if (!confirm('确定要删除此仓库吗？此操作不可撤销。')) {
            return;
        }

        try {
            const response = await fetch(`/api/repositories/${repositoryId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('仓库删除成功');
                this.loadRepositories();
                this.loadStatistics();
            } else {
                this.showError(data.error);
            }

        } catch (error) {
            console.error('Error deleting repository:', error);
            this.showError('删除仓库失败');
        }
    }
    */

    filterRepositories() {
        const searchTerm = document.getElementById('searchRepo').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;

        const filtered = this.repositories.filter(repo => {
            const matchesSearch = !searchTerm ||
                repo.name.toLowerCase().includes(searchTerm) ||
                repo.url.toLowerCase().includes(searchTerm) ||
                (repo.description && repo.description.toLowerCase().includes(searchTerm));

            const matchesStatus = !statusFilter || repo.status === statusFilter;

            return matchesSearch && matchesStatus;
        });

        // 重新渲染过滤后的仓库列表
        const tbody = document.getElementById('repositoriesTable');
        tbody.innerHTML = '';

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">没有找到匹配的仓库</td></tr>';
        } else {
            filtered.forEach(repo => {
                const row = this.createRepositoryRow(repo);
                tbody.appendChild(row);
            });
        }
    }

    // 工具方法
    extractRepoName(url) {
        if (url.endsWith('.git')) {
            url = url.slice(0, -4);
        }
        return url.split('/').pop() || 'repository';
    }

    truncateUrl(url, maxLength = 40) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength - 3) + '...';
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return '未知';
        return new Date(dateString).toLocaleString('zh-CN');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTags(tags) {
        if (!tags || tags.length === 0) return '<span class="text-muted">无</span>';
        return tags.map(tag => `<span class="badge bg-secondary me-1">${this.escapeHtml(tag)}</span>`).join('');
    }

    getComplexityBadgeClass(complexity) {
        const classes = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        };
        return classes[complexity] || 'secondary';
    }

    showUrlError(message) {
        const urlInput = document.getElementById('repoUrl');
        urlInput.classList.add('is-invalid');
        document.getElementById('urlError').textContent = message;
    }

    clearUrlError() {
        const urlInput = document.getElementById('repoUrl');
        urlInput.classList.remove('is-invalid');
        document.getElementById('urlError').textContent = '';
    }

    clearValidation() {
        document.getElementById('validationResult').innerHTML = '';
        this.clearUrlError();
    }

    showSuccess(message) {
        // 使用 Toast 或其他方式显示成功消息
        alert(message); // 简单实现，后续可以改进
    }

    showError(message) {
        // 使用 Toast 或其他方式显示错误消息
        alert(message); // 简单实现，后续可以改进
    }

    // ==================== 仓库删除功能已禁用 ====================

    /*
    async showDeleteConfirmation(repositoryId) {
        try {
            // 获取删除确认信息
            const response = await fetch(`/api/repositories/${repositoryId}/confirm-delete`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('获取删除确认信息失败');
            }

            const data = await response.json();

            if (data.success) {
                this.renderDeleteConfirmation(data);
                // 显示删除确认模态框
                const modal = new bootstrap.Modal(document.getElementById('deleteRepositoryModal'));
                modal.show();
            } else {
                this.showError(data.error || '获取删除确认信息失败');
            }

        } catch (error) {
            console.error('Error getting delete confirmation:', error);
            this.showError('获取删除确认信息失败');
        }
    }
    */

    renderDeleteConfirmation(data) {
        const repository = data.repository;
        const associatedData = data.associated_data;
        const fileCleanup = data.file_cleanup;

        // 渲染仓库基本信息
        const repoInfoHtml = `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fas fa-folder me-2"></i>${this.escapeHtml(repository.name)}
                    </h6>
                    <p class="card-text">
                        <strong>URL:</strong> ${this.escapeHtml(repository.url)}<br>
                        <strong>描述:</strong> ${this.escapeHtml(repository.description || '无描述')}<br>
                        <strong>状态:</strong> ${this.getStatusBadge(repository.status)}<br>
                        <strong>创建时间:</strong> ${this.formatDate(repository.created_at)}
                    </p>
                </div>
            </div>
        `;

        document.getElementById('deleteRepositoryInfo').innerHTML = repoInfoHtml;

        // 设置确认输入的仓库名称
        document.getElementById('confirmRepoName').textContent = repository.name;
        document.getElementById('deleteConfirmInput').value = '';
        document.getElementById('confirmDeleteBtn').disabled = true;

        // 显示删除详情
        const detailsContainer = document.getElementById('deleteDetails');
        const hasAssociatedData = associatedData.documents_count > 0 ||
                                  associatedData.tasks_count > 0 ||
                                  (fileCleanup && fileCleanup.exists && fileCleanup.file_count > 0);

        if (hasAssociatedData) {
            detailsContainer.style.display = 'block';

            // 显示文档数量
            const documentsInfo = document.getElementById('documentsInfo');
            if (associatedData.documents_count > 0) {
                documentsInfo.style.display = 'block';
                document.getElementById('documentsCount').textContent =
                    `${associatedData.documents_count} 个文档`;
            } else {
                documentsInfo.style.display = 'none';
            }

            // 显示任务数量
            const tasksInfo = document.getElementById('tasksInfo');
            if (associatedData.tasks_count > 0) {
                tasksInfo.style.display = 'block';
                document.getElementById('tasksCount').textContent =
                    `${associatedData.tasks_count} 个任务`;
            } else {
                tasksInfo.style.display = 'none';
            }

            // 显示文件数量
            const filesInfo = document.getElementById('filesInfo');
            if (fileCleanup && fileCleanup.exists && fileCleanup.file_count > 0) {
                filesInfo.style.display = 'block';
                document.getElementById('filesCount').textContent =
                    `${fileCleanup.file_count} 个本地文件 (${fileCleanup.size_human})`;
            } else {
                filesInfo.style.display = 'none';
            }
        } else {
            detailsContainer.style.display = 'none';
        }

        // 显示警告消息
        if (data.warning_message) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-danger mt-3';
            warningDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${data.warning_message}`;
            document.getElementById('deleteRepositoryInfo').appendChild(warningDiv);
        }

        // 绑定确认输入事件
        const confirmInput = document.getElementById('deleteConfirmInput');
        const confirmBtn = document.getElementById('confirmDeleteBtn');

        confirmInput.oninput = () => {
            const inputValue = confirmInput.value.trim();
            confirmBtn.disabled = inputValue !== repository.name;
        };

        // 绑定确认删除按钮事件
        confirmBtn.onclick = () => {
            this.deleteRepository(repositoryId);
        };
    }

    // 删除仓库方法已禁用
    /*
    async deleteRepository(repositoryId) {
        try {
            // 隐藏确认模态框，显示进度模态框
            const confirmModal = bootstrap.Modal.getInstance(document.getElementById('deleteRepositoryModal'));
            confirmModal.hide();

            const progressModal = new bootstrap.Modal(document.getElementById('deleteProgressModal'));
            progressModal.show();

            // 发送删除请求
            const response = await fetch(`/api/repositories/${repositoryId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            // 隐藏进度模态框
            progressModal.hide();

            if (!response.ok) {
                throw new Error('删除仓库失败');
            }

            const data = await response.json();

            if (data.success) {
                // 显示成功提示
                this.showDeleteSuccessToast(data.message || '仓库删除成功');

                // 从列表中移除已删除的仓库
                this.removeRepositoryFromList(repositoryId);

                // 重新加载仓库列表和统计数据
                setTimeout(() => {
                    this.loadRepositories();
                    this.loadStatistics();
                }, 1000);

            } else {
                this.showDeleteErrorToast(data.error || '删除仓库失败');
            }

        } catch (error) {
            console.error('Error deleting repository:', error);

            // 隐藏进度模态框
            const progressModal = bootstrap.Modal.getInstance(document.getElementById('deleteProgressModal'));
            if (progressModal) {
                progressModal.hide();
            }

            this.showDeleteErrorToast('删除仓库失败，请稍后重试');
        }
    }
    */

    // 删除仓库相关方法已禁用
    /*
    removeRepositoryFromList(repositoryId) {
        // 从仓库列表中移除已删除的仓库
        const repoRow = document.querySelector(`tr[data-repo-id="${repositoryId}"]`);
        if (repoRow) {
            repoRow.remove();
        }

        // 检查是否还有仓库，如果没有则显示空状态
        const tbody = document.getElementById('repositoriesTable');
        if (tbody && tbody.children.length === 0) {
            document.getElementById('emptyState').style.display = 'block';
        }
    }
    */

    showDeleteSuccessToast(message) {
        const toastElement = document.getElementById('deleteSuccessToast');
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement);
            toastElement.querySelector('.toast-body').textContent = message;
            toast.show();
        } else {
            this.showSuccess(message);
        }
    }

    showDeleteErrorToast(message) {
        const toastElement = document.getElementById('deleteErrorToast');
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement);
            document.getElementById('deleteErrorMessage').textContent = message;
            toast.show();
        } else {
            this.showError(message);
        }
    }

    getStatusBadge(status) {
        const statusConfig = {
            'active': { class: 'bg-success', icon: 'fas fa-check-circle', text: '活跃' },
            'inactive': { class: 'bg-secondary', icon: 'fas fa-pause-circle', text: '非活跃' },
            'cloning': { class: 'bg-info', icon: 'fas fa-download', text: '克隆中' },
            'analyzing': { class: 'bg-warning', icon: 'fas fa-search', text: '分析中' },
            'completed': { class: 'bg-success', icon: 'fas fa-check-double', text: '已完成' },
            'error': { class: 'bg-danger', icon: 'fas fa-exclamation-circle', text: '错误' },
            'failed': { class: 'bg-danger', icon: 'fas fa-times-circle', text: '失败' }
        };

        const config = statusConfig[status] || statusConfig['active'];
        return `<span class="badge ${config.class}"><i class="${config.icon} me-1"></i>${config.text}</span>`;
    }

    formatDate(dateString) {
        if (!dateString) return '无';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    }
}

// 初始化仓库管理器
let repositoryManager;
document.addEventListener('DOMContentLoaded', () => {
    repositoryManager = new RepositoryManager();
});
