"""
System API endpoints for system monitoring and utilities.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import logging
import psutil
import platform
import time
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Create blueprint
system_bp = Blueprint('system', __name__, url_prefix='/api/system')

@system_bp.route('/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    try:
        # 基本系统信息
        system_info = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time(),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent
        }

        # 检查关键服务状态
        services_status = {
            'database': 'healthy',  # 可以添加数据库连接检查
            'redis': 'healthy',     # 可以添加Redis连接检查
            'file_system': 'healthy'
        }

        return jsonify({
            'success': True,
            'system': system_info,
            'services': services_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Health check failed',
            'status': 'unhealthy'
        }), 500

@system_bp.route('/stats', methods=['GET'])
@login_required
def system_stats():
    """系统统计信息"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }

        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

        # 网络IO
        network = psutil.net_io_counters()
        network_info = {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }

        return jsonify({
            'success': True,
            'stats': {
                'cpu': {'percent': cpu_percent},
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"System stats failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get system stats'
        }), 500

@system_bp.route('/browser-compatibility', methods=['POST'])
def browser_compatibility():
    """浏览器兼容性数据收集"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # 记录浏览器兼容性信息
        browser_info = data.get('browser', {})
        features = data.get('features', {})
        timestamp = data.get('timestamp', datetime.now().isoformat())

        # 这里可以存储到数据库或日志文件
        logger.info(f"Browser compatibility data: {browser_info}, features: {features}")

        # 生成兼容性建议
        advice = generate_compatibility_advice(browser_info, features)

        return jsonify({
            'success': True,
            'message': 'Browser compatibility data received',
            'advice': advice,
            'timestamp': timestamp
        })

    except Exception as e:
        logger.error(f"Browser compatibility endpoint failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process browser compatibility data'
        }), 500

def generate_compatibility_advice(browser_info: Dict[str, Any], features: Dict[str, Any]) -> list:
    """生成浏览器兼容性建议"""
    advice = []

    browser_name = browser_info.get('name', 'unknown')
    browser_version = browser_info.get('version', 0)

    # 基于浏览器版本的建议
    if browser_name == 'ie' and browser_version < 12:
        advice.append('建议升级到Microsoft Edge或Chrome浏览器以获得更好的体验')

    if browser_name == 'safari' and browser_version < 12:
        advice.append('建议升级到最新版本的Safari浏览器')

    # 基于功能支持的建议
    if not features.get('fetch', True):
        advice.append('您的浏览器不支持Fetch API，某些功能可能无法正常工作')

    if not features.get('cssGrid', True):
        advice.append('您的浏览器不支持CSS Grid，某些布局可能显示不正常')

    if not features.get('localStorage', True):
        advice.append('您的浏览器不支持Local Storage，某些功能可能无法正常工作')

    if not features.get('promise', True):
        advice.append('您的浏览器不支持Promise，某些功能可能无法正常工作')

    return advice

@system_bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    """获取系统日志（仅管理员）"""
    try:
        # 检查用户权限
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # 这里可以实现日志文件读取逻辑
        logs = []

        return jsonify({
            'success': True,
            'logs': logs
        })

    except Exception as e:
        logger.error(f"Get logs failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get logs'
        }), 500

@system_bp.route('/config', methods=['GET'])
@login_required
def get_config():
    """获取系统配置信息"""
    try:
        # 返回非敏感的配置信息
        config_info = {
            'debug': current_app.config.get('DEBUG', False),
            'environment': current_app.config.get('ENV', 'production'),
            'database_url': '***' if current_app.config.get('DATABASE_URL') else None,
            'redis_url': '***' if current_app.config.get('REDIS_URL') else None,
            'claude_code_enabled': current_app.config.get('CLAUDE_CODE_ENABLED', False),
            'mcp_enabled': current_app.config.get('MCP_ENABLED', False)
        }

        return jsonify({
            'success': True,
            'config': config_info
        })

    except Exception as e:
        logger.error(f"Get config failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get config'
        }), 500
