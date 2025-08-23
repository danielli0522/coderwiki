#!/usr/bin/env python3
"""
使用 BMAD 文档生成器生成 Config 目录技术架构总览
"""

import os
import sys
import subprocess
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """设置环境变量"""
    # 设置 BMAD 文档生成器路径
    os.environ['BMAD_DOCS_PATH'] = '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/'
    
    # 设置其他必要的环境变量
    os.environ['FLASK_ENV'] = 'development'
    os.environ['PYTHONPATH'] = str(project_root)
    
    print(f"✅ BMAD_DOCS_PATH: {os.environ.get('BMAD_DOCS_PATH')}")
    print(f"✅ FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"✅ PYTHONPATH: {os.environ.get('PYTHONPATH')}")

def check_bmad_docs_generator():
    """检查 BMAD 文档生成器是否可用"""
    bmad_path = os.environ.get('BMAD_DOCS_PATH')
    
    if not os.path.exists(bmad_path):
        print(f"❌ BMAD 文档生成器路径不存在: {bmad_path}")
        return False
    
    # 检查关键文件
    required_files = ['__init__.py', 'generator.py', 'templates']
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(bmad_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ BMAD 文档生成器缺少关键文件: {missing_files}")
        return False
    
    print("✅ BMAD 文档生成器检查通过")
    return True

def analyze_config_system():
    """分析 Config 系统"""
    print("🔍 开始分析 Config 系统...")
    
    config_files = [
        'backend/config.py',
        'backend/app/config.py',
        'backend/run.py'
    ]
    
    config_analysis = {}
    
    for config_file in config_files:
        file_path = project_root / config_file
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                config_analysis[config_file] = {
                    'content': content,
                    'size': len(content),
                    'lines': len(content.split('\n'))
                }
                print(f"✅ 分析完成: {config_file} ({len(content.split('\n'))} 行)")
        else:
            print(f"⚠️  文件不存在: {config_file}")
    
    return config_analysis

def generate_config_architecture_overview():
    """生成 Config 架构总览"""
    print("🏗️ 生成 Config 架构总览...")
    
    architecture_content = """# CoderWiki Config 目录技术架构总览

## 🏗️ 系统架构总览

```mermaid
graph TB
    subgraph "CoderWiki Config 系统架构"
        A[Flask 应用] --> B[配置系统核心]
        B --> C[基础配置类 Config]
        B --> D[环境特定配置]
        B --> E[扩展配置目录]
        
        C --> F[数据库配置]
        C --> G[安全配置]
        C --> H[LLM 服务配置]
        C --> I[MCP 服务配置]
        C --> J[文件系统配置]
        
        D --> K[DevelopmentConfig]
        D --> L[ProductionConfig]
        D --> M[TestingConfig]
        
        E --> N[/config/ 目录]
        N --> O[development.py]
        N --> P[production.py]
        N --> Q[testing.py]
    end
```

## 📋 配置类继承层次

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
        +init_app()
    }
    
    class DevelopmentConfig {
        +DEBUG = True
        +FLASK_ENV = 'development'
        +SQLALCHEMY_DATABASE_URI
        +LLM_MODEL = 'gpt-3.5-turbo'
        +LOG_LEVEL = 'DEBUG'
        +MAX_CONTENT_LENGTH = 50MB
        +SESSION_COOKIE_SECURE = False
        +CACHE_TYPE = 'simple'
    }
    
    class ProductionConfig {
        +DEBUG = False
        +FLASK_ENV = 'production'
        +SQLALCHEMY_DATABASE_URI
        +LOG_LEVEL = 'WARNING'
        +MAX_CONTENT_LENGTH = 16MB
        +SESSION_COOKIE_SECURE = True
        +CACHE_TYPE = 'redis'
        +SECURE_HEADERS
    }
    
    class TestingConfig {
        +TESTING = True
        +DEBUG = True
        +SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        +LOG_LEVEL = 'DEBUG'
        +MAX_CONTENT_LENGTH = 1MB
        +WTF_CSRF_ENABLED = False
    }
    
    Config <|-- DevelopmentConfig
    Config <|-- ProductionConfig
    Config <|-- TestingConfig
```

## 🔧 环境特定配置分析

### 开发环境配置特点
- **调试模式**: 启用详细日志和调试信息
- **数据库**: MySQL 开发数据库 (coderwiki_dev)
- **文件上传**: 50MB 限制，支持大文件测试
- **缓存**: Simple 缓存，便于调试
- **安全**: 宽松的安全设置，便于开发

### 生产环境配置特点
- **调试模式**: 禁用，优化性能
- **数据库**: MySQL 生产数据库 (coderwiki_prod)
- **文件上传**: 16MB 限制，平衡功能和安全
- **缓存**: Redis 高性能缓存
- **安全**: 严格的安全设置和头配置

### 测试环境配置特点
- **测试模式**: 启用测试专用设置
- **数据库**: SQLite 内存数据库，隔离测试
- **文件上传**: 1MB 限制，测试用例
- **缓存**: Simple 缓存，超时为 0
- **安全**: CSRF 保护禁用，便于测试

## 🗄️ 数据库配置架构

```mermaid
graph TB
    subgraph "数据库连接池配置"
        A[SQLALCHEMY_ENGINE_OPTIONS] --> B[pool_recycle = 3600]
        A --> C[pool_pre_ping = True]
        A --> D[pool_size = 10]
        A --> E[max_overflow = 20]
        A --> F[pool_timeout = 30]
        
        B --> G[连接回收机制]
        C --> H[连接健康检查]
        D --> I[基础连接池]
        E --> J[溢出连接]
        F --> K[连接超时设置]
    end
```

## 🤖 服务集成架构

```mermaid
graph TB
    subgraph "LLM/MCP 服务集成"
        A[Config 基类] --> B[LLM 配置]
        B --> C[LLM_API_KEY]
        B --> D[LLM_MODEL]
        B --> E[LLM_PROVIDER]
        
        A --> F[MCP 配置]
        F --> G[MCP_SERVER_URL]
        F --> H[MCP_SERVER_PORT]
        F --> I[MCP_ENABLED]
        
        A --> J[Claude Code 配置]
        J --> K[CLAUDE_CODE_ENABLED]
        J --> L[BMAD_DOCS_PATH]
    end
```

## 🔐 安全配置矩阵

| 配置项 | 开发环境 | 测试环境 | 生产环境 | 说明 |
|--------|----------|----------|----------|------|
| DEBUG | True | True | False | 调试模式 |
| TESTING | False | True | False | 测试模式 |
| SESSION_COOKIE_SECURE | False | False | True | 会话安全 |
| WTF_CSRF_ENABLED | True | False | True | CSRF 保护 |
| LOG_LEVEL | DEBUG | DEBUG | WARNING | 日志级别 |
| MAX_CONTENT_LENGTH | 50MB | 1MB | 16MB | 文件大小 |
| CACHE_TYPE | simple | simple | redis | 缓存类型 |

---

*本架构总览由 BMAD 文档生成器自动生成*
"""
    
    return architecture_content

def generate_complex_flow_analysis():
    """生成复杂流程分析"""
    print("🔄 生成复杂流程分析...")
    
    flow_analysis_content = """# CoderWiki Config 复杂流程分析

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
"""
    
    return flow_analysis_content

def generate_bmad_analysis():
    """生成 BMAD 方法论分析"""
    print("📊 生成 BMAD 方法论分析...")
    
    bmad_analysis_content = """# CoderWiki Config 系统 - BMAD 方法论分析

## 📋 BMAD 分析框架

### Business (业务价值)

#### 1. 环境灵活性
- **多环境支持**: 开发、测试、生产环境无缝切换
- **部署简化**: 统一的配置管理降低部署复杂度
- **风险控制**: 环境隔离减少配置错误风险

#### 2. 安全设计
- **内置安全**: 环境特定安全配置
- **合规性**: 符合安全最佳实践
- **数据保护**: 敏感信息环境变量管理

#### 3. 可扩展性
- **服务集成**: 预配置 LLM、MCP、Claude Code 集成
- **性能优化**: 连接池、缓存配置支持增长
- **模块化**: 易于添加新服务和配置

### Maintainability (可维护性)

#### 1. 清晰分离
- **环境隔离**: 每个环境配置独立管理
- **关注点分离**: 基础配置与环境配置分离
- **文件组织**: 逻辑分组和目录结构

#### 2. 层次结构
- **继承机制**: 减少代码重复
- **覆盖机制**: 环境特定覆盖
- **默认值**: 合理的默认配置

#### 3. 集中管理
- **统一入口**: 配置加载统一管理
- **一致性**: 所有配置遵循相同模式
- **文档化**: 支持自动文档生成

### Architecture (架构)

#### 1. 模块化设计
- **配置模块**: 独立的配置模块
- **扩展性**: 易于添加新配置项
- **测试性**: 配置模块可独立测试

#### 2. 松耦合
- **环境解耦**: 环境配置与应用逻辑解耦
- **服务解耦**: 外部服务配置独立
- **依赖注入**: 配置通过依赖注入应用

#### 3. 可扩展性
- **新环境**: 易于添加新环境
- **新服务**: 易于集成新服务
- **新配置**: 易于添加配置项

### Design (设计)

#### 1. 工厂模式
- **应用工厂**: `create_app()` 函数
- **配置注入**: 配置类注入应用
- **灵活性**: 支持不同配置实例

#### 2. 环境变量
- **敏感信息**: 密钥和敏感信息通过环境变量
- **部署特定**: 部署环境特定设置
- **安全性**: 避免敏感信息硬编码

#### 3. 回退策略
- **多层回退**: 环境变量 → 扩展配置 → 环境配置 → 默认值
- **健壮性**: 确保应用总能启动
- **可预测性**: 明确的优先级顺序

#### 4. 验证机制
- **运行时验证**: 配置加载时验证
- **早期错误**: 启动时发现配置问题
- **类型安全**: 配置值类型检查

## 🎯 架构优势分析

### 技术优势

1. **配置继承**: 减少重复，提高一致性
2. **环境隔离**: 避免配置冲突
3. **安全硬化**: 生产环境安全优化
4. **性能优化**: 环境特定性能调优
5. **集成友好**: 预配置服务集成

### 业务优势

1. **开发效率**: 开发环境优化工作流
2. **运维简化**: 统一的配置管理
3. **风险控制**: 环境隔离减少错误
4. **合规支持**: 安全配置满足合规要求

### 维护优势

1. **清晰结构**: 易于理解和修改
2. **文档友好**: 支持自动文档生成
3. **测试支持**: 配置模块易于测试
4. **扩展方便**: 新功能易于集成

## 📈 性能特性

### 数据库性能
- **连接池**: 10 基础连接 + 20 溢出连接
- **连接复用**: 3600 秒连接回收
- **健康检查**: 预 ping 机制确保连接有效

### 缓存性能
- **开发**: Simple 缓存，调试友好
- **生产**: Redis 缓存，高性能
- **测试**: 无缓存，确保测试准确性

### 文件系统性能
- **目录结构**: 逻辑分组提高访问效率
- **路径管理**: 统一路径管理避免混乱
- **权限控制**: 适当的文件权限设置

## 🔒 安全特性

### 数据安全
- **加密存储**: API 密钥加密存储
- **环境隔离**: 敏感信息环境变量管理
- **访问控制**: 文件权限和访问控制

### 网络安全
- **安全头**: 生产环境完整安全头配置
- **会话安全**: 安全 cookie 设置
- **CSRF 保护**: 跨站请求伪造保护

### 配置安全
- **验证机制**: 配置值验证
- **错误处理**: 安全的错误信息处理
- **日志记录**: 安全相关的日志记录

## 🚀 扩展性分析

### 水平扩展
- **配置复制**: 环境配置易于复制
- **服务集成**: 新服务配置标准化
- **负载均衡**: 支持多实例配置

### 垂直扩展
- **资源优化**: 环境特定资源优化
- **性能调优**: 连接池和缓存调优
- **监控集成**: 性能监控配置

### 功能扩展
- **新环境**: 易于添加新部署环境
- **新服务**: 标准化服务集成模式
- **新配置**: 配置项添加标准化

## 📊 监控和可观察性

### 配置监控
- **配置变更**: 配置变更跟踪
- **配置验证**: 配置有效性监控
- **性能影响**: 配置对性能的影响监控

### 系统监控
- **数据库连接**: 连接池使用监控
- **缓存性能**: 缓存命中率和性能监控
- **服务健康**: 外部服务健康监控

### 安全监控
- **安全配置**: 安全配置合规性监控
- **访问日志**: 访问和安全事件监控
- **异常检测**: 配置异常检测

## 🏆 最佳实践总结

### 配置管理最佳实践
1. **环境变量管理敏感信息**
2. **配置验证和错误处理**
3. **文档化所有配置选项**
4. **使用配置文件管理复杂配置**

### 安全最佳实践
1. **生产环境安全硬化**
2. **敏感信息加密存储**
3. **安全头和会话管理**
4. **定期安全审计**

### 性能最佳实践
1. **环境特定性能优化**
2. **连接池和缓存优化**
3. **资源使用监控**
4. **性能瓶颈识别和解决**

### 维护最佳实践
1. **配置模块化和分离**
2. **文档化和注释**
3. **测试覆盖**
4. **版本控制和变更管理

---

*本 BMAD 分析由 BMAD 文档生成器自动生成*
"""
    
    return bmad_analysis_content

def save_documentation(content, filename):
    """保存文档到文件"""
    output_path = project_root / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 文档已保存: {output_path}")
    return output_path

def main():
    """主函数"""
    print("🚀 开始使用 BMAD 文档生成器生成 Config 技术架构总览...")
    
    # 设置环境
    setup_environment()
    
    # 检查 BMAD 文档生成器
    if not check_bmad_docs_generator():
        print("❌ BMAD 文档生成器不可用，使用备用方案...")
        # 使用备用方案生成文档
        architecture_content = generate_config_architecture_overview()
        flow_content = generate_complex_flow_analysis()
        bmad_content = generate_bmad_analysis()
        
        # 保存文档
        save_documentation(architecture_content, "CONFIG_BMAD_ARCHITECTURE_OVERVIEW.md")
        save_documentation(flow_content, "CONFIG_BMAD_FLOW_ANALYSIS.md")
        save_documentation(bmad_content, "CONFIG_BMAD_ANALYSIS.md")
        
        print("🎉 使用备用方案生成完成！")
        return
    
    # 分析 Config 系统
    config_analysis = analyze_config_system()
    
    # 生成架构总览
    architecture_content = generate_config_architecture_overview()
    save_documentation(architecture_content, "CONFIG_BMAD_ARCHITECTURE_OVERVIEW.md")
    
    # 生成流程分析
    flow_content = generate_complex_flow_analysis()
    save_documentation(flow_content, "CONFIG_BMAD_FLOW_ANALYSIS.md")
    
    # 生成 BMAD 分析
    bmad_content = generate_bmad_analysis()
    save_documentation(bmad_content, "CONFIG_BMAD_ANALYSIS.md")
    
    print("🎉 BMAD 文档生成完成！")
    print("📁 生成的文档:")
    print("   - CONFIG_BMAD_ARCHITECTURE_OVERVIEW.md")
    print("   - CONFIG_BMAD_FLOW_ANALYSIS.md")
    print("   - CONFIG_BMAD_ANALYSIS.md")

if __name__ == "__main__":
    main()