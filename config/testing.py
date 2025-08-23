"""
测试环境配置
"""
from backend.config import TestingConfig

class TestConfig(TestingConfig):
    """测试环境配置"""
    
    # 测试环境数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki:coderwiki@localhost/coderwiki_test'
    
    # 测试环境配置
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # 测试环境会话
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    
    # 测试环境文件上传
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
    
    # 测试环境Git配置
    GIT_REPOS_PATH = '/tmp/coderwiki_repos_test'
    
    # 测试环境缓存
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 0
    
    # 测试环境日志
    LOG_LEVEL = 'CRITICAL'
    
    # 测试环境服务器
    SERVER_NAME = 'localhost:5000'
    
    # 测试环境LLM配置
    LLM_MODEL = 'test-model'
    LLM_TEMPERATURE = 0.0
    
    # 测试环境邮件
    MAIL_SUPPRESS_SEND = True
    
    # 测试环境密码
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_SECRET_KEY = 'test-csrf-secret-key'