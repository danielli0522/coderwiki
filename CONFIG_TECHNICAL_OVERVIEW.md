# CoderWiki Config 系统技术总览图

## 🏗️ 系统架构概览

```mermaid
graph TB
    subgraph "Config 系统架构"
        A[Flask 应用] --> B[Config 基类]
        B --> C[DevelopmentConfig]
        B --> D[ProductionConfig]
        B --> E[TestingConfig]
        
        F[环境变量] --> B
        G[配置文件] --> B
        
        C --> H[开发环境设置]
        D --> I[生产环境设置]
        E --> J[测试环境设置]
        
        H --> K[数据库配置]
        I --> K
        J --> L[SQLite 内存数据库]
        
        H --> M[LLM 服务配置]
        I --> M
        J --> M
        
        H --> N[MCP 服务配置]
        I --> N
        J --> N
    end
```

## 📋 配置类层次结构

```mermaid
classDiagram
    class Config {
        +SECRET_KEY
        +SQLALCHEMY_DATABASE_URI
        +SQLALCHEMY_TRACK_MODIFICATIONS
        +SQLALCHEMY_ENGINE_OPTIONS
        +FLASK_APP
        +FLASK_ENV
        +TEMPLATE_FOLDER
        +STATIC_FOLDER
        +PERMANENT_SESSION_LIFETIME
        +MAX_CONTENT_LENGTH
        +UPLOAD_FOLDER
        +LLM_API_KEY
        +LLM_BASE_URL
        +LLM_MODEL
        +LLM_PROVIDER
        +MCP_SERVER_URL
        +MCP_SERVER_PORT
        +MCP_ENABLED
        +CLAUDE_CODE_ENABLED
        +BMAD_DOCS_PATH
        +GIT_REPOS_PATH
        +LOG_LEVEL
        +LOG_FILE
        +WTF_CSRF_ENABLED
        +WTF_CSRF_SECRET_KEY
        +init_app()
    }
    
    class DevelopmentConfig {
        +DEBUG = True
        +FLASK_ENV = 'development'
        +SQLALCHEMY_DATABASE_URI
        +LLM_MODEL
        +LOG_LEVEL = 'DEBUG'
    }
    
    class ProductionConfig {
        +DEBUG = False
        +FLASK_ENV = 'production'
        +SQLALCHEMY_DATABASE_URI
        +LOG_LEVEL = 'WARNING'
    }
    
    class TestingConfig {
        +TESTING = True
        +DEBUG = True
        +SQLALCHEMY_DATABASE_URI
        +SQLALCHEMY_ENGINE_OPTIONS = {}
        +LOG_LEVEL = 'DEBUG'
    }
    
    Config <|-- DevelopmentConfig
    Config <|-- ProductionConfig
    Config <|-- TestingConfig
```

## 🔧 配置加载流程

```mermaid
sequenceDiagram
    participant E as 环境变量
    participant R as run.py
    participant C as Config 类
    participant A as Flask 应用
    participant D as 数据库
    
    E->>R: FLASK_ENV=development
    R->>C: create_app(DevelopmentConfig)
    C->>C: 初始化基础配置
    C->>C: 应用环境特定配置
    C->>A: 返回配置好的应用
    A->>D: 建立数据库连接
    A->>A: 启动 Web 服务器
```

## 🗄️ 数据库配置架构

```mermaid
graph LR
    subgraph "数据库配置"
        A[Config 基类] --> B[MySQL 连接池配置]
        B --> C[pool_recycle = 3600]
        B --> D[pool_pre_ping = True]
        B --> E[pool_size = 10]
        B --> F[max_overflow = 20]
        B --> G[pool_timeout = 30]
        
        A --> H[环境特定数据库]
        H --> I[Development: coderwiki_dev]
        H --> J[Production: coderwiki_prod]
        H --> K[Testing: SQLite 内存]
    end
```

## 🤖 LLM 服务配置

```mermaid
graph TB
    subgraph "LLM 服务集成"
        A[Config 基类] --> B[LLM 配置项]
        B --> C[LLM_API_KEY]
        B --> D[LLM_BASE_URL]
        B --> E[LLM_MODEL]
        B --> F[LLM_PROVIDER]
        
        G[环境变量] --> B
        
        H[开发环境] --> I[gpt-3.5-turbo]
        J[生产环境] --> K[环境变量指定]
        L[测试环境] --> M[gpt-3.5-turbo]
    end
```

## 🔌 MCP 服务配置

```mermaid
graph LR
    subgraph "MCP 服务集成"
        A[Config 基类] --> B[MCP 配置]
        B --> C[MCP_SERVER_URL]
        B --> D[MCP_SERVER_PORT]
        B --> E[MCP_ENABLED]
        
        F[默认值] --> C[http://localhost]
        F --> D[3000]
        F --> E[true]
        
        G[环境变量] --> B
    end
```

## 🔐 安全配置矩阵

```mermaid
graph TB
    subgraph "安全配置"
        A[开发环境] --> B[DEBUG = True]
        A --> C[WTF_CSRF_ENABLED = True]
        A --> D[SESSION_COOKIE_SECURE = False]
        A --> E[LOG_LEVEL = DEBUG]
        
        F[测试环境] --> G[DEBUG = True]
        F --> H[WTF_CSRF_ENABLED = False]
        F --> I[SESSION_COOKIE_SECURE = False]
        F --> J[LOG_LEVEL = DEBUG]
        
        K[生产环境] --> L[DEBUG = False]
        K --> M[WTF_CSRF_ENABLED = True]
        K --> N[SESSION_COOKIE_SECURE = True]
        K --> O[LOG_LEVEL = WARNING]
    end
```

## 📁 文件系统配置

```mermaid
graph TB
    subgraph "文件系统配置"
        A[Config 基类] --> B[路径配置]
        B --> C[TEMPLATE_FOLDER]
        B --> D[STATIC_FOLDER]
        B --> E[UPLOAD_FOLDER]
        B --> F[GIT_REPOS_PATH]
        B --> G[LOG_FILE]
        B --> H[BMAD_DOCS_PATH]
        
        I[文件大小限制]
        I --> J[开发环境: 50MB]
        I --> K[生产环境: 16MB]
        I --> L[测试环境: 1MB]
    end
```

## ⚡ 缓存策略配置

```mermaid
graph TB
    subgraph "缓存策略"
        A[开发环境] --> B[Simple 缓存]
        A --> C[调试友好]
        
        D[测试环境] --> E[Simple 缓存]
        D --> F[超时为 0]
        
        G[生产环境] --> H[Redis 缓存]
        G --> I[高性能]
        G --> J[持久化]
    end
```

## 🚀 配置初始化过程

```mermaid
flowchart TD
    A[应用启动] --> B[读取环境变量]
    B --> C[选择配置类]
    C --> D{环境类型}
    D -->|development| E[DevelopmentConfig]
    D -->|production| F[ProductionConfig]
    D -->|testing| G[TestingConfig]
    
    E --> H[应用开发环境设置]
    F --> I[应用生产环境设置]
    G --> J[应用测试环境设置]
    
    H --> K[初始化数据库连接]
    I --> K
    J --> L[初始化 SQLite 内存数据库]
    
    K --> M[设置日志系统]
    L --> M
    M --> N[创建必要目录]
    N --> O[配置完成]
```

## 📊 配置参数对比表

| 配置项 | 开发环境 | 测试环境 | 生产环境 | 说明 |
|--------|----------|----------|----------|------|
| DEBUG | True | True | False | 调试模式 |
| TESTING | False | True | False | 测试模式 |
| SQLALCHEMY_DATABASE_URI | MySQL: coderwiki_dev | SQLite: :memory: | MySQL: coderwiki_prod | 数据库连接 |
| LOG_LEVEL | DEBUG | DEBUG | WARNING | 日志级别 |
| MAX_CONTENT_LENGTH | 50MB | 1MB | 16MB | 文件上传限制 |
| LLM_MODEL | gpt-3.5-turbo | gpt-3.5-turbo | 环境变量 | LLM 模型 |
| WTF_CSRF_ENABLED | True | False | True | CSRF 保护 |
| SESSION_COOKIE_SECURE | False | False | True | 会话安全 |
| CACHE_TYPE | simple | simple | redis | 缓存类型 |

## 🔧 核心配置模块

### 1. 基础配置模块 (config.py)
- **位置**: `/backend/config.py`
- **作用**: 定义所有环境共享的基础配置
- **特点**: 包含数据库、LLM、MCP 等核心服务配置

### 2. 应用配置模块 (app/config.py)
- **位置**: `/backend/app/config.py`
- **作用**: 应用特定的配置类
- **特点**: 继承基础配置，添加应用级设置

### 3. 环境配置目录 (/config/)
- **位置**: `/config/`
- **作用**: 环境特定的配置文件
- **包含**: development.py, production.py, testing.py

## 🎯 最佳实践

1. **环境隔离**: 每个环境使用独立的配置
2. **安全优先**: 生产环境启用所有安全功能
3. **敏感信息**: 使用环境变量管理密码和密钥
4. **性能优化**: 生产环境使用高性能缓存
5. **日志管理**: 根据环境调整日志级别

## 📈 系统集成点

- **Flask 应用**: 通过 `create_app()` 函数集成
- **数据库**: 通过 SQLAlchemy 集成
- **LLM 服务**: 通过配置的 API 集成
- **MCP 服务**: 通过配置的服务地址集成
- **文件系统**: 通过配置的路径集成
- **日志系统**: 通过配置的日志设置集成

---

*此技术总览图展示了 CoderWiki Config 系统的完整架构和配置关系*