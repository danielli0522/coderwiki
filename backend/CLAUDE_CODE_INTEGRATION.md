# Claude Code 集成说明

## 概述

本项目已集成Claude Code SDK支持，可以通过Claude Code的编排引擎和指定的sub agent生成技术设计文档，而不需要直接调用大模型API。

## 集成流程

### 1. 智能文档管理工具生成技术设计文档
- 用户通过系统界面选择要生成文档的代码仓库
- 选择文档类型（技术设计、API文档、架构文档等）
- 系统调用Claude Code服务

### 2. 调用Claude Code SDK
- 使用Python版本的Claude Code SDK
- 触发Claude Code的编排引擎
- 传递必要的参数和配置

### 3. Claude Code编排引擎处理
- 使用指定的sub agent: `/bmad//bmadDocs:teams:docs-generation-team`
- 完整文件路径: `/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/`
- 生成高质量的技术设计文档

## 配置

### 环境变量

在 `backend/config.py` 中添加了以下Claude Code相关配置：

```python
# Claude Code服务配置
CLAUDE_CODE_ENABLED = os.environ.get('CLAUDE_CODE_ENABLED', 'false').lower() == 'true'
CLAUDE_CODE_PATH = os.environ.get('CLAUDE_CODE_PATH', '/usr/local/bin/claude-code')
BMAD_DOCS_PATH = os.environ.get('BMAD_DOCS_PATH', '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/')
```

### 环境变量设置

```bash
# Claude Code服务配置
export CLAUDE_CODE_ENABLED=true
export CLAUDE_CODE_PATH=/usr/local/bin/claude-code
export BMAD_DOCS_PATH=/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/
```

## 服务架构

### ClaudeCodeService 类

位置：`backend/app/services/claude_code_service.py`

主要功能：
- 与Claude Code SDK通信
- 调用指定的sub agent
- 处理文档生成请求
- 错误处理和重试机制
- 健康检查和状态监控

### DocumentGenerator 类修改

位置：`backend/app/services/document_generator.py`

主要修改：
- 添加Claude Code服务支持
- 根据配置自动选择使用Claude Code、MCP服务或直接LLM API
- 保持向后兼容性

## API端点

### 新增的API端点

1. **获取Claude Code服务状态**
   ```
   GET /api/documents/claude-code/status
   ```

2. **获取支持的文档类型**
   ```
   GET /api/documents/doc-types
   ```

3. **生成文档（支持Claude Code）**
   ```
   POST /api/documents/generate
   ```

### 请求示例

#### 生成文档
```json
{
  "repository_id": 1,
  "llm_config_id": 1,
  "doc_type": "technical_design",
  "doc_title": "技术设计文档"
}
```

#### 响应示例
```json
{
  "success": true,
  "document_id": 123,
  "task_id": 456,
  "document": {
    "id": 123,
    "title": "技术设计文档",
    "content": "# 技术设计文档...",
    "status": "published"
  },
  "generation_stats": {
    "generation_time": 45.2,
    "cost_estimate": 0.0,
    "tokens_used": 0
  }
}
```

## 使用方式

### 1. 启用Claude Code服务

确保环境变量设置正确：
```bash
export CLAUDE_CODE_ENABLED=true
export CLAUDE_CODE_PATH=/usr/local/bin/claude-code
export BMAD_DOCS_PATH=/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/
```

### 2. 安装Claude Code SDK

确保Claude Code SDK已正确安装：
```bash
# 检查Claude Code SDK是否可用
claude-code --version
```

### 3. 检查BMAD文档生成器

确保BMAD文档生成器路径正确：
```bash
ls -la /Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/
```

### 4. 检查服务状态

```bash
curl -X GET http://localhost:5000/api/documents/claude-code/status
```

### 5. 生成文档

```bash
curl -X POST http://localhost:5000/api/documents/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "repository_id": 1,
    "llm_config_id": 1,
    "doc_type": "technical_design",
    "doc_title": "技术设计文档"
  }'
```

## 支持的文档类型

Claude Code服务支持以下文档类型：

- `technical_design` - 技术设计文档
- `api_docs` - API文档
- `architecture` - 架构文档
- `database_design` - 数据库设计文档
- `deployment_guide` - 部署指南
- `user_manual` - 用户手册
- `developer_guide` - 开发者指南
- `system_overview` - 系统概览

## 故障排除

### 1. Claude Code SDK连接失败

检查：
- Claude Code SDK是否已安装
- 路径配置是否正确
- 权限是否足够

### 2. BMAD文档生成器路径错误

检查：
- BMAD文档生成器路径是否存在
- 关键文件是否完整
- 权限是否正确

### 3. 文档生成失败

检查：
- 仓库路径是否正确
- Claude Code服务状态
- 系统日志

### 4. 回退到其他服务

如果Claude Code服务不可用，系统会自动回退到MCP服务或直接LLM API：

```bash
# 禁用Claude Code服务
export CLAUDE_CODE_ENABLED=false
```

## 开发说明

### 添加新的文档类型

1. 在BMAD文档生成器中添加新的文档类型支持
2. 更新 `get_supported_doc_types()` 方法
3. 测试新的文档类型生成

### 自定义Claude Code请求参数

在 `_call_claude_code_for_documentation()` 方法中可以添加自定义参数：

```python
additional_params = {
    'language': 'zh-CN',
    'format': 'markdown',
    'detailed': True,
    'include_examples': True,
    'custom_param': 'value'  # 添加自定义参数
}
```

### 错误处理

Claude Code服务包含完整的错误处理机制：
- 命令执行超时处理
- 重试机制
- 详细的错误信息
- 优雅降级

## 性能优化

### 1. 超时设置

Claude Code请求超时设置为10分钟，适合文档生成任务：
```python
self.timeout = 600  # 10分钟
```

### 2. 重试机制

默认重试3次，每次间隔5秒：
```python
self.max_retries = 3
self.retry_delay = 5
```

### 3. 临时文件管理

使用临时文件处理输出，自动清理：
```python
with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
    temp_output = temp_file.name
```

## 监控和日志

### 日志记录

所有Claude Code相关操作都会记录详细日志：
- 命令执行日志
- 错误日志
- 性能指标

### 健康检查

定期检查Claude Code服务状态：
```bash
curl -X GET http://localhost:5000/api/documents/claude-code/status
```

## 安全考虑

1. **路径验证**：验证所有输入路径的安全性
2. **命令执行**：安全的子进程执行
3. **临时文件**：自动清理临时文件
4. **错误信息**：避免在错误响应中泄露敏感信息

## 未来扩展

1. **多Claude Code实例支持**：支持多个Claude Code实例
2. **负载均衡**：在多个Claude Code实例之间分配负载
3. **缓存机制**：缓存生成的文档内容
4. **异步处理**：支持异步文档生成
5. **实时进度**：提供实时生成进度更新
