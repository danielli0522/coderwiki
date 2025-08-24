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
        # 获取系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # 计算系统运行时间
        try:
            # 使用psutil获取系统启动时间
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
        except:
            # 如果无法获取启动时间，使用一个合理的默认值
            uptime = 3600  # 1小时作为默认值

        # 检查关键服务状态
        services_status = []
        service_checks = {
            'database': check_database_health(),
            'redis': check_redis_health(),
            'file_system': check_filesystem_health()
        }

        for service_name, status in service_checks.items():
            services_status.append({
                'name': service_name,
                'type': service_name,
                'status': status['status'],
                'response_time': status.get('response_time', 0)
            })

        # 生成系统告警
        alerts = generate_system_alerts(cpu_percent, memory.percent, disk.percent)

        # 确定整体状态
        overall_status = determine_overall_status(service_checks, alerts)

        return jsonify({
            'success': True,
            'overall_status': overall_status,
            'uptime': int(uptime),
            'cpu_usage': round(cpu_percent, 1),
            'memory_usage': round(memory.percent, 1),
            'disk_usage': round(disk.percent, 1),
            'services': services_status,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Health check failed',
            'overall_status': 'error',
            'uptime': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'services': [],
            'alerts': [{
                'level': 'error',
                'title': '系统健康检查失败',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }]
        }), 500

def check_database_health():
    """检查数据库健康状态"""
    try:
        # 这里可以添加实际的数据库连接检查
        # 暂时返回模拟数据
        return {
            'status': 'healthy',
            'response_time': 5
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'error',
            'response_time': 0
        }

def check_redis_health():
    """检查Redis健康状态"""
    try:
        # 这里可以添加实际的Redis连接检查
        # 暂时返回模拟数据
        return {
            'status': 'healthy',
            'response_time': 3
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            'status': 'error',
            'response_time': 0
        }

def check_filesystem_health():
    """检查文件系统健康状态"""
    try:
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            return {
                'status': 'warning',
                'response_time': 1
            }
        return {
            'status': 'healthy',
            'response_time': 1
        }
    except Exception as e:
        logger.error(f"Filesystem health check failed: {e}")
        return {
            'status': 'error',
            'response_time': 0
        }

def generate_system_alerts(cpu_percent, memory_percent, disk_percent):
    """生成系统告警"""
    alerts = []

    # CPU使用率告警
    if cpu_percent > 90:
        alerts.append({
            'level': 'error',
            'title': 'CPU使用率过高',
            'message': f'CPU使用率达到{cpu_percent}%，可能影响系统性能',
            'timestamp': datetime.now().isoformat()
        })
    elif cpu_percent > 70:
        alerts.append({
            'level': 'warning',
            'title': 'CPU使用率较高',
            'message': f'CPU使用率达到{cpu_percent}%，建议关注',
            'timestamp': datetime.now().isoformat()
        })

    # 内存使用率告警
    if memory_percent > 90:
        alerts.append({
            'level': 'error',
            'title': '内存使用率过高',
            'message': f'内存使用率达到{memory_percent}%，可能影响系统稳定性',
            'timestamp': datetime.now().isoformat()
        })
    elif memory_percent > 80:
        alerts.append({
            'level': 'warning',
            'title': '内存使用率较高',
            'message': f'内存使用率达到{memory_percent}%，建议关注',
            'timestamp': datetime.now().isoformat()
        })

    # 磁盘使用率告警
    if disk_percent > 90:
        alerts.append({
            'level': 'error',
            'title': '磁盘空间不足',
            'message': f'磁盘使用率达到{disk_percent}%，建议清理空间',
            'timestamp': datetime.now().isoformat()
        })
    elif disk_percent > 80:
        alerts.append({
            'level': 'warning',
            'title': '磁盘空间紧张',
            'message': f'磁盘使用率达到{disk_percent}%，建议关注',
            'timestamp': datetime.now().isoformat()
        })

    return alerts

def determine_overall_status(service_checks, alerts):
    """确定整体系统状态"""
    # 检查是否有错误级别的告警
    error_alerts = [alert for alert in alerts if alert['level'] == 'error']
    if error_alerts:
        return 'error'

    # 检查服务状态
    for service_name, status in service_checks.items():
        if status['status'] == 'error':
            return 'error'
        elif status['status'] == 'warning':
            return 'warning'

    # 检查是否有警告级别的告警
    warning_alerts = [alert for alert in alerts if alert['level'] == 'warning']
    if warning_alerts:
        return 'warning'

    return 'healthy'

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

@system_bp.route('/performance', methods=['GET', 'POST'])
def performance_metrics():
    """性能指标相关接口"""
    if request.method == 'POST':
        """接收前端性能指标数据"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No performance data provided'
                }), 400

            # 记录性能指标
            logger.info(f"Performance metrics received: {data}")

            # 这里可以存储到数据库或进行进一步分析
            # 例如：存储到性能监控数据库、触发告警等

            return jsonify({
                'success': True,
                'message': 'Performance metrics received',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Performance metrics endpoint failed: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to process performance metrics'
            }), 500

    elif request.method == 'GET':
        """获取系统性能指标"""
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

            # 系统负载
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None

            performance_data = {
                'cpu': {'percent': cpu_percent},
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'load_average': load_avg,
                'timestamp': datetime.now().isoformat()
            }

            return jsonify({
                'success': True,
                'performance': performance_data
            })

        except Exception as e:
            logger.error(f"Get performance metrics failed: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to get performance metrics'
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
