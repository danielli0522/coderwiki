# 统一项目结构

## 项目根目录结构

```
coderwiki/
├── .bmad-core/                    # BMAD核心配置文件
├── backend/                        # 后端应用程序
│   ├── app/                       # Flask应用核心
│   │   ├── __init__.py           # 应用初始化
│   │   ├── config.py             # 配置文件
│   │   ├── models/               # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # 用户模型
│   │   │   ├── repository.py     # 仓库模型
│   │   │   ├── document.py       # 文档模型
│   │   │   └── task.py           # 任务模型
│   │   ├── services/             # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py   # 认证服务
│   │   │   ├── repo_service.py   # 仓库服务
│   │   │   ├── doc_service.py    # 文档服务
│   │   │   └── task_service.py   # 任务服务
│   │   ├── api/                  # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # 认证API
│   │   │   ├── repository.py     # 仓库API
│   │   │   ├── document.py       # 文档API
│   │   │   └── task.py           # 任务API
│   │   ├── utils/                # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── git_utils.py      # Git工具
│   │   │   ├── code_analyzer.py  # 代码分析工具
│   │   │   ├── llm_client.py     # LLM客户端
│   │   │   └── doc_formatter.py  # 文档格式化工具
│   │   └── static/               # 静态文件
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   ├── migrations/                # 数据库迁移文件
│   ├── tests/                     # 测试文件
│   │   ├── unit/                  # 单元测试
│   │   ├── integration/           # 集成测试
│   │   └── e2e/                   # 端到端测试
│   ├── requirements.txt           # 依赖包
│   ├── requirements-dev.txt       # 开发依赖
│   ├── run.py                     # 应用启动文件
│   └── config.py                 # 主配置文件
├── frontend/                      # 前端资源
│   ├── templates/                 # HTML模板
│   │   ├── base.html             # 基础模板
│   │   ├── auth/                 # 认证相关模板
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/            # 仪表板模板
│   │   │   ├── index.html
│   │   │   └── stats.html
│   │   ├── repository/           # 仓库管理模板
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── add.html
│   │   ├── document/             # 文档相关模板
│   │   │   ├── view.html
│   │   │   ├── generate.html
│   │   │   └── version.html
│   │   └── partials/              # 可重用组件
│   │       ├── navbar.html
│   │       ├── sidebar.html
│   │       └── footer.html
│   └── static/                    # 静态资源
│       ├── css/                   # CSS文件
│       │   ├── style.css
│       │   ├── dashboard.css
│       │   └── components.css
│       ├── js/                    # JavaScript文件
│       │   ├── main.js
│       │   ├── dashboard.js
│       │   └── components.js
│       └── images/                # 图片资源
├── database/                      # 数据库相关
│   ├── schema.sql                # 数据库结构
│   └── init_data.sql              # 初始数据
├── docs/                          # 项目文档
│   ├── architecture/              # 架构文档
│   │   ├── tech-stack.md
│   │   ├── unified-project-structure.md
│   │   ├── coding-standards.md
│   │   ├── testing-strategy.md
│   │   ├── data-models.md
│   │   ├── database-schema.md
│   │   ├── backend-architecture.md
│   │   ├── rest-api-spec.md
│   │   ├── external-apis.md
│   │   ├── frontend-architecture.md
│   │   └── components.md
│   ├── stories/                  # 用户故事
│   ├── qa/                       # 质量保证
│   └── api/                      # API文档
├── config/                        # 配置文件
│   ├── development.py            # 开发环境配置
│   ├── production.py             # 生产环境配置
│   └── testing.py                # 测试环境配置
├── scripts/                       # 脚本文件
│   ├── setup.sh                  # 环境设置脚本
│   ├── deploy.sh                 # 部署脚本
│   └── backup.sh                 # 备份脚本
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── README.md                     # 项目说明
└── docker-compose.yml            # Docker配置 (可选)
```

## 后端详细结构

### app/ 目录详解

**config.py:** 应用配置文件
- 数据库配置
- 安全配置
- 应用设置
- 环境变量处理

**models/ 目录:** 数据模型定义
- **user.py:** 用户模型（用户、权限、会话）
- **repository.py:** 仓库模型（仓库信息、状态）
- **document.py:** 文档模型（文档内容、版本）
- **task.py:** 任务模型（任务队列、状态）

**services/ 目录:** 业务逻辑层
- **auth_service.py:** 认证相关业务逻辑
- **repo_service.py:** 仓库管理业务逻辑
- **doc_service.py:** 文档生成和管理逻辑
- **task_service.py:** 任务队列管理逻辑

**api/ 目录:** RESTful API路由
- **auth.py:** 认证相关API
- **repository.py:** 仓库管理API
- **document.py:** 文档管理API
- **task.py:** 任务状态API

**utils/ 目录:** 工具函数
- **git_utils.py:** Git操作工具
- **code_analyzer.py:** 代码分析工具
- **llm_client.py:** LLM API客户端
- **doc_formatter.py:** 文档格式化工具

## 前端详细结构

### templates/ 目录详解

**base.html:** 基础模板
- 包含导航栏、侧边栏、页脚
- 定义页面布局结构
- 引入CSS和JavaScript文件

**auth/ 目录:** 认证相关页面
- **login.html:** 登录页面
- **register.html:** 注册页面

**dashboard/ 目录:** 仪表板相关页面
- **index.html:** 主仪表板
- **stats.html:** 统计页面

**repository/ 目录:** 仓库管理页面
- **list.html:** 仓库列表
- **detail.html:** 仓库详情
- **add.html:** 添加仓库

**document/ 目录:** 文档相关页面
- **view.html:** 文档查看
- **generate.html:** 文档生成
- **version.html:** 版本管理

**partials/ 目录:** 可重用组件
- **navbar.html:** 导航栏组件
- **sidebar.html:** 侧边栏组件
- **footer.html:** 页脚组件

## 命名约定

### Python文件命名
- 使用小写字母和下划线
- 例如：`user_service.py`, `git_utils.py`

### 类命名
- 使用PascalCase
- 例如：`UserService`, `GitUtils`

### 函数命名
- 使用小写字母和下划线
- 例如：`get_user()`, `clone_repository()`

### 变量命名
- 使用小写字母和下划线
- 例如：`user_id`, `repository_url`

### 常量命名
- 使用大写字母和下划线
- 例如：`MAX_LOGIN_ATTEMPTS`, `DB_HOST`

## 配置文件

### 环境配置
- **development.py:** 开发环境配置
- **production.py:** 生产环境配置
- **testing.py:** 测试环境配置

### 数据库配置
- 主数据库连接
- 连接池配置
- 迁移配置

### 安全配置
- 密钥配置
- 会话配置
- CSRF配置

## 测试结构

### 单元测试 (tests/unit/)
- 测试单个函数和类
- 使用mock对象
- 快速执行

### 集成测试 (tests/integration/)
- 测试模块间交互
- 使用测试数据库
- 中等执行时间

### 端到端测试 (tests/e2e/)
- 测试完整用户流程
- 使用浏览器自动化
- 较长执行时间

## 部署结构

### 生产环境
- 应用服务器配置
- 数据库配置
- 静态文件配置
- 日志配置

### 开发环境
- 热重载配置
- 调试配置
- 开发数据库配置

### 测试环境
- 测试数据库配置
- 测试覆盖率配置
- 测试报告配置