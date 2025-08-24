"""
智能文档生成 API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from ..services.smart_doc_service import SmartDocumentService
from ..services.workflow_monitor import workflow_monitor
from ..services.credential_validator import credential_validator
from ..services.service_orchestrator import service_orchestrator
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
            return jsonify({
                'success': True,
                'task_id': result['task_id'],
                'document_id': result.get('document_id'),
                'session_id': result.get('session_id'),
                'message': 'Smart document generation started successfully'
            }), 200
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


@bp.route('/workflow/<workflow_id>/status', methods=['GET'])
@login_required
def get_workflow_status(workflow_id):
    """
    获取工作流状态和监控信息
    
    Args:
        workflow_id: 工作流ID
    """
    try:
        # 验证用户权限 - 检查工作流是否属于当前用户
        task = Task.query.filter_by(bmad_workflow_id=workflow_id).first()
        if task:
            # 通过仓库验证用户权限
            repo = Repository.query.get(task.repository_id)
            if not repo or repo.user_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403
        
        # 获取工作流指标
        metrics = workflow_monitor.get_workflow_metrics(workflow_id)
        
        # 获取最近的事件（限制数量以避免数据过大）
        recent_events = workflow_monitor.get_workflow_events(workflow_id)
        recent_events = recent_events[-50:]  # 最近50个事件
        
        # 构建响应数据
        response_data = {
            'workflow_id': workflow_id,
            'status': 'active' if metrics else 'inactive',
            'metrics': {
                'start_time': metrics.start_time.isoformat() if metrics and metrics.start_time else None,
                'end_time': metrics.end_time.isoformat() if metrics and metrics.end_time else None,
                'total_execution_time': metrics.total_execution_time if metrics else None,
                'agent_count': metrics.agent_count if metrics else 0,
                'completed_agents': metrics.completed_agents if metrics else 0,
                'failed_agents': metrics.failed_agents if metrics else 0,
                'error_count': metrics.error_count if metrics else 0,
                'warning_count': metrics.warning_count if metrics else 0
            } if metrics else None,
            'recent_events': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type.value,
                    'agent_name': event.agent_name,
                    'message': event.message,
                    'execution_time': event.execution_time
                }
                for event in recent_events
            ]
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get workflow status: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/workflow/<workflow_id>/events', methods=['GET'])
@login_required
def get_workflow_events(workflow_id):
    """
    获取工作流详细事件日志
    
    Args:
        workflow_id: 工作流ID
    
    Query Parameters:
        event_types: 逗号分隔的事件类型过滤器
        limit: 返回事件数量限制（默认100）
    """
    try:
        # 验证用户权限
        task = Task.query.filter_by(bmad_workflow_id=workflow_id).first()
        if task:
            repo = Repository.query.get(task.repository_id)
            if not repo or repo.user_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403
        
        # 解析查询参数
        event_types_param = request.args.get('event_types', '')
        limit = int(request.args.get('limit', 100))
        
        # 转换事件类型过滤器
        event_types = None
        if event_types_param:
            from ..services.workflow_monitor import WorkflowEventType
            try:
                event_types = [WorkflowEventType(event_type.strip()) for event_type in event_types_param.split(',')]
            except ValueError:
                return jsonify({'error': 'Invalid event_types parameter'}), 400
        
        # 获取事件
        events = workflow_monitor.get_workflow_events(workflow_id, event_types)
        
        # 应用限制
        if limit > 0:
            events = events[-limit:]
        
        # 构建响应
        response_data = {
            'workflow_id': workflow_id,
            'total_events': len(events),
            'events': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type.value,
                    'agent_name': event.agent_name,
                    'message': event.message,
                    'data': event.data,
                    'execution_time': event.execution_time,
                    'error_traceback': event.error_traceback if current_app.debug else None
                }
                for event in events
            ]
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get workflow events: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/workflows/active', methods=['GET'])
@login_required 
def get_active_workflows():
    """
    获取当前用户的活动工作流列表
    """
    try:
        # 获取所有活动工作流
        all_active_workflows = workflow_monitor.get_active_workflows()
        
        # 过滤属于当前用户的工作流
        user_workflows = []
        for workflow_id, metrics in all_active_workflows.items():
            # 通过任务表查找工作流所属用户
            task = Task.query.filter_by(bmad_workflow_id=workflow_id).first()
            if task:
                repo = Repository.query.get(task.repository_id)
                if repo and repo.user_id == current_user.id:
                    user_workflows.append({
                        'workflow_id': workflow_id,
                        'repository_id': task.repository_id,
                        'repository_name': repo.name,
                        'task_id': task.id,
                        'start_time': metrics.start_time.isoformat(),
                        'agent_count': metrics.agent_count,
                        'completed_agents': metrics.completed_agents,
                        'failed_agents': metrics.failed_agents,
                        'error_count': metrics.error_count,
                        'warning_count': metrics.warning_count
                    })
        
        return jsonify({
            'active_workflows': user_workflows,
            'total_count': len(user_workflows)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get active workflows: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/credentials/validate', methods=['POST'])
@login_required
def validate_credentials():
    """
    验证Claude Code凭证
    
    Request Body:
        {
            "api_key": "your-claude-api-key",
            "workspace_id": "your-workspace-id",
            "force_refresh": false  # optional
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        api_key = data.get('api_key')
        workspace_id = data.get('workspace_id') 
        force_refresh = data.get('force_refresh', False)
        
        if not api_key or not workspace_id:
            return jsonify({
                'error': 'Both api_key and workspace_id are required'
            }), 400
        
        # 执行凭证验证
        validation_result = credential_validator.validate_claude_credentials(
            api_key, workspace_id, force_refresh
        )
        
        # 构建响应（隐藏敏感信息）
        response_data = {
            'valid': validation_result['valid'],
            'message': validation_result.get('message', ''),
            'error': validation_result.get('error'),
            'error_type': validation_result.get('error_type'),
            'details': validation_result.get('details', {}),
            'workspace_id': workspace_id,  # 可以显示工作空间ID
            'api_key_preview': f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "****"  # 只显示部分密钥
        }
        
        # 移除敏感的调试信息
        if 'details' in response_data and 'exception' in response_data['details']:
            response_data['details']['exception'] = '[Hidden for security]'
        
        status_code = 200 if validation_result['valid'] else 400
        return jsonify(response_data), status_code
        
    except Exception as e:
        current_app.logger.error(f"Credential validation API error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'valid': False
        }), 500


@bp.route('/credentials/validate-environment', methods=['GET'])
@login_required
def validate_environment_credentials():
    """
    验证环境变量中的Claude Code凭证
    """
    try:
        # 执行环境凭证验证
        validation_result = credential_validator.validate_environment_credentials()
        
        # 构建响应（隐藏敏感信息）
        response_data = {
            'valid': validation_result['valid'],
            'message': validation_result.get('message', ''),
            'error': validation_result.get('error'),
            'error_type': validation_result.get('error_type'),
            'configured': bool(current_app.config.get('CLAUDE_API_KEY') and 
                              current_app.config.get('CLAUDE_WORKSPACE_ID')),
            'validation_time': datetime.utcnow().isoformat()
        }
        
        # 添加配置状态信息（不显示实际值）
        if current_app.config.get('CLAUDE_API_KEY'):
            api_key = current_app.config.get('CLAUDE_API_KEY')
            response_data['api_key_configured'] = True
            response_data['api_key_preview'] = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "****"
        else:
            response_data['api_key_configured'] = False
        
        if current_app.config.get('CLAUDE_WORKSPACE_ID'):
            response_data['workspace_id_configured'] = True
            response_data['workspace_id'] = current_app.config.get('CLAUDE_WORKSPACE_ID')
        else:
            response_data['workspace_id_configured'] = False
        
        status_code = 200 if validation_result['valid'] else 400
        return jsonify(response_data), status_code
        
    except Exception as e:
        current_app.logger.error(f"Environment credential validation error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'valid': False
        }), 500


@bp.route('/credentials/summary', methods=['GET'])
@login_required
def get_credential_validation_summary():
    """
    获取凭证验证摘要信息
    """
    try:
        summary = credential_validator.get_validation_summary()
        
        return jsonify({
            'validation_cache_summary': summary,
            'environment_status': {
                'api_key_configured': bool(current_app.config.get('CLAUDE_API_KEY')),
                'workspace_id_configured': bool(current_app.config.get('CLAUDE_WORKSPACE_ID'))
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get credential summary: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/credentials/clear-cache', methods=['POST'])
@login_required
def clear_credential_cache():
    """
    清空凭证验证缓存
    """
    try:
        credential_validator.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Credential validation cache cleared successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to clear credential cache: {e}")
        return jsonify({
            'error': 'Internal server error',
            'success': False
        }), 500


@bp.route('/services/status', methods=['GET'])
@login_required
def get_services_status():
    """
    获取所有服务状态
    """
    try:
        all_status = service_orchestrator.get_all_service_status()
        
        # 计算整体系统健康状态
        total_services = len(all_status)
        healthy_services = sum(1 for status in all_status.values() 
                              if status and status.get('status') == 'healthy')
        degraded_services = sum(1 for status in all_status.values() 
                               if status and status.get('status') == 'degraded')
        unhealthy_services = sum(1 for status in all_status.values() 
                                if status and status.get('status') in ['unhealthy', 'failed'])
        
        # 确定整体系统状态
        if unhealthy_services > 0:
            overall_status = 'unhealthy'
        elif degraded_services > 0:
            overall_status = 'degraded'
        elif healthy_services == total_services:
            overall_status = 'healthy'
        else:
            overall_status = 'unknown'
        
        response_data = {
            'overall_status': overall_status,
            'summary': {
                'total_services': total_services,
                'healthy': healthy_services,
                'degraded': degraded_services,
                'unhealthy': unhealthy_services
            },
            'services': all_status,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get services status: {e}")
        return jsonify({
            'error': 'Internal server error',
            'overall_status': 'unknown'
        }), 500


@bp.route('/services/<service_name>/status', methods=['GET'])
@login_required
def get_single_service_status(service_name):
    """
    获取单个服务状态
    
    Args:
        service_name: 服务名称
    """
    try:
        status = service_orchestrator.get_service_status(service_name)
        
        if status:
            return jsonify(status), 200
        else:
            return jsonify({
                'error': f'Service {service_name} not found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Failed to get service status for {service_name}: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/services/health-check', methods=['POST'])
@login_required
def trigger_health_check():
    """
    手动触发所有服务的健康检查
    """
    try:
        # 手动执行健康检查
        service_orchestrator._perform_all_health_checks()
        
        # 获取更新后的状态
        all_status = service_orchestrator.get_all_service_status()
        
        return jsonify({
            'success': True,
            'message': 'Health check completed',
            'services': all_status,
            'checked_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to trigger health check: {e}")
        return jsonify({
            'error': 'Internal server error',
            'success': False
        }), 500



