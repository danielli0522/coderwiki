# API 分析报告: CoderWiki

## 1. 概览 (Overview)

### 1.1 模块核心职责

CoderWiki 是一个智能化的代码文档管理平台，核心定位为提供全生命周期的代码仓库分析、文档生成与管理服务。该系统通过集成多种 AI 服务（Claude、OpenAI），实现了从代码分析到智能文档生成的完整工作流，支持多用户租户管理，并提供实时任务监控与状态追踪能力。

### 1.2 接口概览

- **对外提供的 API (Providers):** 识别了 **124** 个核心 API 接口。
- **调用的外部 API (Consumers):** 识别了 **15** 个外部服务调用。

---

## 2. 对外提供的 API (Providers)

### 2.1 用户身份认证管理

**核心职责:** 提供用户注册、登录、登出、身份验证和用户资料管理功能

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| register | POST /api/auth/register | 用户注册 → 验证信息 → 创建账户 | 注册新用户账户 | username, email, password |
| login | POST /api/auth/login | 验证凭证 → 创建会话 → 返回Token | 用户登录认证 | username, password |
| logout | POST /api/auth/logout | 清除会话 → 更新状态 | 用户登出 | - |
| status | GET /api/auth/status | 检查会话 → 返回认证状态 | 获取当前认证状态 | - |
| get_profile | GET /api/auth/profile | 获取用户信息 → 返回资料 | 获取用户个人资料 | - |
| update_profile | PUT /api/auth/profile | 验证数据 → 更新资料 | 更新用户个人资料 | 更新字段(可选) |
| change_password | POST /api/auth/change-password | 验证旧密码 → 更新新密码 | 修改用户密码 | old_password, new_password |

### 2.2 代码仓库管理

**核心职责:** 提供代码仓库的增删改查、同步、分析和状态管理功能

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| get_repositories | GET /api/repositories | 查询仓库 → 分页筛选 → 返回列表 | 获取仓库列表 | page, per_page(可选) |
| add_repository | POST /api/repositories | 验证URL → 克隆仓库 → 创建记录 | 添加新仓库 | url, name(可选), description(可选) |
| get_repository | GET /api/repositories/{id} | 验证权限 → 查询仓库 → 返回详情 | 获取仓库详情 | repository_id |
| update_repository | PUT /api/repositories/{id} | 验证权限 → 更新信息 | 更新仓库信息 | repository_id, 更新字段 |
| delete_repository | DELETE /api/repositories/{id} | 验证权限 → 删除文件 → 清理记录 | 删除仓库 | repository_id |
| sync_repository | POST /api/repositories/{id}/sync | 拉取更新 → 同步代码 | 同步仓库代码 | repository_id |
| analyze_repository | POST /api/repositories/{id}/analyze | 扫描代码 → 生成分析 | 分析仓库代码 | repository_id |
| validate_repository_url | POST /api/repositories/validate-url | 验证格式 → 检查可访问性 | 验证仓库URL | url |
| get_repository_status | GET /api/repositories/{id}/status | 查询状态 → 返回详情 | 获取仓库状态 | repository_id |
| reanalyze_repository | POST /api/repositories/{id}/reanalyze | 重新扫描 → 更新分析 | 重新分析仓库 | repository_id |
| update_github_stats | POST /api/repositories/{id}/github-stats | 获取GitHub数据 → 更新统计 | 更新GitHub统计信息 | repository_id |
| bulk_delete_repositories | POST /api/repositories/bulk-delete | 批量验证 → 批量删除 | 批量删除仓库 | repository_ids[] |
| bulk_analyze_repositories | POST /api/repositories/bulk-analyze | 批量扫描 → 批量分析 | 批量分析仓库 | repository_ids[] |
| generate_document | POST /api/repositories/{id}/generate | 创建任务 → 生成文档 | 为仓库生成文档 | repository_id, document_type |
| get_repository_statistics | GET /api/repositories/statistics | 统计数据 → 返回报表 | 获取仓库统计信息 | - |
| get_enhanced_repository_statistics | GET /api/repositories/enhanced-statistics | 深度统计 → 返回详细报表 | 获取增强统计信息 | - |

### 2.3 文档生命周期管理

**核心职责:** 管理文档的创建、更新、删除、生成、下载和内容管理

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| get_documents | GET /api/documents/ | 查询文档 → 分页过滤 → 返回列表 | 获取文档列表 | page, limit(可选) |
| create_document | POST /api/documents/ | 验证数据 → 创建文档 | 创建新文档 | title, repository_id, document_type |
| create_simple_document | POST /api/documents/simple | 创建默认仓库 → 创建文档 | 创建简单文档 | title, content |
| get_document | GET /api/documents/{id} | 验证权限 → 返回文档 | 获取文档详情 | document_id |
| update_document | PUT /api/documents/{id} | 验证权限 → 更新内容 | 更新文档 | document_id, 更新字段 |
| delete_document | DELETE /api/documents/{id} | 验证权限 → 删除文档 | 删除文档 | document_id |
| generate_document_content | POST /api/documents/{id}/generate | 创建任务 → AI生成内容 | 生成文档内容 | document_id |
| download_document | GET /api/documents/{id}/download | 获取内容 → 生成文件 | 下载文档 | document_id |
| get_document_content | GET /api/documents/{id}/content | 获取内容 → 返回文本 | 获取文档内容 | document_id |
| get_document_toc | GET /api/documents/{id}/toc | 解析内容 → 生成目录 | 获取文档目录 | document_id |
| get_recent_documents | GET /api/documents/recent | 查询近期 → 返回列表 | 获取最近文档 | limit(可选) |
| generate_ai_docs_for_repository | POST /api/documents/repository/{id}/generate-ai-docs | 调用AI → 生成技术文档 | 生成AI技术文档 | repository_id |
| get_ai_docs_status | GET /api/documents/ai-docs/status/{id} | 查询状态 → 返回进度 | 获取AI文档状态 | repository_id |

### 2.4 智能文档生成

**核心职责:** 集成Claude AI和BMAD系统，提供智能化的文档生成和管理功能

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| generate_smart_document | POST /api/smart-document/generate/{id} | 验证仓库 → Claude分析 → BMAD生成 | 生成智能文档 | repository_id, analysis_depth, doc_type |
| get_task_status | GET /api/smart-document/task/{id}/status | 查询任务 → 返回状态 | 获取任务状态 | task_id |
| get_bmad_agents_status | GET /api/smart-document/task/{id}/bmad-agents | 查询代理 → 返回状态 | 获取BMAD代理状态 | task_id |
| get_smart_documents | GET /api/smart-document/repository/{id}/documents | 查询文档 → 返回列表 | 获取智能文档列表 | repository_id |
| get_smart_document | GET /api/smart-document/document/{id} | 验证权限 → 返回文档 | 获取智能文档详情 | document_id |
| get_agent_executions | GET /api/smart-document/task/{id}/agent-executions | 查询执行 → 返回记录 | 获取代理执行记录 | task_id |

### 2.5 MkDocs 站点管理

**核心职责:** 提供MkDocs静态站点的构建、管理和服务功能

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| build_mkdocs_site | POST /api/mkdocs/repositories/{id}/build-site | 收集文档 → 构建站点 → 部署服务 | 构建MkDocs站点 | repository_id, user_id |
| get_site_status | GET /api/mkdocs/repositories/{id}/site-status | 检查站点 → 返回状态 | 获取站点状态 | repository_id |
| delete_mkdocs_site | DELETE /api/mkdocs/repositories/{id}/delete-site | 停止服务 → 清理文件 | 删除MkDocs站点 | repository_id |
| get_all_sites | GET /api/mkdocs/sites | 查询站点 → 返回列表 | 获取所有站点 | - |
| rebuild_mkdocs_site | POST /api/mkdocs/repositories/{id}/rebuild-site | 清理旧站点 → 重新构建 | 重建MkDocs站点 | repository_id |
| get_mkdocs_service_status | GET /api/mkdocs/status | 检查服务 → 返回状态 | 获取服务状态 | - |

### 2.6 任务管理与调度

**核心职责:** 管理异步任务的创建、执行、监控和调度

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| create_task | POST /api/tasks | 验证参数 → 创建任务 → 加入队列 | 创建新任务 | type, repository_id(可选) |
| get_tasks | GET /api/tasks | 查询任务 → 分页过滤 → 返回列表 | 获取任务列表 | page, per_page, status(可选) |
| get_task | GET /api/tasks/{id} | 验证权限 → 返回详情 | 获取任务详情 | task_id |
| delete_task | DELETE /api/tasks/{id} | 验证权限 → 删除任务 | 删除任务 | task_id |
| start_task | POST /api/tasks/{id}/start | 验证状态 → 启动执行 | 启动任务 | task_id |
| update_task_progress | POST /api/tasks/{id}/progress | 更新进度 → 记录日志 | 更新任务进度 | task_id, progress, message |
| get_task_progress | GET /api/tasks/{id}/progress | 查询进度 → 返回状态 | 获取任务进度 | task_id |
| get_pending_tasks | GET /api/tasks/pending | 查询待执行 → 返回列表 | 获取待执行任务 | - |
| get_running_tasks | GET /api/tasks/running | 查询执行中 → 返回列表 | 获取运行中任务 | - |
| cleanup_tasks | POST /api/tasks/cleanup | 清理过期 → 释放资源 | 清理过期任务 | days_old(可选) |
| get_task_statistics | GET /api/tasks/statistics | 统计任务 → 返回报表 | 获取任务统计 | - |
| get_task_performance | GET /api/tasks/performance | 分析性能 → 返回指标 | 获取任务性能 | - |
| get_queue_info | GET /api/tasks/queue/info | 查询队列 → 返回信息 | 获取队列信息 | - |
| get_task_logs | GET /api/tasks/{id}/logs | 查询日志 → 返回记录 | 获取任务日志 | task_id |
| retry_task | POST /api/tasks/{id}/retry | 重置状态 → 重新执行 | 重试任务 | task_id |
| cancel_task | POST /api/tasks/{id}/cancel | 停止执行 → 更新状态 | 取消任务 | task_id |
| create_batch_tasks | POST /api/tasks/batch | 批量创建 → 批量调度 | 批量创建任务 | tasks[] |
| export_tasks | GET /api/tasks/export | 查询任务 → 导出数据 | 导出任务数据 | format(csv/json) |

### 2.7 系统监控与管理

**核心职责:** 提供系统健康检查、性能监控、日志管理和配置管理

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| health_check | GET /api/system/health | 检查组件 → 返回状态 | 系统健康检查 | - |
| get_system_stats | GET /api/system/stats | 收集指标 → 返回统计 | 获取系统统计 | - |
| check_browser_compatibility | POST /api/system/browser-compatibility | 解析UA → 检查兼容性 | 检查浏览器兼容性 | user_agent |
| get_logs | GET /api/system/logs | 读取日志 → 分页返回 | 获取系统日志 | lines(可选), level(可选) |
| system_performance | GET/POST /api/system/performance | 监控性能 → 返回/记录指标 | 系统性能监控 | metrics(POST时) |
| get_config | GET /api/system/config | 读取配置 → 返回设置 | 获取系统配置 | - |

### 2.8 LLM配置管理

**核心职责:** 管理多个LLM提供商的配置，支持模型切换和参数调整

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| get_configs | GET /api/llm/configs | 查询配置 → 返回列表 | 获取LLM配置列表 | - |
| create_config | POST /api/llm/configs | 验证参数 → 创建配置 | 创建LLM配置 | provider, model_name, api_key |
| get_config | GET /api/llm/configs/{id} | 验证权限 → 返回配置 | 获取LLM配置详情 | config_id |
| update_config | PUT /api/llm/configs/{id} | 验证权限 → 更新配置 | 更新LLM配置 | config_id, 更新字段 |
| delete_config | DELETE /api/llm/configs/{id} | 验证权限 → 删除配置 | 删除LLM配置 | config_id |
| test_config | POST /api/llm/configs/{id}/test | 测试连接 → 返回结果 | 测试LLM配置 | config_id |
| set_default_config | POST /api/llm/configs/{id}/set-default | 更新默认 → 返回成功 | 设置默认配置 | config_id |

### 2.9 用户活动跟踪

**核心职责:** 记录和查询用户活动日志

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| get_activities | GET /api/activities | 查询活动 → 分页返回 | 获取用户活动记录 | page, per_page(可选) |

### 2.10 WebSocket实时通信

**核心职责:** 提供实时双向通信支持，用于推送任务状态更新

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| websocket_connect | WS /api/ws/ | 建立连接 → 维持通信 | WebSocket连接 | - |
| websocket_status | GET /api/ws/status | 查询状态 → 返回连接数 | 获取WebSocket状态 | - |

---

## 3. 调用的外部 API (Consumers)

### 3.1 AI服务集成

**核心职责:** 集成Claude AI和其他LLM服务进行智能文档生成和代码分析

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| ClaudeCodeClient | Anthropic Claude API | 发送请求 → AI处理 → 返回结果 | 调用Claude进行文档生成 | api_key, prompt, model |
| OpenAI API | OpenAI Completion API | 发送请求 → 模型推理 → 返回文本 | 调用OpenAI生成内容 | api_key, prompt, model |
| Local LLM API | Custom LLM Endpoint | 发送请求 → 本地处理 → 返回结果 | 调用本地部署的LLM | endpoint, prompt, parameters |

### 3.2 Git服务集成

**核心职责:** 与GitHub/GitLab等Git服务集成，获取仓库信息和统计数据

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| GitHub API | api.github.com/repos/* | 认证 → 请求数据 → 解析响应 | 获取GitHub仓库信息 | token, owner, repo |
| Git Clone | git clone command | 验证URL → 克隆仓库 → 存储本地 | 克隆Git仓库到本地 | repository_url |
| Git Pull | git pull command | 检查更新 → 拉取代码 → 合并更改 | 同步仓库最新代码 | repository_path |

### 3.3 MCP服务集成

**核心职责:** 集成Model Context Protocol服务进行文档处理

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| MCP Service API | localhost:8080/api/mcp | 构建请求 → MCP处理 → 返回结果 | 调用MCP服务生成文档 | method, params |
| MCP Health Check | localhost:8080/health | 发送请求 → 检查状态 | 检查MCP服务健康状态 | - |
| MCP Info | localhost:8080/info | 发送请求 → 获取信息 | 获取MCP服务信息 | - |

### 3.4 数据存储服务

**核心职责:** 与MySQL数据库和Redis缓存服务进行数据交互

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| MySQL Database | mysql://localhost:3306 | 连接 → 执行SQL → 返回结果 | 持久化数据存储 | connection_string, query |
| Redis Cache | redis://localhost:6379 | 连接 → 执行命令 → 返回数据 | 缓存和会话管理 | key, value, ttl |

### 3.5 Puppeteer服务集成

**核心职责:** 集成Puppeteer服务进行网页渲染和截图

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| Puppeteer Navigate | /api/puppeteer/navigate | 打开页面 → 渲染内容 | 导航到指定URL | url, wait_for |
| Puppeteer Screenshot | /api/puppeteer/screenshot | 渲染页面 → 生成截图 | 生成页面截图 | url, viewport |

---

## 4. 系统架构总结

### 4.1 技术栈
- **后端框架:** Flask + SQLAlchemy
- **数据库:** MySQL
- **缓存:** Redis
- **AI集成:** Claude Code SDK + Anthropic API + 自定义LLM支持
- **文档生成:** MkDocs + Markdown
- **实时通信:** WebSocket
- **任务队列:** 自定义异步任务管理系统

### 4.2 核心能力
1. **完整的用户管理系统** - 支持注册、登录、权限控制
2. **强大的仓库管理** - 支持Git仓库克隆、同步、分析
3. **智能文档生成** - 集成多个AI服务自动生成技术文档
4. **MkDocs站点服务** - 自动构建和部署文档站点
5. **实时任务监控** - WebSocket推送任务进度更新
6. **多LLM支持** - 灵活配置和切换不同的AI模型
7. **批量操作支持** - 支持仓库和任务的批量处理

### 4.3 安全特性
- 基于Flask-Login的用户认证
- API级别的权限控制
- 敏感信息加密存储
- 请求参数验证和清理

### 4.4 扩展性设计
- 模块化的服务架构
- 可插拔的LLM配置
- 灵活的任务调度系统
- 支持水平扩展的设计