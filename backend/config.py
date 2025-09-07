"""
Backend Configuration
"""
import os
from pathlib import Path

class Config:
    """基础配置类"""

    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 数据库配置 - 默认使用MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/coderwiki?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30
    }

    # Flask配置
    FLASK_APP = 'app'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')

    # 模板配置
    TEMPLATE_FOLDER = Path(__file__).parent.parent / 'frontend' / 'templates'
    STATIC_FOLDER = Path(__file__).parent.parent / 'frontend' / 'static'

    # 会话配置
    PERMANENT_SESSION_LIFETIME = 1800  # 30分钟

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = Path(__file__).parent / 'uploads'

    # LLM配置
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')

    # MCP服务配置
    MCP_SERVER_URL = os.environ.get('MCP_SERVER_URL', 'http://localhost')
    MCP_SERVER_PORT = int(os.environ.get('MCP_SERVER_PORT', '3000'))
    MCP_ENABLED = os.environ.get('MCP_ENABLED', 'true').lower() == 'true'

    # Claude Code服务配置
    CLAUDE_CODE_ENABLED = os.environ.get('CLAUDE_CODE_ENABLED', 'true').lower() == 'true'
    BMAD_DOCS_PATH = os.environ.get('BMAD_DOCS_PATH', '../bmad-docs-generator/')

    # Claude Code API configuration
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
    CLAUDE_WORKSPACE_ID = os.environ.get('CLAUDE_WORKSPACE_ID')
    CLAUDE_USE_LOCAL_MODE = os.environ.get('CLAUDE_USE_LOCAL_MODE', 'False').lower() == 'true'

    # Git配置
    GIT_REPOS_PATH = Path(__file__).parent / 'repos'

    # 文档生成配置 - 与Git仓库路径保持一致
    REPOSITORY_BASE_PATH = GIT_REPOS_PATH

    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = Path(__file__).parent / 'logs' / 'app.log'

    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-key'

    # 微信登录配置
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID')
    WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET')
    WECHAT_REDIRECT_URI = os.environ.get('WECHAT_REDIRECT_URI', 'http://localhost:5001/api/auth/wechat/callback')
    WECHAT_ENABLED = os.environ.get('WECHAT_ENABLED', 'false').lower() == 'true'

    # CORS Configuration
    CORS_ORIGINS = [
        'http://localhost:5001',
        'http://127.0.0.1:5001',
        'http://localhost:5002',
        'http://10.11.75.81:5001',  # 本地网络IP
        'http://198.18.0.1:5001',   # 本地网络IP
        '*'  # 允许所有来源（开发环境）
    ]
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']
    CORS_HEADERS = ['Content-Type', 'Authorization', 'Accept', 'X-Requested-With']

    @classmethod
    def init_app(cls, app):
        """初始化应用配置"""
        # 创建必要的目录
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.GIT_REPOS_PATH.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # 配置日志
        import logging
        from logging.handlers import RotatingFileHandler

        handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(getattr(logging, cls.LOG_LEVEL))

        app.logger.addHandler(handler)
        app.logger.setLevel(getattr(logging, cls.LOG_LEVEL))
        app.logger.info('CoderWiki application startup')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    FLASK_ENV = 'development'

    # 开发环境数据库 - 使用MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/coderwiki?charset=utf8mb4'

    # 开发环境LLM配置
    LLM_MODEL = os.environ.get('DEV_LLM_MODEL', 'gpt-3.5-turbo')

    # 开发环境日志
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'

    # 生产环境数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/coderwiki?charset=utf8mb4'

    # 生产环境日志
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True

    # 测试环境数据库 - 使用SQLite内存数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'

    # SQLite doesn't support connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # 测试环境日志
    LOG_LEVEL = 'DEBUG'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}
