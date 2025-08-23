# CoderWiki Config 复杂流程分析

## 🚀 应用启动流程

```mermaid
sequenceDiagram
    participant Env as 环境变量
    participant Run as run.py
    participant Config as Config 类
    participant App as Flask 应用
    participant DB as 数据库
    
    Env->>Run: FLASK_ENV=development
    Run->>Config: create_app(DevelopmentConfig)
    Config->>Config: 应用基础配置
    Config->>Config: 应用环境特定配置
    Config->>App: 返回配置完成的应用
    App->>DB: 建立数据库连接
    App->>App: 初始化扩展 (db, migrate, login_manager)
    App->>App: 注册蓝图 (auth, repository, document, etc.)
    App->>App: 初始化 WebSocket 支持
    App->>App: 配置错误处理器
    App->>App: 启动 Web 服务器 (端口 5001)
```

## 🔄 配置加载流程

```mermaid
flowchart TD
    A[应用启动] --> B[读取环境变量]
    B --> C[选择配置类]
    C --> D{FLASK_ENV}
    D -->|development| E[DevelopmentConfig]
    D -->|production| F[ProductionConfig]
    D -->|testing| G[TestingConfig]
    
    E --> H[应用开发配置]
    F --> I[应用生产配置]
    G --> J[应用测试配置]
    
    H --> K[初始化数据库连接池]
    I --> K
    J --> L[初始化 SQLite 内存数据库]
    
    K --> M[设置日志系统]
    L --> M
    M --> N[创建必要目录]
    N --> O[配置会话管理]
    O --> P[注册蓝图]
    P --> Q[启动完成]
```

## 🗄️ 数据库连接管理流程

```mermaid
graph TB
    subgraph "数据库连接池管理"
        A[应用请求] --> B[SQLAlchemy ORM]
        B --> C[检查连接池]
        C --> D{可用连接?}
        D -->|是| E[返回连接]
        D -->|否| F{池大小 < 最大溢出?}
        F -->|是| G[创建新连接]
        F -->|否| H[等待超时]
        G --> I[添加到连接池]
        I --> E
        H --> J[超时错误]
        E --> K[执行查询]
        K --> L[返回结果]
        L --> M[释放连接回池]
    end
```

## 🤖 LLM 服务调用流程

```mermaid
sequenceDiagram
    participant App as 应用请求
    participant LLM as LLM 服务
    participant Config as 配置管理
    participant DB as 数据库
    
    App->>Config: 请求 LLM 配置
    Config->>DB: 查询 LLMConfig
    DB->>Config: 返回加密配置
    Config->>Config: 解密 API 密钥
    Config->>App: 返回 LLM 配置
    
    App->>LLM: 构建请求
    LLM->>LLM: 发送到 LLM 提供商
    LLM->>LLM: 处理响应
    LLM->>App: 返回结果
    App->>App: 集成到应用逻辑
```

## 🔐 安全配置应用流程

```mermaid
graph TB
    subgraph "安全配置应用"
        A[应用启动] --> B[加载 SECRET_KEY]
        B --> C[配置会话 cookies]
        C --> D[设置 SESSION_COOKIE_SECURE]
        D --> E[配置 WTF_CSRF_ENABLED]
        E --> F[应用安全头 (生产环境)]
        F --> G[配置登录管理器]
        G --> H[初始化认证系统]
        H --> I[安全配置完成]
    end
```

## 📁 文件系统配置流程

```mermaid
flowchart LR
    A[配置加载] --> B[设置 UPLOAD_FOLDER]
    A --> C[设置 GIT_REPOS_PATH]
    A --> D[设置 LOG_FILE]
    A --> E[设置 TEMPLATE_FOLDER]
    A --> F[设置 STATIC_FOLDER]
    
    B --> G[创建上传目录]
    C --> H[创建仓库目录]
    D --> I[创建日志目录]
    E --> J[验证模板目录]
    F --> K[验证静态文件目录]
    
    G --> L[目录权限检查]
    H --> L
    I --> L
    J --> L
    K --> L
    
    L --> M[文件系统配置完成]
```

## ⚡ 缓存配置流程

```mermaid
graph TB
    subgraph "缓存配置流程"
        A[环境检测] --> B{环境类型}
        B -->|development| C[Simple 缓存]
        B -->|testing| D[Simple 缓存 + 超时0]
        B -->|production| E[Redis 缓存]
        
        C --> F[调试友好配置]
        D --> G[测试隔离配置]
        E --> H[高性能配置]
        
        F --> I[缓存初始化完成]
        G --> I
        H --> I
    end
```

## 🚨 错误处理流程

```mermaid
graph TB
    subgraph "错误处理流程"
        A[错误发生] --> B{错误类型}
        B -->|404| C[返回页面未找到]
        B -->|500| D[数据库回滚]
        D --> E[返回内部服务器错误]
        B -->|配置错误| F[记录配置错误]
        F --> G[返回配置错误信息]
        B -->|其他| H[记录通用错误]
        H --> I[返回通用错误信息]
        
        J[配置验证] --> K{配置有效?}
        K -->|是| L[继续启动]
        K -->|否| M[记录验证失败]
        M --> N[抛出配置异常]
    end
```

## 🔧 服务集成流程

```mermaid
graph TB
    subgraph "服务集成流程"
        A[应用启动] --> B[检查 MCP_ENABLED]
        B --> C{MCP 启用?}
        C -->|是| D[初始化 MCP 客户端]
        C -->|否| E[跳过 MCP 初始化]
        
        A --> F[检查 CLAUDE_CODE_ENABLED]
        F --> G{Claude Code 启用?}
        G -->|是| H[验证 BMAD_DOCS_PATH]
        G -->|否| I[跳过 Claude Code 初始化]
        
        D --> J[服务健康检查]
        H --> K[路径验证]
        
        J --> L[服务集成完成]
        K --> L
        E --> L
        I --> L
    end
```

## 📊 配置优先级流程

```mermaid
graph LR
    A[配置请求] --> B[环境变量检查]
    B --> C{环境变量存在?}
    C -->|是| D[使用环境变量值]
    C -->|否| E[检查扩展配置类]
    E --> F{扩展配置存在?}
    F -->|是| G[使用扩展配置]
    F -->|否| H[检查环境配置类]
    H --> I{环境配置存在?}
    I -->|是| J[使用环境配置]
    I -->|否| K[使用基类默认值]
    
    D --> L[配置验证]
    G --> L
    J --> L
    K --> L
    
    L --> M[配置应用完成]
```

---

*本流程分析由 BMAD 文档生成器自动生成*
