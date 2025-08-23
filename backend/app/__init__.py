"""
CoderWiki Flask Application

A code documentation auto-generation system.
"""

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder=config_class.TEMPLATE_FOLDER,
                static_folder=config_class.STATIC_FOLDER)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'

    # Configure user loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.api import auth_bp, repository_bp, document_bp, task_bp, analysis_bp, user_bp, system_bp, activities_bp, llm_bp
    from app.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(repository_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(llm_bp)
    app.register_blueprint(main_bp)

    # Initialize WebSocket support
    try:
        from app.api.websocket import init_socketio, websocket_bp
        init_socketio(app)
        # 注册WebSocket蓝图到/api/ws前缀
        app.register_blueprint(websocket_bp, url_prefix='/api/ws')
        app.logger.info("WebSocket support initialized successfully")
    except ImportError as e:
        app.logger.warning(f"WebSocket support not available: {e}")
    except Exception as e:
        app.logger.error(f"Failed to initialize WebSocket: {e}")

    # Register main routes
    @app.route('/')
    def index():
        return redirect(url_for('main.dashboard'))

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return '页面未找到', 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return '内部服务器错误', 500

    return app
