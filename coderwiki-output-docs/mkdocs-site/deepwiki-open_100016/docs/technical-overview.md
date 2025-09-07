基于深入的代码库分析，我现在为您提供详细的技术概览文档：

## 项目概述

- **项目名称**: CodeWiki (智能代码文档管理系统)
- **技术特点**: 
  - Flask单体架构 + AI增强文档生成
  - Claude Code SDK深度集成
  - BMAD多智能体协作系统
  - 实时WebSocket通信支持
- **主要功能模块**: 
  - 代码仓库管理
  - AI驱动的智能文档生成
  - 多智能体协作文档分析
  - MkDocs静态站点生成
  - 实时任务监控与管理

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                               │
│  Bootstrap 5 + Vanilla JS + Jinja2模板 + WebSocket客户端     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                      API网关层                               │
│         Flask路由 + 认证中间件 + CORS配置                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      业务服务层                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ Repository   │ │ Document     │ │ Claude Code  │        │
│  │ Service      │ │ Generation   │ │ Service      │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ BMAD         │ │ MkDocs       │ │ Task         │        │
│  │ Orchestrator │ │ Service      │ │ Service      │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    数据访问层                                │
│         SQLAlchemy ORM + Redis缓存 + 文件系统                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 数据存储层                                   │
│    MySQL/SQLite + Redis + 本地文件存储                       │
└─────────────────────────────────────────────────────────────┘
```

- **层次结构**: 
  - 展示层：响应式Web界面
  - API层：RESTful接口 + WebSocket
  - 服务层：业务逻辑封装
  - 数据层：ORM映射与缓存
  
- **组件关系**: 
  - 松耦合的服务架构
  - 事件驱动的任务处理
  - 智能体协作的文档生成

## 技术栈详情

### 后端技术栈
- **Web框架**: Flask 2.3.3 + Flask-RESTful
- **数据库**: 
  - 开发环境: SQLite
  - 生产环境: MySQL 8.0+
- **核心库**:
  - SQLAlchemy 3.0.5 (ORM)
  - Flask-Login 0.6.3 (认证)
  - Celery 5.3.4 (任务队列)
  - Redis 5.0.1 (缓存/消息队列)
  - Anthropic Claude SDK 0.7.8
  - OpenAI SDK 1.3.0

### 前端技术栈
- **UI框架**: Bootstrap 5.3
- **样式方案**: 自定义CSS + Bootstrap主题
- **JavaScript库**: 
  - 原生ES6+ JavaScript
  - Font Awesome图标库
  - WebSocket客户端

### 数据库设计
- **数据模型**:
  ```sql
  Users (id, username, email, password_hash, created_at)
  Repositories (id, name, url, user_id, status, created_at)
  Documents (id, repository_id, title, content, type, created_at)
  Tasks (id, name, status, progress, result, created_at)
  BMADAgentExecutions (id, task_id, agent_name, status, result)
  ```
- **关系设计**: 用户→仓库→文档的层级关系

## 核心业务逻辑

- **服务层设计**:
  - `RepositoryService`: Git仓库克隆与管理
  - `DocumentGenerationService`: 文档生成工作流
  - `ClaudeCodeService`: Claude AI集成服务
  - `BMADOrchestrator`: 多智能体协调器
  - `MkDocsService`: 静态站点生成

- **API设计**: 
  - RESTful风格接口
  - JWT/Session双重认证
  - 统一错误处理机制

- **数据处理流程**:
  1. 仓库导入 → 代码分析 → 智能体处理 → 文档生成 → 站点发布

## 部署和运维

- **部署方式**: 
  - 单服务器部署
  - Nginx反向代理
  - 进程管理器(systemd/supervisor)

- **配置管理**:
  - 环境变量配置
  - 多环境配置文件
  - 功能开关管理

- **监控和日志**:
  - 结构化日志记录
  - 任务执行追踪
  - 健康检查接口

## 特色功能

### BMAD多智能体系统
- **智能体角色**:
  - Code Analyst (Alex): 代码扫描与模式识别
  - Architecture Analyst: 架构评估与优化建议
  - Flow Analyst (Jordan): 业务流程文档化
  - Problem Solver (Dr. Morgan): 问题诊断与解决方案
  - Doc Engineer (Maya): 文档组装与格式化

### Claude Code集成
- 深度集成Claude API进行智能文档生成
- 支持上下文感知的代码解释
- 自动生成技术文档和API说明

## 优化建议

1. **性能优化**:
   - 实施更细粒度的缓存策略
   - 考虑引入CDN加速静态资源
   - 优化数据库查询性能

2. **架构改进**:
   - 考虑微服务化拆分(文档生成服务独立)
   - 引入消息队列解耦服务
   - 实施API网关统一管理

3. **安全加固**:
   - 增加API速率限制
   - 实施更严格的输入验证
   - 添加审计日志功能

4. **开发体验**:
   - 完善API文档(OpenAPI规范)
   - 增加更多自动化测试
   - 优化开发环境配置

这是一个设计良好、架构清晰的智能文档管理系统，成功将AI能力与传统Web开发模式结合，展现了良好的工程实践和创新思维。