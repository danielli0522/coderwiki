"""
生产环境配置
"""
from backend.config import ProductionConfig

class ProdConfig(ProductionConfig):
    """生产环境配置"""
    
    # 生产环境数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki:coderwiki@localhost/coderwiki_prod'
    
    # 生产环境安全
    DEBUG = False
    FLASK_DEBUG = False
    
    # 生产环境日志
    LOG_LEVEL = 'WARNING'
    LOG_TO_FILE = True
    
    # 生产环境会话
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1小时
    
    # 生产环境文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 生产环境Git配置
    GIT_REPOS_PATH = '/var/opt/coderwiki/repos'
    
    # 生产环境缓存
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 生产环境安全头
    SECURE_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }
    
    # 生产环境监控
    SENTRY_DSN = None  # 设置为实际的Sentry DSN
    ENABLE_METRICS = True