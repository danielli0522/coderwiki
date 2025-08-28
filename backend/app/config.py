"""
Application configuration module.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""

    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///coderwiki.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Flask-Login configuration
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = '请先登录以访问此页面'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    # LLM API configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')

    # Claude Code API configuration
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
    CLAUDE_WORKSPACE_ID = os.environ.get('CLAUDE_WORKSPACE_ID')
    CLAUDE_USE_LOCAL_MODE = os.environ.get('CLAUDE_USE_LOCAL_MODE', 'False').lower() == 'true'
    CLAUDE_USE_CLI_MODE = os.environ.get('CLAUDE_USE_CLI_MODE', 'False').lower() == 'true'

    # Git repository configuration
    REPO_CLONE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repos')
    MAX_REPO_SIZE = 100 * 1024 * 1024  # 100MB max repository size

    # Task queue configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

    @staticmethod
    def init_app(app):
        """Initialize configuration for app."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///coderwiki_dev.db'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///coderwiki_test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///coderwiki_prod.db'

    @classmethod
    def init_app(cls, app):
        """Initialize production configuration."""
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler

        # Configure logging
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')

            file_handler = RotatingFileHandler('logs/coderwiki.log',
                                               maxBytes=10240000,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
