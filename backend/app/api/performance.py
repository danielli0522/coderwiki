"""
Performance monitoring API endpoints.
"""

import time
import psutil
import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.utils.db_context import DatabaseConnectionPool
from app.api.websocket import get_connection_stats

logger = logging.getLogger(__name__)

performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')


@performance_bp.route('/', methods=['POST'])
@login_required
def log_performance_metric():
    """Log a performance metric from the client."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        metric_type = data.get('type')
        metric_value = data.get('value')
        metric_name = data.get('name', 'unknown')
        
        # Log the performance metric
        logger.info(f"Performance metric - User: {current_user.id}, Type: {metric_type}, "
                   f"Name: {metric_name}, Value: {metric_value}ms")
        
        return jsonify({
            'success': True,
            'message': 'Performance metric logged successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error logging performance metric: {e}")
        return jsonify({'error': 'Failed to log performance metric'}), 500


@performance_bp.route('/system', methods=['GET'])
@login_required
def get_system_performance():
    """Get current system performance metrics."""
    try:
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database connection pool stats
        db_stats = DatabaseConnectionPool.get_connection_info()
        
        # WebSocket connection stats
        ws_stats = get_connection_stats()
        
        return jsonify({
            'success': True,
            'system': {
                'cpu_usage': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'database': db_stats,
            'websocket': ws_stats,
            'timestamp': time.time()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system performance: {e}")
        return jsonify({'error': 'Failed to get system performance'}), 500


@performance_bp.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint."""
    try:
        start_time = time.time()
        
        # Database health check
        db_health = DatabaseConnectionPool.health_check()
        
        # WebSocket stats
        ws_stats = get_connection_stats()
        
        # System resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'response_time_ms': (time.time() - start_time) * 1000,
            'database': db_health,
            'websocket': {
                'active_connections': ws_stats.get('active_connections', 0),
                'channels': ws_stats.get('total_channels', 0)
            },
            'resources': {
                'memory_available_gb': memory.available / (1024**3),
                'memory_percent': memory.percent,
                'disk_free_gb': disk.free / (1024**3),
                'disk_percent': (disk.used / disk.total) * 100
            }
        }
        
        # Determine overall health
        if (db_health.get('status') != 'healthy' or 
            memory.percent > 90 or 
            (disk.used / disk.total) * 100 > 90):
            health_status['status'] = 'unhealthy'
            return jsonify(health_status), 503
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 500