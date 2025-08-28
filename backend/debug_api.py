#!/usr/bin/env python3
"""
调试API请求的脚本
"""

import sys
import os
import json
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_login():
    """测试API登录"""
    url = "http://localhost:5001/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        print("🔍 测试API登录...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, ensure_ascii=False)}")

        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 登录成功: {result}")
        else:
            print(f"❌ 登录失败: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到服务器")
    except Exception as e:
        print(f"❌ 请求错误: {e}")

def test_api_status():
    """测试API状态"""
    url = "http://localhost:5001/api/auth/status"

    try:
        print("🔍 测试API状态...")
        response = requests.get(url)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ 请求错误: {e}")

if __name__ == '__main__':
    test_api_status()
    print("\n" + "="*50 + "\n")
    test_api_login()



