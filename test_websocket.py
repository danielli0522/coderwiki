#!/usr/bin/env python3
"""
专门测试WebSocket端点的脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_websocket_endpoints():
    """测试WebSocket相关端点"""
    print("🔍 Testing WebSocket endpoints...")

    endpoints = [
        "/api/ws",
        "/api/ws/",
        "/api/ws/status",
        "/socket.io/",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"  {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                print(f"    Response: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"    Not found")
            else:
                print(f"    Response: {response.text[:100]}...")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")

    print("\n" + "="*50)
    print("WebSocket endpoint test completed")

if __name__ == "__main__":
    test_websocket_endpoints()
