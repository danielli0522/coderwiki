/**
 * 统计信息组件
 * 负责统计数据获取、展示和图表渲染
 */

// 使用立即执行函数表达式避免全局作用域污染
(function() {
    // 检查组件是否已注册
    if (window.ComponentRegistry && window.ComponentRegistry.isRegistered('StatsComponent')) {
        console.log('StatsComponent already registered, reusing existing component');
        return;
    }

    class StatsComponent {
    constructor() {
        this.charts = {};
        this.cache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5分钟缓存
        this.isAuthenticated = false;
        this.init();
    }

    async init() {
        await this.checkAuthentication();
        if (this.isAuthenticated) {
            this.bindEvents();
            this.loadStats();
            this.startAutoRefresh();
        } else {
            console.log('用户未登录，跳过统计组件初始化');
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
        // 绑定刷新按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('#refreshStatsBtn')) {
                this.loadStats(true);
            }
        });
    }

    async loadStats(forceRefresh = false) {
        if (!this.isAuthenticated) {
            console.log('用户未登录，跳过统计数据加载');
            return;
        }

        try {
            const stats = await this.fetchStats(forceRefresh);
            this.updateStatsDisplay(stats);
            this.renderCharts(stats);
        } catch (error) {
            console.error('加载统计数据失败:', error);
            this.showError('加载统计数据失败');
        }
    }

    async fetchStats(forceRefresh = false) {
        const cacheKey = 'dashboard-stats';
        const cached = this.cache.get(cacheKey);

        if (!forceRefresh && cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            return cached.data;
        }

        const response = await fetch('/api/users/stats', {
            redirect: 'manual'
        });

        if (response.status === 302 || response.status === 303) {
            throw new Error('需要登录');
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
    }

    updateStatsDisplay(stats) {
        // 更新统计数字
        this.updateStatNumber('totalRepositories', stats.total_repositories || 0);
        this.updateStatNumber('totalDocuments', stats.total_documents || 0);
        this.updateStatNumber('activeTasks', stats.active_tasks || 0);
        this.updateStatNumber('monthlyGenerated', stats.monthly_generated || 0);
    }

    updateStatNumber(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = this.formatNumber(value);
            this.animateNumber(element, value);
        }
    }

    animateNumber(element, targetValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);

            element.textContent = this.formatNumber(currentValue);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        }
        return num.toString();
    }

    renderCharts(stats) {
        this.renderGenerationChart(stats.generation_trend || []);
        this.renderDocumentTypeChart(stats.document_types || {});
    }

    renderGenerationChart(trendData) {
        const ctx = document.getElementById('generationChart');
        if (!ctx) return;

        // 销毁现有图表
        if (this.charts.generation) {
            this.charts.generation.destroy();
        }

        this.charts.generation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendData.map(item => item.date),
                datasets: [{
                    label: '文档生成数量',
                    data: trendData.map(item => item.count),
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderDocumentTypeChart(typeData) {
        const ctx = document.getElementById('documentTypeChart');
        if (!ctx) return;

        // 销毁现有图表
        if (this.charts.documentType) {
            this.charts.documentType.destroy();
        }

        const labels = Object.keys(typeData);
        const data = Object.values(typeData);
        const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

        this.charts.documentType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    startAutoRefresh() {
        // 每30秒自动刷新一次统计数据
        setInterval(() => {
            this.loadStats();
        }, 30000);
    }

    showError(message) {
        // 显示错误消息
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const statsContainer = document.querySelector('.stats-container');
        if (statsContainer) {
            statsContainer.insertAdjacentHTML('afterbegin', alertHtml);

            // 5秒后自动关闭
            setTimeout(() => {
                const alert = statsContainer.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }

    destroy() {
        // 清理图表实例
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
    }

    // 注册组件到注册表
    if (window.ComponentRegistry) {
        window.ComponentRegistry.register('StatsComponent', StatsComponent);
    } else {
        // 降级方案
        window.StatsComponent = StatsComponent;
    }

    // 确保组件实例被创建
    if (typeof window.statsComponent === 'undefined') {
        window.statsComponent = new StatsComponent();
        console.log('StatsComponent instance created');
    } else {
        console.log('StatsComponent instance already exists, reusing');
    }
})();
