# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目架构

CoderWiki 是一个基于 Flask 的智能代码文档生成与管理平台：

### 核心组件结构
- **backend/app/**: Flask 应用核心
  - `api/`: REST API 接口（认证、仓库管理、文档生成）
  - `models/`: SQLAlchemy 数据模型（用户、仓库、文档等）
  - `services/`: 业务逻辑层（仓库服务、分析服务）
  - `utils/`: 工具模块（代码分析引擎、AI客户端、Git服务等）
  - `routes/`: 页面路由
- **frontend/**: 前端静态资源和模板
- **bmad-docs-generator/**: 智能文档生成系统
- **coderwiki-output-docs/**: 生成的文档输出目录

### 关键技术栈
- Flask 2.3.3 + SQLAlchemy（ORM）
- 数据库：SQLite（开发）/ MySQL（生产）
- AI集成：OpenAI GPT + Anthropic Claude
- 前端：Bootstrap 5 + 原生JavaScript

## 🏗️ 系统架构速览

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


## 关键设计决策
- **分层架构**: 确保职责分离 (Models → Services → API → Frontend)
- **事件驱动**: 异步任务处理分析和文档生成
- **插件化AI**: 支持多种AI模型集成
- **SQLAlchemy ORM**: 数据库抽象和迁移支持


## 💼 核心业务域

## 核心实体

### Repository (代码仓库)
- **概念**: 用户管理的代码项目，是系统的核心业务对象
- **模型位置**: `backend/app/models/repository.py`
- **关键属性**:
  - `name`: 仓库名称
  - `url`: Git仓库URL或本地路径
  - `source_type`: 来源类型 (git_remote, local_directory)
  - `analysis_status`: 分析状态 (pending, running, completed, failed)
  - `user_id`: 所属用户ID
  - `local_source_path`: 本地路径(仅本地仓库)

- **生命周期**: 导入 → 分析 → 文档生成 → 维护更新
- **业务规则**:
  - 每个用户可管理多个仓库
  - 仓库必须先完成分析才能生成文档
  - 支持Git远程仓库和本地目录两种来源
  - 本地路径在同用户内必须唯一

### User (用户)
- **概念**: 系统使用者，拥有和管理代码仓库
- **模型位置**: `backend/app/models/user.py`
- **关键属性**:
  - `username`: 用户名
  - `email`: 邮箱
  - `password_hash`: 密码哈希
  - `repositories`: 关联的仓库列表

- **默认账户** (开发环境):
  - 管理员：admin/admin123
  - 演示用户：demo/demo123
  - 测试用户：testuser/test123

### Analysis (分析任务)
- **概念**: 对代码仓库的结构化分析过程
- **状态机**: pending → running → completed → failed
- **分析内容**:
  - 代码文件结构和组织
  - 编程语言和框架识别
  - 依赖关系分析
  - 代码质量和复杂度指标
- **触发条件**: 手动触发或仓库更新时自动触发
- **输出位置**: 结构化分析报告存储在数据库

### Document (生成文档)
- **概念**: 基于分析结果生成的智能文档
- **文档类型**:
  - API文档：接口说明和使用示例
  - 架构文档：系统设计和组件关系
  - 使用指南：部署和开发说明
- **生成策略**: 基于代码结构分析 + AI推理
- **存储位置**: `coderwiki-output-docs/repos/{repo_name}/`


## 🎨 常用代码模式

### API端点模式
- 参考: `backend/app/api/repository.py`
- 模式: REST API + 统一错误处理 + 权限验证

### 服务层模式
- 参考: `backend/app/services/repository_service.py`
- 模式: 业务逻辑封装 + 数据验证 + 事务管理

### 数据模型模式
- 参考: `backend/app/models/repository.py`
- 模式: SQLAlchemy ORM + 审计字段 + 关系定义

### 测试模式
- 参考: `backend/tests/unit/test_repository_model.py`
- 模式: pytest + factories + 分层测试


## 常用命令

### 开发环境启动
```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 启动应用（推荐端口5001，避免AirPlay冲突）
python run.py
# 或指定端口
PORT=5002 python run.py
```

### 数据库操作
```bash
cd backend
python init_db.py              # 初始化数据库
python create_default_user.py  # 创建默认用户
python manage_users.py list    # 查看用户列表
```

### 测试
```bash
cd backend
python -m pytest tests/unit/        # 单元测试
python -m pytest tests/integration/ # 集成测试
python -m pytest tests/e2e/         # 端到端测试
```

### 代码质量检查
```bash
ruff check .     # 代码检查
black .          # 代码格式化
```

### 诊断工具
```bash
python scripts/diagnose_api_quota.py  # API配额诊断
```

## 开发注意事项

### 目录约定
- **temp/**: 临时生成的文件（测试、诊断）- 不提交到git
- **logs/**: 应用日志文件
- **coderwiki-output-docs/**: 文档生成输出目录

### 重要服务模块
- `app/utils/code_analysis_engine.py`: 核心代码分析引擎
- `app/utils/llm_client.py`: AI客户端封装
- `app/services/repository_service.py`: 仓库管理核心逻辑
- `app/utils/git_service.py`: Git操作封装

### 配置管理
- 开发配置：`backend/app/config.py`
- 环境变量：`.env`文件（参考`.env.example`）
- 生产配置：使用环境变量覆盖

### API端点
- 认证：`/api/auth/*`
- 仓库管理：`/api/repositories/*`
- 文档生成：`/api/repositories/{id}/generate`

### 默认账户（开发环境）
- 管理员：admin/admin123
- 演示用户：demo/demo123
- 测试用户：testuser/test123

### 错误处理
- 同一类缺陷修复3次还没搞定，应该呼叫架构师进行Review
- 临时生成的bug fix的测试文本和诊断方案放在temp目录

## Knowledge Base集成

本项目已集成MVP版本的knowledge base系统：
- **Knowledge目录**: `.speckit-mvp/knowledge/`
- **同步脚本**: `.speckit-mvp/scripts/knowledge-sync.sh`
- **自动更新**: 通过脚本将knowledge信息同步到本文件

### Knowledge结构
- `architecture/`: 系统架构和技术决策
- `business/`: 业务领域模型和流程
- `patterns/`: 常用代码模式和最佳实践

---
*本文件由knowledge-sync.sh自动更新，手动修改可能会被覆盖*
*最后更新: $(date '+%Y-%m-%d %H:%M:%S')*
