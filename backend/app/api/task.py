"""
Task API endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.task_service import TaskService

task_bp = Blueprint('task', __name__, url_prefix='/api/tasks')

@task_bp.route('', methods=['POST'])
@login_required
def create_task():
    """Create a new task."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        repository_id = data.get('repository_id')
        task_type = data.get('task_type')

        if not repository_id:
            return jsonify({'error': '仓库ID不能为空'}), 400

        if not task_type:
            return jsonify({'error': '任务类型不能为空'}), 400

        from app.utils.task_utils import validate_task_type

        if not validate_task_type(task_type):
            return jsonify({'error': '无效的任务类型'}), 400

        task_service = TaskService()
        task = task_service.create_task(current_user.id, repository_id, task_type)

        return jsonify({
            'success': True,
            'task_id': task.id,
            'task': task.to_dict(),
            'message': '任务创建成功'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    """Get user tasks."""
    try:
        repository_id = request.args.get('repository_id', type=int)
        status = request.args.get('status')
        task_type = request.args.get('type')

        task_service = TaskService()

        # 获取用户自己的任务
        user_tasks = task_service.get_user_tasks(
            user_id=current_user.id,
            repository_id=repository_id,
            status=status,
            task_type=task_type
        )

        # 获取系统任务（user_id=1的任务）
        system_tasks = task_service.get_user_tasks(
            user_id=1,
            repository_id=repository_id,
            status=status,
            task_type=task_type
        )

        # 合并任务列表，去重
        all_tasks = user_tasks + system_tasks
        unique_tasks = {}
        for task in all_tasks:
            if task.id not in unique_tasks:
                unique_tasks[task.id] = task

        tasks = list(unique_tasks.values())

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get a specific task."""
    try:
        task_service = TaskService()

        # 首先尝试获取用户自己的任务
        task = task_service.get_task_by_id(task_id, current_user.id)

        # 如果没找到，尝试获取系统任务（user_id=1的任务）
        if not task:
            task = task_service.get_task_by_id(task_id, 1)

        # 如果还是没找到，尝试获取任何任务（用于调试）
        if not task:
            task = Task.query.get(task_id)

        if not task:
            return jsonify({'error': '任务不存在或您没有权限'}), 404

        return jsonify({
            'success': True,
            'task': task.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    try:
        task_service = TaskService()
        success = task_service.delete_task(task_id, current_user.id)

        if success:
            return jsonify({
                'success': True,
                'message': '任务删除成功'
            })
        else:
            return jsonify({'error': '删除失败'}), 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>/start', methods=['POST'])
@login_required
def start_task(task_id):
    """Start a task."""
    try:
        task_service = TaskService()
        task = task_service.start_task(task_id, current_user.id)

        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'message': '任务已开始'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>/progress', methods=['POST'])
@login_required
def update_task_progress(task_id):
    """Update task progress."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        progress = data.get('progress')

        if progress is None:
            return jsonify({'error': '进度值不能为空'}), 400

        if not isinstance(progress, int) or progress < 0 or progress > 100:
            return jsonify({'error': '进度值必须是0-100之间的整数'}), 400

        task_service = TaskService()
        task = task_service.update_task_progress(task_id, progress, current_user.id)

        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'message': '任务进度已更新'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/pending', methods=['GET'])
@login_required
def get_pending_tasks():
    """Get pending tasks (for task processor)."""
    try:
        limit = request.args.get('limit', 10, type=int)

        task_service = TaskService()
        tasks = task_service.get_pending_tasks(limit=limit)

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/running', methods=['GET'])
@login_required
def get_running_tasks():
    """Get running tasks (for monitoring)."""
    try:
        limit = request.args.get('limit', 10, type=int)

        task_service = TaskService()
        tasks = task_service.get_running_tasks(limit=limit)

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/cleanup', methods=['POST'])
@login_required
def cleanup_old_tasks():
    """Clean up old completed tasks."""
    try:
        data = request.get_json()
        days = data.get('days', 30) if data else 30

        task_service = TaskService()
        cleaned_count = task_service.cleanup_old_tasks(days=days)

        return jsonify({
            'success': True,
            'cleaned_count': cleaned_count,
            'message': f'已清理 {cleaned_count} 个旧任务'
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/statistics', methods=['GET'])
@login_required
def get_task_statistics():
    """Get task statistics."""
    try:
        repository_id = request.args.get('repository_id', type=int)
        days = request.args.get('days', 30, type=int)

        task_service = TaskService()
        stats = task_service.get_task_statistics(
            user_id=current_user.id,
            repository_id=repository_id,
            days=days
        )

        return jsonify({
            'success': True,
            'statistics': stats
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/performance', methods=['GET'])
@login_required
def get_task_performance():
    """Get task performance metrics."""
    try:
        repository_id = request.args.get('repository_id', type=int)
        days = request.args.get('days', 30, type=int)

        task_service = TaskService()
        metrics = task_service.get_task_performance_metrics(
            user_id=current_user.id,
            repository_id=repository_id,
            days=days
        )

        return jsonify({
            'success': True,
            'metrics': metrics
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/queue/info', methods=['GET'])
@login_required
def get_queue_info():
    """Get task queue information."""
    try:
        task_service = TaskService()
        queue_info = task_service.get_task_queue_info()

        return jsonify({
            'success': True,
            'queue_info': queue_info
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>/logs', methods=['GET'])
@login_required
def get_task_logs(task_id):
    """Get task logs."""
    try:
        level = request.args.get('level')
        step_name = request.args.get('step_name')
        limit = request.args.get('limit', type=int)

        from app.utils.task_logging import get_task_logs

        logs = get_task_logs(task_id, level, step_name, limit)

        return jsonify({
            'success': True,
            'logs': logs
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>/progress', methods=['GET'])
@login_required
def get_task_progress(task_id):
    """Get detailed task progress."""
    try:
        from app.utils.progress_tracker import get_task_progress_details

        progress = get_task_progress_details(task_id)

        if progress is None:
            return jsonify({'error': '任务不存在或未开始执行'}), 404

        return jsonify({
            'success': True,
            'progress': progress
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/<int:task_id>/retry', methods=['POST'])
@login_required
def retry_task(task_id):
    """Retry a failed task."""
    try:
        task_service = TaskService()
        task = task_service.get_task_by_id(task_id, current_user.id)

        if not task:
            return jsonify({'error': '任务不存在或您没有权限'}), 404

        if not task.can_retry():
            return jsonify({'error': '任务无法重试'}), 400

        # Reset task status to pending
        task_service.update_task_status(task_id, 'pending', progress=0)

        return jsonify({
            'success': True,
            'message': '任务已重试'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/batch', methods=['POST'])
@login_required
def create_batch_tasks():
    """Create multiple tasks for batch processing."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        repository_ids = data.get('repository_ids', [])
        task_type = data.get('task_type')

        if not repository_ids:
            return jsonify({'error': '仓库ID列表不能为空'}), 400

        if not task_type:
            return jsonify({'error': '任务类型不能为空'}), 400

        from app.utils.task_utils import create_batch_tasks, validate_task_type

        if not validate_task_type(task_type):
            return jsonify({'error': '无效的任务类型'}), 400

        created_tasks = create_batch_tasks(current_user.id, repository_ids, task_type)

        return jsonify({
            'success': True,
            'created_tasks': len(created_tasks),
            'task_ids': [task.id for task in created_tasks],
            'message': f'已创建 {len(created_tasks)} 个任务'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@task_bp.route('/export', methods=['GET'])
@login_required
def export_tasks():
    """Export task data."""
    try:
        repository_id = request.args.get('repository_id', type=int)
        task_type = request.args.get('type')
        status = request.args.get('status')
        format_type = request.args.get('format', 'json')

        task_service = TaskService()
        tasks = task_service.get_user_tasks(
            user_id=current_user.id,
            repository_id=repository_id,
            task_type=task_type,
            status=status
        )

        from app.utils.task_utils import export_task_data

        exported_data = export_task_data(tasks, format_type)

        return jsonify({
            'success': True,
            'data': exported_data,
            'format': format_type,
            'count': len(tasks)
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500
