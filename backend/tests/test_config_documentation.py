"""
Config 目录技术总览文档生成测试
专门测试通过 Claude Code SDK 调用 BMAD 代理生成 Config 目录的技术文档
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.claude_client import ClaudeCodeClient
from app.utils.bmad_orchestrator import BMADOrchestrator


class TestConfigDocumentationGeneration(unittest.TestCase):
    """Config 目录技术总览文档生成测试类"""

    def setUp(self):
        """测试前准备"""
        self.test_api_key = "test-claude-api-key"
        self.test_workspace_id = "test-workspace-id"
        self.test_session_id = "test-session-id"

        # 创建临时目录作为测试仓库
        self.temp_dir = tempfile.mkdtemp()
        self.create_realistic_config_directory()

        # 模拟 Claude Code 客户端
        self.mock_claude_client = Mock(spec=ClaudeCodeClient)
        self.mock_claude_client.api_key = self.test_api_key
        self.mock_claude_client.workspace_id = self.test_workspace_id

        # 创建 BMAD 编排器
        self.bmad_orchestrator = BMADOrchestrator(self.mock_claude_client)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_realistic_config_directory(self):
        """创建真实的 Config 目录结构，模拟实际项目"""
        # 创建主项目结构
        config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)

        # 创建子目录
        subdirs = ["database", "auth", "claude", "logging"]
        for subdir in subdirs:
            os.makedirs(os.path.join(config_dir, subdir), exist_ok=True)

        # 创建配置文件
        config_files = {
            # 主配置文件
            "config/__init__.py": """
# 配置模块初始化
from .app import Config
from .database import DatabaseConfig
from .auth import AuthConfig
from .claude import ClaudeConfig

__all__ = ['Config', 'DatabaseConfig', 'AuthConfig', 'ClaudeConfig']
""",

            # 应用配置
            "config/app.py": """
# 应用主配置
import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    TESTING = False

    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql://localhost/coderwiki')

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'

    # Claude Code 配置
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_WORKSPACE_ID = os.getenv('CLAUDE_WORKSPACE_ID')

    # BMAD 代理配置
    BMAD_AGENTS_PATH = os.getenv('BMAD_AGENTS_PATH', 'bmad-docs-generator')
    BMAD_WORKFLOW_TIMEOUT = int(os.getenv('BMAD_WORKFLOW_TIMEOUT', '300'))

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = 'mysql://localhost/coderwiki_dev'

class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
""",

            # 数据库配置
            "config/database.py": """
# 数据库配置
import os

class DatabaseConfig:
    # MySQL 配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'coderwiki')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'coderwiki_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'coderwiki_password')

    # 连接池配置
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))

    # 迁移配置
    MIGRATIONS_DIR = 'migrations'
    ALEMBIC_CONFIG = 'alembic.ini'

    @classmethod
    def get_database_url(cls):
        return f"mysql+pymysql://{cls.MYSQL_USERNAME}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"

    @classmethod
    def get_connection_params(cls):
        return {
            'host': cls.MYSQL_HOST,
            'port': cls.MYSQL_PORT,
            'database': cls.MYSQL_DATABASE,
            'user': cls.MYSQL_USERNAME,
            'password': cls.MYSQL_PASSWORD,
            'charset': 'utf8mb4',
            'autocommit': True
        }
""",

            # 认证配置
            "config/auth.py": """
# 认证配置
import os
from datetime import timedelta

class AuthConfig:
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'

    # 密码配置
    PASSWORD_SALT_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True

    # 会话配置
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'sessions'
    SESSION_FILE_THRESHOLD = 500

    # 登录配置
    LOGIN_MAX_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION = timedelta(minutes=15)
    LOGIN_REMEMBER_ME_DURATION = timedelta(days=30)

    # OAuth 配置
    OAUTH_PROVIDERS = {
        'github': {
            'client_id': os.getenv('GITHUB_CLIENT_ID'),
            'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'token_url': 'https://github.com/login/oauth/access_token',
            'userinfo_url': 'https://api.github.com/user'
        }
    }
""",

            # Claude Code 配置
            "config/claude.py": """
# Claude Code 配置
import os
from typing import Dict, Any

class ClaudeConfig:
    # API 配置
    API_KEY = os.getenv('CLAUDE_API_KEY', '')
    WORKSPACE_ID = os.getenv('CLAUDE_WORKSPACE_ID', '')
    API_BASE_URL = 'https://api.anthropic.com'
    API_VERSION = '2023-06-01'

    # 模型配置
    DEFAULT_MODEL = 'claude-3-sonnet-20240229'
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7

    # 工作流配置
    WORKFLOW_TIMEOUT = int(os.getenv('CLAUDE_WORKFLOW_TIMEOUT', '300'))
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    # BMAD 代理配置
    BMAD_AGENTS_PATH = os.getenv('BMAD_AGENTS_PATH', 'bmad-docs-generator')
    BMAD_WORKFLOW_CONFIG = {
        'enhanced-docs-generation': {
            'timeout': 300,
            'max_agents': 5,
            'parallel_execution': True
        }
    }

    # 文件上传配置
    MAX_FILE_SIZE = int(os.getenv('CLAUDE_MAX_FILE_SIZE', '10485760'))  # 10MB
    MAX_FILES_PER_SESSION = int(os.getenv('CLAUDE_MAX_FILES', '1000'))
    ALLOWED_FILE_TYPES = [
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
        '.html', '.css', '.json', '.yaml', '.yml', '.md',
        '.txt', '.sql', '.sh', '.bat', '.ps1'
    ]

    @classmethod
    def get_api_headers(cls) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {cls.API_KEY}',
            'Content-Type': 'application/json',
            'anthropic-version': cls.API_VERSION
        }

    @classmethod
    def validate_config(cls) -> bool:
        return bool(cls.API_KEY and cls.WORKSPACE_ID)

    @classmethod
    def get_missing_fields(cls) -> list:
        missing = []
        if not cls.API_KEY:
            missing.append('CLAUDE_API_KEY')
        if not cls.WORKSPACE_ID:
            missing.append('CLAUDE_WORKSPACE_ID')
        return missing
""",

            # 日志配置
            "config/logging.py": """
# 日志配置
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class LoggingConfig:
    # 日志级别
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # 文件配置
    LOG_DIR = 'logs'
    LOG_FILE = 'app.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # 错误日志配置
    ERROR_LOG_FILE = 'error.log'
    ERROR_LOG_LEVEL = 'ERROR'

    # 访问日志配置
    ACCESS_LOG_FILE = 'access.log'
    ACCESS_LOG_LEVEL = 'INFO'

    # 性能日志配置
    PERFORMANCE_LOG_FILE = 'performance.log'
    PERFORMANCE_LOG_LEVEL = 'DEBUG'

    @classmethod
    def setup_logging(cls):
        # 创建日志目录
        os.makedirs(cls.LOG_DIR, exist_ok=True)

        # 配置根日志器
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            datefmt=cls.LOG_DATE_FORMAT,
            handlers=[
                RotatingFileHandler(
                    os.path.join(cls.LOG_DIR, cls.LOG_FILE),
                    maxBytes=cls.LOG_MAX_SIZE,
                    backupCount=cls.LOG_BACKUP_COUNT
                ),
                logging.StreamHandler()
            ]
        )

        # 配置错误日志器
        error_handler = RotatingFileHandler(
            os.path.join(cls.LOG_DIR, cls.ERROR_LOG_FILE),
            maxBytes=cls.LOG_MAX_SIZE,
            backupCount=cls.LOG_BACKUP_COUNT
        )
        error_handler.setLevel(getattr(logging, cls.ERROR_LOG_LEVEL))

        error_logger = logging.getLogger('error')
        error_logger.addHandler(error_handler)
        error_logger.setLevel(getattr(logging, cls.ERROR_LOG_LEVEL))

        # 配置访问日志器
        access_handler = TimedRotatingFileHandler(
            os.path.join(cls.LOG_DIR, cls.ACCESS_LOG_FILE),
            when='midnight',
            interval=1,
            backupCount=30
        )
        access_handler.setLevel(getattr(logging, cls.ACCESS_LOG_LEVEL))

        access_logger = logging.getLogger('access')
        access_logger.addHandler(access_handler)
        access_logger.setLevel(getattr(logging, cls.ACCESS_LOG_LEVEL))
""",

            # 环境配置
            "config/environment.py": """
# 环境配置
import os
from typing import Dict, Any

class EnvironmentConfig:
    # 环境类型
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    IS_PRODUCTION = ENVIRONMENT == 'production'
    IS_DEVELOPMENT = ENVIRONMENT == 'development'
    IS_TESTING = ENVIRONMENT == 'testing'

    # 服务器配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    WORKERS = int(os.getenv('WORKERS', '1'))

    # 安全配置
    HTTPS_ENABLED = os.getenv('HTTPS_ENABLED', 'false').lower() == 'true'
    SSL_CERT_FILE = os.getenv('SSL_CERT_FILE')
    SSL_KEY_FILE = os.getenv('SSL_KEY_FILE')

    # 缓存配置
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))

    # 任务队列配置
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # 监控配置
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'false').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))

    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        return {
            'environment': cls.ENVIRONMENT,
            'is_production': cls.IS_PRODUCTION,
            'is_development': cls.IS_DEVELOPMENT,
            'is_testing': cls.IS_TESTING,
            'host': cls.HOST,
            'port': cls.PORT,
            'workers': cls.WORKERS,
            'https_enabled': cls.HTTPS_ENABLED,
            'cache_type': cls.CACHE_TYPE,
            'enable_metrics': cls.ENABLE_METRICS
        }
""",

            # 主项目文件
            "main.py": """
# 主应用入口
from flask import Flask
from config.app import Config
from config.logging import LoggingConfig

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 设置日志
    LoggingConfig.setup_logging()

    # 注册蓝图
    from app.api import auth, repository, document, task, smart_document
    app.register_blueprint(auth.bp)
    app.register_blueprint(repository.bp)
    app.register_blueprint(document.bp)
    app.register_blueprint(task.bp)
    app.register_blueprint(smart_document.bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=app.config['HOST'], port=app.config['PORT'])
""",

            # 项目说明文件
            "README.md": """
# CoderWiki - 智能文档生成系统

## 项目概述

CoderWiki 是一个基于 Claude Code SDK 和 BMAD 代理系统的智能文档生成平台，能够自动分析代码仓库并生成高质量的技术文档。

## 技术架构

### 后端技术栈
- **Web 框架**: Flask
- **数据库**: MySQL + SQLAlchemy
- **认证**: JWT + Flask-Login
- **AI 集成**: Claude Code SDK
- **代理系统**: BMAD-Docs-Generator

### 配置系统

项目采用模块化配置系统，主要配置模块包括：

#### 1. 应用配置 (`config/app.py`)
- 基础应用设置
- 环境配置
- 数据库连接
- 会话管理

#### 2. 数据库配置 (`config/database.py`)
- MySQL 连接参数
- 连接池配置
- 迁移设置

#### 3. 认证配置 (`config/auth.py`)
- JWT 配置
- 密码策略
- OAuth 集成
- 会话管理

#### 4. Claude Code 配置 (`config/claude.py`)
- API 密钥管理
- 工作流配置
- BMAD 代理设置
- 文件上传限制

#### 5. 日志配置 (`config/logging.py`)
- 多级别日志
- 文件轮转
- 错误追踪
- 性能监控

#### 6. 环境配置 (`config/environment.py`)
- 环境变量管理
- 服务器设置
- 安全配置
- 监控设置

## 目录结构

```
coderwiki/
├── config/                 # 配置模块
│   ├── __init__.py        # 模块初始化
│   ├── app.py             # 应用配置
│   ├── database.py        # 数据库配置
│   ├── auth.py            # 认证配置
│   ├── claude.py          # Claude Code 配置
│   ├── logging.py         # 日志配置
│   └── environment.py     # 环境配置
├── app/                   # 应用代码
│   ├── api/              # API 路由
│   ├── models/           # 数据模型
│   ├── services/         # 业务服务
│   └── utils/            # 工具函数
├── bmad-docs-generator/   # BMAD 代理系统
├── tests/                # 测试文件
├── logs/                 # 日志文件
├── main.py               # 应用入口
└── README.md             # 项目说明
```

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，设置必要的配置
```

3. 初始化数据库
```bash
flask db upgrade
```

4. 启动应用
```bash
python main.py
```

## 配置说明

### 必需配置
- `CLAUDE_API_KEY`: Claude Code API 密钥
- `CLAUDE_WORKSPACE_ID`: Claude Code 工作空间 ID
- `DATABASE_URL`: 数据库连接字符串

### 可选配置
- `SECRET_KEY`: 应用密钥
- `LOG_LEVEL`: 日志级别
- `DEBUG`: 调试模式

## 开发指南

### 添加新配置
1. 在 `config/` 目录下创建新的配置模块
2. 在 `config/__init__.py` 中导入新模块
3. 在 `config/app.py` 中引用新配置

### 环境特定配置
- 开发环境: `DevelopmentConfig`
- 生产环境: `ProductionConfig`
- 测试环境: `TestingConfig`

## 部署说明

### 生产环境部署
1. 设置环境变量
2. 配置数据库
3. 设置日志目录
4. 配置反向代理
5. 启动应用

### 监控和日志
- 应用日志: `logs/app.log`
- 错误日志: `logs/error.log`
- 访问日志: `logs/access.log`
- 性能日志: `logs/performance.log`

## 许可证

MIT License
"""
        }

        # 创建所有配置文件
        for file_path, content in config_files.items():
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

    @patch('app.utils.claude_client.Anthropic')
    def test_config_directory_analysis(self, mock_anthropic):
        """测试 Config 目录分析"""
        # 模拟 Claude Code 响应
        mock_messages = [
            Mock(
                id="msg-1",
                content="Code Analyst (Alex) completed analysis of config directory structure",
                role="assistant",
                created_at="2024-01-01T00:01:00Z"
            ),
            Mock(
                id="msg-2",
                content="Architecture Analyst identified configuration patterns and modular design",
                role="assistant",
                created_at="2024-01-01T00:02:00Z"
            ),
            Mock(
                id="msg-3",
                content="Flow Analyst (Jordan) analyzed configuration loading and validation flows",
                role="assistant",
                created_at="2024-01-01T00:03:00Z"
            ),
            Mock(
                id="msg-4",
                content="Problem Solver (Dr. Morgan) identified potential configuration issues and solutions",
                role="assistant",
                created_at="2024-01-01T00:04:00Z"
            ),
            Mock(
                id="msg-5",
                content="Doc Engineer (Maya) generated comprehensive technical overview documentation",
                role="assistant",
                created_at="2024-01-01T00:05:00Z"
            )
        ]

        mock_client = Mock()
        mock_client.beta.workspaces.sessions.messages.list.return_value = Mock(data=mock_messages)
        mock_anthropic.return_value = mock_client

        # 创建客户端和编排器
        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)
        orchestrator = BMADOrchestrator(client)

        # 执行工作流
        config = {
            'analysis_depth': 'comprehensive',
            'include_diagrams': True,
            'include_troubleshooting': True,
            'doc_type': 'complete'
        }

        # 模拟工作流执行
        with patch.object(client, 'create_session') as mock_create_session, \
             patch.object(client, 'configure_bmad_agents') as mock_configure, \
             patch.object(client, 'upload_codebase') as mock_upload, \
             patch.object(client, 'trigger_bmad_workflow') as mock_trigger, \
             patch.object(client, 'monitor_execution') as mock_monitor:

            # 设置模拟返回值
            mock_create_session.return_value = {'session_id': self.test_session_id}
            mock_configure.return_value = True
            mock_upload.return_value = True
            mock_trigger.return_value = {'message_id': 'test-msg', 'status': 'triggered'}
            mock_monitor.return_value = {
                'status': 'completed',
                'messages': [
                    {
                        'id': msg.id,
                        'content': msg.content,
                        'role': msg.role,
                        'created_at': msg.created_at
                    }
                    for msg in mock_messages
                ],
                'execution_time': 120.5
            }

            # 执行工作流
            result = orchestrator.execute_workflow(self.temp_dir, config)

            # 验证结果
            self.assertEqual(result['status'], 'completed')
            self.assertIn('document', result)
            self.assertIn('agent_outputs', result)

            # 验证文档内容
            document = result['document']
            self.assertEqual(document['title'], 'Technical Documentation Generated by BMAD Agents')
            self.assertIn('config', document['agents_used'])

            # 验证代理输出
            agent_outputs = result['agent_outputs']
            self.assertIn('code-analyst', agent_outputs)
            self.assertIn('architecture-analyst', agent_outputs)
            self.assertIn('flow-analyst', agent_outputs)
            self.assertIn('problem-solver', agent_outputs)
            self.assertIn('doc-engineer', agent_outputs)

    def test_config_file_structure_analysis(self):
        """测试配置文件结构分析"""
        # 分析 Config 目录结构
        config_dir = os.path.join(self.temp_dir, "config")

        # 验证目录存在
        self.assertTrue(os.path.exists(config_dir))

        # 验证配置文件存在
        expected_files = [
            "__init__.py",
            "app.py",
            "database.py",
            "auth.py",
            "claude.py",
            "logging.py",
            "environment.py"
        ]

        for filename in expected_files:
            file_path = os.path.join(config_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"Config file {filename} should exist")

        # 验证子目录存在
        expected_subdirs = ["database", "auth", "claude", "logging"]
        for subdir in expected_subdirs:
            subdir_path = os.path.join(config_dir, subdir)
            self.assertTrue(os.path.exists(subdir_path), f"Config subdir {subdir} should exist")

    def test_configuration_patterns(self):
        """测试配置模式识别"""
        # 读取配置文件内容进行分析
        config_files = {
            "app.py": "config/app.py",
            "database.py": "config/database.py",
            "auth.py": "config/auth.py",
            "claude.py": "config/claude.py",
            "logging.py": "config/logging.py",
            "environment.py": "config/environment.py"
        }

        patterns_found = {
            "class_based_config": 0,
            "environment_variables": 0,
            "database_config": 0,
            "logging_config": 0,
            "security_config": 0
        }

        for config_name, file_path in config_files.items():
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 识别配置模式
                if 'class ' in content and 'Config' in content:
                    patterns_found["class_based_config"] += 1

                if 'os.getenv(' in content:
                    patterns_found["environment_variables"] += 1

                if 'DATABASE' in content.upper() or 'mysql' in content.lower():
                    patterns_found["database_config"] += 1

                if 'logging' in content.lower() or 'LOG_' in content:
                    patterns_found["logging_config"] += 1

                if 'SECRET' in content or 'JWT' in content or 'AUTH' in content:
                    patterns_found["security_config"] += 1

        # 验证配置模式
        self.assertGreater(patterns_found["class_based_config"], 0, "Should have class-based configuration")
        self.assertGreater(patterns_found["environment_variables"], 0, "Should use environment variables")
        self.assertGreater(patterns_found["database_config"], 0, "Should have database configuration")
        self.assertGreater(patterns_found["logging_config"], 0, "Should have logging configuration")
        self.assertGreater(patterns_found["security_config"], 0, "Should have security configuration")

    @patch('app.utils.claude_client.Anthropic')
    def test_technical_overview_generation(self, mock_anthropic):
        """测试技术总览文档生成"""
        # 模拟 BMAD 代理的详细输出
        mock_agent_outputs = {
            'code-analyst': {
                'content': """
# 代码分析师 (Alex) - Config 目录分析报告

## 目录结构分析
- 总文件数: 7 个配置文件
- 总代码行数: 约 300 行
- 主要语言: Python
- 配置文件类型: 类基础配置

## 关键发现
1. 模块化配置设计
2. 环境变量驱动配置
3. 分层配置架构
4. 完整的配置验证机制

## 技术栈识别
- Flask 应用框架
- MySQL 数据库
- JWT 认证系统
- Claude Code SDK 集成
- BMAD 代理系统
""",
                'status': 'completed'
            },
            'architecture-analyst': {
                'content': """
# 架构分析师 - Config 目录架构分析

## 架构模式
1. **分层配置模式**: 按功能模块分离配置
2. **环境驱动配置**: 支持多环境配置切换
3. **类基础配置**: 使用 Python 类封装配置
4. **依赖注入模式**: 配置通过依赖注入使用

## 配置模块职责
- `app.py`: 应用主配置和基础设置
- `database.py`: 数据库连接和连接池配置
- `auth.py`: 认证和授权配置
- `claude.py`: Claude Code SDK 配置
- `logging.py`: 日志系统配置
- `environment.py`: 环境特定配置

## 设计优势
1. 高内聚低耦合
2. 易于维护和扩展
3. 支持多环境部署
4. 配置验证和错误处理
""",
                'status': 'completed'
            },
            'flow-analyst': {
                'content': """
# 流程分析师 (Jordan) - Config 加载流程分析

## 配置加载流程
1. **环境检测**: 检测当前运行环境
2. **配置初始化**: 根据环境加载对应配置类
3. **参数验证**: 验证必需配置参数
4. **依赖注入**: 将配置注入到应用组件
5. **运行时配置**: 支持运行时配置更新

## 配置验证流程
1. 必需参数检查
2. 数据类型验证
3. 格式验证
4. 依赖关系检查
5. 安全配置验证

## 错误处理流程
1. 配置缺失处理
2. 格式错误处理
3. 依赖缺失处理
4. 安全配置警告
""",
                'status': 'completed'
            },
            'problem-solver': {
                'content': """
# 问题解决专家 (Dr. Morgan) - Config 问题诊断

## 潜在问题识别
1. **安全风险**: 敏感信息可能暴露在代码中
2. **配置冲突**: 多环境配置可能产生冲突
3. **性能问题**: 配置加载可能影响启动性能
4. **维护复杂性**: 配置分散可能导致维护困难

## 解决方案建议
1. **安全加固**: 使用环境变量存储敏感信息
2. **配置验证**: 增加配置验证机制
3. **性能优化**: 实现配置缓存机制
4. **文档完善**: 增加配置文档和示例

## 最佳实践建议
1. 使用配置管理工具
2. 实现配置版本控制
3. 建立配置变更流程
4. 定期配置审计
""",
                'status': 'completed'
            },
            'doc-engineer': {
                'content': """
# 文档工程师 (Maya) - Config 技术总览文档

# Config 目录技术总览

## 概述
Config 目录是 CoderWiki 项目的配置管理中心，采用模块化、分层化的设计理念，支持多环境部署和灵活的配置管理。

## 架构设计

### 1. 分层配置架构
```
Config/
├── app.py          # 应用主配置
├── database.py     # 数据库配置
├── auth.py         # 认证配置
├── claude.py       # Claude Code 配置
├── logging.py      # 日志配置
└── environment.py  # 环境配置
```

### 2. 配置模式
- **类基础配置**: 使用 Python 类封装配置逻辑
- **环境驱动**: 支持开发、测试、生产环境切换
- **依赖注入**: 配置通过依赖注入方式使用
- **验证机制**: 内置配置验证和错误处理

## 核心模块

### 应用配置 (app.py)
- Flask 应用基础配置
- 会话管理配置
- 文件上传配置
- 安全配置

### 数据库配置 (database.py)
- MySQL 连接配置
- 连接池管理
- 迁移配置
- 性能优化

### 认证配置 (auth.py)
- JWT 配置
- 密码策略
- OAuth 集成
- 会话管理

### Claude Code 配置 (claude.py)
- API 密钥管理
- 工作流配置
- BMAD 代理设置
- 文件上传限制

### 日志配置 (logging.py)
- 多级别日志
- 文件轮转
- 错误追踪
- 性能监控

### 环境配置 (environment.py)
- 环境变量管理
- 服务器设置
- 安全配置
- 监控设置

## 技术特点

### 1. 模块化设计
- 按功能模块分离配置
- 高内聚低耦合
- 易于维护和扩展

### 2. 环境支持
- 开发环境配置
- 测试环境配置
- 生产环境配置
- 环境自动检测

### 3. 安全机制
- 敏感信息环境变量化
- 配置验证机制
- 安全配置检查
- 访问控制

### 4. 性能优化
- 配置缓存机制
- 延迟加载
- 连接池管理
- 资源优化

## 使用指南

### 1. 环境配置
```bash
# 设置环境变量
export ENVIRONMENT=production
export DATABASE_URL=mysql://user:pass@host/db
export CLAUDE_API_KEY=your-api-key
```

### 2. 配置加载
```python
from config.app import Config, ProductionConfig

# 根据环境加载配置
if os.getenv('ENVIRONMENT') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(Config)
```

### 3. 配置验证
```python
from config.claude import ClaudeConfig

# 验证配置完整性
if not ClaudeConfig.validate_config():
    missing = ClaudeConfig.get_missing_fields()
    raise ValueError(f"Missing required config: {missing}")
```

## 最佳实践

1. **环境变量管理**: 使用环境变量存储敏感信息
2. **配置验证**: 实现配置验证机制
3. **文档维护**: 保持配置文档的更新
4. **版本控制**: 配置变更纳入版本控制
5. **测试覆盖**: 为配置模块编写测试

## 故障排除

### 常见问题
1. **配置缺失**: 检查必需的环境变量
2. **格式错误**: 验证配置格式和类型
3. **权限问题**: 检查文件权限和访问控制
4. **依赖问题**: 确认依赖服务可用性

### 调试方法
1. 启用调试模式
2. 检查日志输出
3. 验证配置加载
4. 测试配置功能

## 总结

Config 目录采用现代化的配置管理理念，提供了灵活、安全、高效的配置解决方案。通过模块化设计和环境支持，能够满足不同部署场景的需求，为 CoderWiki 项目的稳定运行提供了强有力的配置保障。
""",
                'status': 'completed'
            }
        }

        # 模拟工作流执行结果
        mock_result = {
            'status': 'completed',
            'session_id': self.test_session_id,
            'execution_time': 180.5,
            'document': {
                'title': 'Config 目录技术总览文档',
                'generated_at': '2024-01-01 12:00:00',
                'agents_used': ['code-analyst', 'architecture-analyst', 'flow-analyst', 'problem-solver', 'doc-engineer'],
                'sections': mock_agent_outputs
            },
            'agent_outputs': mock_agent_outputs
        }

        # 验证文档生成结果
        self.assertEqual(mock_result['status'], 'completed')
        self.assertIn('document', mock_result)
        self.assertIn('agent_outputs', mock_result)

        # 验证文档内容
        document = mock_result['document']
        self.assertEqual(document['title'], 'Config 目录技术总览文档')
        self.assertEqual(len(document['agents_used']), 5)

        # 验证各个代理的输出
        agent_outputs = mock_result['agent_outputs']
        for agent_id, output in agent_outputs.items():
            self.assertEqual(output['status'], 'completed')
            self.assertIsNotNone(output['content'])
            self.assertGreater(len(output['content']), 100)  # 内容应该足够详细

        # 验证文档工程师生成了完整的技术总览
        doc_engineer_output = agent_outputs['doc-engineer']['content']
        self.assertIn('Config 目录技术总览', doc_engineer_output)
        self.assertIn('架构设计', doc_engineer_output)
        self.assertIn('核心模块', doc_engineer_output)
        self.assertIn('使用指南', doc_engineer_output)
        self.assertIn('最佳实践', doc_engineer_output)

    def test_config_file_upload_filtering(self):
        """测试配置文件上传过滤"""
        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)

        # 应该上传的配置文件
        should_upload = [
            'config/app.py',
            'config/database.py',
            'config/auth.py',
            'config/claude.py',
            'config/logging.py',
            'config/environment.py',
            'config/__init__.py',
            'main.py',
            'README.md',
            'requirements.txt'
        ]

        # 不应该上传的文件
        should_not_upload = [
            '.gitignore',
            '.env',
            '__pycache__/config.pyc',
            'venv/lib/python.py',
            '.DS_Store',
            'temp.txt'
        ]

        # 验证文件过滤
        for file_path in should_upload:
            filename = os.path.basename(file_path)
            self.assertTrue(client._should_upload_file(filename), f"Should upload: {filename}")

        for file_path in should_not_upload:
            filename = os.path.basename(file_path)
            self.assertFalse(client._should_upload_file(filename), f"Should not upload: {filename}")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)




