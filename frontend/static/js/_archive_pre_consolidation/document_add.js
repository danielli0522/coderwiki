/**
 * Document Add Page JavaScript
 * Handles document creation, AI generation, and template selection
 */

class DocumentAddManager {
    constructor() {
        this.initializeEventListeners();
        this.initializeTemplates();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Manual document form submission
        const manualForm = document.getElementById('manualDocumentForm');
        if (manualForm) {
            manualForm.addEventListener('submit', this.handleManualSubmit.bind(this));
        }

        // AI document form submission
        const aiForm = document.getElementById('aiDocumentForm');
        if (aiForm) {
            aiForm.addEventListener('submit', this.handleAISubmit.bind(this));
        }

        // Template card clicks
        const templateCards = document.querySelectorAll('.template-card');
        templateCards.forEach(card => {
            card.addEventListener('click', this.handleTemplateClick.bind(this));
        });

        // Form validation
        this.setupFormValidation();
    }

    /**
     * Initialize template data
     */
    initializeTemplates() {
        this.templates = {
            'api-doc': {
                title: 'API 文档',
                content: `# API 文档

## 概述
简要描述 API 的功能和用途。

## 认证
描述认证方式和获取访问令牌的方法。

## 端点

### 1. 获取数据
\`\`\`http
GET /api/data
\`\`\`

**参数：**
- \`page\` (可选): 页码，默认为 1
- \`limit\` (可选): 每页数量，默认为 20

**响应：**
\`\`\`json
{
  "success": true,
  "data": [],
  "total": 0,
  "page": 1,
  "limit": 20
}
\`\`\`

### 2. 创建数据
\`\`\`http
POST /api/data
\`\`\`

**请求体：**
\`\`\`json
{
  "name": "示例名称",
  "description": "示例描述"
}
\`\`\`

## 错误码
| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 示例代码

### JavaScript
\`\`\`javascript
fetch('/api/data', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
\`\`\`

### Python
\`\`\`python
import requests

response = requests.get('/api/data', headers={
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
})
data = response.json()
print(data)
\`\`\`
`,
                tags: 'API,技术文档,接口'
            },
            'tutorial': {
                title: '教程指南',
                content: `# 教程指南

## 简介
简要介绍本教程的目标和适用人群。

## 前置要求
- 列出学习本教程前需要掌握的知识
- 需要安装的软件和工具

## 步骤

### 第一步：环境准备
1. 安装必要的软件
2. 配置开发环境
3. 验证安装

### 第二步：基础操作
1. 创建项目
2. 配置设置
3. 运行示例

### 第三步：进阶功能
1. 高级配置
2. 自定义设置
3. 性能优化

## 注意事项
- 重要提醒和警告
- 常见问题解决方案
- 最佳实践建议

## 总结
总结学习成果和下一步建议。

## 参考资料
- 相关文档链接
- 推荐阅读材料
- 社区资源
`,
                tags: '教程,指南,学习'
            },
            'design-doc': {
                title: '设计文档',
                content: `# 设计文档

## 项目概述
### 背景
描述项目的背景和动机。

### 目标
明确项目的目标和期望成果。

### 范围
定义项目的范围和边界。

## 系统架构

### 整体架构
描述系统的整体架构设计。

### 技术栈
- 前端技术
- 后端技术
- 数据库
- 部署方案

### 模块设计
详细描述各个模块的设计。

## 数据模型

### 实体关系图
描述数据实体之间的关系。

### 数据库设计
- 表结构设计
- 索引设计
- 约束设计

## 接口设计

### API 接口
定义系统对外提供的接口。

### 内部接口
定义模块间的接口规范。

## 安全设计

### 认证授权
描述用户认证和权限控制方案。

### 数据安全
描述数据保护措施。

## 性能设计

### 性能指标
定义系统的性能要求。

### 优化策略
描述性能优化方案。

## 部署方案

### 环境要求
描述部署环境的要求。

### 部署流程
详细描述部署步骤。

## 测试策略

### 测试计划
描述测试策略和计划。

### 测试用例
提供关键测试用例。

## 风险评估

### 技术风险
识别技术风险点。

### 应对措施
描述风险应对方案。

## 时间计划

### 里程碑
定义项目里程碑。

### 时间安排
详细的时间计划。
`,
                tags: '设计,架构,技术文档'
            },
            'user-guide': {
                title: '用户手册',
                content: `# 用户手册

## 产品介绍
### 产品概述
简要介绍产品功能和特点。

### 适用场景
描述产品的适用场景。

### 产品优势
列出产品的主要优势。

## 快速开始

### 安装指南
1. 系统要求
2. 下载安装
3. 首次配置

### 基本操作
1. 登录系统
2. 界面介绍
3. 基本功能

## 功能详解

### 核心功能
详细描述核心功能的使用方法。

### 高级功能
介绍高级功能的使用技巧。

### 设置选项
说明各种设置选项的含义。

## 操作指南

### 常见操作
提供常见操作的详细步骤。

### 快捷键
列出常用快捷键。

### 操作技巧
分享实用的操作技巧。

## 常见问题

### FAQ
常见问题及解答。

### 故障排除
常见故障的解决方法。

### 联系支持
获取技术支持的方式。

## 更新日志

### 版本历史
记录各版本的更新内容。

### 新功能介绍
介绍新版本的新功能。

## 附录

### 术语表
解释专业术语。

### 参考链接
相关资源链接。
`,
                tags: '用户手册,使用指南,帮助'
            }
        };
    }

    /**
     * Handle manual document form submission
     */
    async handleManualSubmit(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            content: formData.get('content'),
            tags: formData.get('tags'),
            visibility: formData.get('visibility')
        };

        try {
            const response = await this.submitDocument(data);
            this.showSuccessModal(response);
        } catch (error) {
            this.showError('创建文档失败: ' + error.message);
        }
    }

    /**
     * Handle AI document form submission
     */
    async handleAISubmit(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            title: formData.get('aiTitle'),
            prompt: formData.get('aiPrompt'),
            document_type: formData.get('documentType'),
            tags: formData.get('aiTags'),
            visibility: formData.get('aiVisibility')
        };

        try {
            this.showGenerationProgress();
            const response = await this.generateAIDocument(data);
            this.hideGenerationProgress();
            this.showSuccessModal(response);
        } catch (error) {
            this.hideGenerationProgress();
            this.showError('AI 生成文档失败: ' + error.message);
        }
    }

    /**
     * Handle template card click
     */
    handleTemplateClick(event) {
        const card = event.currentTarget;
        const templateKey = card.dataset.template;
        const template = this.templates[templateKey];

        if (template) {
            // Fill the manual form with template data
            document.getElementById('title').value = template.title;
            document.getElementById('content').value = template.content;
            document.getElementById('tags').value = template.tags;

            // Scroll to manual form
            document.getElementById('manualDocumentForm').scrollIntoView({
                behavior: 'smooth'
            });

            // Show success message
            this.showSuccess('模板已加载到手动创建表单中');
        }
    }

    /**
     * Submit document to server
     */
    async submitDocument(data) {
        const response = await fetch('/api/documents/simple', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '创建文档失败');
        }

        return await response.json();
    }

    /**
     * Generate AI document
     */
    async generateAIDocument(data) {
        // For now, we'll simulate AI generation by creating a simple document
        // In a real implementation, this would call an AI service
        const mockContent = `# ${data.title}

## 概述
这是基于您的提示生成的文档内容。

## 生成提示
${data.prompt}

## 文档类型
${data.document_type}

## 内容
这是一个示例文档，展示了AI生成的内容结构。

### 主要特点
- 自动生成的内容
- 结构化的格式
- 易于阅读和理解

### 使用说明
1. 查看生成的内容
2. 根据需要编辑
3. 保存文档

## 总结
这是一个AI生成的文档模板，您可以根据实际需求进行修改和完善。

---
*生成时间: ${new Date().toLocaleString()}*
*文档类型: ${data.document_type}*
`;

        // Create a simple document with the generated content
        const documentData = {
            title: data.title,
            content: mockContent,
            description: `AI生成的文档 - ${data.document_type}`,
            document_type: data.document_type
        };

        return await this.submitDocument(documentData);
    }

    /**
     * Show generation progress
     */
    showGenerationProgress() {
        const progressDiv = document.getElementById('generationProgress');
        const progressBar = progressDiv.querySelector('.progress-bar');
        const progressText = document.getElementById('progressText');
        const generateBtn = document.getElementById('generateBtn');

        progressDiv.style.display = 'block';
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';

        // Simulate progress
        let progress = 0;
        this.progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;

            progressBar.style.width = progress + '%';

            if (progress < 30) {
                progressText.textContent = '正在分析需求...';
            } else if (progress < 60) {
                progressText.textContent = '正在生成内容...';
            } else {
                progressText.textContent = '正在优化格式...';
            }
        }, 500);
    }

    /**
     * Hide generation progress
     */
    hideGenerationProgress() {
        const progressDiv = document.getElementById('generationProgress');
        const progressBar = progressDiv.querySelector('.progress-bar');
        const generateBtn = document.getElementById('generateBtn');

        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        progressBar.style.width = '100%';
        document.getElementById('progressText').textContent = '生成完成！';

        setTimeout(() => {
            progressDiv.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> 生成文档';
        }, 1000);
    }

    /**
     * Show success modal
     */
    showSuccessModal(response) {
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        const documentInfo = document.getElementById('documentInfo');
        const viewDocumentBtn = document.getElementById('viewDocumentBtn');

        documentInfo.innerHTML = `
            <div class="alert alert-success">
                <strong>文档标题:</strong> ${response.title}<br>
                <strong>创建时间:</strong> ${new Date(response.created_at).toLocaleString()}<br>
                <strong>文档ID:</strong> ${response.id}
            </div>
        `;

        viewDocumentBtn.href = `/documents/${response.id}/view`;

        modal.show();
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        // Use Bootstrap toast or alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }

    /**
     * Show error message
     */
    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        // Real-time validation for title
        const titleInput = document.getElementById('title');
        if (titleInput) {
            titleInput.addEventListener('input', () => {
                if (titleInput.value.length < 3) {
                    titleInput.classList.add('is-invalid');
                } else {
                    titleInput.classList.remove('is-invalid');
                }
            });
        }

        // Real-time validation for content
        const contentInput = document.getElementById('content');
        if (contentInput) {
            contentInput.addEventListener('input', () => {
                if (contentInput.value.length < 10) {
                    contentInput.classList.add('is-invalid');
                } else {
                    contentInput.classList.remove('is-invalid');
                }
            });
        }
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentAddManager();
});
