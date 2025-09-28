# CoderWiki系统架构概览

## 系统组件图
```
[Web Frontend] ←→ [Flask Backend] ←→ [Analysis Engine] ←→ [AI Services]
       ↓                ↓                    ↓              ↓
   [Bootstrap UI]   [SQLAlchemy]    [Git Service]    [OpenAI/Claude]
       ↓                ↓                    ↓              ↓
   [Static Files]   [Database]      [File System]    [API Clients]
```

## 核心组件职责

### Web Frontend (frontend/)
- **技术栈**: Bootstrap 5 + 原生JavaScript + Jinja2模板
- **职责**: 用户界面和交互逻辑
- **关键模块**:
  - `templates/`: Jinja2页面模板
  - `static/`: CSS、JS、图片资源

### Flask Backend (backend/app/)
- **技术栈**: Python 3.8+ + Flask 2.3.3 + SQLAlchemy
- **职责**: API服务和业务逻辑
- **分层架构**:
  - `api/`: REST API端点层 (认证、仓库管理、文档生成)
  - `services/`: 业务逻辑层 (仓库服务、分析服务)
  - `models/`: 数据模型层 (SQLAlchemy实体)
  - `utils/`: 工具层 (代码分析引擎、AI客户端、Git服务)
  - `routes/`: 页面路由层

### Analysis Engine (backend/app/utils/)
- **核心模块**: `code_analysis_engine.py`
- **职责**: 代码分析和处理
- **功能**: 多语言代码扫描、结构提取、质量分析

### AI Services Integration
- **核心模块**: `llm_client.py`
- **支持模型**: OpenAI GPT-4 + Anthropic Claude
- **职责**: 智能文档生成和代码理解

### BMAD文档生成器 (bmad-docs-generator/)
- **职责**: 专门的智能文档生成系统
- **输出**: `coderwiki-output-docs/` 目录

## 数据流向
1. **仓库导入**: 用户通过Frontend上传/配置代码仓库
2. **代码分析**: Analysis Engine扫描和分析代码结构
3. **AI处理**: AI Services基于分析结果生成文档
4. **结果展示**: Frontend展示分析结果和生成的文档

## 关键设计决策
- **分层架构**: 确保职责分离 (Models → Services → API → Frontend)
- **事件驱动**: 异步任务处理分析和文档生成
- **插件化AI**: 支持多种AI模型集成
- **SQLAlchemy ORM**: 数据库抽象和迁移支持

## 部署架构
- **开发环境**: SQLite + Flask dev server
- **生产环境**: MySQL + WSGI server
- **推荐端口**: 5001 (避免macOS AirPlay冲突)

## 核心依赖
- **后端**: Flask 2.3.3, SQLAlchemy, requests, python-dotenv
- **前端**: Bootstrap 5, 原生JavaScript
- **AI集成**: OpenAI Python SDK, Anthropic SDK
- **代码分析**: GitPython, ast, 语言特定解析器

## 性能特点
- **API响应**: 目标 <200ms
- **文档生成**: 目标 <2s (简单项目)
- **并发支持**: 基于Flask threading
- **缓存策略**: 分析结果本地缓存