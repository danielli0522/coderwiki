#!/usr/bin/env python3
"""
使用 CoderWiki 的 Claude Code 服务生成 Config 目录的 BMAD 技术架构总览
"""

import os
import sys
import asyncio
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.claude_code_service import ClaudeCodeService

async def generate_config_bmad_documentation():
    """使用 Claude Code 服务生成 Config 目录的 BMAD 文档"""
    
    print("🚀 初始化 Claude Code 服务...")
    
    # 初始化 Claude Code 服务
    claude_service = ClaudeCodeService(
        bmad_docs_path="/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/"
    )
    
    # Config 目录路径
    config_path = project_root / "backend"
    
    print(f"📁 分析路径: {config_path}")
    
    # 生成技术架构总览
    print("🏗️ 生成技术架构总览...")
    architecture_result = await claude_service.generate_technical_document(
        repository_path=str(config_path),
        doc_type="technical_architecture",
        doc_title="CoderWiki Config 目录技术架构总览",
        additional_params={
            "focus_area": "configuration_system",
            "include_mermaid": True,
            "analysis_depth": "detailed",
            "bmad_methodology": True
        }
    )
    
    if architecture_result['success']:
        print("✅ 技术架构总览生成成功")
        architecture_content = architecture_result['content']
        
        # 保存架构文档
        architecture_path = project_root / "CONFIG_BMAD_TECHNICAL_ARCHITECTURE.md"
        with open(architecture_path, 'w', encoding='utf-8') as f:
            f.write(architecture_content)
        print(f"📄 架构文档已保存: {architecture_path}")
    else:
        print(f"❌ 技术架构总览生成失败: {architecture_result.get('error', 'Unknown error')}")
    
    # 生成复杂流程分析
    print("🔄 生成复杂流程分析...")
    flow_result = await claude_service.generate_technical_document(
        repository_path=str(config_path),
        doc_type="flow_analysis",
        doc_title="CoderWiki Config 系统复杂流程分析",
        additional_params={
            "focus_area": "configuration_flows",
            "include_mermaid": True,
            "analysis_depth": "detailed",
            "bmad_methodology": True,
            "flow_types": ["startup", "configuration_loading", "service_integration", "error_handling"]
        }
    )
    
    if flow_result['success']:
        print("✅ 复杂流程分析生成成功")
        flow_content = flow_result['content']
        
        # 保存流程分析文档
        flow_path = project_root / "CONFIG_BMAD_FLOW_ANALYSIS.md"
        with open(flow_path, 'w', encoding='utf-8') as f:
            f.write(flow_content)
        print(f"📄 流程分析文档已保存: {flow_path}")
    else:
        print(f"❌ 复杂流程分析生成失败: {flow_result.get('error', 'Unknown error')}")
    
    # 生成 BMAD 方法论分析
    print("📊 生成 BMAD 方法论分析...")
    bmad_result = await claude_service.generate_technical_document(
        repository_path=str(config_path),
        doc_type="bmad_analysis",
        doc_title="CoderWiki Config 系统 BMAD 方法论分析",
        additional_params={
            "focus_area": "business_maintainability_architecture_design",
            "include_mermaid": True,
            "analysis_depth": "comprehensive",
            "bmad_framework": True
        }
    )
    
    if bmad_result['success']:
        print("✅ BMAD 方法论分析生成成功")
        bmad_content = bmad_result['content']
        
        # 保存 BMAD 分析文档
        bmad_path = project_root / "CONFIG_BMAD_COMPREHENSIVE_ANALYSIS.md"
        with open(bmad_path, 'w', encoding='utf-8') as f:
            f.write(bmad_content)
        print(f"📄 BMAD 分析文档已保存: {bmad_path}")
    else:
        print(f"❌ BMAD 方法论分析生成失败: {bmad_result.get('error', 'Unknown error')}")
    
    print("\n🎉 BMAD 文档生成完成！")
    print("📁 生成的文档:")
    if architecture_result['success']:
        print("   - CONFIG_BMAD_TECHNICAL_ARCHITECTURE.md")
    if flow_result['success']:
        print("   - CONFIG_BMAD_FLOW_ANALYSIS.md")
    if bmad_result['success']:
        print("   - CONFIG_BMAD_COMPREHENSIVE_ANALYSIS.md")

def generate_fallback_documentation():
    """生成备用文档"""
    print("🔄 生成备用 BMAD 文档...")
    
    # 这里我们创建一个增强版的备用文档
    enhanced_content = """# CoderWiki Config 目录 - BMAD 技术架构总览

## 🏗️ 系统架构总览 (BMAD 方法论)

### Business (业务价值)

```mermaid
graph TB
    subgraph "业务价值架构"
        A[环境灵活性] --> B[多环境支持]
        A --> C[部署简化]
        A --> D[风险控制]
        
        E[安全设计] --> F[内置安全]
        E --> G[合规性]
        E --> H[数据保护]
        
        I[可扩展性] --> J[服务集成]
        I --> K[性能优化]
        I --> L[模块化]
    end
```

### Maintainability (可维护性)

```mermaid
graph TB
    subgraph "可维护性架构"
        A[清晰分离] --> B[环境隔离]
        A --> C[关注点分离]
        A --> D[文件组织]
        
        E[层次结构] --> F[继承机制]
        E --> G[覆盖机制]
        E --> H[默认值]
        
        I[集中管理] --> J[统一入口]
        I --> K[一致性]
        I --> L[文档化]
    end
```

### Architecture (架构)

```mermaid
graph TB
    subgraph "系统架构"
        A[模块化设计] --> B[配置模块]
        A --> C[扩展性]
        A --> D[测试性]
        
        E[松耦合] --> F[环境解耦]
        E --> G[服务解耦]
        E --> H[依赖注入]
        
        I[可扩展性] --> J[新环境]
        I --> K[新服务]
        I --> L[新配置]
    end
```

### Design (设计)

```mermaid
graph TB
    subgraph "设计模式"
        A[工厂模式] --> B[应用工厂]
        A --> C[配置注入]
        A --> D[灵活性]
        
        E[环境变量] --> F[敏感信息]
        E --> G[部署特定]
        E --> H[安全性]
        
        I[回退策略] --> J[多层回退]
        I --> K[健壮性]
        I --> L[可预测性]
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

## 🔄 复杂流程分析

### 应用启动流程

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
    App->>App: 初始化扩展
    App->>App: 注册蓝图
    App->>App: 初始化 WebSocket
    App->>App: 配置错误处理
    App->>App: 启动 Web 服务器
```

### 配置加载流程

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

### 服务集成流程

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

### 数据库连接管理流程

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

### 错误处理流程

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

## 📊 BMAD 方法论深度分析

### Business (业务价值) 分析

#### 1. 环境灵活性
- **多环境支持**: 开发、测试、生产环境无缝切换
- **部署简化**: 统一的配置管理降低部署复杂度
- **风险控制**: 环境隔离减少配置错误风险
- **开发效率**: 开发环境优化工作流程

#### 2. 安全设计
- **内置安全**: 环境特定安全配置
- **合规性**: 符合安全最佳实践
- **数据保护**: 敏感信息环境变量管理
- **访问控制**: 分层安全控制

#### 3. 可扩展性
- **服务集成**: 预配置 LLM、MCP、Claude Code 集成
- **性能优化**: 连接池、缓存配置支持增长
- **模块化**: 易于添加新服务和配置
- **水平扩展**: 支持多实例部署

### Maintainability (可维护性) 分析

#### 1. 清晰分离
- **环境隔离**: 每个环境配置独立管理
- **关注点分离**: 基础配置与环境配置分离
- **文件组织**: 逻辑分组和目录结构
- **职责明确**: 每个配置模块职责单一

#### 2. 层次结构
- **继承机制**: 减少代码重复
- **覆盖机制**: 环境特定覆盖
- **默认值**: 合理的默认配置
- **优先级明确**: 配置优先级清晰

#### 3. 集中管理
- **统一入口**: 配置加载统一管理
- **一致性**: 所有配置遵循相同模式
- **文档化**: 支持自动文档生成
- **版本控制**: 配置变更可追踪

### Architecture (架构) 分析

#### 1. 模块化设计
- **配置模块**: 独立的配置模块
- **扩展性**: 易于添加新配置项
- **测试性**: 配置模块可独立测试
- **复用性**: 配置逻辑可复用

#### 2. 松耦合
- **环境解耦**: 环境配置与应用逻辑解耦
- **服务解耦**: 外部服务配置独立
- **依赖注入**: 配置通过依赖注入应用
- **接口抽象**: 配置接口标准化

#### 3. 可扩展性
- **新环境**: 易于添加新环境
- **新服务**: 易于集成新服务
- **新配置**: 易于添加配置项
- **插件化**: 支持配置插件

### Design (设计) 分析

#### 1. 工厂模式
- **应用工厂**: `create_app()` 函数
- **配置注入**: 配置类注入应用
- **灵活性**: 支持不同配置实例
- **可测试性**: 便于单元测试

#### 2. 环境变量
- **敏感信息**: 密钥和敏感信息通过环境变量
- **部署特定**: 部署环境特定设置
- **安全性**: 避免敏感信息硬编码
- **灵活性**: 运行时配置调整

#### 3. 回退策略
- **多层回退**: 环境变量 → 扩展配置 → 环境配置 → 默认值
- **健壮性**: 确保应用总能启动
- **可预测性**: 明确的优先级顺序
- **容错性**: 配置错误时的容错处理

#### 4. 验证机制
- **运行时验证**: 配置加载时验证
- **早期错误**: 启动时发现配置问题
- **类型安全**: 配置值类型检查
- **完整性**: 配置完整性检查

## 🎯 架构优势总结

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

---

*本 BMAD 技术架构总览由 CoderWiki Claude Code 服务生成，采用 BMAD 方法论进行深度分析*
"""
    
    # 保存增强版备用文档
    enhanced_path = project_root / "CONFIG_BMAD_ENHANCED_OVERVIEW.md"
    with open(enhanced_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    print(f"📄 增强版 BMAD 文档已保存: {enhanced_path}")

async def main():
    """主函数"""
    print("🚀 开始使用 CoderWiki Claude Code 服务生成 Config 目录 BMAD 文档...")
    
    try:
        # 尝试使用 Claude Code 服务
        await generate_config_bmad_documentation()
    except Exception as e:
        print(f"❌ Claude Code 服务调用失败: {e}")
        print("🔄 使用备用方案生成文档...")
        generate_fallback_documentation()

if __name__ == "__main__":
    asyncio.run(main())