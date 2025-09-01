"""
Main routes for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_required, current_user
import os
from pathlib import Path

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

@main_bp.route('/test-navigation')
def test_navigation():
    """Navigation test page."""
    return render_template('test-navigation.html')

@main_bp.route('/test-nav-fix')
def test_nav_fix():
    """Navigation fix test page."""
    return render_template('test-nav-fix.html')

@main_bp.route('/overlay-test')
def overlay_test():
    """Comprehensive overlay elimination test suite."""
    return render_template('overlay-test.html')

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
    """Document viewer page with MkDocs site redirection."""
    from app.services.doc_service import DocumentService
    from app.services.mkdocs_service import MkDocsService
    from app.models.document import Document
    from app.models.repository import Repository
    import re

    # 获取文档信息
    doc_service = DocumentService()
    document_data = doc_service.get_document(document_id, current_user.id)

    if not document_data:
        flash('文档不存在或您没有权限访问', 'danger')
        return redirect(url_for('main.documents'))

    # 获取文档对象
    document = Document.query.get(document_id)
    
    # 如果文档关联了仓库，尝试重定向到MkDocs站点
    if document and document.repository_id:
        try:
            repository = Repository.query.get(document.repository_id)
            if repository and repository.user_id == current_user.id:
                # 检查MkDocs站点是否存在
                mkdocs_service = MkDocsService()
                site_exists = mkdocs_service.check_site_exists(document.repository_id)
                
                if site_exists:
                    # 构建MkDocs站点URL并重定向
                    sanitized_name = re.sub(r'[^\w\-_]', '_', repository.name)
                    mkdocs_url = f"/sites/{sanitized_name}_{document.repository_id}/"
                    return redirect(mkdocs_url)
        except Exception as e:
            # 如果检查失败，记录错误但继续使用传统查看器
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to check MkDocs site for document {document_id}: {e}")

    # 降级到传统文档查看器
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

@main_bp.route('/test-error-fix')
def test_error_fix():
    """Test error handling fix page."""
    return render_template('test-error-fix.html')

@main_bp.route('/test-winston-modal-unified')
def test_winston_modal_unified():
    """Winston unified modal system test page."""
    return render_template('test-winston-modal-unified.html')

@main_bp.route('/system-status')
def system_status():
    """系统状态页面 - 公开访问"""
    return render_template('system_status.html')


@main_bp.route('/sites/<path:site_path>')
@login_required
def serve_mkdocs_site(site_path):
    """Serve MkDocs generated static files."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"*** DEBUG: serve_mkdocs_site function started with site_path: '{site_path}'")
    try:
        from app.services.mkdocs_service import MkDocsService

        # 获取MkDocs服务配置的基础路径
        mkdocs_service = MkDocsService()
        base_mkdocs_dir = mkdocs_service.base_mkdocs_dir
        logger.info(f"Serving site_path: {site_path}, base_mkdocs_dir: {base_mkdocs_dir}")

        # 解析路径 - 支持两种格式: repo_<id>_<name> 或 <name>_<id>
        path_parts = site_path.split('/', 1)
        if len(path_parts) < 1:
            abort(404)

        site_name = path_parts[0]
        file_path = path_parts[1] if len(path_parts) > 1 else ''
        logger.info(f"Parsed site_name: {site_name}, file_path: {file_path}")

        # 从站点名称提取repository_id - 支持两种格式
        repository_id = None
        try:
            if site_name.startswith('repo_'):
                # 格式: repo_<id>_<name>
                name_parts = site_name[5:].split('_', 1)  # 去掉 'repo_' 前缀
                repository_id = int(name_parts[0])
            elif '_' in site_name:
                # 格式: <name>_<id> (新格式)
                name_parts = site_name.rsplit('_', 1)  # 从右侧分割，获取最后一部分作为ID
                repository_id = int(name_parts[1])
            else:
                abort(404)
        except (IndexError, ValueError):
            logger.error(f"Failed to extract repository_id from site_name: {site_name}")
            abort(404)
        
        logger.info(f"Extracted repository_id: {repository_id}")

        # 验证用户是否有权限访问此仓库
        from app.services.repository_service import RepositoryService
        repo_service = RepositoryService()
        repository = repo_service.get_repository_by_id(repository_id, current_user.id)

        if not repository:
            abort(403)  # 用户无权限访问

        # 构建完整的文件路径 - 使用灵活的目录匹配
        from app.services.mkdocs_service import MkDocsService
        mkdocs_service_instance = MkDocsService()
        site_dir = mkdocs_service_instance._get_existing_site_build_path(repository.name, repository_id)
        logger.info(f"Found site directory using flexible resolution: {site_dir}")
        
        if not site_dir:
            # 站点未构建
            logger.warning(f"Site directory does not exist for repository {repository_id}: {repository.name}")
            flash('MkDocs站点尚未构建，请先生成文档并构建站点', 'warning')
            # 降级到文档列表页面，并传递repository_id参数用于过滤
            return redirect(url_for('main.documents') + f'?repository_id={repository_id}')
        
        logger.info(f"Found site directory: {site_dir}, exists: {site_dir.exists()}")

        # 如果请求的是目录，默认返回index.html
        full_path = site_dir / file_path
        logger.info(f"Initial full_path: {full_path}, is_dir: {full_path.is_dir()}, exists: {full_path.exists()}")
        
        if full_path.is_dir():
            full_path = full_path / 'index.html'
            file_path = str(Path(file_path) / 'index.html')
            logger.info(f"Converted to directory index: {full_path}")

        # 检查文件是否存在
        logger.info(f"Final full_path: {full_path}, exists: {full_path.exists()}, is_file: {full_path.is_file() if full_path.exists() else 'N/A'}")
        if not full_path.exists() or not full_path.is_file():
            # 尝试查找index.html
            if file_path == 'index.html' or file_path == '' or file_path == '/':
                index_path = site_dir / 'index.html'
                if index_path.exists():
                    full_path = index_path
                    file_path = 'index.html'
                else:
                    abort(404)
            else:
                abort(404)

        # 安全检查：确保文件在允许的目录内
        try:
            full_path.resolve().relative_to(site_dir.resolve())
            logger.info(f"Security check passed for file: {full_path}")
        except ValueError:
            # 路径在站点目录外，拒绝访问
            logger.error(f"Security check failed for file: {full_path}")
            abort(403)

        # 确定目录和文件名
        directory = str(site_dir.resolve())
        filename = file_path if file_path else 'index.html'
        logger.info(f"send_from_directory parameters: directory='{directory}', filename='{filename}'")

        # 设置适当的MIME类型
        mimetype = None
        if filename.endswith('.html'):
            mimetype = 'text/html'
        elif filename.endswith('.css'):
            mimetype = 'text/css'
        elif filename.endswith('.js'):
            mimetype = 'application/javascript'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.svg'):
            mimetype = 'image/svg+xml'
        elif filename.endswith('.ico'):
            mimetype = 'image/x-icon'

        try:
            logger.info(f"About to call send_from_directory with directory='{directory}', filename='{filename}'")
            from flask import Response
            import mimetypes
            
            # Use direct file reading as a fallback since send_from_directory is causing issues
            full_file_path = Path(directory) / filename
            logger.info(f"Reading file directly: {full_file_path}")
            
            with open(full_file_path, 'rb') as f:
                file_content = f.read()
            
            # Determine MIME type
            content_type = mimetypes.guess_type(str(full_file_path))[0] or 'application/octet-stream'
            
            return Response(file_content, mimetype=content_type)
            
        except Exception as send_error:
            logger.error(f"File serving failed: {send_error}")
            raise

    except Exception as e:
        # 记录错误但不暴露详细信息给用户
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error serving MkDocs site {site_path}: {str(e)}")
        abort(500)


@main_bp.route('/mkdocs')
@login_required
def mkdocs_dashboard():
    """MkDocs管理仪表板"""
    return render_template('mkdocs/index.html')
