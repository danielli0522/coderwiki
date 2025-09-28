/**
 * 代码分析管理器
 * 负责处理代码分析相关的所有操作
 */
class AnalysisManager {
    constructor() {
        this.repositoryId = null;
        this.analysisResults = {};
        this.analysisHistory = [];
        this.currentAnalysis = null;
        this.pollingInterval = null;
        this.apiClient = window.api || new ApiClient();

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadRepositoryList();
        this.loadAnalysisResults();
    }

    bindEvents() {
        // 绑定仓库选择事件
        this.bindElement('analysisRepoSelect', 'change', (e) => {
            this.repositoryId = e.target.value;
            this.loadAnalysisResults();
        });

        // 绑定分析按钮事件
        this.bindElement('startAnalysisBtn', 'click', () => this.startAnalysis());
        this.bindElement('startFirstAnalysisBtn', 'click', () => this.startAnalysis());
        this.bindElement('stopAnalysisBtn', 'click', () => this.stopAnalysis());
        this.bindElement('newAnalysisBtn', 'click', () => this.showNewAnalysisModal());

        // 绑定模态框事件
        this.bindElement('modalStartAnalysisBtn', 'click', () => this.startAnalysisFromModal());
        this.bindElement('cancelAnalysisBtn', 'click', () => this.cancelAnalysis());
        
        // 绑定其他操作按钮
        this.bindElement('refreshAnalysisBtn', 'click', () => this.refreshAnalysis());
        this.bindElement('clearCacheBtn', 'click', () => this.clearCache());

        // 绑定分析类型选择事件
        document.querySelectorAll('input[id$="Analysis"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateAnalysisButtonState());
        });

        // 绑定配置选项事件
        document.querySelectorAll('input[name="analysisConfig"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateAnalysisButtonState());
        });
    }

    bindElement(selector, event, handler) {
        const element = document.getElementById(selector);
        if (element) {
            element.addEventListener(event, handler);
        } else {
            console.warn(`Element with id '${selector}' not found`);
        }
    }

    async loadRepositoryList() {
        try {
            const repositories = await this.apiClient.getRepositories();
            this.populateRepositorySelect(repositories);
        } catch (error) {
            console.error('Error loading repositories:', error);
            this.showError('加载仓库列表失败');
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
                select.appendChild(option);
            });

            // 自动选择第一个仓库
            if (repositories.length > 0) {
                select.value = repositories[0].id;
                this.repositoryId = repositories[0].id;
                this.loadAnalysisResults();
            }
        }

        if (modalSelect) {
            modalSelect.innerHTML = '<option value="">请选择仓库</option>';
            repositories.forEach(repo => {
                const option = document.createElement('option');
                option.value = repo.id;
                option.textContent = repo.name;
                modalSelect.appendChild(option);
            });
        }

        // 默认选择一些基础分析类型
        this.setDefaultAnalysisTypes();
    }

    async loadAnalysisResults() {
        if (!this.repositoryId) {
            this.showEmptyState();
            return;
        }

        try {
            document.getElementById('analysisLoading').style.display = 'block';

            const results = await this.apiClient.getAnalysisResults(this.repositoryId);

            if (results && Object.keys(results).length > 0) {
                this.analysisResults = results;
                this.renderAnalysisResults();
                this.updateAnalysisStatus();
            } else {
                this.showEmptyState();
            }

        } catch (error) {
            console.error('Error loading analysis results:', error);
            this.showError('加载分析结果失败');
            this.showEmptyState();
        } finally {
            document.getElementById('analysisLoading').style.display = 'none';
        }
    }

    async loadAnalysisHistory() {
        if (!this.repositoryId) return;

        try {
            const history = await this.apiClient.getAnalysisHistory(this.repositoryId);
            this.analysisHistory = history;
            this.renderAnalysisHistory();
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

    async startAnalysis() {
        if (!this.repositoryId) {
            this.showError('请先选择一个仓库');
            return;
        }

        const analysisTypes = this.getSelectedAnalysisTypes();
        const config = this.getAnalysisConfig();

        if (analysisTypes.length === 0) {
            this.showError('请至少选择一种分析类型');
            return;
        }

        try {
            const analysisId = await this.apiClient.startAnalysis(this.repositoryId, analysisTypes, config);
            this.showProgressModal();
            this.currentAnalysis = analysisId;
            this.startPolling();
            this.updateAnalysisButtons(true);
            this.showSuccess('分析已开始');
        } catch (error) {
            console.error('Error starting analysis:', error);
            
            let errorMessage;
            if (error.message && error.message.includes('Authentication required')) {
                errorMessage = '用户未登录，请先登录后再试';
            } else if (error.message && error.message.includes('网络连接失败')) {
                errorMessage = '网络连接失败，请检查网络连接或稍后重试';
            } else if (error.message && error.message.includes('Failed to fetch')) {
                errorMessage = '无法连接到服务器，请检查网络连接或联系管理员';
            } else if (error.message && error.message.includes('HTTP error! status: 400')) {
                errorMessage = '请求参数有误，请检查仓库是否存在且已完成克隆';
            } else if (error.message && error.message.includes('HTTP error! status: 403')) {
                errorMessage = '无权限访问此仓库，请检查权限设置';
            } else if (error.message && error.message.includes('HTTP error! status: 404')) {
                errorMessage = '仓库不存在，请检查仓库是否已正确添加';
            } else if (error.message && error.message.includes('HTTP error! status: 500')) {
                errorMessage = '服务器内部错误，请稍后重试或联系管理员';
            } else {
                errorMessage = error.message ? `开始分析失败: ${error.message}` : '开始分析失败，请稍后重试';
            }
            
            this.showError(errorMessage);
        }
    }

    async startAnalysisFromModal() {
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
            await this.apiClient.cancelAnalysis(this.currentAnalysis);
            this.stopPolling();
            this.updateAnalysisButtons(false);
            this.hideProgressModal();
            this.showSuccess('分析已停止');
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
            const data = await this.apiClient.getAnalysisStatus(this.currentAnalysis);
            this.updateProgress(data);

            if (data.status === 'completed' || data.status === 'failed') {
                this.stopPolling();
                this.updateAnalysisButtons(false);
                this.hideProgressModal();

                if (data.status === 'completed') {
                    this.showSuccess('分析完成');
                    this.loadAnalysisResults();
                    this.loadAnalysisHistory();
                    // No need to call loadAnalysisStatistics here as it's not part of the new_code_analysis_results
                } else {
                    this.showError('分析失败: ' + (data.error_message || '未知错误'));
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
        const modal = new bootstrap.Modal(document.getElementById('newAnalysisModal'));
        modal.show();
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
        // No need to call loadAnalysisStatistics here as it's not part of the new_code_analysis_results
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
            await this.apiClient.clearCache(this.repositoryId);
            this.showSuccess('缓存已清除');
            this.analysisResults = {};
            this.showEmptyState();
            this.loadAnalysisHistory();
        } catch (error) {
            console.error('Error clearing cache:', error);
            this.showError('清除缓存失败');
        }
    }

    getSelectedAnalysisTypes() {
        const types = [];

        // ID到API名称的映射
        const typeMapping = {
            'structureAnalysis': 'structure',
            'dependenciesAnalysis': 'dependencies',
            'complexityAnalysis': 'complexity',
            'techStackAnalysis': 'tech_stack',
            'securityAnalysis': 'security',
            'patternsAnalysis': 'patterns',
            'qualityAnalysis': 'quality'
        };

        document.querySelectorAll('input[id$="Analysis"]:checked').forEach(checkbox => {
            const apiType = typeMapping[checkbox.id];
            if (apiType) {
                types.push(apiType);
            }
        });

        return types;
    }

    getAnalysisConfig() {
        const config = {};
        document.querySelectorAll('input[name="analysisConfig"]:checked').forEach(checkbox => {
            config[checkbox.id] = checkbox.checked;
        });
        return config;
    }

    setDefaultAnalysisTypes() {
        // 默认选择一些基础分析类型（最可靠的4种）
        const defaultTypes = ['structure', 'tech_stack', 'dependencies', 'security'];

        defaultTypes.forEach(type => {
            const checkbox = document.getElementById(type + 'Analysis');
            if (checkbox) {
                checkbox.checked = true;
                console.log(`Auto-selected analysis type: ${type}`);
            }
        });

        // 更新按钮状态
        this.updateAnalysisButtonState();
    }

    updateAnalysisButtonState() {
        // 更新分析类型选择的UI反馈
        document.querySelectorAll('input[id$="Analysis"]').forEach(checkbox => {
            const label = checkbox.nextElementSibling;
            if (checkbox.checked) {
                label.style.fontWeight = '600';
                label.style.color = '#007bff';
            } else {
                label.style.fontWeight = 'normal';
                label.style.color = 'inherit';
            }
        });

        // 更新配置选项的UI反馈
        document.querySelectorAll('input[name="analysisConfig"]').forEach(checkbox => {
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
        // 使用Bootstrap toast或alert
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            // 创建toast通知
            this.createToast('success', message);
        } else {
            alert(message);
        }
    }

    showError(message) {
        // 使用Bootstrap toast或alert
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            // 创建toast通知
            this.createToast('danger', message);
        } else {
            alert(message);
        }
    }

    createToast(type, message) {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();

        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // 自动移除toast元素
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
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
