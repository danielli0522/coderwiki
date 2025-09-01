/**
 * Winston Modal Template System for Dashboard Components
 * Provides reusable, managed modal templates with lifecycle control
 * Phase 4 FINAL: Unified Modal Management Architecture
 */

class WinstonModalTemplates {
    constructor() {
        this.templates = new Map();
        this.modalInstances = new Map();
        this.activeModals = new Set();
        this.modalCounter = 0;
        
        // Initialize template registry
        this.initializeTemplates();
        
        console.log('🏗️ Winston Modal Template System initialized');
    }

    // =================================================================
    // TEMPLATE REGISTRY SYSTEM
    // =================================================================

    initializeTemplates() {
        // Register dashboard-specific modal templates
        this.registerTemplate('addRepository', this.getAddRepositoryTemplate());
        this.registerTemplate('generateDocument', this.getGenerateDocumentTemplate());
        this.registerTemplate('taskProgress', this.getTaskProgressTemplate());
        this.registerTemplate('confirmation', this.getConfirmationTemplate());
        this.registerTemplate('error', this.getErrorTemplate());
        this.registerTemplate('success', this.getSuccessTemplate());
    }

    registerTemplate(name, template) {
        this.templates.set(name, template);
        console.log(`✅ Registered modal template: ${name}`);
    }

    getTemplate(name) {
        if (!this.templates.has(name)) {
            console.error(`❌ Template not found: ${name}`);
            return null;
        }
        return this.templates.get(name);
    }

    // =================================================================
    // DASHBOARD MODAL TEMPLATES
    // =================================================================

    getAddRepositoryTemplate() {
        return {
            id: 'addRepositoryModal',
            title: '添加仓库',
            size: 'modal-lg',
            content: `
                <form id="addRepositoryForm" class="needs-validation" novalidate>
                    <div class="mb-3">
                        <label for="repoName" class="form-label">
                            <i class="fas fa-tag text-primary me-2"></i>仓库名称
                        </label>
                        <input type="text" class="form-control" id="repoName" name="repoName" 
                               placeholder="输入仓库名称" required>
                        <div class="invalid-feedback">请输入仓库名称</div>
                    </div>
                    <div class="mb-3">
                        <label for="repoUrl" class="form-label">
                            <i class="fas fa-link text-primary me-2"></i>仓库URL
                        </label>
                        <input type="url" class="form-control" id="repoUrl" name="repoUrl" 
                               placeholder="https://github.com/user/repo.git" required>
                        <div class="form-text">
                            <i class="fas fa-info-circle text-muted"></i>
                            支持GitHub、GitLab等Git仓库地址
                        </div>
                        <div class="invalid-feedback">请输入有效的仓库URL</div>
                    </div>
                    <div class="mb-3">
                        <label for="repoDescription" class="form-label">
                            <i class="fas fa-align-left text-primary me-2"></i>描述
                        </label>
                        <textarea class="form-control" id="repoDescription" name="repoDescription" 
                                rows="3" placeholder="简单描述这个仓库的用途（可选）"></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="repoBranch" class="form-label">
                            <i class="fas fa-code-branch text-primary me-2"></i>分支
                        </label>
                        <input type="text" class="form-control" id="repoBranch" name="repoBranch" 
                               value="main" placeholder="main">
                        <div class="form-text">
                            <i class="fas fa-info-circle text-muted"></i>
                            指定要分析的分支（默认: main）
                        </div>
                    </div>
                </form>
            `,
            buttons: [
                {
                    text: '取消',
                    class: 'btn-secondary',
                    dismiss: true
                },
                {
                    text: '<i class="fas fa-save me-2"></i>保存仓库',
                    class: 'btn-primary',
                    id: 'saveRepositoryBtn'
                }
            ],
            handlers: {
                onShow: (modal, config) => {
                    // Focus first input
                    setTimeout(() => {
                        modal.querySelector('#repoName').focus();
                    }, 100);
                },
                onShown: (modal, config) => {
                    // Enable form validation
                    modal.querySelector('#addRepositoryForm').addEventListener('submit', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (e.target.checkValidity()) {
                            config.onSave && config.onSave(modal);
                        }
                        e.target.classList.add('was-validated');
                    });
                }
            }
        };
    }

    getGenerateDocumentTemplate() {
        return {
            id: 'generateDocumentModal',
            title: '智能文档生成',
            size: 'modal-lg',
            content: `
                <form id="generateDocumentForm" class="needs-validation" novalidate>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="documentRepo" class="form-label">
                                    <i class="fas fa-repository text-primary me-2"></i>选择仓库
                                </label>
                                <select class="form-select" id="documentRepo" required>
                                    <option value="">请选择仓库...</option>
                                </select>
                                <div class="invalid-feedback">请选择一个仓库</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="documentType" class="form-label">
                                    <i class="fas fa-file-alt text-primary me-2"></i>文档类型
                                </label>
                                <select class="form-select" id="documentType" required>
                                    <option value="readme">📄 README文档</option>
                                    <option value="api">🔌 API文档</option>
                                    <option value="architecture">🏗️ 架构文档</option>
                                    <option value="user_guide">👥 用户指南</option>
                                    <option value="developer_guide">👨‍💻 开发指南</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="documentFormat" class="form-label">
                                    <i class="fas fa-file-export text-primary me-2"></i>输出格式
                                </label>
                                <select class="form-select" id="documentFormat" required>
                                    <option value="markdown">📝 Markdown</option>
                                    <option value="html">🌐 HTML</option>
                                    <option value="pdf">📄 PDF</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="analysisDepth" class="form-label">
                                    <i class="fas fa-search text-primary me-2"></i>分析深度
                                </label>
                                <select class="form-select" id="analysisDepth">
                                    <option value="basic">🔍 基础分析</option>
                                    <option value="detailed" selected>🔬 详细分析</option>
                                    <option value="comprehensive">🧪 全面分析</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="includeDiagrams" checked>
                            <label class="form-check-label" for="includeDiagrams">
                                <i class="fas fa-sitemap text-info me-2"></i>包含架构图和流程图
                            </label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="includeTroubleshooting" checked>
                            <label class="form-check-label" for="includeTroubleshooting">
                                <i class="fas fa-tools text-warning me-2"></i>包含故障排除指南
                            </label>
                        </div>
                    </div>
                </form>
                <div id="generateProgress" class="d-none">
                    <div class="progress mb-3">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%"></div>
                    </div>
                    <div class="text-center text-muted">
                        <i class="fas fa-robot me-2"></i>AI正在分析代码，请稍候...
                    </div>
                </div>
            `,
            buttons: [
                {
                    text: '取消',
                    class: 'btn-secondary',
                    dismiss: true
                },
                {
                    text: '<i class="fas fa-magic me-2"></i>开始生成',
                    class: 'btn-primary',
                    id: 'generateDocumentBtn'
                }
            ],
            handlers: {
                onShow: (modal, config) => {
                    // Load repository options
                    config.loadRepositories && config.loadRepositories(modal);
                },
                onShown: (modal, config) => {
                    // Setup form validation and submission
                    const form = modal.querySelector('#generateDocumentForm');
                    form.addEventListener('submit', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (e.target.checkValidity()) {
                            config.onGenerate && config.onGenerate(modal);
                        }
                        e.target.classList.add('was-validated');
                    });
                }
            }
        };
    }

    getTaskProgressTemplate() {
        return {
            id: 'taskProgressModal',
            title: '任务进度',
            size: 'modal-lg',
            content: `
                <div class="task-progress-container">
                    <div class="d-flex align-items-center mb-3">
                        <div class="spinner-border spinner-border-sm text-primary me-3" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <div>
                            <h6 class="mb-0" id="taskTitle">处理中...</h6>
                            <small class="text-muted" id="taskDescription">正在执行任务</small>
                        </div>
                    </div>
                    <div class="progress mb-3" style="height: 8px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%" id="taskProgressBar"></div>
                    </div>
                    <div class="row text-center mb-3">
                        <div class="col-4">
                            <div class="text-muted small">已完成</div>
                            <div class="fw-bold text-success" id="completedSteps">0</div>
                        </div>
                        <div class="col-4">
                            <div class="text-muted small">进行中</div>
                            <div class="fw-bold text-primary" id="currentStep">1</div>
                        </div>
                        <div class="col-4">
                            <div class="text-muted small">总步骤</div>
                            <div class="fw-bold text-info" id="totalSteps">-</div>
                        </div>
                    </div>
                    <div class="task-log bg-light p-3 rounded" style="max-height: 200px; overflow-y: auto;">
                        <div class="small text-muted" id="taskLog">
                            <div><i class="fas fa-play text-success"></i> 任务已开始...</div>
                        </div>
                    </div>
                </div>
            `,
            buttons: [
                {
                    text: '后台运行',
                    class: 'btn-secondary',
                    dismiss: true
                },
                {
                    text: '取消任务',
                    class: 'btn-outline-danger',
                    id: 'cancelTaskBtn'
                }
            ],
            handlers: {
                onShow: (modal, config) => {
                    // Initialize task monitoring
                    config.onInitialize && config.onInitialize(modal);
                }
            }
        };
    }

    getConfirmationTemplate() {
        return {
            id: 'confirmationModal',
            title: '确认操作',
            size: '',
            content: `
                <div class="text-center py-3">
                    <div class="mb-3">
                        <i class="fas fa-question-circle fa-3x text-warning"></i>
                    </div>
                    <h5 id="confirmationMessage">确定要执行此操作吗？</h5>
                    <p class="text-muted mb-0" id="confirmationDetails">此操作可能无法撤销</p>
                </div>
            `,
            buttons: [
                {
                    text: '取消',
                    class: 'btn-secondary',
                    dismiss: true
                },
                {
                    text: '确认',
                    class: 'btn-warning',
                    id: 'confirmBtn'
                }
            ]
        };
    }

    getErrorTemplate() {
        return {
            id: 'errorModal',
            title: '操作失败',
            size: '',
            content: `
                <div class="text-center py-3">
                    <div class="mb-3">
                        <i class="fas fa-exclamation-triangle fa-3x text-danger"></i>
                    </div>
                    <h5 class="text-danger" id="errorMessage">操作失败</h5>
                    <p class="text-muted mb-3" id="errorDetails">请稍后重试或联系管理员</p>
                    <div class="collapse" id="errorTechnicalDetails">
                        <div class="alert alert-light text-start">
                            <small class="font-monospace" id="errorStack"></small>
                        </div>
                    </div>
                    <button class="btn btn-link btn-sm" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#errorTechnicalDetails">
                        <i class="fas fa-chevron-down me-1"></i>技术详情
                    </button>
                </div>
            `,
            buttons: [
                {
                    text: '关闭',
                    class: 'btn-secondary',
                    dismiss: true
                },
                {
                    text: '重试',
                    class: 'btn-outline-primary',
                    id: 'retryBtn'
                }
            ]
        };
    }

    getSuccessTemplate() {
        return {
            id: 'successModal',
            title: '操作成功',
            size: '',
            content: `
                <div class="text-center py-3">
                    <div class="mb-3">
                        <i class="fas fa-check-circle fa-3x text-success"></i>
                    </div>
                    <h5 class="text-success" id="successMessage">操作完成</h5>
                    <p class="text-muted mb-0" id="successDetails">您的操作已成功完成</p>
                </div>
            `,
            buttons: [
                {
                    text: '完成',
                    class: 'btn-success',
                    dismiss: true
                }
            ]
        };
    }

    // =================================================================
    // MODAL LIFECYCLE MANAGEMENT
    // =================================================================

    createModal(templateName, config = {}) {
        const template = this.getTemplate(templateName);
        if (!template) {
            console.error(`❌ Cannot create modal: template ${templateName} not found`);
            return null;
        }

        // Generate unique modal ID if not provided
        const modalId = config.modalId || `${template.id}_${++this.modalCounter}`;
        
        // Clean up any existing modal with same ID
        this.cleanupModal(modalId);

        // Create modal HTML
        const modalHtml = this.generateModalHtml(template, modalId, config);
        
        // Insert into DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
            console.error(`❌ Failed to create modal element: ${modalId}`);
            return null;
        }

        // Register with Winston modal dispatcher
        if (window.modalDispatcher) {
            window.modalDispatcher.register(modalId, {
                onShow: (event) => template.handlers?.onShow?.(modalElement, config),
                onShown: (event) => template.handlers?.onShown?.(modalElement, config),
                onHide: (event) => template.handlers?.onHide?.(modalElement, config),
                onHidden: (event) => {
                    template.handlers?.onHidden?.(modalElement, config);
                    this.cleanupModal(modalId);
                }
            });
        }

        // Create Bootstrap modal instance
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: config.backdrop !== false,
            keyboard: config.keyboard !== false
        });

        // Store modal instance
        this.modalInstances.set(modalId, {
            element: modalElement,
            bootstrap: bsModal,
            template: templateName,
            config: config
        });

        console.log(`✅ Created Winston modal: ${modalId} (template: ${templateName})`);
        return {
            element: modalElement,
            bootstrap: bsModal,
            id: modalId
        };
    }

    generateModalHtml(template, modalId, config) {
        const modalSize = template.size ? ` ${template.size}` : '';
        const title = config.title || template.title;
        const content = config.content || template.content;

        let buttonsHtml = '';
        if (template.buttons && template.buttons.length > 0) {
            buttonsHtml = template.buttons.map(button => {
                const dismissAttr = button.dismiss ? ' data-bs-dismiss="modal"' : '';
                const idAttr = button.id ? ` id="${button.id}"` : '';
                return `<button type="button" class="btn ${button.class}"${idAttr}${dismissAttr}>${button.text}</button>`;
            }).join(' ');
        }

        return `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog${modalSize}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                        ${buttonsHtml ? `<div class="modal-footer">${buttonsHtml}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    showModal(templateName, config = {}) {
        const modal = this.createModal(templateName, config);
        if (modal) {
            this.activeModals.add(modal.id);
            modal.bootstrap.show();
            return modal;
        }
        return null;
    }

    hideModal(modalId) {
        const modalInstance = this.modalInstances.get(modalId);
        if (modalInstance) {
            modalInstance.bootstrap.hide();
        } else {
            console.warn(`⚠️ Modal instance not found: ${modalId}`);
        }
    }

    cleanupModal(modalId) {
        // Remove from active set
        this.activeModals.delete(modalId);

        // Get modal instance
        const modalInstance = this.modalInstances.get(modalId);
        if (modalInstance) {
            // Dispose Bootstrap modal
            modalInstance.bootstrap.dispose();
            
            // Remove DOM element
            modalInstance.element.remove();
            
            // Remove from instance map
            this.modalInstances.delete(modalId);
            
            console.log(`🗑️ Cleaned up modal: ${modalId}`);
        }

        // Cleanup orphaned modal with same ID in DOM
        const orphanedModal = document.getElementById(modalId);
        if (orphanedModal) {
            orphanedModal.remove();
            console.log(`🗑️ Removed orphaned modal: ${modalId}`);
        }
    }

    // =================================================================
    // PUBLIC API
    // =================================================================

    isModalActive(modalId) {
        return this.activeModals.has(modalId);
    }

    getActiveModals() {
        return Array.from(this.activeModals);
    }

    getModalInstance(modalId) {
        return this.modalInstances.get(modalId);
    }

    // Emergency cleanup - removes all modals
    cleanupAllModals() {
        console.log('🧹 Emergency modal cleanup initiated');
        
        // Hide and cleanup all tracked modals
        for (const modalId of this.modalInstances.keys()) {
            this.cleanupModal(modalId);
        }

        // Cleanup any orphaned modals in DOM
        document.querySelectorAll('.modal').forEach(modal => {
            if (modal.id && this.modalInstances.has(modal.id)) {
                return; // Already cleaned up
            }
            modal.remove();
        });

        // Remove orphaned backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.remove();
        });

        // Reset body state
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        console.log('✅ Emergency modal cleanup completed');
    }
}

// =================================================================
// GLOBAL INITIALIZATION
// =================================================================

// Initialize global instance
if (typeof window.WinstonModalTemplates === 'undefined') {
    window.WinstonModalTemplates = WinstonModalTemplates;
    window.winstonModalTemplates = new WinstonModalTemplates();
    
    // Integrate with error recovery system
    if (window.winstonErrorRecovery) {
        // Add modal cleanup to emergency recovery
        const originalCleanup = window.winstonErrorRecovery.fixModalIssues.bind(window.winstonErrorRecovery);
        window.winstonErrorRecovery.fixModalIssues = function() {
            originalCleanup();
            window.winstonModalTemplates.cleanupAllModals();
        };
    }
    
    console.log('🏗️ Winston Modal Template System globally initialized');
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WinstonModalTemplates };
}