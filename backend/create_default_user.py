#!/usr/bin/env python3
"""
创建默认用户账户
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.user import User
from config import DevelopmentConfig
from werkzeug.security import generate_password_hash

def create_default_users():
    """创建默认用户账户"""
    app, socketio = create_app(DevelopmentConfig)

    with app.app_context():
        # 检查是否已存在用户
        existing_users = User.query.all()
        if existing_users:
            print("⚠️  数据库中已存在用户，跳过默认用户创建")
            print("现有用户:")
            for user in existing_users:
                print(f"  - {user.username} ({user.email})")
            return

        print("🔧 创建默认用户账户...")

        # 创建管理员用户
        admin_user = User(
            username='admin',
            email='admin@coderwiki.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True
        )

        # 创建演示用户
        demo_user = User(
            username='demo',
            email='demo@coderwiki.com',
            password_hash=generate_password_hash('demo123'),
            is_admin=False,
            is_active=True
        )

        # 创建测试用户
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testuser123'),
            is_admin=False,
            is_active=True
        )

        try:
            # 添加到数据库
            db.session.add(admin_user)
            db.session.add(demo_user)
            db.session.add(test_user)
            db.session.commit()

            print("✅ 默认用户创建成功！")
            print("\n📋 默认账户信息:")
            print("=" * 50)
            print("🔐 管理员账户:")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   邮箱: admin@coderwiki.com")
            print("   权限: 管理员")
            print()
            print("👤 演示账户:")
            print("   用户名: demo")
            print("   密码: demo123")
            print("   邮箱: demo@coderwiki.com")
            print("   权限: 普通用户")
            print()
            print("🧪 测试账户:")
            print("   用户名: testuser")
            print("   密码: testuser123")
            print("   邮箱: test@example.com")
            print("   权限: 普通用户")
            print("=" * 50)
            print("\n💡 提示:")
            print("   - 建议首次登录后修改默认密码")
            print("   - 管理员账户可以访问所有功能")
            print("   - 演示账户适合体验基本功能")

        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建用户失败: {str(e)}")
            return False

        return True

if __name__ == '__main__':
    create_default_users()

