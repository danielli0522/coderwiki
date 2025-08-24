/**
 * Analysis Management JavaScript
 * Enhanced version with better error handling and navigation support
 */

class AnalysisManager {
    constructor(options = {}) {
        this.repositoryId = options.repositoryId || null;
        this.repositoryName = options.repositoryName || '';
        this.currentAnalysis = null;
        this.analysisResults = null;
        this.analysisHistory = [];
        this.pollingInterval = null;
        this.isInitialized = false;
        this.apiClient = new ApiClient('/api');
        this.userRepositories = []; // 存储用户可访问的仓库列表
        this.init();
    }

    init() {
        console.log('Initializing AnalysisManager...');
        this.bindEvents();
        this.loadRepositories();
        this.loadAnalysisStatistics();
        this.isInitialized = true;
        console.log('AnalysisManager initialized successfully');
    }

    bindEvents() {
        // 分析控制事件
        this.bindElement('startAnalysisBtn', 'click', () => this.startAnalysis());
        this.bindElement('startFirstAnalysisBtn', 'click', () => this.startAnalysis());
        this.bindElement('stopAnalysisBtn', 'click', () => this.stopAnalysis());
        this.bindElement('cancelAnalysisBtn', 'click', () => this.cancelAnalysis());
        this.bindElement('modalStartAnalysisBtn', 'click', () => this.startAnalysisFromModal());

        // 其他操作事件
        this.bindElement('refreshAnalysisBtn', 'click', () => this.refreshAnalysis());
        this.bindElement('clearCacheBtn', 'click', () => this.clearCache());
        this.bindElement('newAnalysisBtn', 'click', () => this.showNewAnalysisModal());

        // 分析类型选择事件
        document.querySelectorAll('input[type="checkbox"][id$="Analysis"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateAnalysisTypes());
        });

        // 仓库选择事件
        this.bindElement('analysisRepoSelect', 'change', (e) => {
            const selectedRepoId = e.target.value;
            if (selectedRepoId) {
                this.selectRepository(selectedRepoId);
            } else {
                this.clearRepositorySelection();
            }
        });

        // 搜索和过滤事件
        this.bindElement('analysisSearch', 'input', (e) => this.filterAnalysisHistory(e.target.value));
        this.bindElement('analysisStatusFilter', 'change', (e) => this.filterAnalysisHistory('', e.target.value));
    }

    bindElement(selector, event, handler) {
        const element = document.getElementById(selector);
        if (element) {
            element.addEventListener(event, handler);
        } else {
            console.warn(`Element with id '${selector}' not found`);
        }
    }

    async loadRepositories() {
        try {
            console.log('Loading user repositories...');
            const data = await this.apiClient.get('/repositories');

            if (data.success && data.repositories) {
                this.userRepositories = data.repositories;
                this.populateRepositorySelect(data.repositories);
                console.log(`Loaded ${data.repositories.length} repositories`);
            } else {
                console.error('Failed to load repositories:', data.message);
                this.showError('加载仓库列表失败: ' + (data.message || '未知错误'));
            }

        } catch (error) {
            console.error('Error loading repositories:', error);
            this.showError('加载仓库列表失败: ' + error.message);
        }
    }

    populateRepositorySelect(repositories) {
        const select = document.getElementById('analysisRepoSelect');
        const modalSelect = document.getElementById('analysisRepo');

        if (select) {
            select.innerHTML = '<option value="">请选择仓库</option>';
            repositories.forEach(repo => {
                const option = document.createElement('option');
                option.value = repo.id;
                option.textContent = repo.name;
                // 添加仓库状态信息
                if (repo.clone_status === 'completed' && repo.local_path) {
                    option.textContent += ' (已克隆)';
                } else if (repo.clone_status === 'cloning') {
                    option.textContent += ' (克隆中)';
                } else if (repo.clone_status === 'failed') {
                    option.textContent += ' (克隆失败)';
                }
                select.appendChild(option);
            });
        }

        if (modalSelect) {
            modalSelect.innerHTML = '<option value="">请选择仓库</option>';
            repositories.forEach(repo => {
                const option = document.createElement('option');
                option.value = repo.id;
                option.textContent = repo.name;
                // 添加仓库状态信息
                if (repo.clone_status === 'completed' && repo.local_path) {
                    option.textContent += ' (已克隆)';
                } else if (repo.clone_status === 'cloning') {
                    option.textContent += ' (克隆中)';
                } else if (repo.clone_status === 'failed') {
                    option.textContent += ' (克隆失败)';
                }
                modalSelect.appendChild(option);
            });
        }
    }

    selectRepository(repositoryId) {
        // 验证仓库是否存在且可访问
        const repository = this.userRepositories.find(repo => repo.id == repositoryId);
        if (!repository) {
            this.showError('选择的仓库不存在或您没有访问权限');
            return;
        }

        // 检查仓库是否已克隆
        if (repository.clone_status !== 'completed' || !repository.local_path) {
            this.showError(`仓库 "${repository.name}" 尚未克隆完成，无法进行分析。请等待克隆完成后再试。`);
            return;
        }

        this.repositoryId = repositoryId;
        this.repositoryName = repository.name;

        console.log(`Selected repository: ${repository.name} (ID: ${repositoryId})`);

        // 加载分析结果和历史
        this.loadAnalysisResults();
        this.loadAnalysisHistory();

        // 更新UI状态
        this.updateRepositorySelectionUI();
    }

    clearRepositorySelection() {
        this.repositoryId = null;
        this.repositoryName = '';
        this.analysisResults = null;
        this.showEmptyState();
        this.updateRepositorySelectionUI();
    }

    updateRepositorySelectionUI() {
        // 更新仓库选择相关的UI元素
        const repoInfoElement = document.getElementById('selectedRepoInfo');
        if (repoInfoElement) {
            if (this.repositoryName) {
                repoInfoElement.textContent = `当前仓库: ${this.repositoryName}`;
                repoInfoElement.style.display = 'block';
            } else {
                repoInfoElement.style.display = 'none';
            }
        }
    }

    async loadAnalysisStatistics() {
        try {
            const data = await this.apiClient.get('/analysis/statistics');

            if (data.success && data.statistics) {
                this.updateStatistics(data.statistics);
            }

        } catch (error) {
            console.error('Error loading analysis statistics:', error);
        }
    }

    updateStatistics(statistics) {
        const elements = {
            'totalAnalyses': statistics.total_analyses || 0,
            'successAnalyses': statistics.completed_analyses || 0,
            'runningAnalyses': statistics.pending_analyses || 0,
            'failedAnalyses': statistics.failed_analyses || 0
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    async loadAnalysisResults() {
        if (!this.repositoryId) {
            this.showEmptyState();
            return;
        }

        try {
            console.log(`Loading analysis results for repository ${this.repositoryId}...`);
            document.getElementById('analysisLoading').style.display = 'block';

            const data = await this.apiClient.get(`/analysis/results/${this.repositoryId}`);

            if (data.success) {
                this.analysisResults = data.results;
                this.renderAnalysisResults();
                this.updateAnalysisStatus();
                console.log('Analysis results loaded successfully');
            } else {
                console.warn('No analysis results found:', data.message);
                this.showEmptyState();
                // 显示友好的提示信息
                if (data.message && data.message.includes('No analyses found')) {
                    this.showInfo('该仓库尚未进行过代码分析，请点击"开始分析"按钮开始第一次分析。');
                }
            }

        } catch (error) {
            console.error('Error loading analysis results:', error);

            // 根据错误类型显示不同的消息
            if (error.message && error.message.includes('404')) {
                this.showError('仓库不存在或您没有访问权限');
            } else if (error.message && error.message.includes('401')) {
                this.showError('请先登录后再访问分析功能');
            } else if (error.message && error.message.includes('403')) {
                this.showError('您没有权限访问此仓库的分析结果');
            } else {
                this.showError('加载分析结果失败: ' + error.message);
            }

            this.showEmptyState();
        } finally {
            document.getElementById('analysisLoading').style.display = 'none';
        }
    }

    async loadAnalysisHistory() {
        if (!this.repositoryId) return;

        try {
            const data = await this.apiClient.get(`/analysis/history/${this.repositoryId}`);

            if (data.success) {
                this.analysisHistory = data.history;
                this.renderAnalysisHistory();
            }

        } catch (error) {
            console.error('Error loading analysis history:', error);
        }
    }

    renderAnalysisResults() {
        if (!this.analysisResults || Object.keys(this.analysisResults).length === 0) {
            this.showEmptyState();
            return;
        }

        document.getElementById('analysisResults').style.display = 'block';
        document.getElementById('analysisEmpty').style.display = 'none';

        // 渲染各个分析结果
        this.renderStructureResults();
        this.renderDependenciesResults();
        this.renderComplexityResults();
        this.renderTechStackResults();
        this.renderSecurityResults();
        this.renderPatternsResults();
        this.renderQualityResults();
    }

    renderStructureResults() {
        const structure = this.analysisResults.structure;
        if (!structure) return;

        const statsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${this.formatNumber(structure.total_files)}</div>
                        <div class="metric-label">总文件数</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${this.formatNumber(structure.total_directories)}</div>
                        <div class="metric-label">总目录数</div>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6>文件类型分布</h6>
                    <div class="progress" style="height: 20px;">
                        ${this.renderFileTypeProgress(structure.file_types)}
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('structureStats');
        if (container) {
            container.innerHTML = statsHtml;
        }
    }

    renderDependenciesResults() {
        const dependencies = this.analysisResults.dependencies;
        if (!dependencies) return;

        // 渲染包管理器
        const packageManagersHtml = dependencies.package_managers?.map(pm =>
            `<span class="badge bg-primary me-1">${this.escapeHtml(pm)}</span>`
        ).join('') || '<span class="text-muted">无</span>';

        const container = document.getElementById('packageManagers');
        if (container) {
            container.innerHTML = packageManagersHtml;
        }
    }

    renderComplexityResults() {
        const complexity = this.analysisResults.complexity;
        if (!complexity) return;

        const metricsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${complexity.average_complexity?.toFixed(1) || '0'}</div>
                        <div class="metric-label">平均复杂度</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${complexity.max_complexity || '0'}</div>
                        <div class="metric-label">最大复杂度</div>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('complexityMetrics');
        if (container) {
            container.innerHTML = metricsHtml;
        }
    }

    renderTechStackResults() {
        const techStack = this.analysisResults.tech_stack;
        if (!techStack) return;

        // 渲染编程语言
        const languagesHtml = techStack.languages?.map(lang => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>${this.escapeHtml(lang.name)}</span>
                <div>
                    <span class="badge bg-primary me-1">${lang.file_count} 文件</span>
                    <span class="badge bg-secondary">${lang.percentage}%</span>
                </div>
            </div>
        `).join('') || '<p class="text-muted">无</p>';

        const container = document.getElementById('programmingLanguages');
        if (container) {
            container.innerHTML = languagesHtml;
        }
    }

    renderSecurityResults() {
        const security = this.analysisResults.security;
        if (!security) return;

        const securityHtml = security.issues?.map(issue => `
            <div class="security-issue ${issue.severity}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6>${this.escapeHtml(issue.title)}</h6>
                        <p class="mb-1">${this.escapeHtml(issue.description)}</p>
                        <small class="text-muted">文件: ${this.escapeHtml(issue.file)}</small>
                    </div>
                    <div>
                        <span class="badge bg-${this.getSeverityBadgeClass(issue.severity)}">${issue.severity}</span>
                    </div>
                </div>
            </div>
        `).join('') || '<p class="text-muted">未发现安全问题</p>';

        const container = document.getElementById('securityIssues');
        if (container) {
            container.innerHTML = securityHtml;
        }
    }

    renderPatternsResults() {
        const patterns = this.analysisResults.patterns;
        if (!patterns) return;

        const patternsHtml = patterns.design_patterns?.map(pattern => `
            <div class="pattern-card">
                <h6>${this.escapeHtml(pattern.name)}</h6>
                <p class="mb-1">${this.escapeHtml(pattern.description)}</p>
                <small class="text-muted">使用次数: ${pattern.count}</small>
            </div>
        `).join('') || '<p class="text-muted">未识别到设计模式</p>';

        const container = document.getElementById('designPatterns');
        if (container) {
            container.innerHTML = patternsHtml;
        }
    }

    renderQualityResults() {
        const quality = this.analysisResults.quality;
        if (!quality) return;

        const metricsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${quality.maintainability_index?.toFixed(1) || '0'}</div>
                        <div class="metric-label">可维护性指数</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${quality.technical_debt_ratio?.toFixed(1) || '0'}%</div>
                        <div class="metric-label">技术债务比率</div>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('qualityMetrics');
        if (container) {
            container.innerHTML = metricsHtml;
        }
    }

    renderAnalysisHistory() {
        const historyHtml = this.analysisHistory.map(item => `
            <div class="history-item border-bottom pb-2 mb-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>分析 #${item.id}</strong>
                        <span class="badge bg-${this.getStatusBadgeClass(item.status)} ms-2">${this.getStatusText(item.status)}</span>
                    </div>
                    <div class="timestamp text-muted">${this.formatDate(item.created_at)}</div>
                </div>
                <div class="analysis-types mt-1">
                    <span class="badge bg-outline-secondary me-1">${item.analysis_type}</span>
                </div>
            </div>
        `).join('') || '<p class="text-muted">暂无分析历史</p>';

        const container = document.getElementById('analysisHistory');
        if (container) {
            container.innerHTML = historyHtml;
        }
    }

    // 认证检查辅助方法
    async checkAuthentication() {
        try {
            const authResponse = await fetch('/api/auth/status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!authResponse.ok || authResponse.status === 302) {
                this.showError('请先登录后再开始分析');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
                return false;
            }

            const authData = await authResponse.json();
            if (!authData.logged_in) {
                this.showError('请先登录后再开始分析');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
                return false;
            }

            return true;
        } catch (error) {
            console.error('认证检查失败:', error);
            this.showError('认证检查失败，请重新登录');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return false;
        }
    }

    async startAnalysis() {
        // 检查用户是否已登录
        if (!(await this.checkAuthentication())) {
            return;
        }

        if (!this.repositoryId) {
            this.showError('请先选择一个仓库');
            return;
        }

        // 验证仓库状态
        const repository = this.userRepositories.find(repo => repo.id == this.repositoryId);
        if (!repository) {
            this.showError('选择的仓库不存在或您没有访问权限');
            return;
        }

        if (repository.clone_status !== 'completed' || !repository.local_path) {
            this.showError(`仓库 "${repository.name}" 尚未克隆完成，无法进行分析。请等待克隆完成后再试。`);
            return;
        }

        const analysisTypes = this.getSelectedAnalysisTypes();
        const config = this.getAnalysisConfig();

        if (analysisTypes.length === 0) {
            this.showError('请至少选择一种分析类型');
            return;
        }

        try {
            console.log(`Starting analysis for repository ${this.repositoryId} with types: ${analysisTypes.join(', ')}`);

            const data = await this.apiClient.post('/analysis/start', {
                repository_id: parseInt(this.repositoryId), // 确保是整数
                analysis_types: analysisTypes,
                config: config
            });

            if (data.success) {
                this.showProgressModal();
                this.currentAnalysis = data.analysis_ids[0];
                this.startPolling();
                this.updateAnalysisButtons(true);
                this.showSuccess(`分析已开始，正在分析 ${analysisTypes.length} 个方面...`);
                console.log('Analysis started successfully:', data);
            } else {
                console.error('Failed to start analysis:', data.message);
                this.showError(data.message || '开始分析失败');
            }

        } catch (error) {
            console.error('Error starting analysis:', error);

            // 根据错误类型显示不同的消息
            if (error.message && error.message.includes('Authentication required')) {
                this.showError('请先登录后再开始分析');
                // 延迟重定向到登录页面
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else if (error.message && error.message.includes('400')) {
                this.showError('请求参数错误，请检查分析配置');
            } else if (error.message && error.message.includes('401')) {
                this.showError('请先登录后再开始分析');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else if (error.message && error.message.includes('403')) {
                this.showError('您没有权限对此仓库进行分析');
            } else if (error.message && error.message.includes('404')) {
                this.showError('仓库不存在或已被删除');
            } else {
                this.showError('开始分析失败: ' + error.message);
            }
        }
    }

    async startAnalysisFromModal() {
        // 检查用户是否已登录
        if (!(await this.checkAuthentication())) {
            return;
        }

        const modalRepoSelect = document.getElementById('analysisRepo');
        const repositoryId = modalRepoSelect.value;

        if (!repositoryId) {
            this.showError('请选择仓库');
            return;
        }

        this.repositoryId = repositoryId;

        // 更新主界面的仓库选择
        const mainRepoSelect = document.getElementById('analysisRepoSelect');
        if (mainRepoSelect) {
            mainRepoSelect.value = repositoryId;
        }

        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('newAnalysisModal'));
        if (modal) {
            modal.hide();
        }

        // 开始分析
        await this.startAnalysis();
    }

    async stopAnalysis() {
        if (!this.currentAnalysis) return;

        try {
            const data = await this.apiClient.post(`/analysis/cancel/${this.currentAnalysis}`);

            if (data.success) {
                this.stopPolling();
                this.updateAnalysisButtons(false);
                this.hideProgressModal();
                this.showSuccess('分析已停止');
            } else {
                this.showError(data.message || '停止分析失败');
            }

        } catch (error) {
            console.error('Error stopping analysis:', error);
            this.showError('停止分析失败');
        }
    }

    cancelAnalysis() {
        this.stopAnalysis();
    }

    startPolling() {
        this.pollingInterval = setInterval(() => {
            this.pollAnalysisStatus();
        }, 2000);
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    async pollAnalysisStatus() {
        if (!this.currentAnalysis) return;

        try {
            const data = await this.apiClient.get(`/analysis/status/${this.currentAnalysis}`);

            if (data.success) {
                this.updateProgress(data);

                if (data.status === 'completed' || data.status === 'failed') {
                    this.stopPolling();
                    this.updateAnalysisButtons(false);
                    this.hideProgressModal();

                    if (data.status === 'completed') {
                        this.showSuccess('分析完成');
                        this.loadAnalysisResults();
                        this.loadAnalysisHistory();
                        this.loadAnalysisStatistics();
                    } else {
                        this.showError('分析失败: ' + (data.error_message || '未知错误'));
                    }
                }
            }

        } catch (error) {
            console.error('Error polling analysis status:', error);
        }
    }

    updateProgress(data) {
        const progressBar = document.getElementById('analysisProgressBar');
        const progressText = document.getElementById('analysisProgressText');

        if (progressBar) {
            progressBar.style.width = `${data.progress || 0}%`;
        }

        if (progressText) {
            progressText.textContent = data.message || '分析中...';
        }
    }

    showProgressModal() {
        const modal = new bootstrap.Modal(document.getElementById('analysisProgressModal'));
        modal.show();
    }

    hideProgressModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('analysisProgressModal'));
        if (modal) {
            modal.hide();
        }
    }

    showNewAnalysisModal() {
        console.log('显示新建分析模态框');

        // 使用全局模态框管理器
        if (window.modalManager) {
            window.modalManager.showModal('newAnalysisModal', {
                beforeShow: (modalElement) => {
                    // 重新加载仓库列表
                    this.loadRepositories();
                },
                onShown: () => {
                    // 绑定开始分析按钮事件
                    const startBtn = document.getElementById('modalStartAnalysisBtn');
                    if (startBtn) {
                        startBtn.onclick = () => this.startAnalysisFromModal();
                    }
                }
            });
        } else {
            // 降级处理：使用原始方法
            const modalElement = document.getElementById('newAnalysisModal');
            if (!modalElement) {
                console.error('新建分析模态框元素不存在');
                return;
            }

            // 创建并显示模态框
            const modal = new bootstrap.Modal(modalElement);
            modal.show();

            // 重新加载仓库列表
            this.loadRepositories();

            // 确保模态框可以正常交互
            setTimeout(() => {
                // 强制启用所有输入框
                const inputs = modalElement.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    input.disabled = false;
                    input.readOnly = false;
                    input.style.pointerEvents = 'auto';
                    input.style.opacity = '1';
                    input.style.visibility = 'visible';
                });

                // 绑定开始分析按钮事件
                const startBtn = document.getElementById('modalStartAnalysisBtn');
                if (startBtn) {
                    startBtn.onclick = () => this.startAnalysisFromModal();
                }
            }, 300);
        }
    }

    updateAnalysisButtons(isAnalyzing) {
        const startBtn = document.getElementById('startAnalysisBtn');
        const stopBtn = document.getElementById('stopAnalysisBtn');

        if (startBtn) {
            startBtn.style.display = isAnalyzing ? 'none' : 'inline-block';
        }

        if (stopBtn) {
            stopBtn.style.display = isAnalyzing ? 'inline-block' : 'none';
        }
    }

    updateAnalysisStatus() {
        if (!this.analysisResults) return;

        const status = this.analysisResults.status || 'unknown';
        const completedAnalyses = this.analysisResults.completed_analyses || 0;
        const analysisTypes = this.analysisResults.analysis_types || [];
        const lastUpdated = this.analysisResults.last_updated;

        const statusElement = document.getElementById('analysisStatus');
        if (statusElement) {
            statusElement.textContent = this.getStatusText(status);
        }

        const completedElement = document.getElementById('completedAnalyses');
        if (completedElement) {
            completedElement.textContent = completedAnalyses;
        }

        const typesElement = document.getElementById('analysisTypesCount');
        if (typesElement) {
            typesElement.textContent = analysisTypes.length;
        }

        const updatedElement = document.getElementById('lastUpdated');
        if (updatedElement) {
            updatedElement.textContent = this.formatDate(lastUpdated);
        }
    }

    async refreshAnalysis() {
        await this.loadAnalysisResults();
        await this.loadAnalysisHistory();
        await this.loadAnalysisStatistics();
        this.showSuccess('分析结果已刷新');
    }

    async clearCache() {
        if (!this.repositoryId) {
            this.showError('请先选择一个仓库');
            return;
        }

        if (!confirm('确定要清除分析缓存吗？这将删除所有分析结果。')) {
            return;
        }

        try {
            const data = await this.apiClient.post(`/analysis/cache/clear/${this.repositoryId}`);

            if (data.success) {
                this.showSuccess('缓存已清除');
                this.analysisResults = null;
                this.showEmptyState();
                this.loadAnalysisHistory();
            } else {
                this.showError(data.message || '清除缓存失败');
            }

        } catch (error) {
            console.error('Error clearing cache:', error);
            this.showError('清除缓存失败');
        }
    }

    getSelectedAnalysisTypes() {
        const types = [];
        document.querySelectorAll('input[type="checkbox"][id$="Analysis"]:checked').forEach(checkbox => {
            const type = checkbox.id.replace('Analysis', '');
            types.push(type);
        });
        return types;
    }

    getAnalysisConfig() {
        return {
            max_file_size: 10 * 1024 * 1024, // 10MB
            timeout: 300, // 5 minutes
            enable_cache: true,
            parallel_processing: true
        };
    }

    updateAnalysisTypes() {
        // 更新分析类型选择的UI反馈
        document.querySelectorAll('input[type="checkbox"][id$="Analysis"]').forEach(checkbox => {
            const label = checkbox.nextElementSibling;
            if (checkbox.checked) {
                label.style.fontWeight = '600';
                label.style.color = '#007bff';
            } else {
                label.style.fontWeight = 'normal';
                label.style.color = 'inherit';
            }
        });
    }

    filterAnalysisHistory(searchTerm = '', statusFilter = '') {
        // 实现分析历史过滤功能
        console.log('Filtering analysis history:', { searchTerm, statusFilter });
    }

    showEmptyState() {
        const resultsContainer = document.getElementById('analysisResults');
        const emptyContainer = document.getElementById('analysisEmpty');

        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }

        if (emptyContainer) {
            emptyContainer.style.display = 'block';
        }
    }

    // 渲染辅助方法
    renderFileTypeProgress(fileTypes) {
        if (!fileTypes) return '';

        const total = Object.values(fileTypes).reduce((sum, count) => sum + count, 0);
        return Object.entries(fileTypes).map(([type, count]) => {
            const percentage = (count / total * 100).toFixed(1);
            return `<div class="progress-bar" style="width: ${percentage}%" title="${type}: ${count} files (${percentage}%)">${type}</div>`;
        }).join('');
    }

    // 工具方法
    formatNumber(num) {
        return new Intl.NumberFormat().format(num || 0);
    }

    formatDate(dateString) {
        if (!dateString) return '未知';
        return new Date(dateString).toLocaleString('zh-CN');
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getStatusText(status) {
        const statusMap = {
            'pending': '待处理',
            'running': '分析中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
    }

    getStatusBadgeClass(status) {
        const classMap = {
            'pending': 'secondary',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'warning'
        };
        return classMap[status] || 'secondary';
    }

    getSeverityBadgeClass(severity) {
        const classMap = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        };
        return classMap[severity] || 'secondary';
    }

    showSuccess(message) {
        console.log('Success:', message);
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            this.createToast('success', message);
        } else {
            alert('成功: ' + message);
        }
    }

    showError(message) {
        console.error('Error:', message);
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            this.createToast('error', message);
        } else {
            alert('错误: ' + message);
        }
    }

    showInfo(message) {
        // 使用Bootstrap toast或alert
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            // 创建toast通知
            this.createToast('info', message);
        } else {
            alert(message);
        }
    }

    createToast(type, message) {
        // 创建toast容器（如果不存在）
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // 创建toast元素
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">${type === 'error' ? '错误' : type === 'success' ? '成功' : '信息'}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        // 显示toast
        const toastElement = document.getElementById(toastId);
        if (toastElement && typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastElement, {
                autohide: true,
                delay: type === 'error' ? 5000 : 3000
            });
            toast.show();

            // 自动移除toast元素
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }
}

// 全局实例
window.analysisManager = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing analysis functionality...');
    window.analysisManager = new AnalysisManager();
});

// 导出类供其他模块使用
window.AnalysisManager = AnalysisManager;
