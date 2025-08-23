# CoderWiki Config System Technical Overview

## Overview

This document provides a comprehensive technical overview of the CoderWiki Config system architecture. The system employs a hierarchical configuration model with environment-specific settings and inheritance mechanisms.

## System Architecture

### Configuration System Components

```mermaid
graph TB
    subgraph "Config System Architecture"
        A[Base Config Classes] --> B[Environment Configs]
        A --> C[App Config Classes]
        B --> D[Environment-Specific Configs]
        C --> E[Flask Application]
    end
    
    subgraph "Base Config Classes (/backend/config.py)"
        A1[Config] --> A2[DevelopmentConfig]
        A1 --> A3[ProductionConfig] 
        A1 --> A4[TestingConfig]
    end
    
    subgraph "App Config Classes (/backend/app/config.py)"
        C1[Config] --> C2[DevelopmentConfig]
        C1 --> C3[ProductionConfig]
        C1 --> C4[TestingConfig]
    end
    
    subgraph "Environment-Specific Configs (/config/)"
        D1[DevConfig] --> A2
        D2[ProdConfig] --> A3
        D3[TestConfig] --> A4
    end
    
    A --> A1
    C --> C1
    B --> D1
    B --> D2
    B --> D3
```

## Configuration Class Hierarchy

### Primary Config System (/backend/config.py)

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
        +init_app(app)
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

### Environment-Specific Configuration Extensions

```mermaid
classDiagram
    class DevConfig {
        +SQLALCHEMY_DATABASE_URI = 'mysql://.../coderwiki_dev'
        +DEBUG = True
        +FLASK_DEBUG = True
        +LLM_MODEL = 'gpt-3.5-turbo'
        +LLM_TEMPERATURE = 0.7
        +LOG_LEVEL = 'DEBUG'
        +LOG_TO_FILE = False
        +WTF_CSRF_ENABLED = True
        +SESSION_COOKIE_SECURE = False
        +SESSION_COOKIE_HTTPONLY = True
        +MAX_CONTENT_LENGTH = 50MB
        +GIT_REPOS_PATH = '/tmp/coderwiki_repos_dev'
        +CACHE_TYPE = 'simple'
        +CACHE_DEFAULT_TIMEOUT = 300
    }
    
    class ProdConfig {
        +SQLALCHEMY_DATABASE_URI = 'mysql://.../coderwiki_prod'
        +DEBUG = False
        +FLASK_DEBUG = False
        +LOG_LEVEL = 'WARNING'
        +LOG_TO_FILE = True
        +SESSION_COOKIE_SECURE = True
        +SESSION_COOKIE_HTTPONLY = True
        +SESSION_COOKIE_SAMESITE = 'Lax'
        +PERMANENT_SESSION_LIFETIME = 3600
        +MAX_CONTENT_LENGTH = 16MB
        +GIT_REPOS_PATH = '/var/opt/coderwiki/repos'
        +CACHE_TYPE = 'redis'
        +CACHE_REDIS_URL
        +CACHE_DEFAULT_TIMEOUT = 300
        +SECURE_HEADERS
        +SENTRY_DSN
        +ENABLE_METRICS = True
    }
    
    class TestConfig {
        +SQLALCHEMY_DATABASE_URI = 'mysql://.../coderwiki_test'
        +TESTING = True
        +WTF_CSRF_ENABLED = False
        +SESSION_COOKIE_SECURE = False
        +SESSION_COOKIE_HTTPONLY = False
        +MAX_CONTENT_LENGTH = 1MB
        +GIT_REPOS_PATH = '/tmp/coderwiki_repos_test'
        +CACHE_TYPE = 'simple'
        +CACHE_DEFAULT_TIMEOUT = 0
        +LOG_LEVEL = 'CRITICAL'
        +SERVER_NAME = 'localhost:5000'
        +LLM_MODEL = 'test-model'
        +LLM_TEMPERATURE = 0.0
        +MAIL_SUPPRESS_SEND = True
        +SECRET_KEY = 'test-secret-key'
        +WTF_CSRF_SECRET_KEY = 'test-csrf-secret-key'
    }
    
    DevelopmentConfig <|-- DevConfig
    ProductionConfig <|-- ProdConfig
    TestingConfig <|-- TestConfig
```

## Configuration Loading Flow

```mermaid
sequenceDiagram
    participant App as Flask Application
    participant Env as Environment Variables
    participant Config as Config Module
    participant Base as Base Config Classes
    participant EnvConfig as Environment Configs
    
    App->>Env: Read FLASK_ENV, CONFIG_MODULE
    App->>Config: Load config module
    Config->>Base: Import base classes
    Config->>EnvConfig: Import environment configs
    EnvConfig->>Base: Inherit from base classes
    Config->>App: Return configuration object
    App->>App: Apply configuration settings
```

## Database Configuration Architecture

```mermaid
graph LR
    subgraph "Database Configuration by Environment"
        A[Environment Variable] --> B[Database URI Selection]
        B --> C[Development DB]
        B --> D[Production DB]
        B --> E[Testing DB]
        
        C --> F[MySQL: coderwiki_dev]
        D --> G[MySQL: coderwiki_prod]
        E --> H[MySQL: coderwiki_test]
        
        I[Connection Pooling] --> J[pool_recycle=3600]
        I --> K[pool_pre_ping=True]
        I --> L[pool_size=10]
        I --> M[max_overflow=20]
        I --> N[pool_timeout=30]
        
        F --> I
        G --> I
        H -.->|Testing uses SQLite| O[SQLite: :memory:]
    end
```

## LLM Service Configuration

```mermaid
graph TD
    subgraph "LLM Configuration Components"
        A[Environment Variables] --> B[LLM Settings]
        
        B --> C[API Keys]
        B --> D[Model Selection]
        B --> E[Provider Settings]
        B --> F[Temperature Settings]
        
        C --> G[LLM_API_KEY]
        C --> H[ANTHROPIC_API_KEY]
        C --> I[OPENAI_API_KEY]
        
        D --> J[LLM_MODEL]
        D --> K[DEV_LLM_MODEL]
        
        E --> L[LLM_PROVIDER]
        E --> M[LLM_BASE_URL]
        
        F --> N[LLM_TEMPERATURE]
        F --> O[DEV_LLM_TEMPERATURE]
        
        P[Environment Overrides] --> Q[Development: gpt-3.5-turbo]
        P --> R[Testing: test-model]
        P --> S[Production: gpt-3.5-turbo]
    end
```

## MCP Service Integration

```mermaid
graph LR
    subgraph "MCP Configuration"
        A[MCP_ENABLED] --> B{MCP Server}
        B --> C[MCP_SERVER_URL]
        B --> D[MCP_SERVER_PORT]
        
        C --> E[Default: http://localhost]
        D --> F[Default: 3000]
        
        G[Environment Control] --> H[MCP_ENABLED=true/false]
        H --> I[Service Integration]
        
        I --> J[Claude Code Service]
        I --> K[Task Processing]
    end
```

## Security Configuration Matrix

```mermaid
graph TB
    subgraph "Security Configuration by Environment"
        A[Security Settings] --> B[Development]
        A --> C[Testing]
        A --> D[Production]
        
        B --> E[DEBUG=True]
        B --> F[SESSION_COOKIE_SECURE=False]
        B --> G[WTF_CSRF_ENABLED=True]
        
        C --> H[TESTING=True]
        C --> I[WTF_CSRF_ENABLED=False]
        C --> J[SESSION_COOKIE_SECURE=False]
        
        D --> K[DEBUG=False]
        D --> L[SESSION_COOKIE_SECURE=True]
        D --> M[WTF_CSRF_ENABLED=True]
        D --> N[SECURE_HEADERS]
        
        N --> O[Strict-Transport-Security]
        N --> P[X-Content-Type-Options]
        N --> Q[X-Frame-Options]
        N --> R[X-XSS-Protection]
    end
```

## File System and Storage Configuration

```mermaid
graph TD
    subgraph "File System Configuration"
        A[Base Paths] --> B[UPLOAD_FOLDER]
        A --> C[GIT_REPOS_PATH]
        A --> D[LOG_FILE]
        
        B --> E[Development: /backend/uploads]
        B --> F[Testing: /backend/uploads]
        B --> G[Production: /backend/uploads]
        
        C --> H[Development: /backend/repos]
        C --> I[Testing: /tmp/coderwiki_repos_test]
        C --> J[Production: /var/opt/coderwiki/repos]
        
        D --> K[Development: /backend/logs/app.log]
        D --> L[Testing: /backend/logs/app.log]
        D --> M[Production: /backend/logs/app.log]
        
        N[File Size Limits] --> O[Development: 50MB]
        N --> P[Testing: 1MB]
        N --> Q[Production: 16MB]
    end
```

## Caching Strategy Configuration

```mermaid
graph LR
    subgraph "Caching Configuration"
        A[CACHE_TYPE] --> B[Development: simple]
        A --> C[Testing: simple]
        A --> D[Production: redis]
        
        E[CACHE_TIMEOUT] --> F[Development: 300s]
        E --> G[Testing: 0s]
        E --> H[Production: 300s]
        
        I[Redis Configuration] --> J[CACHE_REDIS_URL]
        I --> K[redis://localhost:6379/0]
        
        D --> I
    end
```

## Configuration Initialization Process

```mermaid
flowchart TD
    A[Application Start] --> B[Load Environment Variables]
    B --> C{Determine Environment}
    C -->|development| D[Load DevelopmentConfig]
    C -->|production| E[Load ProductionConfig]
    C -->|testing| F[Load TestingConfig]
    
    D --> G[Apply DevConfig Overrides]
    E --> H[Apply ProdConfig Overrides]
    F --> I[Apply TestConfig Overrides]
    
    G --> J[Initialize App Config]
    H --> J
    I --> J
    
    J --> K[Create Required Directories]
    K --> L[Configure Logging]
    L --> M[Setup Database Connections]
    M --> N[Initialize External Services]
    N --> O[Application Ready]
```

## Configuration Access Patterns

```mermaid
graph TB
    subgraph "Configuration Access Methods"
        A[Direct Access] --> B[app.config['SETTING_NAME']]
        
        C[Environment Variable] --> D[os.environ.get('VAR_NAME')]
        
        E[Config Class Method] --> F[Config.init_app(app)]
        
        G[Runtime Configuration] --> H[Dynamic Setting Override]
        
        I[Configuration Validation] --> J[Setting Existence Check]
        I --> K[Type Validation]
        I --> L[Range Validation]
    end
```

## Configuration Best Practices and Patterns

### 1. **Hierarchical Inheritance**
- Base configuration provides common settings
- Environment-specific configs extend base classes
- Environment variables override hardcoded values

### 2. **Environment Isolation**
- Separate databases for each environment
- Different security settings per environment
- Environment-specific file paths and limits

### 3. **Security Considerations**
- Production environment has strict security settings
- Development environment has relaxed security for debugging
- Testing environment disables CSRF for automated testing

### 4. **Performance Optimization**
- Production uses Redis for caching
- Development uses simple in-memory caching
- Testing has minimal caching to avoid interference

### 5. **Logging Configuration**
- Development: DEBUG level for detailed debugging
- Production: WARNING level to reduce noise
- Testing: CRITICAL level to minimize output

## Configuration File Locations

```
coderwiki/
├── config/
│   ├── development.py          # Development environment overrides
│   ├── production.py           # Production environment overrides
│   └── testing.py              # Testing environment overrides
├── backend/
│   ├── config.py               # Primary configuration system
│   └── app/
│       └── config.py           # Secondary configuration system
└── env.example                # Environment variables template
```

## Environment Variables Reference

### Core Configuration
- `FLASK_ENV`: Application environment (development/production/testing)
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: Database connection string

### LLM Configuration
- `LLM_API_KEY`: LLM service API key
- `LLM_MODEL`: Default LLM model
- `LLM_PROVIDER`: LLM service provider

### MCP Configuration
- `MCP_ENABLED`: Enable MCP service (true/false)
- `MCP_SERVER_URL`: MCP server URL
- `MCP_SERVER_PORT`: MCP server port

### Claude Code Integration
- `CLAUDE_CODE_ENABLED`: Enable Claude Code integration
- `BMAD_DOCS_PATH`: BMAD documentation generator path

## Configuration Validation and Error Handling

```mermaid
graph TD
    A[Configuration Load] --> B{Validation Checks}
    B --> C[Required Settings Present?]
    B --> D[Database URI Valid?]
    B --> E[File Paths Writable?]
    B --> F[API Keys Configured?]
    
    C -->|No| G[Raise Configuration Error]
    D -->|No| H[Raise Database Error]
    E -->|No| I[Raise Permission Error]
    F -->|No| J[Raise API Configuration Error]
    
    C -->|Yes| K[Continue Initialization]
    D -->|Yes| K
    E -->|Yes| K
    F -->|Yes| K
    
    K --> L[Application Startup]
```

## Configuration Migration Strategy

```mermaid
graph LR
    subgraph "Configuration Migration Path"
        A[Legacy Config] --> B[Current Config]
        B --> C[Future Config]
        
        A --> D[/backend/app/config.py]
        B --> E[/backend/config.py]
        C --> F[Unified Config System]
        
        G[Migration Steps] --> H[Deprecate Legacy Config]
        G --> I[Standardize Environment Variables]
        G --> J[Implement Configuration Validation]
        G --> K[Add Configuration Documentation]
    end
```

## Conclusion

The CoderWiki Config system implements a robust, hierarchical configuration architecture that provides:

1. **Environment Isolation**: Separate configurations for development, testing, and production
2. **Security Hardening**: Progressive security measures from development to production
3. **Flexibility**: Environment variable overrides and modular design
4. **Maintainability**: Clear inheritance hierarchy and documentation
5. **Scalability**: Support for multiple services and external integrations

The system follows Flask configuration best practices while providing extensions for LLM services, MCP integration, and Claude Code functionality. The dual-config system (legacy and current) provides backward compatibility during migration phases.

---

*Generated by Claude Code SDK - Config System Technical Overview*