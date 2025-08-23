"""
LLM API endpoints for managing LLM configurations and operations.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.llm_service import LLMService
from app.services.document_generator import DocumentGenerator

llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')
llm_service = LLMService()
document_generator = DocumentGenerator()

@llm_bp.route('/configs', methods=['GET'])
@login_required
def get_configs():
    """获取用户的LLM配置列表"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        configs = llm_service.get_user_configs(current_user.id, include_inactive)
        
        return jsonify({
            'success': True,
            'configs': [config.to_dict() for config in configs]
        })
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs', methods=['POST'])
@login_required
def create_config():
    """创建LLM配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 验证必需字段
        required_fields = ['provider', 'model_name', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        result = llm_service.create_config(
            user_id=current_user.id,
            provider=data['provider'],
            model_name=data['model_name'],
            api_key=data['api_key'],
            base_url=data.get('base_url'),
            max_tokens=data.get('max_tokens', 4000),
            temperature=data.get('temperature', 0.7),
            config_metadata=data.get('config_metadata')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            status_code = 400
            if result.get('error_type') == 'unsupported_provider':
                status_code = 400
            elif 'validation_errors' in result:
                status_code = 422
            
            return jsonify(result), status_code
            
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs/<int:config_id>', methods=['GET'])
@login_required
def get_config(config_id):
    """获取特定LLM配置"""
    try:
        config = llm_service.get_config_by_id(config_id, current_user.id)
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        return jsonify({
            'success': True,
            'config': config.to_dict()
        })
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs/<int:config_id>', methods=['PUT'])
@login_required
def update_config(config_id):
    """更新LLM配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = llm_service.update_config(config_id, current_user.id, **data)
        
        if result['success']:
            return jsonify(result)
        else:
            status_code = 400
            if result.get('error_type') == 'not_found':
                status_code = 404
            elif 'validation_errors' in result:
                status_code = 422
            
            return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@login_required
def delete_config(config_id):
    """删除LLM配置"""
    try:
        result = llm_service.delete_config(config_id, current_user.id)
        
        if result['success']:
            return jsonify(result)
        else:
            status_code = 400
            if result.get('error_type') == 'not_found':
                status_code = 404
            elif result.get('error_type') == 'has_dependencies':
                status_code = 409
        
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs/<int:config_id>/activate', methods=['POST'])
@login_required
def activate_config(config_id):
    """激活LLM配置"""
    try:
        result = llm_service.set_active_config(config_id, current_user.id)
        
        if result['success']:
            return jsonify(result)
        else:
            status_code = 404 if result.get('error_type') == 'not_found' else 400
            return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs/<int:config_id>/test', methods=['POST'])
@login_required
def test_config(config_id):
    """测试LLM配置"""
    try:
        result = llm_service.test_config(config_id, current_user.id)
        
        if result['success']:
            return jsonify(result)
        else:
            status_code = 404 if result.get('error_type') == 'not_found' else 400
            return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/configs/active', methods=['GET'])
@login_required
def get_active_config():
    """获取活跃的LLM配置"""
    try:
        config = llm_service.get_active_config(current_user.id)
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'No active configuration found'
            }), 404
        
            return jsonify({
            'success': True,
            'config': config.to_dict()
        })
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取LLM配置统计信息"""
    try:
        result = llm_service.get_config_stats(current_user.id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/providers', methods=['GET'])
@login_required
def get_providers():
    """获取可用的LLM提供商"""
    try:
        from app.utils.llm_client import LLMClientFactory
        
        factory = LLMClientFactory()
        providers = factory.get_available_providers()
        
        return jsonify({
            'success': True,
            'providers': providers
        })
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# Document Generation Endpoints
@llm_bp.route('/repositories/<int:repository_id>/generate-docs', methods=['POST'])
@login_required
def generate_repository_documentation():
    """生成技术文档"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 验证必需字段
        required_fields = ['llm_config_id', 'doc_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        repository_id = request.view_args['repository_id']
        llm_config_id = data['llm_config_id']
        doc_type = data['doc_type']
        doc_title = data.get('doc_title')
        
        # 验证文档类型
        valid_doc_types = ['overview', 'api', 'database', 'architecture', 'quality', 'testing']
        if doc_type not in valid_doc_types:
            return jsonify({
                'success': False,
                'error': f'Invalid document type: {doc_type}',
                'valid_types': valid_doc_types
            }), 400
        
        # 生成文档
        result = document_generator.generate_document(
            repository_id=repository_id,
            user_id=current_user.id,
            llm_config_id=llm_config_id,
            doc_type=doc_type,
            doc_title=doc_title
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            status_code = 400
            if result.get('error_type') == 'not_found':
                status_code = 404
            
            return jsonify(result), status_code
            
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/tasks/<int:task_id>/status', methods=['GET'])
@login_required
def get_generation_status(task_id):
    """获取文档生成状态"""
    try:
        result = document_generator.get_generation_status(task_id, current_user.id)
        
        if result['success']:
            return jsonify(result)
        else:
            status_code = 404 if result.get('error_type') == 'not_found' else 400
            return jsonify(result), status_code
            
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/documents', methods=['GET'])
@login_required
def get_user_documents():
    """获取用户文档列表"""
    try:
        repository_id = request.args.get('repository_id', type=int)
        doc_type = request.args.get('doc_type')
        limit = request.args.get('limit', 50, type=int)
        
        documents = document_generator.get_user_documents(
            user_id=current_user.id,
            repository_id=repository_id,
            doc_type=doc_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents],
            'total': len(documents)
        })
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/documents/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    """获取特定文档"""
    try:
        document = document_generator.get_document_by_id(document_id, current_user.id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document': document.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/prompt-templates', methods=['GET'])
@login_required
def get_prompt_templates():
    """获取提示词模板"""
    try:
        from app.services.prompt_service import PromptService
        
        prompt_service = PromptService()
        templates = prompt_service.get_available_templates()
        
        return jsonify({
            'success': True,
            'templates': templates,
            'categories': prompt_service.get_categories()
        })
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/prompt-templates/<template_name>', methods=['GET'])
@login_required
def get_prompt_template(template_name):
    """获取特定提示词模板"""
    try:
        from app.services.prompt_service import PromptService
        
        prompt_service = PromptService()
        template = prompt_service.get_template_by_name(template_name)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        return jsonify({
            'success': True,
            'template': template
        })
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@llm_bp.route('/prompt-templates/format', methods=['POST'])
@login_required
def format_prompt_template():
    """格式化提示词模板"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        template_name = data.get('template_name')
        variables = data.get('variables', {})
        
        if not template_name:
            return jsonify({
                'success': False,
                'error': 'Template name is required'
            }), 400
        
        from app.services.prompt_service import PromptService
        
        prompt_service = PromptService()
        result = prompt_service.format_prompt(template_name, variables)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500