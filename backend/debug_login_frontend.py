#!/usr/bin/env python3
"""
前端登录调试工具
"""
import requests
import json
from datetime import datetime

def test_login_with_headers():
    """测试带完整请求头的登录"""
    print("🔍 测试带完整请求头的登录...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5001',
        'Referer': 'http://localhost:5001/login',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    test_cases = [
        {"username": "demo", "password": "demo123", "name": "演示用户"},
        {"username": "admin", "password": "admin123", "name": "管理员"}
    ]
    
    for test_case in test_cases:
        print(f"\n   测试 {test_case['name']} 登录...")
        try:
            response = requests.post(
                "http://localhost:5001/api/auth/login",
                json={
                    "username": test_case["username"],
                    "password": test_case["password"]
                },
                headers=headers,
                timeout=10
            )
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ {test_case['name']} 登录成功")
                    print(f"   用户信息: {data['user']['username']} ({data['user']['email']})")
                    print(f"   会话Cookie: {response.cookies.get('session', '无')}")
                else:
                    print(f"   ❌ {test_case['name']} 登录失败: {data.get('error', '未知错误')}")
            else:
                print(f"   ❌ {test_case['name']} HTTP错误: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except Exception as e:
            print(f"   ❌ {test_case['name']} 请求失败: {str(e)}")

def test_session_management():
    """测试会话管理"""
    print("\n🔍 测试会话管理...")
    
    try:
        # 先登录
        login_response = requests.post(
            "http://localhost:5001/api/auth/login",
            json={"username": "demo", "password": "demo123"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            print("   ✅ 登录成功")
            session_cookie = login_response.cookies.get('session')
            print(f"   会话Cookie: {session_cookie}")
            
            # 使用会话Cookie访问需要认证的页面
            if session_cookie:
                cookies = {'session': session_cookie}
                dashboard_response = requests.get(
                    "http://localhost:5001/dashboard",
                    cookies=cookies
                )
                
                print(f"   仪表板访问状态码: {dashboard_response.status_code}")
                if dashboard_response.status_code == 200:
                    print("   ✅ 会话管理正常")
                else:
                    print("   ❌ 会话管理有问题")
            else:
                print("   ❌ 没有获取到会话Cookie")
        else:
            print("   ❌ 登录失败，无法测试会话管理")
            
    except Exception as e:
        print(f"   ❌ 会话管理测试失败: {str(e)}")

def test_cors_and_preflight():
    """测试CORS和预检请求"""
    print("\n🔍 测试CORS和预检请求...")
    
    try:
        # 测试OPTIONS预检请求
        preflight_response = requests.options(
            "http://localhost:5001/api/auth/login",
            headers={
                'Origin': 'http://localhost:5001',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        
        print(f"   预检请求状态码: {preflight_response.status_code}")
        print(f"   CORS头: {dict(preflight_response.headers)}")
        
        if preflight_response.status_code in [200, 204]:
            print("   ✅ CORS配置正常")
        else:
            print("   ❌ CORS配置可能有问题")
            
    except Exception as e:
        print(f"   ❌ CORS测试失败: {str(e)}")

def generate_debug_report():
    """生成调试报告"""
    print("=" * 60)
    print("🔧 CoderWiki 前端登录调试报告")
    print("=" * 60)
    print(f"调试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行各项测试
    test_login_with_headers()
    test_session_management()
    test_cors_and_preflight()
    
    print("\n" + "=" * 60)
    print("📋 调试建议")
    print("=" * 60)
    print("如果后端API正常但前端无法登录，请检查:")
    print("1. 浏览器控制台是否有JavaScript错误")
    print("2. 网络请求是否被阻止")
    print("3. 浏览器是否启用了JavaScript")
    print("4. 是否有浏览器扩展干扰")
    print("5. 尝试使用无痕模式")
    print("\n💡 快速测试方法:")
    print("1. 访问: http://localhost:5001/test-login")
    print("2. 使用curl测试: curl -X POST http://localhost:5001/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"demo\",\"password\":\"demo123\"}'")
    print("=" * 60)

if __name__ == "__main__":
    generate_debug_report()
