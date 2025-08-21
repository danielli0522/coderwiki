# 代码文档自动生成系统 - 系统架构设计

## 1. 项目概述

### 1.1 项目目标
构建一个轻量级的代码文档自动生成系统，让开发团队能够自主、按需地为代码仓库生成技术设计文档。

### 1.2 技术约束
- 架构：单体架构
- 数据库：MySQL
- 后端：Python
- 前端：简单HTML/JavaScript
- 支持10人同时在线

## 2. 系统架构 - 五视图设计

### 2.1 逻辑视图 (Logical View)

#### 2.1.1 核心模块划分
```
代码文档自动生成系统
├── 用户管理模块 (User Management)
│   ├── 用户认证
│   ├── 用户注册
│   └── 会话管理
├── 仓库管理模块 (Repository Management)
│   ├── 仓库添加/删除
│   ├── 仓库信息同步
│   └── 仓库状态监控
├── 文档生成模块 (Document Generation)
│   ├── 代码分析器
│   ├── LLM集成器
│   └── 文档格式化器
├── 任务管理模块 (Task Management)
│   ├── 任务调度
│   ├── 进度跟踪
│   └── 错误处理
├── 文档管理模块 (Document Management)
│   ├── 版本控制
│   ├── 文档存储
│   └── 文档检索
└── 前端展示模块 (Frontend Display)
    ├── 页面路由
    ├── 用户界面
    └── 交互处理
```

#### 2.1.2 模块间依赖关系
- 用户管理模块 → 仓库管理模块
- 仓库管理模块 → 任务管理模块
- 任务管理模块 → 文档生成模块
- 文档生成模块 → 文档管理模块
- 所有模块 → 数据库访问层

### 2.2 开发视图 (Development View)

#### 2.2.1 项目结构
```
coderwiki/
├── backend/                    # 后端应用
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置文件
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── repository.py
│   │   │   ├── document.py
│   │   │   └── task.py
│   │   ├── services/           # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── repo_service.py
│   │   │   ├── doc_service.py
│   │   │   └── task_service.py
│   │   ├── api/                # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── repository.py
│   │   │   ├── document.py
│   │   │   └── task.py
│   │   ├── utils/              # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── git_utils.py
│   │   │   ├── code_analyzer.py
│   │   │   ├── llm_client.py
│   │   │   └── doc_formatter.py
│   │   └── static/             # 静态文件
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   ├── migrations/             # 数据库迁移
│   ├── tests/                  # 测试文件
│   ├── requirements.txt        # 依赖包
│   └── run.py                  # 启动文件
├── frontend/                   # 前端文件
│   ├── templates/              # HTML模板
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── repository.html
│   │   └── document.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── dashboard.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── dashboard.js
│   │       └── document.js
├── database/                   # 数据库相关
│   ├── schema.sql              # 数据库结构
│   └── init_data.sql           # 初始数据
├── docs/                       # 项目文档
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
├── config/                     # 配置文件
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── scripts/                    # 脚本文件
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
└── README.md
```

#### 2.2.2 技术栈选择
- **Web框架**: Flask (轻量级，易于部署)
- **ORM**: SQLAlchemy (数据库操作)
- **数据库**: MySQL 8.0 (稳定可靠)
- **前端**: Bootstrap + jQuery (快速开发)
- **代码分析**: GitPython + AST
- **AI集成**: OpenAI API (或其他LLM API)
- **任务队列**: Python threading (简单任务处理)
- **认证**: Flask-Login (会话管理)

### 2.3 进程视图 (Process View)

#### 2.3.1 系统进程架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │    │   Worker Pool   │    │   Scheduler     │
│   (Flask App)   │    │                 │    │                 │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Main Thread │ │    │ │ Worker 1    │ │    │ │ Task Queue  │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ │ - HTTP Req  │ │    │ │ - Doc Gen   │ │    │ │ - Schedule  │ │
│ │ - Auth      │ │    │ │ - Code Ana  │ │    │ │ - Monitor   │ │
│ │ - Static    │ │    │ │ - LLM Call  │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │                 │
│ │ Background  │ │    │ │ Worker 2    │ │    │                 │
│ │             │ │    │ │             │ │    │                 │
│ │ - Task Mon  │ │    │ │ - Doc Gen   │ │    │                 │
│ │ - Clean Up  │ │    │ │ - Code Ana  │ │    │                 │
│ │ - Health    │ │    │ │ - LLM Call  │ │    │                 │
│ └─────────────┘ │    │ └─────────────┘ │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ MySQL       │ │
                    │ │             │ │
                    │ │ - Users     │ │
                    │ │ - Repos     │ │
                    │ │ - Docs      │ │
                    │ │ - Tasks     │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

#### 2.3.2 关键流程时序

**文档生成流程:**
```
用户 → 点击生成 → API请求 → 创建任务 → 入队 → Worker处理 → 代码分析 → LLM调用 → 文档格式化 → 保存结果 → 更新状态 → 通知用户
```

**仓库添加流程:**
```
用户 → 输入URL → 验证格式 → 克隆仓库 → 分析结构 → 提取信息 → 保存数据库 → 返回成功
```

### 2.4 物理视图 (Physical View)

#### 2.4.1 部署架构
```
┌─────────────────────────────────────────────────────────────┐
│                    Web Server                              │
│                  (Single Instance)                         │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Nginx        │  │   Flask App     │  │   Worker    │ │
│  │                 │  │                 │  │             │ │
│  │ - Static Files │  │ - API Routes    │  │ - Task Proc  │ │
│  │ - Reverse Proxy│  │ - Auth          │  │ - Background │ │
│  │ - SSL Terminate│  │ - Business Logic│  │ - Monitoring │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Database Server                        │
│                  (MySQL 8.0)                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 MySQL Instance                         │ │
│  │                                                         │ │
│  │  - coderwiki_db                                         │ │
│  │  ├── users                                              │ │
│  │  ├── repositories                                       │ │
│  │  ├── documents                                          │ │
│  │  └── tasks                                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  External Services                          │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   GitHub API    │  │   GitLab API    │  │   LLM API   │ │
│  │                 │  │                 │  │             │ │
│  │ - Repo Clone    │  │ - Repo Clone    │  │ - Doc Gen   │ │
│  │ - Info Fetch    │  │ - Info Fetch    │  │ - Text Proc │ │
│  │ - Webhook       │  │ - Webhook       │  │ - Analysis  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 2.4.2 硬件需求
- **服务器**: 1台虚拟机 (2核4G内存)
- **存储**: 50GB SSD (代码仓库临时存储)
- **数据库**: 20GB (文档数据存储)
- **网络**: 10Mbps带宽
- **操作系统**: Ubuntu 20.04 LTS

### 2.5 场景视图 (Scenarios View)

#### 2.5.1 关键使用场景

**场景1: 用户首次使用系统**
```
1. 用户访问系统首页
2. 系统重定向到登录页面
3. 用户注册新账户
4. 系统创建用户记录
5. 用户登录成功
6. 系统显示仓库管理页面
7. 用户添加第一个GitHub仓库
8. 系统验证并克隆仓库
9. 系统分析仓库结构
10. 系统显示仓库信息
11. 用户点击生成文档
12. 系统创建文档生成任务
13. Worker处理任务
14. 系统生成技术文档
15. 用户查看生成的文档
```

**场景2: 文档重新生成**
```
1. 用户登录系统
2. 用户进入仓库列表页面
3. 用户选择需要更新的仓库
4. 用户点击"重新生成"按钮
5. 系统确认用户意图
6. 系统创建新的生成任务
7. 系统更新任务状态为"处理中"
8. Worker获取任务并处理
9. 系统定期更新任务进度
10. 文档生成完成
11. 系统创建新版本文档
12. 系统通知用户生成完成
13. 用户查看最新版本文档
```

**场景3: 多用户并发使用**
```
1. 用户A同时生成文档X
2. 用户B同时生成文档Y
3. 用户C添加新仓库Z
4. 系统同时处理多个请求
5. 任务队列调度执行
6. Worker池并行处理
7. 数据库并发访问
8. 各用户独立获得结果
9. 系统保持稳定响应
```

#### 2.5.2 异常处理场景

**场景4: LLM API调用失败**
```
1. 系统调用LLM API生成文档
2. API返回错误响应
3. 系统捕获异常并记录
4. 系统重试API调用(最多3次)
5. 如果仍然失败，标记任务失败
6. 保存错误信息到数据库
7. 通知用户生成失败
8. 提供重试选项
```

**场景5: 仓库克隆失败**
```
1. 用户添加仓库URL
2. 系统尝试克隆仓库
3. 克隆操作失败(网络/权限)
4. 系统记录失败原因
5. 更新仓库状态为"错误"
6. 通知用户添加失败
7. 提供重新添加选项
```

## 3. 数据模型设计

### 3.1 用户表 (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3.2 仓库表 (repositories)
```sql
CREATE TABLE repositories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    description TEXT,
    status ENUM('active', 'error', 'processing') DEFAULT 'active',
    last_analysis TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 3.3 文档表 (documents)
```sql
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    repository_id INT NOT NULL,
    version INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    status ENUM('draft', 'published', 'archived') DEFAULT 'published',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);
```

### 3.4 任务表 (tasks)
```sql
CREATE TABLE tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    repository_id INT NOT NULL,
    type ENUM('analysis', 'generation', 'update') NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    progress INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);
```

## 4. 接口设计

### 4.1 用户认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息

### 4.2 仓库管理接口
- `GET /api/repositories` - 获取仓库列表
- `POST /api/repositories` - 添加仓库
- `GET /api/repositories/{id}` - 获取仓库详情
- `DELETE /api/repositories/{id}` - 删除仓库
- `POST /api/repositories/{id}/sync` - 同步仓库信息

### 4.3 文档生成接口
- `POST /api/repositories/{id}/generate` - 生成文档
- `GET /api/repositories/{id}/documents` - 获取文档列表
- `GET /api/documents/{id}` - 获取文档详情
- `GET /api/tasks/{id}/status` - 获取任务状态

### 4.4 系统监控接口
- `GET /api/system/health` - 系统健康检查
- `GET /api/system/stats` - 系统统计信息

## 5. 安全设计

### 5.1 认证安全
- 使用bcrypt进行密码哈希
- JWT Token进行会话管理
- Token过期时间控制

### 5.2 数据安全
- SQL注入防护
- XSS攻击防护
- CSRF防护
- 敏感数据加密存储

### 5.3 访问控制
- 基于用户ID的数据隔离
- API访问频率限制
- 输入参数验证

## 6. 性能优化

### 6.1 数据库优化
- 合理的索引设计
- 查询优化
- 连接池管理

### 6.2 缓存策略
- Redis缓存热点数据
- 静态资源CDN加速
- 浏览器缓存控制

### 6.3 并发处理
- 异步任务处理
- 数据库连接池
- 请求限流机制

## 7. 监控和日志

### 7.1 系统监控
- 服务器资源监控
- 应用性能监控
- 数据库性能监控

### 7.2 日志管理
- 结构化日志记录
- 日志分级管理
- 错误日志追踪

### 7.3 告警机制
- 系统异常告警
- 任务失败告警
- 性能阈值告警