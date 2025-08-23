"""
WebSocket API endpoints for real-time communication.
"""

from flask import Blueprint, request, current_app, jsonify

websocket_bp = Blueprint('websocket', __name__)

@websocket_bp.route('/')
def websocket_endpoint():
    """WebSocket endpoint for real-time communication."""
    return jsonify({
        'status': 'available',
        'message': 'WebSocket endpoint is available',
        'socketio_url': '/socket.io/'
    })

@websocket_bp.route('/status')
def websocket_status():
    """Get WebSocket connection status."""
    return jsonify({
        'status': 'active',
        'connections': 0
    })

def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    try:
        from flask_socketio import SocketIO
        socketio = SocketIO()
        socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
        app.logger.info("SocketIO initialized successfully")
    except ImportError as e:
        app.logger.warning(f"Flask-SocketIO not available: {e}")
    except Exception as e:
        app.logger.error(f"Failed to initialize SocketIO: {e}")
