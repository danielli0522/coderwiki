#!/usr/bin/env python3
"""
用户管理脚本
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

def list_users():
    """列出所有用户"""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        users = User.query.all()

        if not users:
            print("📭 数据库中没有用户")
            return

        print(f"📋 用户列表 (共 {len(users)} 个用户):")
        print("=" * 80)
        print(f"{'ID':<4} {'用户名':<15} {'邮箱':<25} {'管理员':<8} {'状态':<8} {'创建时间':<20}")
        print("-" * 80)

        for user in users:
            admin_status = "是" if user.is_admin else "否"
            active_status = "激活" if user.is_active else "禁用"
            created_time = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "未知"

            print(f"{user.id:<4} {user.username:<15} {user.email:<25} {admin_status:<8} {active_status:<8} {created_time:<20}")

def create_user(username, email, password, is_admin=False):
    """创建新用户"""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            print(f"❌ 用户名 '{username}' 已存在")
            return False

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            print(f"❌ 邮箱 '{email}' 已存在")
            return False

        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin,
            is_active=True
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"✅ 用户 '{username}' 创建成功")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建用户失败: {str(e)}")
            return False

def reset_password(username, new_password):
    """重置用户密码"""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if not user:
            print(f"❌ 用户 '{username}' 不存在")
            return False

        try:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"✅ 用户 '{username}' 密码重置成功")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ 密码重置失败: {str(e)}")
            return False

def delete_user(username):
    """删除用户"""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if not user:
            print(f"❌ 用户 '{username}' 不存在")
            return False

        try:
            db.session.delete(user)
            db.session.commit()
            print(f"✅ 用户 '{username}' 删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ 删除用户失败: {str(e)}")
            return False

def show_help():
    """显示帮助信息"""
    print("🔧 CoderWiki 用户管理工具")
    print("=" * 50)
    print("用法:")
    print("  python manage_users.py list                    # 列出所有用户")
    print("  python manage_users.py create <用户名> <邮箱> <密码> [--admin]  # 创建用户")
    print("  python manage_users.py reset <用户名> <新密码>  # 重置密码")
    print("  python manage_users.py delete <用户名>          # 删除用户")
    print("  python manage_users.py help                    # 显示帮助")
    print()
    print("示例:")
    print("  python manage_users.py list")
    print("  python manage_users.py create john john@example.com password123")
    print("  python manage_users.py create admin admin@example.com admin123 --admin")
    print("  python manage_users.py reset john newpassword123")
    print("  python manage_users.py delete john")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        list_users()
    elif command == "create":
        if len(sys.argv) < 5:
            print("❌ 创建用户需要提供用户名、邮箱和密码")
            print("用法: python manage_users.py create <用户名> <邮箱> <密码> [--admin]")
            return

        username = sys.argv[2]
        email = sys.argv[3]
        password = sys.argv[4]
        is_admin = "--admin" in sys.argv

        create_user(username, email, password, is_admin)
    elif command == "reset":
        if len(sys.argv) < 4:
            print("❌ 重置密码需要提供用户名和新密码")
            print("用法: python manage_users.py reset <用户名> <新密码>")
            return

        username = sys.argv[2]
        new_password = sys.argv[3]

        reset_password(username, new_password)
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ 删除用户需要提供用户名")
            print("用法: python manage_users.py delete <用户名>")
            return

        username = sys.argv[2]

        # 确认删除
        confirm = input(f"⚠️  确定要删除用户 '{username}' 吗？(y/N): ")
        if confirm.lower() in ['y', 'yes']:
            delete_user(username)
        else:
            print("❌ 操作已取消")
    elif command == "help":
        show_help()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == '__main__':
    main()

