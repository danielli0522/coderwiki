#!/usr/bin/env python3
"""
创建新用户脚本
"""
from app import create_app, db
from app.models.user import User

def create_user(username, email, password, is_admin=False):
    """创建新用户"""
    app = create_app()

    with app.app_context():
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            print(f"❌ 用户名 {username} 已存在")
            return False

        if User.query.filter_by(email=email).first():
            print(f"❌ 邮箱 {email} 已存在")
            return False

        # 创建新用户
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ 用户 {username} 创建成功")
            print(f"   用户名: {username}")
            print(f"   邮箱: {email}")
            print(f"   管理员: {'是' if is_admin else '否'}")
            return True
        except Exception as e:
            print(f"❌ 创建用户失败: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🔧 CoderWiki 用户创建工具")
    print("=" * 40)

    # 示例：创建新用户
    print("创建示例用户...")

    # 创建普通用户
    create_user("newuser", "newuser@example.com", "NewPassword123!")

    # 创建管理员用户
    create_user("newadmin", "newadmin@example.com", "AdminPassword123!", is_admin=True)

    print("\n完成！")
