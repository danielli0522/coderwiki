"""
Repository API endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.repository_service import RepositoryService
from app.utils.repository_analyzer import RepositoryAnalyzer

repository_bp = Blueprint('repository', __name__, url_prefix='/api/repositories')

@repository_bp.route('', methods=['GET'])
@login_required
def get_repositories():
    """Get user repositories with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_field = request.args.get('sort_field', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        status_filter = request.args.get('status')
        search_query = request.args.get('search')

        # Validate parameters
        if per_page < 1 or per_page > 50:
            per_page = 10
        if page < 1:
            page = 1

        repo_service = RepositoryService()
        result = repo_service.get_repositories_paginated(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            status_filter=status_filter,
            search_query=search_query
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/statistics', methods=['GET'])
@login_required
def get_repository_statistics():
    """Get repository statistics for current user."""
    try:
        repo_service = RepositoryService()
        stats = repo_service.get_repository_statistics(current_user.id)

        return jsonify({
            'success': True,
            'statistics': stats
        })

    except Exception as e:
        return jsonify({'error': '获取统计数据失败'}), 500

@repository_bp.route('', methods=['POST'])
@login_required
def add_repository():
    """Add a new repository."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        url = data.get('url')
        name = data.get('name')
        description = data.get('description')

        if not url:
            return jsonify({'error': '仓库URL不能为空'}), 400

        repo_service = RepositoryService()
        result = repo_service.create_repository(
            user_id=current_user.id,
            url=url,
            name=name,
            description=description
        )

        if result['success']:
            try:
                # Get the created repository
                logger.info(f"Getting repository by ID: {result['repository_id']} for user {current_user.id}")
                repository = repo_service.get_repository_by_id(result['repository_id'], current_user.id)
                
                if not repository:
                    logger.error(f"Repository {result['repository_id']} not found after creation")
                    return jsonify({'error': '创建的仓库未找到'}), 500
                    
                logger.info(f"Converting repository to dict: {repository.name}")
                repo_dict = repository.to_dict()
                
                return jsonify({
                    'success': True,
                    'repository': repo_dict,
                    'message': result['message']
                }), 201
            
            except Exception as e:
                logger.error(f"Error getting created repository: {e}")
                # 返回基本信息，即使to_dict()失败
                return jsonify({
                    'success': True,
                    'repository': {
                        'id': result['repository_id'],
                        'name': result.get('name', name),
                        'url': url,
                        'status': 'cloning'
                    },
                    'message': result['message']
                }), 201
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        logger.error(f"Add repository failed: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>', methods=['GET'])
@login_required
def get_repository(repository_id):
    """Get a specific repository."""
    try:
        repo_service = RepositoryService()
        repository = repo_service.get_repository_by_id(repository_id, current_user.id)

        if not repository:
            return jsonify({'error': '仓库不存在或您没有权限'}), 404

        return jsonify({
            'success': True,
            'repository': repository.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>', methods=['PUT'])
@login_required
def update_repository(repository_id):
    """Update a repository."""
    print(f"DEBUG: PUT /api/repositories/{repository_id} - Method: {request.method}")
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        repo_service = RepositoryService()
        result = repo_service.update_repository(
            repository_id=repository_id,
            user_id=current_user.id,
            **data
        )

        if result['success']:
            repository = repo_service.get_repository_by_id(repository_id, current_user.id)
            return jsonify({
                'success': True,
                'repository': repository.to_dict(),
                'message': result['message']
            })
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/confirm-delete', methods=['GET'])
@login_required
def get_delete_confirmation(repository_id):
    """Get deletion confirmation information for a repository."""
    try:
        repo_service = RepositoryService()
        result = repo_service.get_delete_confirmation(repository_id, current_user.id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>', methods=['DELETE'])
@login_required
def delete_repository(repository_id):
    """Delete a repository."""
    print(f"DEBUG: DELETE /api/repositories/{repository_id} - Method: {request.method}")
    try:
        repo_service = RepositoryService()
        result = repo_service.delete_repository(repository_id, current_user.id)

        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'repository_id': result.get('repository_id'),
                'repository_name': result.get('repository_name'),
                'file_cleanup': result.get('file_cleanup')
            })
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/sync', methods=['POST'])
@login_required
def sync_repository(repository_id):
    """Sync a repository."""
    try:
        repo_service = RepositoryService()
        result = repo_service.sync_repository(repository_id, current_user.id)

        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/analyze', methods=['POST'])
@login_required
def analyze_repository(repository_id):
    """Analyze a repository."""
    try:
        repo_service = RepositoryService()
        repository = repo_service.get_repository_by_id(repository_id, current_user.id)

        if not repository:
            return jsonify({'error': '仓库不存在或您没有权限'}), 404

        if not repository.is_ready_for_analysis():
            return jsonify({'error': '仓库未准备好进行分析'}), 400

        # Analyze repository
        analyzer = RepositoryAnalyzer(repository.local_path)
        analysis = analyzer.analyze_repository()

        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': '仓库分析完成'
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500


@repository_bp.route('/enhanced-statistics', methods=['GET'])
@login_required
def get_enhanced_repository_statistics():
    """Get enhanced repository statistics for dashboard."""
    try:
        repo_service = RepositoryService()
        statistics = repo_service.get_enhanced_repository_statistics(current_user.id)

        return jsonify(statistics)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/validate-url', methods=['POST'])
@login_required
def validate_repository_url():
    """Validate repository URL."""
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({'error': '请提供仓库URL'}), 400

        url = data['url']

        # Validate URL format
        if not Repository.validate_github_url(url) and not Repository.validate_git_url(url):
            return jsonify({
                'success': False,
                'valid': False,
                'message': '无效的仓库URL格式'
            })

        # Check if URL is accessible
        from app.utils.git_service import GitService
        git_service = GitService()
        is_accessible = git_service.validate_repository_url(url)

        return jsonify({
            'success': True,
            'valid': is_accessible,
            'message': 'URL格式有效' if is_accessible else 'URL无法访问'
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/status', methods=['GET'])
@login_required
def get_repository_status(repository_id):
    """Get detailed repository status."""
    try:
        repo_service = RepositoryService()
        result = repo_service.get_repository_status(repository_id, current_user.id)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/reanalyze', methods=['POST'])
@login_required
def reanalyze_repository(repository_id):
    """Start reanalysis of a repository."""
    try:
        repo_service = RepositoryService()
        result = repo_service.reanalyze_repository(repository_id, current_user.id)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/progress', methods=['PUT'])
@login_required
def update_analysis_progress(repository_id):
    """Update repository analysis progress."""
    try:
        data = request.get_json()

        if not data or 'progress' not in data:
            return jsonify({'error': '缺少进度参数'}), 400

        progress = data['progress']
        if not isinstance(progress, int) or progress < 0 or progress > 100:
            return jsonify({'error': '进度必须是0-100之间的整数'}), 400

        repo_service = RepositoryService()
        result = repo_service.update_repository_analysis_progress(
            repository_id, current_user.id, progress
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/github-stats', methods=['POST'])
@login_required
def update_github_stats(repository_id):
    """Update repository GitHub statistics."""
    try:
        repo_service = RepositoryService()
        result = repo_service.update_repository_github_stats(repository_id, current_user.id)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_repositories():
    """Delete multiple repositories."""
    try:
        data = request.get_json()

        if not data or 'repository_ids' not in data:
            return jsonify({'error': '缺少仓库ID列表'}), 400

        repository_ids = data['repository_ids']
        if not isinstance(repository_ids, list) or not repository_ids:
            return jsonify({'error': '仓库ID列表必须是非空数组'}), 400

        repo_service = RepositoryService()
        result = repo_service.bulk_delete_repositories(current_user.id, repository_ids)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500

@repository_bp.route('/<int:repository_id>/generate', methods=['POST'])
@login_required
def generate_document(repository_id):
    """Generate document for a repository."""
    try:
        data = request.get_json() or {}

        # 验证仓库是否存在
        repo_service = RepositoryService()
        repository = repo_service.get_repository_by_id(repository_id, current_user.id)

        if not repository:
            return jsonify({'error': '仓库不存在或您没有权限'}), 404

        # 获取生成参数
        document_type = data.get('document_type', 'readme')
        output_format = data.get('output_format', 'markdown')
        title = data.get('title', f'{repository.name} {document_type.title()}文档')
        description = data.get('description', f'为{repository.name}生成的{document_type}文档')

        # 创建文档记录
        from app.services.doc_service import DocumentService
        doc_service = DocumentService()

        document = doc_service.create_document(
            user_id=current_user.id,
            title=title,
            repository_id=repository_id,
            document_type=document_type,
            description=description
        )

        # 启动文档生成任务
        success = doc_service.generate_document_content(document['id'], current_user.id)

        if success:
            # 获取创建的任务ID
            from app.models.task import Task
            task = Task.query.filter_by(
                user_id=current_user.id,
                repository_id=repository_id,
                type='generate_document'
            ).order_by(Task.created_at.desc()).first()

            task_id = task.id if task else None

            return jsonify({
                'success': True,
                'message': '文档生成任务已启动',
                'document_id': document['id'],
                'task_id': task_id
            })
        else:
            return jsonify({'error': '启动文档生成任务失败'}), 500

    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500
