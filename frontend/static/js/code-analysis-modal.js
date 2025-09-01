/**
 * 代码分析模态框交互逻辑
 * 提供流畅的用户体验和表单验证
 */

class CodeAnalysisModal {
    constructor() {
        this.currentStep = 2;
        this.selectedAnalysisType = null;
        this.selectedRepository = 'deepwiki_open';
        this.config = {
            depth: 'standard',
            threads: 4,
            includeTests: true,
            generateReport: false,
            ignorePatterns: '*.min.js, node_modules/*, __pycache__/*',
            customRules: ''
        };
        this.isAnalyzing = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateProgressSteps();
        this.initializeForm();
    }

    bindEvents() {
        // 分析类型选择
        this.bindAnalysisTypeSelection();
        
        // 配置标签页切换
        this.bindConfigTabSwitching();
        
        // 表单控件事件
        this.bindFormControls();
        
        // 按钮事件
        this.bindButtonEvents();
        
        // 模态框事件
        this.bindModalEvents();
    }

    bindAnalysisTypeSelection() {
        const analysisCards = document.querySelectorAll('.analysis-type-card');
        
        analysisCards.forEach(card => {
            card.addEventListener('click', () => {
                // 移除之前的选择
                analysisCards.forEach(c => c.classList.remove('selected'));
                
                // 添加当前选择
                card.classList.add('selected');
                
                // 获取分析类型
                const title = card.querySelector('.analysis-type-title').textContent;
                this.selectedAnalysisType = title;
                
                // 添加动画效果
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    card.style.transform = '';
                }, 150);
                
                // 更新配置
                this.updateConfigForAnalysisType(title);
                
                console.log('选择的分析类型:', title);
            });
        });
    }

    bindConfigTabSwitching() {
        const configTabs = document.querySelectorAll('.config-tab');
        
        configTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // 移除活跃状态
                configTabs.forEach(t => t.classList.remove('active'));
                
                // 添加当前活跃状态
                tab.classList.add('active');
                
                // 切换配置内容
                const tabText = tab.textContent.trim();
                this.switchConfigContent(tabText);
                
                console.log('切换到配置标签:', tabText);
            });
        });
    }

    bindFormControls() {
        // 范围滑块
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(range => {
            const updateLabel = () => {
                const label = range.nextElementSibling;
                if (label && label.tagName === 'SMALL') {
                    const value = range.value;
                    const max = range.max;
                    label.textContent = `当前: ${value} 线程${value == max ? ' (最大)' : ''}`;
                }
            };
            
            range.addEventListener('input', updateLabel);
            updateLabel(); // 初始化
        });

        // 开关控件
        const switches = document.querySelectorAll('.switch-input');
        switches.forEach(switchEl => {
            switchEl.addEventListener('click', () => {
                switchEl.classList.toggle('checked');
                
                // 获取开关状态
                const isChecked = switchEl.classList.contains('checked');
                const label = switchEl.nextElementSibling?.textContent;
                
                // 更新配置
                this.updateSwitchConfig(label, isChecked);
                
                console.log(`${label}: ${isChecked ? '开启' : '关闭'}`);
            });
        });

        // 下拉选择框
        const selects = document.querySelectorAll('select.form-control');
        selects.forEach(select => {
            select.addEventListener('change', (e) => {
                const label = e.target.previousElementSibling?.textContent;
                const value = e.target.value;
                
                console.log(`${label}: ${value}`);
            });
        });

        // 文本区域实时验证
        const textarea = document.querySelector('textarea.form-control');
        if (textarea) {
            textarea.addEventListener('input', this.validateJSON.bind(this));
            textarea.addEventListener('blur', this.formatJSON.bind(this));
        }

        // 输入框验证
        const inputs = document.querySelectorAll('input.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateInput.bind(this));
        });
    }

    bindButtonEvents() {
        // 开始分析按钮
        const startBtn = document.getElementById('startAnalysisBtn');
        if (startBtn) {
            startBtn.addEventListener('click', this.startAnalysis.bind(this));
        }

        // 取消按钮 (通过事件委托处理)
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-dismiss="modal"]')) {
                this.resetModal();
            }
        });
    }

    bindModalEvents() {
        const modal = document.getElementById('codeAnalysisModal');
        if (modal) {
            // 模态框显示时
            modal.addEventListener('show.bs.modal', () => {
                this.resetModal();
                this.animateModalOpen();
            });

            // 模态框隐藏时
            modal.addEventListener('hide.bs.modal', () => {
                this.animateModalClose();
            });

            // 模态框完全隐藏后
            modal.addEventListener('hidden.bs.modal', () => {
                this.resetModal();
            });
        }
    }

    updateProgressSteps() {
        const steps = document.querySelectorAll('.progress-step');
        
        steps.forEach((step, index) => {
            const circle = step.querySelector('.step-circle');
            const stepNumber = index + 1;
            
            // 重置状态
            step.classList.remove('active', 'completed');
            circle.classList.remove('active', 'completed');
            
            if (stepNumber < this.currentStep) {
                step.classList.add('completed');
                circle.classList.add('completed');
                circle.innerHTML = '<i class="fas fa-check"></i>';
            } else if (stepNumber === this.currentStep) {
                step.classList.add('active');
                circle.classList.add('active');
                circle.textContent = stepNumber;
            } else {
                circle.textContent = stepNumber;
            }
        });
        
        // 更新进度条背景
        const progressBar = document.querySelector('.progress-steps::before');
        const progressPercentage = ((this.currentStep - 1) / 2) * 100;
        // 通过CSS变量更新进度条
        document.documentElement.style.setProperty('--progress-percentage', progressPercentage + '%');
    }

    updateConfigForAnalysisType(analysisType) {
        const configBody = document.querySelector('.config-body');
        if (!configBody) return;

        // 根据分析类型显示不同的配置选项
        const configs = {
            '结构分析': {
                depth: ['快速扫描', '标准分析', '深度分析'],
                options: ['包含测试文件', '分析依赖关系', '生成图表']
            },
            '复杂度分析': {
                depth: ['基础检查', '标准分析', '详细分析'],
                options: ['包含测试文件', '计算圈复杂度', '性能分析']
            },
            '质量分析': {
                depth: ['快速检查', '标准扫描', '全面审查'],
                options: ['包含测试文件', '代码规范检查', '最佳实践分析']
            },
            '安全分析': {
                depth: ['基础扫描', '标准检查', '深度审计'],
                options: ['包含依赖检查', '漏洞扫描', '安全评级']
            }
        };

        const config = configs[analysisType];
        if (config) {
            // 这里可以动态更新配置选项
            console.log('更新配置选项:', config);
        }
    }

    switchConfigContent(tabName) {
        const configForm = document.getElementById('advancedConfig');
        if (!configForm) return;

        // 添加切换动画
        configForm.style.opacity = '0';
        configForm.style.transform = 'translateX(-10px)';
        
        setTimeout(() => {
            // 这里可以根据不同的标签页显示不同的内容
            switch (tabName) {
                case '基础配置':
                    this.showBasicConfig();
                    break;
                case '高级配置':
                    this.showAdvancedConfig();
                    break;
                case '预设模板':
                    this.showPresetTemplates();
                    break;
            }
            
            // 恢复动画
            configForm.style.opacity = '1';
            configForm.style.transform = 'translateX(0)';
        }, 150);
    }

    showBasicConfig() {
        // 显示基础配置选项
        console.log('显示基础配置');
    }

    showAdvancedConfig() {
        // 显示高级配置选项（当前默认显示的）
        console.log('显示高级配置');
    }

    showPresetTemplates() {
        // 显示预设模板
        console.log('显示预设模板');
    }

    validateJSON(e) {
        const textarea = e.target;
        const value = textarea.value.trim();
        
        if (!value) {
            this.resetValidationState(textarea);
            return;
        }

        try {
            JSON.parse(value);
            this.setValidationState(textarea, true);
        } catch (error) {
            this.setValidationState(textarea, false, error.message);
        }
    }

    formatJSON(e) {
        const textarea = e.target;
        const value = textarea.value.trim();
        
        if (!value) return;

        try {
            const parsed = JSON.parse(value);
            const formatted = JSON.stringify(parsed, null, 2);
            textarea.value = formatted;
            this.setValidationState(textarea, true);
        } catch (error) {
            // JSON无效，不格式化
        }
    }

    validateInput(e) {
        const input = e.target;
        const value = input.value.trim();
        const type = input.type;
        
        let isValid = true;
        let message = '';

        // 根据不同类型进行验证
        switch (type) {
            case 'text':
                if (input.placeholder?.includes('例如:') && value) {
                    // 验证文件模式格式
                    const patterns = value.split(',').map(p => p.trim());
                    const validPattern = /^[\w\*\.\-\/]+$/;
                    
                    isValid = patterns.every(pattern => validPattern.test(pattern));
                    message = isValid ? '' : '请输入有效的文件模式';
                }
                break;
        }

        this.setValidationState(input, isValid, message);
    }

    setValidationState(element, isValid, message = '') {
        element.style.borderColor = isValid ? 'var(--success-color)' : 'var(--error-color)';
        
        // 移除之前的错误消息
        const existingError = element.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // 添加错误消息
        if (!isValid && message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.cssText = 'color: var(--error-color); font-size: 0.75rem; margin-top: 0.25rem;';
            errorDiv.textContent = message;
            element.parentNode.appendChild(errorDiv);
        }
    }

    resetValidationState(element) {
        element.style.borderColor = '';
        const errorMessage = element.parentNode.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    updateSwitchConfig(label, isChecked) {
        // 更新内部配置状态
        switch (label?.trim()) {
            case '包含测试文件':
                this.config.includeTests = isChecked;
                break;
            case '生成详细报告':
                this.config.generateReport = isChecked;
                break;
        }
    }

    async startAnalysis() {
        if (this.isAnalyzing) return;

        const startBtn = document.getElementById('startAnalysisBtn');
        if (!startBtn) return;

        // 验证表单
        if (!this.validateForm()) {
            this.showError('请完善所有必填配置项');
            return;
        }

        this.isAnalyzing = true;
        
        // 更新按钮状态
        const originalContent = startBtn.innerHTML;
        startBtn.innerHTML = '<div class="loading-spinner me-1"></div>正在启动分析...';
        startBtn.disabled = true;

        try {
            // 收集分析配置
            const analysisConfig = this.collectAnalysisConfig();
            
            // 发送分析请求
            const result = await this.submitAnalysisRequest(analysisConfig);
            
            if (result.success) {
                // 显示成功状态
                startBtn.innerHTML = '<i class="fas fa-check me-1"></i>分析已启动';
                
                // 延迟关闭模态框
                setTimeout(() => {
                    this.closeModal();
                    this.showSuccess('代码分析已成功启动，请在任务列表中查看进度');
                }, 1500);
            } else {
                throw new Error(result.message || '启动分析失败');
            }
        } catch (error) {
            console.error('分析启动失败:', error);
            this.showError('启动分析失败: ' + error.message);
            
            // 恢复按钮状态
            startBtn.innerHTML = originalContent;
            startBtn.disabled = false;
            this.isAnalyzing = false;
        }
    }

    validateForm() {
        // 检查是否选择了分析类型
        if (!this.selectedAnalysisType) {
            this.highlightAnalysisTypes();
            return false;
        }

        // 检查JSON配置是否有效
        const textarea = document.querySelector('textarea.form-control');
        if (textarea && textarea.value.trim()) {
            try {
                JSON.parse(textarea.value);
            } catch (error) {
                this.setValidationState(textarea, false, 'JSON格式错误');
                return false;
            }
        }

        return true;
    }

    highlightAnalysisTypes() {
        const typesContainer = document.querySelector('.analysis-types');
        if (typesContainer) {
            typesContainer.style.outline = '2px solid var(--error-color)';
            typesContainer.style.borderRadius = 'var(--border-radius)';
            
            setTimeout(() => {
                typesContainer.style.outline = '';
            }, 2000);
        }
    }

    collectAnalysisConfig() {
        return {
            repository: this.selectedRepository,
            analysisType: this.selectedAnalysisType,
            depth: document.querySelector('select.form-control')?.value || 'standard',
            threads: document.querySelector('input[type="range"]')?.value || 4,
            includeTests: document.querySelector('.switch-input.checked') !== null,
            ignorePatterns: document.querySelector('input.form-control')?.value || '',
            customRules: document.querySelector('textarea.form-control')?.value || ''
        };
    }

    async submitAnalysisRequest(config) {
        // 模拟API请求
        console.log('提交分析配置:', config);
        
        // 这里应该调用实际的API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ success: true, taskId: 'task_' + Date.now() });
            }, 2000);
        });
    }

    closeModal() {
        const modal = document.getElementById('codeAnalysisModal');
        if (modal) {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    }

    resetModal() {
        // 重置步骤
        this.currentStep = 2;
        this.updateProgressSteps();
        
        // 重置分析状态
        this.isAnalyzing = false;
        
        // 重置按钮状态
        const startBtn = document.getElementById('startAnalysisBtn');
        if (startBtn) {
            startBtn.innerHTML = '<i class="fas fa-play me-1"></i>开始分析';
            startBtn.disabled = false;
        }
        
        // 清除验证状态
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => this.resetValidationState(input));
    }

    animateModalOpen() {
        const modalContent = document.querySelector('#codeAnalysisModal .modal-content');
        if (modalContent) {
            modalContent.style.animation = 'modalSlideIn 0.3s ease';
        }
        
        // 添加淡入动画到内容区域
        const animatableElements = document.querySelectorAll('.fade-in, .slide-in');
        animatableElements.forEach((element, index) => {
            element.style.animationDelay = (index * 0.1) + 's';
        });
    }

    animateModalClose() {
        const modalContent = document.querySelector('#codeAnalysisModal .modal-content');
        if (modalContent) {
            modalContent.style.animation = 'modalSlideOut 0.2s ease';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? 'var(--success-color)' : 'var(--error-color)'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius-sm);
            box-shadow: var(--shadow);
            z-index: 10000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 350px;
            word-wrap: break-word;
        `;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
        notification.innerHTML = `
            <i class="fas ${icon} me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    initializeForm() {
        // 设置默认选中的分析类型
        const complexityCard = document.querySelector('.analysis-type-card.selected');
        if (complexityCard) {
            this.selectedAnalysisType = complexityCard.querySelector('.analysis-type-title').textContent;
        }
    }
}

// 添加模态框动画样式
const modalAnimationStyles = `
    @keyframes modalSlideIn {
        from {
            opacity: 0;
            transform: translateY(-50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes modalSlideOut {
        from {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
        to {
            opacity: 0;
            transform: translateY(-20px) scale(0.95);
        }
    }
`;

// 添加样式到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = modalAnimationStyles;
document.head.appendChild(styleSheet);

// 初始化代码分析模态框
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否存在模态框元素
    const modal = document.getElementById('codeAnalysisModal');
    if (modal) {
        window.codeAnalysisModal = new CodeAnalysisModal();
        console.log('✅ 代码分析模态框已初始化');
    }
});

// 导出类供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CodeAnalysisModal;
}