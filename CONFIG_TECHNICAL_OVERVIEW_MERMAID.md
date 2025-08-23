# CoderWiki Config 系统技术总览图 (Mermaid 版本)

## 🏗️ 系统架构总览

```mermaid
graph TB
    subgraph "Config 系统架构"
        A[Flask 应用] --> B[Config 基类]
        B --> C[DevelopmentConfig]
        B --> D[ProductionConfig]  
        B --> E[TestingConfig]
        
        F[环境变量] --> B
        G[配置文件] --> B
        
        C --> H[开发环境]
        D --> I[生产环境]
        E --> J[测试环境]
        
        H --> K[MySQL: coderwiki_dev]
        I --> L[MySQL: coderwiki_prod]
        J --> M[SQLite: memory]
        
        H --> N[LLM: gpt-3.5-turbo]
        I --> O[LLM: 环境变量]
        J --> P[LLM: gpt-3.5-turbo]
        
        H --> Q[MCP: localhost:3000]
        I --> Q
        J --> Q
    end
```

## 📋 配置类继承关系

```mermaid
classDiagram
    class Config {
        +SECRET_KEY
        +SQLALCHEMY_DATABASE_URI
        +SQLALCHEMY_TRACK_MODIFICATIONS
        +FLASK_APP
        +FLASK_ENV
        +TEMPLATE_FOLDER
        +STATIC_FOLDER
        +MAX_CONTENT_LENGTH
        +UPLOAD_FOLDER
        +LLM_API_KEY
        +LLM_MODEL
        +LLM_PROVIDER
        +MCP_SERVER_URL
        +MCP_SERVER_PORT
        +MCP_ENABLED
        +BMAD_DOCS_PATH
        +LOG_LEVEL
        +LOG_FILE
        +WTF_CSRF_ENABLED
        +init_app()
    }
    
    class DevelopmentConfig {
        +DEBUG = True
        +FLASK_ENV = development
        +SQLALCHEMY_DATABASE_URI = mysql://coderwiki_dev
        +LLM_MODEL = gpt-3.5-turbo
        +LOG_LEVEL = DEBUG
        +MAX_CONTENT_LENGTH = 50MB
    }
    
    class ProductionConfig {
        +DEBUG = False
        +FLASK_ENV = production
        +SQLALCHEMY_DATABASE_URI = mysql://coderwiki_prod
        +LOG_LEVEL = WARNING
        +MAX_CONTENT_LENGTH = 16MB
    }
    
    class TestingConfig {
        +TESTING = True
        +DEBUG = True
        +SQLALCHEMY_DATABASE_URI = sqlite:///:memory:
        +LOG_LEVEL = DEBUG
        +MAX_CONTENT_LENGTH = 1MB
        +WTF_CSRF_ENABLED = False
    }
    
    Config <|-- DevelopmentConfig
    Config <|-- ProductionConfig
    Config <|-- TestingConfig
```

## 🔧 配置加载流程

```mermaid
sequenceDiagram
    participant Env as 环境变量
    participant Run as run.py
    participant Config as Config类
    participant App as Flask应用
    participant DB as 数据库
    
    Env->>Run: FLASK_ENV=development
    Run->>Config: create_app(DevelopmentConfig)
    Config->>Config: 应用基础配置
    Config->>Config: 应用环境特定配置
    Config->>App: 返回配置完成的应用
    App->>DB: 建立数据库连接
    App->>App: 启动Web服务器(端口5001)
```

## 🗄️ 数据库配置架构

```mermaid
graph TB
    subgraph "数据库配置架构"
        A[Config基类] --> B[MySQL连接池配置]
        B --> C[pool_recycle=3600]
        B --> D[pool_pre_ping=True]
        B --> E[pool_size=10]
        B --> F[max_overflow=20]
        B --> G[pool_timeout=30]
        
        H[环境配置] --> I[开发环境]
        H --> J[生产环境]
        H --> K[测试环境]
        
        I --> L[coderwiki_dev]
        J --> M[coderwiki_prod]
        K --> N[SQLite内存数据库]
    end
```

## 🤖 LLM服务配置

```mermaid
graph LR
    subgraph "LLM服务配置"
        A[Config基类] --> B[LLM配置项]
        B --> C[LLM_API_KEY]
        B --> D[LLM_BASE_URL]
        B --> E[LLM_MODEL]
        B --> F[LLM_PROVIDER]
        
        G[环境配置] --> H[开发环境]
        G --> I[生产环境]
        G --> J[测试环境]
        
        H --> K[gpt-3.5-turbo]
        I --> L[环境变量指定]
        J --> M[gpt-3.5-turbo]
    end
```

## 🔌 MCP服务配置

```mermaid
graph TB
    subgraph "MCP服务配置"
        A[Config基类] --> B[MCP配置]
        B --> C[MCP_SERVER_URL]
        B --> D[MCP_SERVER_PORT]
        B --> E[MCP_ENABLED]
        B --> F[CLAUDE_CODE_ENABLED]
        B --> G[BMAD_DOCS_PATH]
        
        H[默认配置] --> I[localhost:3000]
        H --> J[enabled=true]
        H --> K[/BMAD-METHOD/...]
    end
```

## 🔐 安全配置矩阵

```mermaid
graph TB
    subgraph "安全配置对比"
        A[开发环境] --> B[DEBUG=True]
        A --> C[WTF_CSRF_ENABLED=True]
        A --> D[SESSION_COOKIE_SECURE=False]
        A --> E[LOG_LEVEL=DEBUG]
        
        F[测试环境] --> G[DEBUG=True]
        F --> H[WTF_CSRF_ENABLED=False]
        F --> I[SESSION_COOKIE_SECURE=False]
        F --> J[LOG_LEVEL=DEBUG]
        
        K[生产环境] --> L[DEBUG=False]
        K --> M[WTF_CSRF_ENABLED=True]
        K --> N[SESSION_COOKIE_SECURE=True]
        K --> O[LOG_LEVEL=WARNING]
    end
```

## 📁 文件系统配置

```mermaid
graph TB
    subgraph "文件系统配置"
        A[Config基类] --> B[路径配置]
        B --> C[TEMPLATE_FOLDER]
        B --> D[STATIC_FOLDER]
        B --> E[UPLOAD_FOLDER]
        B --> F[GIT_REPOS_PATH]
        B --> G[LOG_FILE]
        B --> H[BMAD_DOCS_PATH]
        
        I[文件大小限制]
        I --> J[开发: 50MB]
        I --> K[生产: 16MB]
        I --> L[测试: 1MB]
    end
```

## ⚡ 缓存策略配置

```mermaid
graph TB
    subgraph "缓存策略"
        A[开发环境] --> B[Simple缓存]
        A --> C[调试友好]
        
        D[测试环境] --> E[Simple缓存]
        D --> F[超时=0]
        
        G[生产环境] --> H[Redis缓存]
        G --> I[高性能]
        G --> J[持久化]
    end
```

## 🚀 应用启动流程

```mermaid
flowchart TD
    A[启动应用] --> B[读取环境变量]
    B --> C[选择配置类]
    C --> D{FLASK_ENV}
    D -->|development| E[DevelopmentConfig]
    D -->|production| F[ProductionConfig]
    D -->|testing| G[TestingConfig]
    
    E --> H[应用开发配置]
    F --> I[应用生产配置]
    G --> J[应用测试配置]
    
    H --> K[初始化数据库]
    I --> K
    J --> L[初始化SQLite]
    
    K --> M[设置日志系统]
    L --> M
    M --> N[创建必要目录]
    N --> O[启动Web服务器]
    O --> P[监听端口5001]
```

## 📊 配置参数对比

```mermaid
graph TB
    subgraph "配置参数对比表"
        A[配置项] --> B[DEBUG]
        A --> C[TESTING]
        A --> D[数据库]
        A --> E[日志级别]
        A --> F[文件大小]
        A --> G[CSRF保护]
        
        H[开发环境] --> I[True]
        H --> J[False]
        H --> K[MySQL_dev]
        H --> L[DEBUG]
        H --> M[50MB]
        H --> N[True]
        
        O[测试环境] --> P[True]
        O --> Q[True]
        O --> R[SQLite内存]
        O --> S[DEBUG]
        O --> T[1MB]
        O --> U[False]
        
        V[生产环境] --> W[False]
        V --> X[False]
        V --> Y[MySQL_prod]
        V --> Z[WARNING]
        V --> AA[16MB]
        V --> BB[True]
    end
```

## 🔧 核心服务集成

```mermaid
graph TB
    subgraph "核心服务集成"
        A[Config系统] --> B[Flask应用]
        A --> C[SQLAlchemy]
        A --> D[Flask-Login]
        A --> E[Flask-Migrate]
        
        F[外部服务] --> G[LLM服务]
        F --> H[MCP服务]
        F --> I[BMAD文档生成器]
        
        J[文件系统] --> K[模板目录]
        J --> L[静态文件]
        J --> M[上传目录]
        J --> N[日志文件]
    end
```

## 🎯 配置管理最佳实践

```mermaid
graph TB
    subgraph "配置管理最佳实践"
        A[环境隔离] --> B[开发/测试/生产分离]
        C[安全优先] --> D[生产环境安全加固]
        E[敏感信息] --> F[环境变量管理]
        G[性能优化] --> H[生产环境Redis缓存]
        I[日志管理] --> J[环境级别日志控制]
    end
```

---

*此技术总览图使用 Mermaid 格式展示了 CoderWiki Config 系统的完整架构*

## 📝 使用说明

1. **查看架构**: 使用支持 Mermaid 的 Markdown 查看器查看图表
2. **环境切换**: 通过 `FLASK_ENV` 环境变量切换配置
3. **自定义配置**: 继承相应配置类进行扩展
4. **安全配置**: 生产环境请确保所有安全选项已启用

## 🔗 相关文件

- **主配置文件**: `/backend/config.py`
- **应用配置**: `/backend/app/config.py`
- **启动脚本**: `/backend/run.py`
- **环境配置**: `/config/` 目录