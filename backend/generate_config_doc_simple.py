"""
生成Config目录文档的脚本
"""

import os

def generate_config_document():
    """生成Config目录文档"""

    document = """# CoderWiki Config目录配置文档

## 概述

CoderWiki项目采用分层配置架构，通过不同的配置文件管理开发、测试和生产环境的设置。本文档详细介绍了Config目录的结构、配置项和使用方法。

## 目录结构

```
config/
├── development.py    # 开发环境配置
├── production.py     # 生产环境配置
└── testing.py        # 测试环境配置
```

## 配置架构

### 基础配置类

所有环境配置都继承自`backend.config`模块中的基础配置类：

- `DevelopmentConfig`: 开发环境基础配置
- `ProductionConfig`: 生产环境基础配置
- `TestingConfig`: 测试环境基础配置

### 环境特定配置

#### 1. 开发环境配置 (DevConfig)

```python
class DevConfig(DevelopmentConfig):
    # 开发环境配置

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki:coderwiki@localhost/coderwiki_dev'

    # 调试配置
    DEBUG = True
    FLASK_DEBUG = True

    # LLM配置
    LLM_MODEL = 'gpt-3.5-turbo'
    LLM_TEMPERATURE = 0.7

    # 日志配置
    LOG_LEVEL = 'DEBUG'
    LOG_TO_FILE = False

    # 安全配置
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True

    # 文件上传
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

    # Git仓库路径
    GIT_REPOS_PATH = '/tmp/coderwiki_repos_dev'

    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
```

**特点：**
- 启用调试模式，便于开发调试
- 使用开发数据库，避免影响生产数据
- 较宽松的安全设置，便于开发测试
- 大文件上传限制，便于测试大文件功能

#### 2. 生产环境配置 (ProdConfig)

```python
class ProdConfig(ProductionConfig):
    # 生产环境配置

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki:coderwiki@localhost/coderwiki_prod'

    # 安全配置
    DEBUG = False
    FLASK_DEBUG = False

    # 日志配置
    LOG_LEVEL = 'WARNING'
    LOG_TO_FILE = True

    # 会话配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1小时

    # 文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Git仓库路径
    GIT_REPOS_PATH = '/var/opt/coderwiki/repos'

    # 缓存配置
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300

    # 安全头
    SECURE_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }

    # 监控配置
    SENTRY_DSN = None
    ENABLE_METRICS = True
```

**特点：**
- 严格的安全设置，禁用调试模式
- 使用Redis缓存提高性能
- 完整的安全头配置
- 生产级监控和日志
- 合理的文件上传限制

#### 3. 测试环境配置 (TestConfig)

```python
class TestConfig(TestingConfig):
    # 测试环境配置

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki:coderwiki@localhost/coderwiki_test'

    # 测试配置
    TESTING = True
    WTF_CSRF_ENABLED = False

    # 会话配置
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False

    # 文件上传
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB

    # Git仓库路径
    GIT_REPOS_PATH = '/tmp/coderwiki_repos_test'

    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 0

    # 日志配置
    LOG_LEVEL = 'CRITICAL'

    # 服务器配置
    SERVER_NAME = 'localhost:5000'

    # LLM配置
    LLM_MODEL = 'test-model'
    LLM_TEMPERATURE = 0.0

    # 邮件配置
    MAIL_SUPPRESS_SEND = True

    # 密钥配置
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_SECRET_KEY = 'test-csrf-secret-key'
```

**特点：**
- 测试模式启用，禁用CSRF保护
- 使用测试数据库，避免污染生产数据
- 最小化的日志输出
- 禁用邮件发送功能
- 使用测试专用密钥

## 配置项对比

### 数据库配置

| 环境 | 数据库URI | 用途 |
|------|----------|------|
| 开发 | `coderwiki_dev` | 开发调试 |
| 测试 | `coderwiki_test` | 自动化测试 |
| 生产 | `coderwiki_prod` | 生产环境 |

### 调试与日志

| 配置项 | 开发环境 | 测试环境 | 生产环境 |
|--------|----------|----------|----------|
| DEBUG | True | False | False |
| LOG_LEVEL | DEBUG | CRITICAL | WARNING |
| LOG_TO_FILE | False | False | True |

### 安全配置

| 配置项 | 开发环境 | 测试环境 | 生产环境 |
|--------|----------|----------|----------|
| SESSION_COOKIE_SECURE | False | False | True |
| WTF_CSRF_ENABLED | True | False | True |
| MAX_CONTENT_LENGTH | 50MB | 1MB | 16MB |

### 缓存配置

| 配置项 | 开发环境 | 测试环境 | 生产环境 |
|--------|----------|----------|----------|
| CACHE_TYPE | simple | simple | redis |
| CACHE_DEFAULT_TIMEOUT | 300s | 0s | 300s |

## 使用方法

### 1. 环境变量配置

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

### 2. 代码中加载配置

```python
from flask import Flask
import os

app = Flask(__name__)

# 根据环境变量加载配置
config_module = os.environ.get('CONFIG_MODULE', 'config.development')
app.config.from_object(config_module)
```

### 3. 配置访问

```python
# 访问配置项
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
debug_mode = app.config['DEBUG']
max_upload_size = app.config['MAX_CONTENT_LENGTH']
```

## 最佳实践

### 1. 配置管理

- **敏感信息**：不要在配置文件中硬编码敏感信息，使用环境变量
- **环境隔离**：确保不同环境的配置完全隔离
- **版本控制**：配置文件应该纳入版本控制，但敏感信息除外

### 2. 安全建议

- **生产环境**：始终禁用调试模式，启用所有安全功能
- **密钥管理**：使用强密码和密钥，定期更换
- **权限控制**：限制配置文件的访问权限

### 3. 性能优化

- **缓存策略**：生产环境使用Redis等高性能缓存
- **日志级别**：生产环境使用适当的日志级别避免性能影响
- **资源限制**：设置合理的文件上传和内存使用限制

## 扩展配置

### 1. 自定义配置

```python
# 在基础配置类中添加自定义配置
class CustomConfig:
    CUSTOM_SETTING = 'default_value'

# 在环境配置中覆盖
class DevConfig(DevelopmentConfig, CustomConfig):
    CUSTOM_SETTING = 'dev_value'
```

### 2. 条件配置

```python
import os

class DynamicConfig:
    # 根据环境变量动态设置
    API_URL = os.environ.get('API_URL', 'https://api.example.com')

    # 根据条件启用功能
    ENABLE_FEATURE_X = os.environ.get('ENABLE_FEATURE_X', 'false').lower() == 'true'
```

## 故障排除

### 常见问题

1. **配置加载失败**
   - 检查配置文件路径是否正确
   - 确认环境变量设置

2. **数据库连接错误**
   - 验证数据库URI格式
   - 检查数据库服务状态

3. **权限问题**
   - 确认文件上传目录权限
   - 检查Git仓库目录权限

### 调试方法

```python
# 调试配置加载
print(f"Current config: {app.config}")
print(f"Environment: {app.env}")

# 检查特定配置
if app.config['DEBUG']:
    print("Debug mode is enabled")
```

## 总结

CoderWiki的配置系统采用了分层架构，通过环境隔离和继承机制实现了灵活的配置管理。每个环境都有其特定的配置需求，从开发环境的便利性到生产环境的安全性，都得到了充分考虑。

这种配置架构的优势：

1. **环境隔离**：不同环境完全独立，避免配置冲突
2. **继承机制**：减少重复配置，提高维护性
3. **安全可控**：生产环境严格的安全设置
4. **易于扩展**：支持自定义配置和动态配置
5. **最佳实践**：遵循Flask应用的配置最佳实践

通过合理的配置管理，CoderWiki能够在不同环境中稳定运行，同时保持开发效率和生产安全性的平衡。

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
    print("\n文档开头预览:")
    print(document[:500] + "...")
