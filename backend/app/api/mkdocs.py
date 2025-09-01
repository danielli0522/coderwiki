"""
MkDocs API endpoints for static documentation site generation
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.mkdocs_service import MkDocsService
from app.utils.logger import get_logger

logger = get_logger(__name__)

mkdocs_bp = Blueprint('mkdocs', __name__, url_prefix='/api/mkdocs')


@mkdocs_bp.route('/repositories/<int:repository_id>/build-site', methods=['POST'])
@login_required
def build_mkdocs_site(repository_id):
    """Build MkDocs static site for a repository."""
    try:
        mkdocs_service = MkDocsService()
        result = mkdocs_service.build_site_for_repository(repository_id, current_user.id)
        
        if result['success']:
            logger.info(f"MkDocs site built successfully for repository {repository_id} by user {current_user.id}")
            return jsonify(result), 200
        else:
            logger.warning(f"Failed to build MkDocs site for repository {repository_id}: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in build_mkdocs_site for repository {repository_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500


@mkdocs_bp.route('/repositories/<int:repository_id>/site-status', methods=['GET'])
@login_required
def get_site_status(repository_id):
    """Get MkDocs site build status for a repository."""
    try:
        mkdocs_service = MkDocsService()
        result = mkdocs_service.get_site_status(repository_id, current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in get_site_status for repository {repository_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500


@mkdocs_bp.route('/repositories/<int:repository_id>/delete-site', methods=['DELETE'])
@login_required
def delete_mkdocs_site(repository_id):
    """Delete MkDocs site for a repository."""
    try:
        mkdocs_service = MkDocsService()
        result = mkdocs_service.delete_site(repository_id, current_user.id)
        
        if result['success']:
            logger.info(f"MkDocs site deleted successfully for repository {repository_id} by user {current_user.id}")
            return jsonify(result), 200
        else:
            logger.warning(f"Failed to delete MkDocs site for repository {repository_id}: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in delete_mkdocs_site for repository {repository_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500


@mkdocs_bp.route('/sites', methods=['GET'])
@login_required
def list_user_sites():
    """List all MkDocs sites for current user."""
    try:
        mkdocs_service = MkDocsService()
        result = mkdocs_service.list_all_sites(current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in list_user_sites for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500


@mkdocs_bp.route('/repositories/<int:repository_id>/rebuild-site', methods=['POST'])
@login_required
def rebuild_mkdocs_site(repository_id):
    """Rebuild MkDocs site for a repository (delete and build)."""
    try:
        mkdocs_service = MkDocsService()
        
        # 首先删除现有站点（如果存在）
        delete_result = mkdocs_service.delete_site(repository_id, current_user.id)
        if not delete_result['success'] and 'does not exist' not in delete_result.get('message', ''):
            return jsonify(delete_result), 400
        
        # 然后重新构建站点
        build_result = mkdocs_service.build_site_for_repository(repository_id, current_user.id)
        
        if build_result['success']:
            logger.info(f"MkDocs site rebuilt successfully for repository {repository_id} by user {current_user.id}")
            build_result['message'] = 'MkDocs site rebuilt successfully'
            return jsonify(build_result), 200
        else:
            logger.warning(f"Failed to rebuild MkDocs site for repository {repository_id}: {build_result.get('error')}")
            return jsonify(build_result), 400
            
    except Exception as e:
        logger.error(f"Error in rebuild_mkdocs_site for repository {repository_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500


@mkdocs_bp.route('/status', methods=['GET'])
@login_required
def get_mkdocs_service_status():
    """Get MkDocs service status and configuration."""
    try:
        mkdocs_service = MkDocsService()
        
        # 检查MkDocs命令是否可用
        mkdocs_cmd = mkdocs_service._get_mkdocs_command()
        
        status_info = {
            'success': True,
            'mkdocs_available': mkdocs_cmd is not None,
            'mkdocs_command': mkdocs_cmd,
            'base_docs_dir': str(mkdocs_service.base_docs_dir),
            'base_mkdocs_dir': str(mkdocs_service.base_mkdocs_dir),
            'mkdocs_dir_exists': mkdocs_service.base_mkdocs_dir.exists(),
            'docs_dir_exists': mkdocs_service.base_docs_dir.exists()
        }
        
        # 获取用户站点统计
        user_sites = mkdocs_service.list_all_sites(current_user.id)
        if user_sites['success']:
            status_info['user_sites_count'] = user_sites['total_sites']
            status_info['built_sites_count'] = user_sites['built_sites']
        
        return jsonify(status_info), 200
        
    except Exception as e:
        logger.error(f"Error in get_mkdocs_service_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500