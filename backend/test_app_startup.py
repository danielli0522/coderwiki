#!/usr/bin/env python3
"""
测试应用启动和API端点
"""

import requests
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """测试应用启动"""
    print("🔍 测试应用启动...")

    try:
        from app import create_app
        from config import Config

        print("✅ 成功导入应用模块")

        app = create_app(Config)
        print("✅ 成功创建Flask应用")

        with app.test_client() as client:
            # 测试健康检查端点
            response = client.get('/api/system/health')
            print(f"健康检查: {response.status_code}")

            # 测试WebSocket端点
            response = client.get('/api/ws/')
            print(f"WebSocket端点: {response.status_code}")

            # 测试浏览器兼容性端点
            response = client.post('/api/system/browser-compatibility',
                                 json={'browser': {'name': 'chrome', 'version': 100}})
            print(f"浏览器兼容性端点: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ 应用启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🔍 测试API端点...")

    base_url = "http://localhost:5001"
    endpoints = [
        "/api/system/health",
        "/api/ws/",
        "/api/ws/status",
        "/api/auth/status"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"  {endpoint}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  {endpoint}: 连接失败 (应用可能未启动)")
        except Exception as e:
            print(f"  {endpoint}: 错误 - {e}")

def main():
    """主函数"""
    print("CoderWiki 应用测试")
    print("=" * 50)

    # 测试应用启动
    if test_app_startup():
        print("\n✅ 应用启动测试通过")

        # 等待应用启动
        print("\n⏳ 等待应用启动...")
        time.sleep(3)

        # 测试API端点
        test_api_endpoints()
    else:
        print("\n❌ 应用启动测试失败")

if __name__ == "__main__":
    main()
