# MCP (Model Context Protocol) 集成说明

## 概述

本项目已集成 MCP 服务支持，可以通过 doc-generator-tool 的 MCP 服务生成文档，而不需要直接调用大模型 API。

## 配置

### 环境变量

在 `backend/config.py` 中添加了以下 MCP 相关配置：

```python
# MCP服务配置
MCP_SERVER_URL = os.environ.get('MCP_SERVER_URL', 'http://localhost')
MCP_SERVER_PORT = int(os.environ.get('MCP_SERVER_PORT', '3000'))
MCP_ENABLED = os.environ.get('MCP_ENABLED', 'true').lower() == 'true'
```

### 环境变量设置

```bash
# MCP服务配置
export MCP_SERVER_URL=http://localhost
export MCP_SERVER_PORT=3000
export MCP_ENABLED=true
```

## 服务架构

### MCPService 类

位置：`backend/app/services/mcp_service.py`

主要功能：

- 与 doc-generator-tool 的 MCP 服务通信
- 处理文档生成请求
- 错误处理和重试机制
- 健康检查和状态监控

### DocumentGenerator 类修改

位置：`backend/app/services/document_generator.py`

主要修改：

- 添加 MCP 服务支持
- 根据配置自动选择使用 MCP 服务或直接 LLM API
- 保持向后兼容性

## API 端点

### 新增的 API 端点

1. **获取 MCP 服务状态**

   ```
   GET /api/documents/mcp/status
   ```

2. **获取支持的文档类型**

   ```
   GET /api/documents/mcp/doc-types
   ```

3. **生成文档（支持 MCP）**
   ```
   POST /api/documents/generate
   ```

### 请求示例

#### 生成文档

```json
{
  "repository_id": 1,
  "llm_config_id": 1,
  "doc_type": "overview",
  "doc_title": "项目概览文档"
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
    "title": "项目概览文档",
    "content": "# 项目概览...",
    "status": "published"
  },
  "generation_stats": {
    "generation_time": 45.2,
    "cost_estimate": 0.05,
    "tokens_used": 1500
  }
}
```

## 使用方式

### 1. 启用 MCP 服务

确保环境变量设置正确：

```bash
export MCP_ENABLED=true
export MCP_SERVER_URL=http://localhost
export MCP_SERVER_PORT=3000
```

### 2. 启动 doc-generator-tool MCP 服务

确保 doc-generator-tool 的 MCP 服务正在运行在指定端口。

### 3. 检查服务状态

```bash
curl -X GET http://localhost:5000/api/documents/mcp/status
```

### 4. 生成文档

```bash
curl -X POST http://localhost:5000/api/documents/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "repository_id": 1,
    "llm_config_id": 1,
    "doc_type": "overview",
    "doc_title": "项目概览文档"
  }'
```

## 故障排除

### 1. MCP 服务连接失败

检查：

- MCP 服务是否正在运行
- 端口配置是否正确
- 网络连接是否正常

### 2. 文档生成失败

检查：

- LLM 配置是否正确
- 仓库路径是否存在
- MCP 服务日志

### 3. 回退到直接 LLM API

如果 MCP 服务不可用，系统会自动回退到直接调用 LLM API：

```python
# 禁用MCP服务
export MCP_ENABLED=false
```

## 开发说明

### 添加新的文档类型

1. 在 MCP 服务中添加新的文档类型支持
2. 更新 `get_available_doc_types()` 方法
3. 测试新的文档类型生成

### 自定义 MCP 请求参数

在 `_call_mcp_for_documentation()` 方法中可以添加自定义参数：

```python
additional_params = {
    'max_tokens': llm_config.max_tokens,
    'temperature': llm_config.temperature,
    'language': 'zh-CN',
    'format': 'markdown',
    'custom_param': 'value'  # 添加自定义参数
}
```

### 错误处理

MCP 服务包含完整的错误处理机制：

- 网络超时处理
- 重试机制
- 详细的错误信息
- 优雅降级

## 性能优化

### 1. 超时设置

MCP 请求超时设置为 5 分钟，适合文档生成任务：

```python
self.timeout = 300  # 5分钟
```

### 2. 重试机制

默认重试 3 次，每次间隔 2 秒：

```python
self.max_retries = 3
self.retry_delay = 2
```

### 3. 连接池

使用 requests 库的连接池优化性能。

## 监控和日志

### 日志记录

所有 MCP 相关操作都会记录详细日志：

- 请求/响应日志
- 错误日志
- 性能指标

### 健康检查

定期检查 MCP 服务状态：

```bash
curl -X GET http://localhost:5000/api/documents/mcp/status
```

## 安全考虑

1. **API 密钥管理**：LLM 配置中的 API 密钥通过安全方式传递
2. **请求验证**：所有 API 请求都需要用户认证
3. **错误信息**：避免在错误响应中泄露敏感信息
4. **超时控制**：防止长时间运行的请求

## 未来扩展

1. **多 MCP 服务支持**：支持多个 MCP 服务实例
2. **负载均衡**：在多个 MCP 服务之间分配负载
3. **缓存机制**：缓存生成的文档内容
4. **异步处理**：支持异步文档生成
5. **实时进度**：提供实时生成进度更新
