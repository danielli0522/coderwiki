#!/usr/bin/env python3
"""
使用CoderWiki现有服务生成deepwiki-open文档
职责分离实现：仓库服务 → 文档服务 → MkDocs服务
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

def check_coderwiki_service():
    """检查CoderWiki服务是否运行"""
    try:
        response = requests.get('http://localhost:5001/system-status', timeout=5)
        if response.status_code == 200:
            print("✅ CoderWiki服务运行正常")
            return True
    except:
        print("❌ CoderWiki服务未运行，请先启动服务")
        return False

def add_repository():
    """添加deepwiki-open仓库到CoderWiki"""
    print("📁 添加deepwiki-open仓库...")
    
    repo_data = {
        "name": "deepwiki-open",
        "url": "https://github.com/AsyncFuncAI/deepwiki-open",
        "branch": "main",
        "description": "DeepWiki开源版本 - 基于AI的知识图谱和文档生成平台",
        "category": "AI/ML",
        "is_private": False
    }
    
    try:
        # 登录获取token（使用默认账户）
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.text}")
            return None
            
        # 添加仓库
        headers = {}
        if 'Set-Cookie' in login_response.headers:
            headers['Cookie'] = login_response.headers['Set-Cookie']
            
        add_response = requests.post('http://localhost:5001/api/repositories', 
                                   json=repo_data, headers=headers)
        
        if add_response.status_code == 201:
            repo_info = add_response.json()
            print(f"✅ 仓库添加成功，ID: {repo_info['id']}")
            return repo_info['id']
        else:
            print(f"❌ 添加仓库失败: {add_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 添加仓库出错: {e}")
        return None

def generate_documentation(repo_id):
    """调用文档生成服务"""
    print("📚 开始生成文档...")
    
    try:
        # 登录获取token
        login_data = {
            "username": "admin", 
            "password": "admin123"
        }
        
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        headers = {}
        if 'Set-Cookie' in login_response.headers:
            headers['Cookie'] = login_response.headers['Set-Cookie']
        
        # 调用智能文档生成
        doc_data = {
            "document_type": "comprehensive",
            "include_architecture": True,
            "include_api_docs": True,
            "include_deployment": True
        }
        
        generate_response = requests.post(
            f'http://localhost:5001/api/repositories/{repo_id}/generate',
            json=doc_data,
            headers=headers
        )
        
        if generate_response.status_code == 200:
            task_info = generate_response.json()
            task_id = task_info.get('task_id')
            print(f"✅ 文档生成任务已启动，任务ID: {task_id}")
            
            # 等待任务完成
            print("⏳ 等待文档生成完成...")
            max_wait = 300  # 5分钟
            wait_time = 0
            
            while wait_time < max_wait:
                task_status_response = requests.get(
                    f'http://localhost:5001/api/tasks/{task_id}',
                    headers=headers
                )
                
                if task_status_response.status_code == 200:
                    status_info = task_status_response.json()
                    status = status_info.get('status')
                    
                    print(f"📊 任务状态: {status}")
                    
                    if status == 'completed':
                        print("🎉 文档生成完成！")
                        return task_id
                    elif status == 'failed':
                        print("❌ 文档生成失败")
                        print(f"错误信息: {status_info.get('error_message', 'Unknown error')}")
                        return None
                        
                time.sleep(10)
                wait_time += 10
                
            print("⏰ 文档生成超时")
            return None
            
        else:
            print(f"❌ 启动文档生成失败: {generate_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 文档生成出错: {e}")
        return None

def build_mkdocs_site(repo_id):
    """构建MkDocs站点"""
    print("🏗️ 构建MkDocs站点...")
    
    try:
        # 登录获取token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        headers = {}
        if 'Set-Cookie' in login_response.headers:
            headers['Cookie'] = login_response.headers['Set-Cookie']
        
        # 调用MkDocs构建API
        build_response = requests.post(
            f'http://localhost:5001/api/repositories/{repo_id}/build-mkdocs',
            headers=headers
        )
        
        if build_response.status_code == 200:
            build_info = build_response.json()
            print("✅ MkDocs站点构建成功！")
            print(f"🌐 站点URL: {build_info.get('site_url', 'http://localhost:5001/docs')}")
            return True
        else:
            print(f"❌ MkDocs构建失败: {build_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MkDocs构建出错: {e}")
        return False

def main():
    """主函数：按职责分离执行文档生成流程"""
    print("🚀 开始DeepWiki-Open文档生成流程")
    print("=" * 60)
    
    # 1. 检查服务状态
    if not check_coderwiki_service():
        return False
    
    # 2. 仓库服务：添加仓库
    repo_id = add_repository()
    if not repo_id:
        return False
    
    # 3. 文档生成服务：调用Claude生成文档
    task_id = generate_documentation(repo_id)
    if not task_id:
        return False
    
    # 4. MkDocs服务：构建站点
    success = build_mkdocs_site(repo_id)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 文档生成流程完成！")
        print("=" * 60)
        print("\n📋 完成的任务:")
        print("  ✅ 仓库服务: 成功克隆deepwiki-open仓库")
        print("  ✅ 文档服务: 成功调用Claude生成技术文档")
        print("  ✅ MkDocs服务: 成功构建文档站点")
        
        print("\n🌐 访问方式:")
        print(f"  - 仓库详情: http://localhost:5001/repository/{repo_id}")
        print(f"  - 文档页面: http://localhost:5001/document/")
        print(f"  - 任务状态: http://localhost:5001/task/{task_id}")
        
        print("\n💡 技术特点:")
        print("  🏗️ 职责分离的微服务架构")
        print("  🤖 基于Claude的智能文档生成")
        print("  📚 自动化MkDocs站点构建")
        print("  🔄 完整的任务跟踪和状态监控")
        
        return True
    else:
        print("\n❌ 文档生成流程失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)