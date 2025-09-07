"""
Document API endpoints.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from app.services.claude_code_service import ClaudeCodeService
from app.services.document_generator import DocumentGenerator
from app.services.document_generation_service import DocumentGenerationService
from app.utils.logger import get_logger
from app import db
from sqlalchemy import and_
from pathlib import Path
import io

document_bp = Blueprint('document', __name__, url_prefix='/api/documents')
claude_service = ClaudeCodeService()
doc_generator = DocumentGenerator()
doc_generation_service = DocumentGenerationService()
logger = get_logger(__name__)


@document_bp.route('/', methods=['GET'])
@login_required
def get_documents():
    """获取用户文档列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '')
        status = request.args.get('status', '')

        documents, stats, pagination = claude_service.get_documents(
            current_user.id, page, limit, search, status
        )

        return jsonify({
            'success': True,
            'documents': documents,
            'stats': stats,
            'pagination': pagination
        })

    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return jsonify({'error': '获取文档列表失败'}), 500


@document_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_documents():
    """获取最近创建的文档"""
    try:
        limit = int(request.args.get('limit', 5))
        limit = min(max(1, limit), 20)  # Limit between 1 and 20

        from app.models.document import Document
        from datetime import datetime, timedelta

        # Get documents from the last 30 days, ordered by creation date
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_documents = Document.query.filter(
            Document.user_id == current_user.id,
            Document.created_at >= thirty_days_ago
        ).order_by(Document.created_at.desc()).limit(limit).all()

        documents_data = []
        for doc in recent_documents:
            doc_dict = doc.to_dict()
            # Add repository information if available
            if doc.repository:
                doc_dict['repository'] = {
                    'id': doc.repository.id,
                    'name': doc.repository.name,
                    'url': doc.repository.url
                }
            documents_data.append(doc_dict)

        return jsonify({
            'success': True,
            'documents': documents_data,
            'total': len(documents_data),
            'limit': limit
        })

    except Exception as e:
        logger.error(f"获取最近文档失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取最近文档失败',
            'documents': []
        }), 500


@document_bp.route('/', methods=['POST'])
@login_required
def create_document():
    """创建新文档"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        required_fields = ['title', 'repository_id', 'document_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        document = claude_service.create_document(
            user_id=current_user.id,
            title=data['title'],
            repository_id=data['repository_id'],
            document_type=data['document_type'],
            description=data.get('description', '')
        )

        return jsonify({
            'success': True,
            'document': document
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建文档失败: {e}")
        return jsonify({'error': '创建文档失败'}), 500


@document_bp.route('/simple', methods=['POST'])
@login_required
def create_simple_document():
    """创建简单文档（不需要仓库）"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        # 创建一个默认仓库或使用系统仓库
        from app.models.repository import Repository

        # 查找或创建用户的默认文档仓库
        default_repo = Repository.query.filter(
            and_(
                Repository.user_id == current_user.id,
                Repository.name == '个人文档'
            )
        ).first()

        if not default_repo:
            default_repo = Repository(
                name='个人文档',
                description='个人创建的文档集合',
                user_id=current_user.id,
                is_public=False
            )
            db.session.add(default_repo)
            db.session.commit()

        document = claude_service.create_document(
            user_id=current_user.id,
            title=data['title'],
            repository_id=default_repo.id,
            document_type=data.get('document_type', 'manual'),
            description=data.get('description', ''),
            content=data['content']
        )

        return jsonify({
            'success': True,
            'id': document['id'],
            'title': document['title'],
            'created_at': document['created_at']
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建简单文档失败: {e}")
        return jsonify({'error': '创建文档失败'}), 500


@document_bp.route('/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    """获取单个文档"""
    try:
        document = claude_service.get_document(document_id, current_user.id)

        if not document:
            return jsonify({'error': '文档不存在或无权限访问'}), 404

        return jsonify({
            'success': True,
            'document': document
        })

    except Exception as e:
        logger.error(f"获取文档失败: {e}")
        return jsonify({'error': '获取文档失败'}), 500


@document_bp.route('/claude-code/status', methods=['GET'])
@login_required
def get_claude_code_status():
    """获取Claude Code服务状态"""
    try:
        status = doc_generator.check_claude_code_service_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取Claude Code服务状态失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取Claude Code服务状态失败',
            'details': str(e)
        }), 500


@document_bp.route('/mcp/status', methods=['GET'])
@login_required
def get_mcp_status():
    """获取MCP服务状态"""
    try:
        status = doc_generator.check_mcp_service_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取MCP服务状态失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取MCP服务状态失败',
            'details': str(e)
        }), 500


@document_bp.route('/doc-types', methods=['GET'])
@login_required
def get_doc_types():
    """获取支持的文档类型"""
    try:
        doc_types = doc_generator.get_available_doc_types()
        return jsonify(doc_types)
    except Exception as e:
        logger.error(f"获取文档类型失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取文档类型失败',
            'details': str(e)
        }), 500


@document_bp.route('/mcp/doc-types', methods=['GET'])
@login_required
def get_mcp_doc_types():
    """获取MCP服务支持的文档类型"""
    try:
        doc_types = doc_generator.get_available_doc_types()
        return jsonify(doc_types)
    except Exception as e:
        logger.error(f"获取MCP文档类型失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取MCP文档类型失败',
            'details': str(e)
        }), 500


@document_bp.route('/generate', methods=['POST'])
@login_required
def generate_new_document():
    """生成文档（支持MCP服务）"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        required_fields = ['repository_id', 'llm_config_id', 'doc_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        # 调用文档生成器
        result = doc_generator.generate_document(
            repository_id=data['repository_id'],
            user_id=current_user.id,
            llm_config_id=data['llm_config_id'],
            doc_type=data['doc_type'],
            doc_title=data.get('doc_title')
        )

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"生成文档失败: {e}")
        return jsonify({
            'success': False,
            'error': '生成文档失败',
            'details': str(e)
        }), 500


@document_bp.route('/<int:document_id>', methods=['PUT'])
@login_required
def update_document(document_id):
    """更新文档"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        document = claude_service.update_document(document_id, current_user.id, **data)

        if not document:
            return jsonify({'error': '文档不存在或无权限访问'}), 404

        return jsonify({
            'success': True,
            'document': document
        })

    except Exception as e:
        logger.error(f"更新文档失败: {e}")
        return jsonify({'error': '更新文档失败'}), 500


@document_bp.route('/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """删除文档"""
    try:
        success = claude_service.delete_document(document_id, current_user.id)

        if not success:
            return jsonify({'error': '文档不存在或无权限删除'}), 404

        return jsonify({'message': '文档删除成功'})

    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        return jsonify({'error': '删除文档失败'}), 500


@document_bp.route('/<int:document_id>/generate', methods=['POST'])
@login_required
def generate_document(document_id):
    """生成文档内容"""
    try:
        success = claude_service.generate_document_content(document_id, current_user.id)

        if not success:
            return jsonify({'error': '文档不存在或无权限生成'}), 404

        return jsonify({'message': '文档生成任务已启动'})
    except Exception as e:
        logger.error(f"生成文档失败: {e}")
        return jsonify({'error': '生成文档失败'}), 500


@document_bp.route('/<int:document_id>/download', methods=['GET'])
@login_required
def download_document(document_id):
    """下载文档"""
    try:
        result = claude_service.download_document(document_id, current_user.id)

        if not result:
            return jsonify({'error': '文档不存在或无权限下载'}), 404

        # 创建内存文件对象
        file_obj = io.BytesIO(result['content'].encode('utf-8'))
        file_obj.seek(0)

        return send_file(
            file_obj,
            as_attachment=True,
            download_name=result['filename'],
            mimetype=result['content_type']
        )

    except Exception as e:
        logger.error(f"下载文档失败: {e}")
        return jsonify({'error': '下载文档失败'}), 500


@document_bp.route('/<int:document_id>/content', methods=['GET'])
@login_required
def get_document_content(document_id):
    """获取文档内容"""
    try:
        document = claude_service.get_document(document_id, current_user.id)

        if not document:
            return jsonify({'error': '文档不存在或无权限访问'}), 404

        return jsonify({
            'success': True,
            'content': document.get('content', ''),
            'metadata': {
                'id': document['id'],
                'title': document['title'],
                'status': document['status'],
                'document_type': document['document_type'],
                'version': '1.0.0'
            }
        })

    except Exception as e:
        logger.error(f"获取文档内容失败: {e}")
        return jsonify({'error': '获取文档内容失败'}), 500


@document_bp.route('/<int:document_id>/toc', methods=['GET'])
@login_required
def get_document_toc(document_id):
    """获取文档目录"""
    try:
        document = claude_service.get_document(document_id, current_user.id)

        if not document:
            return jsonify({'error': '文档不存在或无权限访问'}), 404

        content = document.get('content', '')
        toc = claude_service.generate_toc(content)

        return jsonify({
            'success': True,
            'toc': toc
        })

    except Exception as e:
        logger.error(f"获取文档目录失败: {e}")
        return jsonify({'error': '获取文档目录失败'}), 500


@document_bp.route('/repository/<int:repository_id>/generate-ai-docs', methods=['POST'])
@login_required
def generate_ai_docs_for_repository(repository_id):
    """为仓库生成AI技术文档"""
    try:
        from app.models.repository import Repository
        
        # 验证仓库存在且用户有权限
        repository = Repository.query.filter_by(id=repository_id, user_id=current_user.id).first()
        if not repository:
            return jsonify({'error': '仓库不存在或无权限访问'}), 404
        
        logger.info(f"开始为仓库 {repository.name} (ID: {repository_id}) 生成AI文档")
        
        # 调用优化后的文档生成服务
        result = doc_generation_service.generate_docs_for_repository(
            repository_id=repository_id
        )
        
        if result['success']:
            logger.info(f"文档生成成功: {result['output_directory']}")
            return jsonify({
                'success': True,
                'message': f"成功生成 {result['statistics']['successful_prompts']}/{result['statistics']['total_prompts']} 个文档",
                'output_directory': result['output_directory'],
                'generated_files': result['generated_files'],
                'results': result['results'],
                'statistics': result['statistics']
            })
        else:
            logger.error(f"文档生成失败: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"AI文档生成过程发生异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'文档生成失败: {str(e)}'
        }), 500


@document_bp.route('/ai-docs/status/<int:repository_id>', methods=['GET'])
@login_required
def get_ai_docs_status(repository_id):
    """获取仓库AI文档生成状态"""
    try:
        from app.models.repository import Repository
        from app.models.document import Document
        
        # 验证仓库存在且用户有权限
        repository = Repository.query.filter_by(id=repository_id, user_id=current_user.id).first()
        if not repository:
            return jsonify({'error': '仓库不存在或无权限访问'}), 404
        
        # 查找AI生成的文档
        ai_documents = Document.query.filter_by(
            repository_id=repository_id,
            document_type='ai_generated'
        ).all()
        
        # 使用DirectoryService检查输出目录
        from app.services.directory_service import DirectoryService
        directory_service = DirectoryService()
        output_dir_path = directory_service.get_ai_docs_directory(repository.name, repository_id)
        output_dir = Path(output_dir_path)
        
        return jsonify({
            'success': True,
            'repository_name': repository.name,
            'repository_id': repository_id,
            'has_ai_docs': len(ai_documents) > 0,
            'ai_documents_count': len(ai_documents),
            'output_directory_exists': output_dir.exists(),
            'output_path': str(output_dir) if output_dir.exists() else None,
            'ai_documents': [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'created_at': doc.created_at.isoformat(),
                    'status': doc.status,
                    'file_path': doc.file_path
                }
                for doc in ai_documents
            ]
        })
        
    except Exception as e:
        logger.error(f"获取AI文档状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取状态失败: {str(e)}'
        }), 500
