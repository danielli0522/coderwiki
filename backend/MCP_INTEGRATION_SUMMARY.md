# MCP 集成修改总结

## 概述

已成功修改项目代码，支持通过 doc-generator-tool 的 MCP 服务生成文档，而不需要直接调用大模型 API。

## 修改的文件列表

### 1. 新增文件

- `backend/app/services/mcp_service.py` - MCP 服务类
- `backend/MCP_INTEGRATION.md` - MCP 集成详细说明文档
- `backend/test_mcp_integration.py` - MCP 集成测试脚本
- `backend/env.example` - 环境变量配置示例
- `backend/start_with_mcp.sh` - MCP 服务启动脚本
- `backend/MCP_INTEGRATION_SUMMARY.md` - 本总结文档

### 2. 修改的文件

#### `backend/config.py`

- 添加了 MCP 服务相关配置：
  - `MCP_SERVER_URL`
  - `MCP_SERVER_PORT`
  - `MCP_ENABLED`

#### `backend/app/services/document_generator.py`

- 添加了 MCP 服务导入
- 修改了`__init__`方法，支持 MCP 服务配置
- 添加了`_call_mcp_for_documentation`方法
- 修改了文档生成流程，支持 MCP 服务调用
- 添加了`check_mcp_service_status`和`get_available_doc_types`方法

#### `backend/app/api/document.py`

- 添加了 DocumentGenerator 导入
- 添加了 MCP 相关的 API 端点：
  - `GET /api/documents/mcp/status` - 获取 MCP 服务状态
  - `GET /api/documents/mcp/doc-types` - 获取支持的文档类型
  - `POST /api/documents/generate` - 生成文档（支持 MCP）

## 主要功能

### 1. MCP 服务集成

- 支持与 doc-generator-tool 的 MCP 服务通信
- 自动处理 LLM 配置传递
- 完整的错误处理和重试机制
- 健康检查和状态监控

### 2. 向后兼容性

- 保持原有的直接 LLM API 调用功能
- 通过环境变量控制是否使用 MCP 服务
- 如果 MCP 服务不可用，自动回退到直接 API 调用

### 3. 配置灵活性

- 支持通过环境变量配置 MCP 服务
- 支持动态启用/禁用 MCP 服务
- 支持自定义 MCP 服务器地址和端口

### 4. API 扩展

- 新增 MCP 服务状态检查 API
- 新增文档类型查询 API
- 扩展文档生成 API 支持 MCP

## 使用方法

### 1. 环境配置

```bash
# 启用MCP服务
export MCP_ENABLED=true
export MCP_SERVER_URL=http://localhost
export MCP_SERVER_PORT=3000

# 或者禁用MCP服务，使用直接API调用
export MCP_ENABLED=false
```

### 2. 启动服务

```bash
# 使用启动脚本
./backend/start_with_mcp.sh

# 或者手动启动
cd backend
source venv/bin/activate
python run.py
```

### 3. 测试集成

```bash
# 运行测试脚本
cd backend
python test_mcp_integration.py
```

### 4. API 调用示例

```bash
# 检查MCP服务状态
curl -X GET http://localhost:5000/api/documents/mcp/status

# 获取支持的文档类型
curl -X GET http://localhost:5000/api/documents/mcp/doc-types

# 生成文档
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

## 技术特点

### 1. 错误处理

- 网络超时处理（5 分钟超时）
- 自动重试机制（最多 3 次）
- 详细的错误信息返回
- 优雅降级处理

### 2. 性能优化

- 连接池管理
- 请求超时控制
- 重试间隔优化
- 异步处理支持

### 3. 安全性

- API 密钥安全传递
- 请求验证和认证
- 错误信息脱敏
- 超时控制防止长时间请求

### 4. 监控和日志

- 详细的请求/响应日志
- 性能指标记录
- 健康状态监控
- 错误追踪和调试

## 配置选项

### 环境变量

| 变量名          | 默认值           | 说明              |
| --------------- | ---------------- | ----------------- |
| MCP_ENABLED     | true             | 是否启用 MCP 服务 |
| MCP_SERVER_URL  | http://localhost | MCP 服务器地址    |
| MCP_SERVER_PORT | 3000             | MCP 服务器端口    |

### 代码配置

- 超时时间：300 秒（5 分钟）
- 重试次数：3 次
- 重试间隔：2 秒
- 最大令牌数：根据文档类型自动调整

## 故障排除

### 常见问题

1. **MCP 服务连接失败**

   - 检查 MCP 服务是否运行
   - 验证端口配置
   - 检查网络连接

2. **文档生成失败**

   - 检查 LLM 配置
   - 验证仓库路径
   - 查看 MCP 服务日志

3. **性能问题**
   - 调整超时设置
   - 优化重试策略
   - 检查网络延迟

### 调试方法

1. 运行测试脚本：`python test_mcp_integration.py`
2. 检查日志文件
3. 使用健康检查 API
4. 查看 MCP 服务状态

## 未来扩展

### 计划功能

1. 多 MCP 服务支持
2. 负载均衡
3. 缓存机制
4. 实时进度更新
5. 更多文档类型支持

### 性能优化

1. 连接池优化
2. 请求批处理
3. 结果缓存
4. 异步处理改进

## 总结

通过这次修改，项目成功集成了 MCP 服务支持，实现了：

1. ✅ 通过 doc-generator-tool 的 MCP 服务生成文档
2. ✅ 保持向后兼容性
3. ✅ 完整的错误处理和重试机制
4. ✅ 灵活的配置选项
5. ✅ 详细的监控和日志
6. ✅ 安全的 API 密钥管理
7. ✅ 优雅的降级处理

项目现在可以根据配置灵活选择使用 MCP 服务或直接 LLM API 调用，为用户提供了更多的选择和更好的可靠性。
