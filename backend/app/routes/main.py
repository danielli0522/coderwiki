"""
Main routes for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard/index.html')

@main_bp.route('/login')
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

@main_bp.route('/register')
def register():
    """Register page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/register.html')

@main_bp.route('/test-login')
def test_login():
    """Test login page."""
    return render_template('test_login_page.html')

@main_bp.route('/simple-login')
def simple_login():
    """Simple login page for debugging."""
    return render_template('simple_login.html')

@main_bp.route('/login-fixed')
def login_fixed():
    """Fixed login page without JS conflicts."""
    return render_template('auth/login_fixed.html')

@main_bp.route('/emergency-close')
def emergency_close():
    """Emergency modal close page."""
    return render_template('emergency-close.html')

@main_bp.route('/emergency-modal-close')
def emergency_modal_close():
    """Emergency modal close page for repository management."""
    return render_template('emergency-modal-close.html')

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('user/profile.html')

@main_bp.route('/repositories')
@login_required
def repositories():
    """Repository management page."""
    return render_template('repository/index.html')

@main_bp.route('/repositories/add')
@login_required
def add_repository():
    """Add repository page."""
    return render_template('repository/add.html')

@main_bp.route('/repositories/<int:repository_id>')
@login_required
def repository_detail(repository_id):
    """Repository detail page."""
    from app.models.repository import Repository
    repository = Repository.query.get_or_404(repository_id)
    if repository.user_id != current_user.id:
        flash('您没有权限访问此仓库', 'danger')
        return redirect(url_for('main.repositories'))
    return render_template('repository/detail.html', repository=repository)

@main_bp.route('/repositories/<int:repository_id>/edit')
@login_required
def edit_repository(repository_id):
    """Edit repository page."""
    from app.models.repository import Repository
    repository = Repository.query.get_or_404(repository_id)
    if repository.user_id != current_user.id:
        flash('您没有权限编辑此仓库', 'danger')
        return redirect(url_for('main.repositories'))
    return render_template('repository/edit.html', repository=repository)

@main_bp.route('/tasks')
@login_required
def tasks():
    """Task management page."""
    return render_template('task/index.html')

@main_bp.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    """Task detail page."""
    from app.models.task import Task
    from app.services.task_service import TaskService

    task_service = TaskService()
    task = task_service.get_task_by_id(task_id, current_user.id)

    if not task:
        flash('任务不存在或您没有权限访问', 'danger')
        return redirect(url_for('main.tasks'))

    return render_template('task/detail.html', task=task)

@main_bp.route('/analysis')
@login_required
def analysis():
    """Code analysis page."""
    return render_template('analysis/index.html')

@main_bp.route('/analysis/<int:repository_id>')
@login_required
def analysis_results(repository_id):
    """Analysis results page for a repository."""
    from app.models.repository import Repository
    # Check if repository exists and user has access
    repository = Repository.query.get_or_404(repository_id)

    if repository.user_id != current_user.id:
        flash('您没有权限访问此仓库', 'danger')
        return redirect(url_for('main.repositories'))

    return render_template('analysis/results.html', repository=repository)

@main_bp.route('/settings')
@login_required
def settings():
    """System settings page."""
    return render_template('settings/index.html')

@main_bp.route('/documents')
@login_required
def documents():
    """Document management page."""
    return render_template('document/index.html')

@main_bp.route('/documents/add')
@login_required
def add_document():
    """Add document page."""
    return render_template('document/add.html')

@main_bp.route('/documents/<int:document_id>')
@login_required
def document_detail(document_id):
    """Document detail page."""
    from app.models.document import Document
    document = Document.query.get_or_404(document_id)
    if document.user_id != current_user.id:
        flash('您没有权限访问此文档', 'danger')
        return redirect(url_for('main.documents'))
    return render_template('document/detail.html', document=document)

@main_bp.route('/documents/<int:document_id>/edit')
@login_required
def edit_document(document_id):
    """Edit document page."""
    from app.models.document import Document
    document = Document.query.get_or_404(document_id)
    if document.user_id != current_user.id:
        flash('您没有权限编辑此文档', 'danger')
        return redirect(url_for('main.documents'))
    return render_template('document/edit.html', document=document)

@main_bp.route('/documents/<int:document_id>/view')
@login_required
def document_viewer(document_id):
    """Document viewer page."""
    from app.services.doc_service import DocumentService
    from app.models.document import Document

    # 获取文档信息
    doc_service = DocumentService()
    document_data = doc_service.get_document(document_id, current_user.id)

    if not document_data:
        flash('文档不存在或您没有权限访问', 'danger')
        return redirect(url_for('main.documents'))

    # 获取文档对象用于模板渲染
    document = Document.query.get(document_id)

    return render_template('document/viewer.html', document=document)

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')

@main_bp.route('/help')
def help():
    """Help page."""
    return render_template('help.html')

@main_bp.route('/test-modal')
def test_modal():
    """Modal test page."""
    return render_template('test-modal.html')

@main_bp.route('/test-repository-modal')
def test_repository_modal():
    """Repository modal test page."""
    return render_template('test-repository-modal.html')

@main_bp.route('/test-navigation')
def test_navigation():
    """Navigation test page."""
    return render_template('test-navigation.html')

@main_bp.route('/system-status')
def system_status():
    """系统状态页面 - 公开访问"""
    return render_template('system_status.html')
