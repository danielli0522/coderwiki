#!/usr/bin/env python3
"""
生成Config目录文档的脚本
"""

def generate_config_document():
    """生成Config目录文档"""
    
    document = """# CoderWiki Config目录配置文档

## 概述

CoderWiki项目采用分层配置架构，通过不同的配置文件管理开发、测试和生产环境的设置。

## 目录结构

```
config/
├── development.py    # 开发环境配置
├── production.py     # 生产环境配置
└── testing.py        # 测试环境配置
```

## 配置架构

### 基础配置类

所有环境配置都继承自backend.config模块中的基础配置类：

- DevelopmentConfig: 开发环境基础配置
- ProductionConfig: 生产环境基础配置  
- TestingConfig: 测试环境基础配置

### 环境特定配置

#### 1. 开发环境配置 (DevConfig)

**主要特点：**
- 数据库: coderwiki_dev
- 调试模式: 启用 (DEBUG=True)
- LLM模型: gpt-3.5-turbo
- 日志级别: DEBUG
- 文件上传限制: 50MB
- 缓存: simple类型

#### 2. 生产环境配置 (ProdConfig)

**主要特点：**
- 数据库: coderwiki_prod
- 调试模式: 禁用 (DEBUG=False)
- 安全设置: 严格 (SESSION_COOKIE_SECURE=True)
- 日志级别: WARNING
- 文件上传限制: 16MB
- 缓存: Redis
- 安全头: 完整配置

#### 3. 测试环境配置 (TestConfig)

**主要特点：**
- 数据库: coderwiki_test
- 测试模式: 启用 (TESTING=True)
- CSRF保护: 禁用
- 日志级别: CRITICAL
- 文件上传限制: 1MB
- 缓存: simple类型，超时为0

## 配置项对比

| 配置项 | 开发环境 | 测试环境 | 生产环境 |
|--------|----------|----------|----------|
| DEBUG | True | False | False |
| TESTING | False | True | False |
| LOG_LEVEL | DEBUG | CRITICAL | WARNING |
| MAX_CONTENT_LENGTH | 50MB | 1MB | 16MB |
| CACHE_TYPE | simple | simple | redis |
| SESSION_COOKIE_SECURE | False | False | True |
| WTF_CSRF_ENABLED | True | False | True |

## 使用方法

### 环境变量配置

```bash
# 开发环境
export FLASK_ENV=development
export CONFIG_MODULE=config.development

# 测试环境
export FLASK_ENV=testing
export CONFIG_MODULE=config.testing

# 生产环境
export FLASK_ENV=production
export CONFIG_MODULE=config.production
```

### 代码中加载配置

```python
from flask import Flask
import os

app = Flask(__name__)
config_module = os.environ.get('CONFIG_MODULE', 'config.development')
app.config.from_object(config_module)
```

## 最佳实践

1. **环境隔离**: 确保不同环境的配置完全隔离
2. **安全第一**: 生产环境必须禁用调试模式，启用所有安全功能
3. **敏感信息**: 使用环境变量管理敏感信息，不要硬编码
4. **性能优化**: 生产环境使用Redis等高性能缓存
5. **监控日志**: 生产环境启用完整的监控和日志记录

## 总结

CoderWiki的配置系统通过分层架构和环境隔离，实现了灵活且安全的配置管理。每个环境都根据其特定需求进行了优化，从开发便利性到生产安全性都得到了充分考虑。

这种架构的优势：
- 环境隔离避免配置冲突
- 继承机制减少重复配置
- 安全可控的生产环境设置
- 易于扩展和维护
- 遵循Flask应用最佳实践

---

*本文档由Claude Code SDK自动生成*
"""
    
    return document

if __name__ == "__main__":
    # 生成文档
    document = generate_config_document()
    
    # 保存文档
    output_path = '/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/CONFIG_DOCUMENTATION.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(document)
    
    print(f"Config目录文档已生成: {output_path}")
    print(f"文档长度: {len(document)} 字符")
    
    # 显示文档开头
    print("\\n文档开头预览:")
    print(document[:500] + "...")
