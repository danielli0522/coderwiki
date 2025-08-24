"""
Serena API端点
提供与Serena AI助手交互的接口
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from typing import Dict, Any
import asyncio

from ..services.serena_service import SerenaService

logger = logging.getLogger(__name__)

# 创建蓝图
serena_bp = Blueprint('serena', __name__, url_prefix='/api/serena')


@serena_bp.route('/status', methods=['GET'])
@login_required
def get_serena_status():
    """获取Serena服务状态"""
    try:
        serena_service = SerenaService()
        status = serena_service.get_serena_status()

        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"获取Serena状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@serena_bp.route('/assist', methods=['POST'])
@login_required
def get_serena_assistance():
    """获取Serena协助"""
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': '缺少查询内容'
            }), 400

        query = data['query']
        context = data.get('context', {})

        # 添加用户上下文
        context.update({
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': data.get('timestamp')
        })

        serena_service = SerenaService()

        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                serena_service.get_serena_assistance(query, context)
            )
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"获取Serena协助失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@serena_bp.route('/optimize-code', methods=['POST'])
@login_required
def optimize_code_with_serena():
    """使用Serena优化代码"""
    try:
        data = request.get_json()

        if not data or 'code_content' not in data:
            return jsonify({
                'success': False,
                'error': '缺少代码内容'
            }), 400

        code_content = data['code_content']
        language = data.get('language', 'python')

        serena_service = SerenaService()

        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                serena_service.optimize_code_with_serena(code_content, language)
            )
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"代码优化失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@serena_bp.route('/generate-docs', methods=['POST'])
@login_required
def generate_documentation_with_serena():
    """使用Serena生成文档"""
    try:
        data = request.get_json()

        if not data or 'project_info' not in data:
            return jsonify({
                'success': False,
                'error': '缺少项目信息'
            }), 400

        project_info = data['project_info']

        serena_service = SerenaService()

        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                serena_service.generate_documentation_with_serena(project_info)
            )
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"文档生成失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@serena_bp.route('/chat', methods=['POST'])
@login_required
def chat_with_serena():
    """与Serena进行对话"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '缺少消息内容'
            }), 400

        message = data['message']
        conversation_history = data.get('history', [])

        # 构建上下文
        context = {
            'user_id': current_user.id,
            'username': current_user.username,
            'conversation_history': conversation_history,
            'session_id': data.get('session_id')
        }

        serena_service = SerenaService()

        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                serena_service.get_serena_assistance(message, context)
            )
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"与Serena对话失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@serena_bp.route('/capabilities', methods=['GET'])
@login_required
def get_serena_capabilities():
    """获取Serena的能力列表"""
    try:
        serena_service = SerenaService()
        capabilities = serena_service.serena_config['capabilities']

        return jsonify({
            'success': True,
            'data': {
                'capabilities': capabilities,
                'description': 'Serena是一个专业的AI助手，专门帮助开发者和技术团队'
            }
        })

    except Exception as e:
        logger.error(f"获取Serena能力列表失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

