"""
开发环境配置
"""
from backend.config import DevelopmentConfig

# 开发环境特定配置
class DevConfig(DevelopmentConfig):
    """开发环境配置"""
    
    # 开发环境数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki:coderwiki@localhost/coderwiki_dev'
    
    # 开发环境调试
    DEBUG = True
    FLASK_DEBUG = True
    
    # 开发环境LLM配置
    LLM_MODEL = 'gpt-3.5-turbo'
    LLM_TEMPERATURE = 0.7
    
    # 开发环境日志
    LOG_LEVEL = 'DEBUG'
    LOG_TO_FILE = False
    
    # 开发环境安全
    WTF_CSRF_ENABLED = True
    
    # 开发环境会话
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    
    # 开发环境文件上传
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # 开发环境Git配置
    GIT_REPOS_PATH = '/tmp/coderwiki_repos_dev'
    
    # 开发环境缓存
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300