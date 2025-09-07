#!/usr/bin/env python3
"""
调试登录功能的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import DevelopmentConfig
from app.services.auth_service import AuthService
from app.models.user import User

def test_login():
    """测试登录功能"""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        print("🔍 检查数据库中的用户...")

        # 检查用户是否存在
        users = User.query.all()
        print(f"数据库中共有 {len(users)} 个用户:")

        for user in users:
            print(f"  - {user.username} ({user.email}) - 管理员: {user.is_admin}")

        if not users:
            print("❌ 数据库中没有用户")
            return

        # 测试登录
        print("\n🔐 测试登录功能...")
        auth_service = AuthService()

        try:
            # 测试管理员登录
            print("测试管理员登录...")
            user = auth_service.login_user('admin', 'admin123')
            print(f"✅ 登录成功: {user.username}")

        except ValueError as e:
            print(f"❌ 登录失败 (ValueError): {e}")
        except Exception as e:
            print(f"❌ 登录失败 (Exception): {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_login()





