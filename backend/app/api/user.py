"""
User statistics API endpoints.
"""

from flask import Blueprint, jsonify, current_app
from flask_login import current_user, login_required
from app.models.repository import Repository
from app.models.document import Document
from app.models.task import Task
from app import db

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user statistics for dashboard."""
    try:
        # Count repositories
        total_repositories = Repository.query.filter_by(user_id=current_user.id).count()
        
        # Count documents
        total_documents = Document.query.filter_by(user_id=current_user.id).count()
        
        # Count active tasks
        active_tasks = Task.query.filter_by(
            user_id=current_user.id,
            status='running'
        ).count()
        
        # Count monthly generated documents
        from datetime import datetime, timedelta
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        monthly_generated = Document.query.filter(
            Document.user_id == current_user.id,
            Document.created_at >= one_month_ago
        ).count()
        
        # Get generation trend for the last 7 days
        from sqlalchemy import func, extract
        trend_data = []
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            count = Document.query.filter(
                Document.user_id == current_user.id,
                func.date(Document.created_at) == date.date()
            ).count()
            trend_data.append({'date': date_str, 'count': count})
        
        # Get document type distribution
        document_types = {}
        documents = Document.query.filter_by(user_id=current_user.id).all()
        for doc in documents:
            doc_type = doc.document_type or 'unknown'
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
        
        return jsonify({
            'total_repositories': total_repositories,
            'total_documents': total_documents,
            'active_tasks': active_tasks,
            'monthly_generated': monthly_generated,
            'generation_trend': trend_data,
            'document_types': document_types
        })
        
    except Exception as e:
        current_app.logger.error(f"获取用户统计失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500