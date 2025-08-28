"""
CoderWiki Flask Application

A code documentation auto-generation system.
"""

from flask import Flask, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = None

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
    login_manager.login_view = 'main.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'

    # Configure user loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.api import auth_bp, repository_bp, document_bp, task_bp, analysis_bp, user_bp, system_bp, activities_bp, llm_bp, mkdocs_bp, performance_bp, smart_document_bp
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
    app.register_blueprint(mkdocs_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(smart_document_bp)
    app.register_blueprint(main_bp)

    # Register template filters
    @app.template_filter('get_status_badge_class')
    def get_status_badge_class(status):
        classes = {
            'pending': 'bg-secondary',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        }
        return classes.get(status, 'bg-secondary')

    @app.template_filter('get_status_text')
    def get_status_text(status):
        texts = {
            'pending': '待处理',
            'running': '进行中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        }
        return texts.get(status, status)

    @app.template_filter('get_priority_badge_class')
    def get_priority_badge_class(priority):
        classes = {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger',
            'urgent': 'bg-danger'
        }
        return classes.get(priority, 'bg-secondary')

    @app.template_filter('get_priority_text')
    def get_priority_text(priority):
        texts = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '紧急'
        }
        return texts.get(priority, priority)

    @app.template_filter('format_datetime')
    def format_datetime(date_obj):
        if not date_obj:
            return '-'
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')

    # Initialize WebSocket support
    global socketio
    try:
        from flask_socketio import SocketIO
        from app.api.websocket import websocket_bp, setup_socketio_handlers
        
        socketio = SocketIO()
        socketio.init_app(app, 
                         cors_allowed_origins="*", 
                         async_mode='threading',
                         logger=True,
                         engineio_logger=True,
                         allow_unsafe_werkzeug=True)
        
        # Setup WebSocket event handlers within app context
        with app.app_context():
            setup_socketio_handlers(socketio)
        
        # Register WebSocket blueprint for REST endpoints
        app.register_blueprint(websocket_bp, url_prefix='/api/ws')
        
        app.logger.info("WebSocket support initialized successfully")
    except ImportError as e:
        app.logger.warning(f"WebSocket support not available: {e}")
        socketio = None
    except Exception as e:
        app.logger.error(f"Failed to initialize WebSocket: {e}")
        socketio = None

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


    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({'error': '方法不被允许', 'method': request.method, 'url': request.url}), 405

    return app, socketio
