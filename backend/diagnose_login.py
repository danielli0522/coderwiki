#!/usr/bin/env python3
"""
登录问题诊断脚本
"""
import requests
import json
import sys
from datetime import datetime

def check_server_status():
    """检查服务器状态"""
    print("🔍 检查服务器状态...")

    try:
        response = requests.get("http://localhost:5001/", timeout=5)
        print(f"✅ 服务器运行正常 (状态码: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 (localhost:5001)")
        print("   请确保Flask应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False

def check_login_page():
    """检查登录页面"""
    print("\n🔍 检查登录页面...")

    try:
        response = requests.get("http://localhost:5001/login", timeout=5)
        if response.status_code == 200:
            print("✅ 登录页面可以访问")
            return True
        else:
            print(f"❌ 登录页面返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问登录页面失败: {str(e)}")
        return False

def test_login_api():
    """测试登录API"""
    print("\n🔍 测试登录API...")

    test_users = [
        {"username": "admin", "password": "admin123", "name": "管理员"},
        {"username": "demo", "password": "demo123", "name": "演示用户"},
        {"username": "testuser", "password": "TestPassword123!", "name": "测试用户"}
    ]

    success_count = 0

    for user in test_users:
        print(f"\n   测试 {user['name']} 登录...")
        try:
            response = requests.post(
                "http://localhost:5001/api/auth/login",
                json={
                    "username": user["username"],
                    "password": user["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ {user['name']} 登录成功")
                    success_count += 1
                else:
                    print(f"   ❌ {user['name']} 登录失败: {data.get('error', '未知错误')}")
            else:
                print(f"   ❌ {user['name']} HTTP错误: {response.status_code}")

        except Exception as e:
            print(f"   ❌ {user['name']} 请求失败: {str(e)}")

    return success_count > 0

def check_database_connection():
    """检查数据库连接"""
    print("\n🔍 检查数据库连接...")

    try:
        from app import create_app, db
        from app.models.user import User

        app = create_app()
        with app.app_context():
            user_count = User.query.count()
            print(f"✅ 数据库连接正常，用户总数: {user_count}")

            # 显示用户列表
            users = User.query.all()
            print("   用户列表:")
            for user in users:
                print(f"   - {user.username} ({user.email}) - 激活: {user.is_active}")

            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def check_configuration():
    """检查配置"""
    print("\n🔍 检查配置...")

    try:
        from config import Config

        print(f"✅ 配置加载成功")
        print(f"   数据库URI: {Config.SQLALCHEMY_DATABASE_URI}")
        print(f"   模板文件夹: {Config.TEMPLATE_FOLDER}")
        print(f"   静态文件夹: {Config.STATIC_FOLDER}")
        print(f"   会话超时: {Config.PERMANENT_SESSION_LIFETIME}秒")

        return True
    except Exception as e:
        print(f"❌ 配置检查失败: {str(e)}")
        return False

def generate_report():
    """生成诊断报告"""
    print("=" * 60)
    print("🔧 CoderWiki 登录问题诊断报告")
    print("=" * 60)
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 执行各项检查
    server_ok = check_server_status()
    login_page_ok = check_login_page() if server_ok else False
    api_ok = test_login_api() if server_ok else False
    db_ok = check_database_connection()
    config_ok = check_configuration()

    # 总结
    print("\n" + "=" * 60)
    print("📋 诊断总结")
    print("=" * 60)

    if all([server_ok, login_page_ok, api_ok, db_ok, config_ok]):
        print("✅ 所有检查都通过！登录功能应该正常工作。")
        print("\n💡 如果仍然无法登录，请尝试以下步骤:")
        print("   1. 清除浏览器缓存和cookie")
        print("   2. 使用不同的浏览器测试")
        print("   3. 检查浏览器控制台是否有JavaScript错误")
        print("   4. 确保使用正确的用户名和密码")
    else:
        print("❌ 发现问题:")
        if not server_ok:
            print("   - 服务器未运行或无法访问")
        if not login_page_ok:
            print("   - 登录页面无法访问")
        if not api_ok:
            print("   - 登录API有问题")
        if not db_ok:
            print("   - 数据库连接有问题")
        if not config_ok:
            print("   - 配置有问题")

        print("\n🔧 建议的解决方案:")
        if not server_ok:
            print("   1. 启动Flask应用: python run.py")
        if not db_ok:
            print("   2. 检查数据库连接和用户表")
        if not api_ok:
            print("   3. 检查认证服务和用户密码")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    generate_report()
