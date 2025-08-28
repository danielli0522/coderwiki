"""
智能文档生成 API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from ..services.smart_doc_service import SmartDocumentService
from ..models.repository import Repository
from ..models.task import Task
from ..models.document import Document
from ..models.bmad_agent_execution import BMADAgentExecution

bp = Blueprint('smart_document', __name__, url_prefix='/api/smart-document')


@bp.route('/generate/<int:repository_id>', methods=['POST'])
@login_required
def generate_smart_document(repository_id):
    """
    启动智能文档生成

    Args:
        repository_id: 仓库ID

    Request Body:
        {
            "analysis_depth": "detailed",  # 分析深度: basic, detailed, comprehensive
            "include_diagrams": true,      # 是否包含图表
            "include_troubleshooting": true, # 是否包含故障排除
            "doc_type": "complete"         # 文档类型: overview, architecture, flow, complete
        }
    """
    try:
        # 验证仓库是否存在且属于当前用户
        repository = Repository.query.filter_by(
            id=repository_id,
            user_id=current_user.id
        ).first()

        if not repository:
            return jsonify({'error': 'Repository not found'}), 404

        # 获取请求参数
        data = request.get_json() or {}
        config = {
            'analysis_depth': data.get('analysis_depth', 'detailed'),
            'include_diagrams': data.get('include_diagrams', True),
            'include_troubleshooting': data.get('include_troubleshooting', True),
            'doc_type': data.get('doc_type', 'complete')
        }

        # 创建智能文档服务
        smart_service = SmartDocumentService()

        # 启动生成任务
        result = smart_service.generate_smart_document(
            repository_id=repository_id,
            user_id=current_user.id,
            config=config
        )

        if result['success']:
            response_data = {
                'success': True,
                'task_id': result['task_id'],
                'document_id': result.get('document_id'),
                'session_id': result.get('session_id'),
                'message': 'Smart document generation started successfully'
            }
            
            # 添加MkDocs站点URL（如果成功构建）
            if result.get('mkdocs_url'):
                response_data['mkdocs_url'] = result['mkdocs_url']
                response_data['message'] = 'Smart document generation and MkDocs site build completed successfully'
            
            return jsonify(response_data), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500

    except Exception as e:
        current_app.logger.error(f"Smart document generation failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/task/<int:task_id>/status', methods=['GET'])
@login_required
def get_task_status(task_id):
    """
    获取任务状态

    Args:
        task_id: 任务ID
    """
    try:
        # 验证任务是否存在且属于当前用户
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # 获取任务状态
        smart_service = SmartDocumentService()
        status = smart_service.get_task_status(task_id)

        if 'error' in status:
            return jsonify(status), 500

        return jsonify(status), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get task status: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/task/<int:task_id>/bmad-agents', methods=['GET'])
@login_required
def get_bmad_agents_status(task_id):
    """
    获取 BMAD 代理状态

    Args:
        task_id: 任务ID
    """
    try:
        # 验证任务是否存在且属于当前用户
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # 获取代理状态
        smart_service = SmartDocumentService()
        agent_status = smart_service.get_bmad_agents_status(task_id)

        if 'error' in agent_status:
            return jsonify(agent_status), 500

        return jsonify(agent_status), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get BMAD agents status: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/repository/<int:repository_id>/documents', methods=['GET'])
@login_required
def get_smart_documents(repository_id):
    """
    获取仓库的智能生成文档列表

    Args:
        repository_id: 仓库ID
    """
    try:
        # 验证仓库是否存在且属于当前用户
        repository = Repository.query.filter_by(
            id=repository_id,
            user_id=current_user.id
        ).first()

        if not repository:
            return jsonify({'error': 'Repository not found'}), 404

        # 获取智能生成的文档
        documents = Document.query.filter_by(
            repository_id=repository_id,
            doc_type='complete_documentation'
        ).order_by(Document.created_at.desc()).all()

        return jsonify({
            'documents': [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'version': doc.version,
                    'status': doc.status,
                    'created_at': doc.created_at.isoformat(),
                    'claude_session_id': doc.claude_session_id,
                    'bmad_workflow_id': doc.bmad_workflow_id
                }
                for doc in documents
            ]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get smart documents: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/document/<int:document_id>', methods=['GET'])
@login_required
def get_smart_document(document_id):
    """
    获取智能生成文档详情

    Args:
        document_id: 文档ID
    """
    try:
        # 验证文档是否存在且属于当前用户
        document = Document.query.join(Repository).filter(
            Document.id == document_id,
            Repository.user_id == current_user.id
        ).first()

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        return jsonify({
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'version': document.version,
            'status': document.status,
            'doc_type': document.doc_type,
            'created_at': document.created_at.isoformat(),
            'claude_session_id': document.claude_session_id,
            'bmad_workflow_id': document.bmad_workflow_id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get smart document: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/task/<int:task_id>/agent-executions', methods=['GET'])
@login_required
def get_agent_executions(task_id):
    """
    获取代理执行记录

    Args:
        task_id: 任务ID
    """
    try:
        # 验证任务是否存在且属于当前用户
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # 获取代理执行记录
        executions = BMADAgentExecution.get_by_task_id(task_id)

        return jsonify({
            'executions': [execution.to_dict() for execution in executions]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get agent executions: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/config', methods=['GET'])
@login_required
def get_generation_config():
    """
    获取智能文档生成配置选项
    """
    try:
        config_options = {
            'analysis_depth': [
                {'value': 'basic', 'label': 'Basic Analysis', 'description': 'Quick overview and basic structure'},
                {'value': 'detailed', 'label': 'Detailed Analysis', 'description': 'Comprehensive code and architecture analysis'},
                {'value': 'comprehensive', 'label': 'Comprehensive Analysis', 'description': 'Deep analysis with all BMAD agents'}
            ],
            'doc_type': [
                {'value': 'overview', 'label': 'Technical Overview', 'description': 'High-level project overview'},
                {'value': 'architecture', 'label': 'Architecture Analysis', 'description': 'Detailed architecture documentation'},
                {'value': 'flow', 'label': 'Flow Analysis', 'description': 'Business process and data flow analysis'},
                {'value': 'complete', 'label': 'Complete Documentation', 'description': 'Full technical documentation with all sections'}
            ],
            'features': [
                {'name': 'include_diagrams', 'label': 'Include Diagrams', 'description': 'Generate visual diagrams and charts'},
                {'name': 'include_troubleshooting', 'label': 'Include Troubleshooting', 'description': 'Add problem diagnosis and solutions'},
                {'name': 'include_code_examples', 'label': 'Include Code Examples', 'description': 'Add relevant code snippets and examples'}
            ]
        }

        return jsonify(config_options), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get generation config: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


