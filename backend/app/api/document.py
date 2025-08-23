"""
Document API endpoints.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from app.services.doc_service import DocumentService
from app.services.document_generator import DocumentGenerator
from app.utils.logger import get_logger
import io

document_bp = Blueprint('document', __name__, url_prefix='/api/documents')
doc_service = DocumentService()
doc_generator = DocumentGenerator()
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

        documents, stats = doc_service.get_documents(
            current_user.id, page, limit, search, status
        )

        return jsonify({
            'success': True,
            'documents': documents,
            'stats': stats,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': stats.get('total', 0)
            }
        })

    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return jsonify({'error': '获取文档列表失败'}), 500


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

        document = doc_service.create_document(
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


@document_bp.route('/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    """获取单个文档"""
    try:
        document = doc_service.get_document(document_id, current_user.id)

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

        document = doc_service.update_document(document_id, current_user.id, **data)

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
        success = doc_service.delete_document(document_id, current_user.id)

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
        success = doc_service.generate_document_content(document_id, current_user.id)

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
        result = doc_service.download_document(document_id, current_user.id)

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
        document = doc_service.get_document(document_id, current_user.id)

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
        document = doc_service.get_document(document_id, current_user.id)

        if not document:
            return jsonify({'error': '文档不存在或无权限访问'}), 404

        content = document.get('content', '')
        toc = doc_service.generate_toc(content)

        return jsonify({
            'success': True,
            'toc': toc
        })

    except Exception as e:
        logger.error(f"获取文档目录失败: {e}")
        return jsonify({'error': '获取文档目录失败'}), 500
