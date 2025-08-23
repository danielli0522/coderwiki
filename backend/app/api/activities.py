"""
Activities API endpoints for user activity tracking.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.repository import Repository
from app.models.document import Document
from app.models.task import Task
from app.models.user import User
from app import db
from datetime import datetime, timedelta

activities_bp = Blueprint('activities', __name__, url_prefix='/api/activities')

@activities_bp.route('', methods=['GET'])
@login_required
def get_activities():
    """Get user activities for the recent activity component."""
    try:
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        activity_type = request.args.get('type')
        
        # Time range (last 7 days by default)
        days = request.args.get('days', 7, type=int)
        since_date = datetime.utcnow() - timedelta(days=days)
        
        activities = []
        
        # Get recent repositories
        repos = Repository.query.filter(
            Repository.user_id == current_user.id,
            Repository.created_at >= since_date
        ).order_by(Repository.created_at.desc()).limit(limit).all()
        
        for repo in repos:
            activities.append({
                'id': f'repo_{repo.id}',
                'type': 'repository_added',
                'title': f'添加了仓库 {repo.name}',
                'description': repo.description or '无描述',
                'timestamp': repo.created_at.isoformat(),
                'icon': 'fas fa-code-branch',
                'color': 'primary',
                'metadata': {
                    'repository_id': repo.id,
                    'repository_name': repo.name,
                    'repository_url': repo.url
                }
            })
        
        # Get recent documents
        docs = Document.query.filter(
            Document.user_id == current_user.id,
            Document.created_at >= since_date
        ).order_by(Document.created_at.desc()).limit(limit).all()
        
        for doc in docs:
            activities.append({
                'id': f'doc_{doc.id}',
                'type': 'document_generated',
                'title': f'生成了文档 {doc.title}',
                'description': f'类型: {doc.document_type}, 格式: {doc.format}',
                'timestamp': doc.created_at.isoformat(),
                'icon': 'fas fa-file-alt',
                'color': 'success',
                'metadata': {
                    'document_id': doc.id,
                    'document_type': doc.document_type,
                    'document_format': doc.format,
                    'repository_id': doc.repository_id
                }
            })
        
        # Get recent tasks
        tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.created_at >= since_date
        ).order_by(Task.created_at.desc()).limit(limit).all()
        
        for task in tasks:
            status_icon = {
                'pending': 'fas fa-clock',
                'running': 'fas fa-spinner fa-spin',
                'completed': 'fas fa-check-circle',
                'failed': 'fas fa-times-circle',
                'cancelled': 'fas fa-ban'
            }.get(task.status, 'fas fa-question')
            
            status_color = {
                'pending': 'warning',
                'running': 'info',
                'completed': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            }.get(task.status, 'secondary')
            
            activities.append({
                'id': f'task_{task.id}',
                'type': 'task_' + task.status,
                'title': f'任务 "{task.title}" {task.status}',
                'description': task.description or '无描述',
                'timestamp': task.created_at.isoformat(),
                'icon': status_icon,
                'color': status_color,
                'metadata': {
                    'task_id': task.id,
                    'task_status': task.status,
                    'task_type': task.task_type,
                    'repository_id': task.repository_id
                }
            })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply filtering by type if specified
        if activity_type:
            activities = [a for a in activities if a['type'] == activity_type]
        
        # Apply pagination
        total_count = len(activities)
        paginated_activities = activities[offset:offset + limit]
        
        return jsonify({
            'activities': paginated_activities,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        })
        
    except Exception as e:
        current_app.logger.error(f"获取活动记录失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500