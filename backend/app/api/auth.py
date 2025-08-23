"""
Authentication API endpoints.
"""

import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app.services.auth_service import AuthService

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'GET':
        # 如果用户已登录，重定向到仪表板
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        # 否则渲染注册页面
        return render_template('auth/register.html')

    # POST 请求处理注册逻辑
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400

        auth_service = AuthService()
        user = auth_service.register_user(username, email, password)

        # Log in the user after registration
        login_user(user)

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': '注册成功'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"注册失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login a user."""
    if request.method == 'GET':
        # 如果用户已登录，重定向到仪表板
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        # 否则渲染登录页面
        return render_template('auth/login.html')

    # POST 请求处理登录逻辑
    try:
        logger.info("开始处理登录请求")
        data = request.get_json()
        logger.debug(f"接收到的数据: {data}")

        if not data:
            logger.warning("请求数据为空")
            return jsonify({'error': '请求数据为空'}), 400

        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)

        logger.debug(f"用户名: {username}, 记住我: {remember}")

        if not username or not password:
            logger.warning("用户名或密码为空")
            return jsonify({'error': '用户名和密码不能为空'}), 400

        logger.info("调用认证服务")
        auth_service = AuthService()
        user = auth_service.login_user(username, password, remember)
        logger.info(f"认证服务返回用户: {user.username}")

        # 在API层调用Flask-Login的login_user
        logger.info("调用Flask-Login的login_user")
        login_user(user, remember=remember)
        logger.info("Flask-Login登录成功")

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': '登录成功'
        })

    except ValueError as e:
        logger.warning(f"登录验证失败: {str(e)}")
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout the current user."""
    try:
        auth_service = AuthService()
        auth_service.logout_user()

        return jsonify({
            'success': True,
            'message': '退出成功'
        })

    except Exception as e:
        logger.error(f"退出失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/status', methods=['GET'])
def status():
    """Get current authentication status."""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'logged_in': True,
                'user': current_user.to_dict()
            })
        else:
            return jsonify({
                'logged_in': False,
                'user': None
            })

    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile."""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })

    except Exception as e:
        logger.error(f"获取个人资料失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user profile."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        auth_service = AuthService()
        user = auth_service.update_user_profile(current_user.id, **data)

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': '个人资料更新成功'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新个人资料失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change current user password."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({'error': '当前密码和新密码不能为空'}), 400

        auth_service = AuthService()
        auth_service.change_password(current_user.id, old_password, new_password)

        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500
