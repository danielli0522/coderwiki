#!/usr/bin/env python3
"""
测试登录功能
"""
import requests
import json

def test_login():
    """测试登录功能"""
    base_url = "http://localhost:5001"

    # 测试数据
    test_cases = [
        {
            "username": "admin",
            "password": "admin123",
            "description": "管理员登录"
        },
        {
            "username": "demo",
            "password": "demo123",
            "description": "演示用户登录"
        },
        {
            "username": "testuser",
            "password": "TestPassword123!",
            "description": "测试用户登录"
        }
    ]

    print("开始测试登录功能...")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"用户名: {test_case['username']}")

        try:
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={
                    "username": test_case["username"],
                    "password": test_case["password"]
                },
                headers={"Content-Type": "application/json"}
            )

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ 登录成功")
                    print(f"用户信息: {data['user']['username']} ({data['user']['email']})")
                else:
                    print("❌ 登录失败")
                    print(f"错误信息: {data.get('error', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")

        except requests.exceptions.ConnectionError:
            print("❌ 连接错误: 无法连接到服务器")
        except Exception as e:
            print(f"❌ 其他错误: {str(e)}")

    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_login()
