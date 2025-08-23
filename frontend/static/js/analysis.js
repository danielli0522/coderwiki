/**
 * Analysis Management JavaScript
 */

class AnalysisManager {
    constructor(options = {}) {
        this.repositoryId = options.repositoryId;
        this.repositoryName = options.repositoryName || '';
        this.currentAnalysis = null;
        this.analysisResults = null;
        this.analysisHistory = [];
        this.pollingInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadAnalysisResults();
        this.loadAnalysisHistory();
    }

    bindEvents() {
        // 分析控制事件
        document.getElementById('startAnalysisBtn').addEventListener('click', () => this.startAnalysis());
        document.getElementById('startFirstAnalysisBtn').addEventListener('click', () => this.startAnalysis());
        document.getElementById('stopAnalysisBtn').addEventListener('click', () => this.stopAnalysis());
        document.getElementById('cancelAnalysisBtn').addEventListener('click', () => this.cancelAnalysis());
        
        // 其他操作事件
        document.getElementById('refreshAnalysisBtn').addEventListener('click', () => this.refreshAnalysis());
        document.getElementById('exportResultsBtn').addEventListener('click', () => this.exportResults());
        document.getElementById('clearCacheBtn').addEventListener('click', () => this.clearCache());
        
        // 分析类型选择事件
        document.querySelectorAll('input[type="checkbox"][id$="Analysis"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateAnalysisTypes());
        });
    }

    async loadAnalysisResults() {
        try {
            const response = await fetch(`/api/analysis/results/${this.repositoryId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('加载分析结果失败');
            }

            const data = await response.json();
            
            if (data.success) {
                this.analysisResults = data.results;
                this.renderAnalysisResults();
                this.updateAnalysisStatus();
            } else {
                this.showEmptyState();
            }
            
        } catch (error) {
            console.error('Error loading analysis results:', error);
            this.showError('加载分析结果失败');
        } finally {
            document.getElementById('analysisLoading').style.display = 'none';
        }
    }

    async loadAnalysisHistory() {
        try {
            const response = await fetch(`/api/analysis/history/${this.repositoryId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('加载分析历史失败');
            }

            const data = await response.json();
            
            if (data.success) {
                this.analysisHistory = data.history;
                this.renderAnalysisHistory();
            }
            
        } catch (error) {
            console.error('Error loading analysis history:', error);
        }
    }

    renderAnalysisResults() {
        if (!this.analysisResults) {
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

        document.getElementById('structureStats').innerHTML = statsHtml;

        // 渲染目录树
        if (structure.directory_tree) {
            document.getElementById('directoryTree').innerHTML = this.renderDirectoryTree(structure.directory_tree);
        }
    }

    renderDependenciesResults() {
        const dependencies = this.analysisResults.dependencies;
        if (!dependencies) return;

        // 渲染包管理器
        const packageManagersHtml = dependencies.package_managers.map(pm => 
            `<span class="badge bg-primary me-1">${this.escapeHtml(pm)}</span>`
        ).join('');

        document.getElementById('packageManagers').innerHTML = packageManagersHtml || '<span class="text-muted">无</span>';

        // 渲染依赖关系图（简化版本）
        const dependencyGraphHtml = `
            <div class="text-center">
                <i class="fas fa-project-diagram fa-4x text-muted mb-3"></i>
                <p class="text-muted">依赖关系图功能开发中...</p>
                <small>检测到 ${Object.keys(dependencies.dependencies || {}).length} 个依赖</small>
            </div>
        `;

        document.getElementById('dependencyGraph').innerHTML = dependencyGraphHtml;
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
            <div class="row mt-3">
                <div class="col-12">
                    <h6>复杂度分布</h6>
                    <div class="progress" style="height: 20px;">
                        ${this.renderComplexityProgress(complexity.complexity_distribution)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('complexityMetrics').innerHTML = metricsHtml;

        // 渲染复杂度图表
        const complexityChartHtml = `
            <div class="text-center">
                <i class="fas fa-chart-bar fa-4x text-muted mb-3"></i>
                <p class="text-muted">复杂度图表功能开发中...</p>
            </div>
        `;

        document.getElementById('complexityChart').innerHTML = complexityChartHtml;
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

        document.getElementById('programmingLanguages').innerHTML = languagesHtml;

        // 渲染框架和工具
        const frameworksHtml = `
            <div class="mb-3">
                <strong>框架:</strong>
                <div class="mt-1">
                    ${techStack.frameworks?.map(f => `<span class="badge bg-success me-1">${this.escapeHtml(f)}</span>`).join('') || '<span class="text-muted">无</span>'}
                </div>
            </div>
            <div class="mb-3">
                <strong>数据库:</strong>
                <div class="mt-1">
                    ${techStack.databases?.map(d => `<span class="badge bg-info me-1">${this.escapeHtml(d)}</span>`).join('') || '<span class="text-muted">无</span>'}
                </div>
            </div>
            <div class="mb-3">
                <strong>工具:</strong>
                <div class="mt-1">
                    ${techStack.tools?.map(t => `<span class="badge bg-warning me-1">${this.escapeHtml(t)}</span>`).join('') || '<span class="text-muted">无</span>'}
                </div>
            </div>
        `;

        document.getElementById('frameworksTools').innerHTML = frameworksHtml;
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

        document.getElementById('securityIssues').innerHTML = securityHtml;
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

        document.getElementById('designPatterns').innerHTML = patternsHtml;
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

        document.getElementById('qualityMetrics').innerHTML = metricsHtml;

        // 渲染质量评分
        const qualityScoreHtml = `
            <div class="text-center">
                <div class="quality-score-gauge">
                    <div class="metric-card">
                        <div class="metric-value">${quality.overall_score || '0'}</div>
                        <div class="metric-label">总体质量评分</div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('qualityScore').innerHTML = qualityScoreHtml;
    }

    renderAnalysisHistory() {
        const historyHtml = this.analysisHistory.map(item => `
            <div class="history-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>分析 #${item.id}</strong>
                        <span class="badge bg-${this.getStatusBadgeClass(item.status)} ms-2">${item.status}</span>
                    </div>
                    <div class="timestamp">${this.formatDate(item.created_at)}</div>
                </div>
                <div class="analysis-types">
                    ${item.analysis_types?.map(type => `<span class="badge bg-outline-secondary me-1">${type}</span>`).join('')}
                </div>
            </div>
        `).join('') || '<p class="text-muted">暂无分析历史</p>';

        document.getElementById('analysisHistory').innerHTML = historyHtml;
    }

    async startAnalysis() {
        const analysisTypes = this.getSelectedAnalysisTypes();
        const config = this.getAnalysisConfig();

        if (analysisTypes.length === 0) {
            this.showError('请至少选择一种分析类型');
            return;
        }

        try {
            const response = await fetch('/api/analysis/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repository_id: this.repositoryId,
                    analysis_types: analysisTypes,
                    config: config
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showProgressModal();
                this.currentAnalysis = data.analysis_ids[0];
                this.startPolling();
                this.updateAnalysisButtons(true);
            } else {
                this.showError(data.message);
            }

        } catch (error) {
            console.error('Error starting analysis:', error);
            this.showError('开始分析失败');
        }
    }

    async stopAnalysis() {
        if (!this.currentAnalysis) return;

        try {
            const response = await fetch(`/api/analysis/cancel/${this.currentAnalysis}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.stopPolling();
                this.updateAnalysisButtons(false);
                this.hideProgressModal();
                this.showSuccess('分析已停止');
            } else {
                this.showError(data.message);
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
            const response = await fetch(`/api/analysis/status/${this.currentAnalysis}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.updateProgress(data.status);
                
                if (data.status.status === 'completed' || data.status.status === 'failed') {
                    this.stopPolling();
                    this.updateAnalysisButtons(false);
                    this.hideProgressModal();
                    
                    if (data.status.status === 'completed') {
                        this.showSuccess('分析完成');
                        this.loadAnalysisResults();
                        this.loadAnalysisHistory();
                    } else {
                        this.showError('分析失败: ' + data.status.message);
                    }
                }
            }

        } catch (error) {
            console.error('Error polling analysis status:', error);
        }
    }

    updateProgress(status) {
        const progressBar = document.getElementById('analysisProgressBar');
        const progressText = document.getElementById('analysisProgressText');
        const progressDetails = document.getElementById('analysisProgressDetails');

        progressBar.style.width = `${status.progress || 0}%`;
        progressText.textContent = status.message || '分析中...';

        if (status.details) {
            progressDetails.innerHTML = `
                <div class="progress-details">
                    <small>当前步骤: ${status.details.current_step}</small>
                    <br>
                    <small>已处理文件: ${status.details.processed_files || 0}</small>
                    <br>
                    <small>预计剩余时间: ${status.details.estimated_time || '未知'}</small>
                </div>
            `;
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

    updateAnalysisButtons(isAnalyzing) {
        const startBtn = document.getElementById('startAnalysisBtn');
        const stopBtn = document.getElementById('stopAnalysisBtn');

        if (isAnalyzing) {
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
        } else {
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
        }
    }

    updateAnalysisStatus() {
        if (!this.analysisResults) return;

        const status = this.analysisResults.status || 'unknown';
        const completedAnalyses = this.analysisResults.completed_analyses || 0;
        const analysisTypes = this.analysisResults.analysis_types || [];
        const lastUpdated = this.analysisResults.last_updated;

        document.getElementById('analysisStatus').textContent = this.getStatusText(status);
        document.getElementById('completedAnalyses').textContent = completedAnalyses;
        document.getElementById('analysisTypesCount').textContent = analysisTypes.length;
        document.getElementById('lastUpdated').textContent = this.formatDate(lastUpdated);
    }

    async refreshAnalysis() {
        await this.loadAnalysisResults();
        await this.loadAnalysisHistory();
        this.showSuccess('分析结果已刷新');
    }

    async exportResults() {
        try {
            const response = await fetch(`/api/analysis/results/${this.repositoryId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                const blob = new Blob([JSON.stringify(data.results, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `analysis-results-${this.repositoryId}-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                this.showSuccess('分析结果已导出');
            } else {
                this.showError('导出失败');
            }

        } catch (error) {
            console.error('Error exporting results:', error);
            this.showError('导出失败');
        }
    }

    async clearCache() {
        if (!confirm('确定要清除分析缓存吗？这将删除所有分析结果。')) {
            return;
        }

        try {
            const response = await fetch(`/api/analysis/cache/clear/${this.repositoryId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('缓存已清除');
                this.analysisResults = null;
                this.showEmptyState();
                this.loadAnalysisHistory();
            } else {
                this.showError(data.message);
            }

        } catch (error) {
            console.error('Error clearing cache:', error);
            this.showError('清除缓存失败');
        }
    }

    getSelectedAnalysisTypes() {
        const types = [];
        document.querySelectorAll('input[type="checkbox"][id$="Analysis"]:checked').forEach(checkbox => {
            types.push(checkbox.id.replace('Analysis', ''));
        });
        return types;
    }

    getAnalysisConfig() {
        return {
            max_file_size: parseInt(document.getElementById('maxFileSize').value) * 1024 * 1024,
            timeout: parseInt(document.getElementById('timeout').value),
            enable_cache: document.getElementById('enableCache').checked,
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

    showEmptyState() {
        document.getElementById('analysisResults').style.display = 'none';
        document.getElementById('analysisEmpty').style.display = 'block';
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

    renderComplexityProgress(distribution) {
        if (!distribution) return '';
        
        const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
        return Object.entries(distribution).map(([level, count]) => {
            const percentage = (count / total * 100).toFixed(1);
            const colorClass = this.getComplexityColorClass(level);
            return `<div class="progress-bar bg-${colorClass}" style="width: ${percentage}%" title="${level}: ${count} files (${percentage}%)">${level}</div>`;
        }).join('');
    }

    renderDirectoryTree(tree, level = 0) {
        if (!tree) return '';
        
        let html = '';
        Object.entries(tree).forEach(([name, children]) => {
            const indent = '  '.repeat(level);
            if (children && typeof children === 'object') {
                html += `<div class="tree-item">${indent}${name}/</div>`;
                html += this.renderDirectoryTree(children, level + 1);
            } else {
                html += `<div class="tree-item">${indent}${name}</div>`;
            }
        });
        return html;
    }

    // 工具方法
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
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

    getComplexityColorClass(complexity) {
        const classMap = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        };
        return classMap[complexity] || 'secondary';
    }

    showSuccess(message) {
        alert(message); // 简单实现，可以改进为Toast
    }

    showError(message) {
        alert(message); // 简单实现，可以改进为Toast
    }
}