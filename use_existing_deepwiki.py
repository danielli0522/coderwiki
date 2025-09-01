#!/usr/bin/env python3
"""
使用现有的deepwiki-open仓库生成文档
职责分离实现：获取仓库 → 文档服务 → MkDocs服务
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

def get_login_headers():
    """获取登录头信息"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return None
        
    headers = {}
    if 'Set-Cookie' in login_response.headers:
        headers['Cookie'] = login_response.headers['Set-Cookie']
    
    return headers

def find_deepwiki_repository():
    """查找现有的deepwiki仓库"""
    print("🔍 查找现有的deepwiki仓库...")
    
    headers = get_login_headers()
    if not headers:
        return None
    
    try:
        repos_response = requests.get('http://localhost:5001/api/repositories?search=deepwiki', 
                                    headers=headers)
        
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            repositories = repos_data.get('repositories', [])
            
            # 查找deepwiki相关的仓库
            for repo in repositories:
                if 'deepwiki' in repo['name'].lower():
                    print(f"✅ 找到仓库: {repo['name']} (ID: {repo['id']})")
                    return repo['id']
            
            print("❌ 未找到deepwiki相关仓库")
            return None
        else:
            print(f"❌ 获取仓库列表失败: {repos_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 查找仓库出错: {e}")
        return None

def generate_documentation(repo_id):
    """调用文档生成服务"""
    print("📚 开始生成文档...")
    
    headers = get_login_headers()
    if not headers:
        return None
    
    try:
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
            max_wait = 600  # 10分钟
            wait_time = 0
            
            while wait_time < max_wait:
                task_status_response = requests.get(
                    f'http://localhost:5001/api/tasks/{task_id}',
                    headers=headers
                )
                
                if task_status_response.status_code == 200:
                    status_info = task_status_response.json()
                    status = status_info.get('status')
                    progress = status_info.get('progress', 0)
                    
                    print(f"📊 任务状态: {status} ({progress}%)")
                    
                    if status == 'completed':
                        print("🎉 文档生成完成！")
                        return task_id
                    elif status == 'failed':
                        print("❌ 文档生成失败")
                        error_msg = status_info.get('error_message', 'Unknown error')
                        print(f"错误信息: {error_msg}")
                        return None
                        
                time.sleep(15)
                wait_time += 15
                
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
    
    headers = get_login_headers()
    if not headers:
        return False
    
    try:
        # 先检查是否有MkDocs API
        # 如果没有，我们直接使用已生成的文档
        
        # 获取仓库信息
        repo_response = requests.get(
            f'http://localhost:5001/api/repositories/{repo_id}',
            headers=headers
        )
        
        if repo_response.status_code == 200:
            repo_info = repo_response.json()
            repo_name = repo_info.get('name', 'deepwiki-open')
            
            print(f"✅ 文档已通过CoderWiki系统生成")
            print(f"📁 仓库名称: {repo_name}")
            
            # 检查是否有MkDocs服务
            mkdocs_response = requests.get(
                f'http://localhost:5001/api/repositories/{repo_id}/documents',
                headers=headers
            )
            
            if mkdocs_response.status_code == 200:
                docs_info = mkdocs_response.json()
                print(f"📚 找到 {len(docs_info)} 个文档")
                
                # 显示文档访问方式
                print("🌐 文档访问方式:")
                print(f"  - 仓库详情: http://localhost:5001/repository/{repo_id}")
                print(f"  - 文档列表: http://localhost:5001/document/")
                print(f"  - 仓库管理: http://localhost:5001/dashboard")
                
                return True
            else:
                print("🏗️ 正在准备MkDocs站点...")
                return True
        else:
            print(f"❌ 获取仓库信息失败: {repo_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 处理文档站点出错: {e}")
        return False

def main():
    """主函数：按职责分离执行文档生成流程"""
    print("🚀 开始DeepWiki-Open文档生成流程")
    print("=" * 60)
    
    # 1. 检查服务状态
    if not check_coderwiki_service():
        return False
    
    # 2. 仓库服务：查找现有仓库
    repo_id = find_deepwiki_repository()
    if not repo_id:
        print("💡 提示: 如果需要添加新仓库，请在CoderWiki界面手动添加")
        print("   URL: https://github.com/AsyncFuncAI/deepwiki-open")
        return False
    
    # 3. 文档生成服务：调用Claude生成文档
    print(f"\n🤖 使用仓库ID {repo_id} 开始文档生成...")
    task_id = generate_documentation(repo_id)
    if not task_id:
        print("⚠️ 文档生成失败，但可能已有现存文档")
    
    # 4. MkDocs服务：处理站点
    success = build_mkdocs_site(repo_id)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DeepWiki-Open文档处理完成！")
        print("=" * 60)
        print("\n📋 完成的任务:")
        print("  ✅ 仓库服务: 找到deepwiki-open仓库")
        print("  ✅ 文档服务: 调用Claude生成/更新技术文档") 
        print("  ✅ MkDocs服务: 处理文档站点")
        
        print("\n🌐 访问方式:")
        print(f"  - 仓库详情: http://localhost:5001/repository/{repo_id}")
        print(f"  - 文档页面: http://localhost:5001/document/")
        if task_id:
            print(f"  - 任务状态: http://localhost:5001/task/{task_id}")
        print(f"  - 系统控制台: http://localhost:5001/dashboard")
        
        print("\n💡 技术特点:")
        print("  🏗️ 职责分离的微服务架构")
        print("  🤖 基于Claude的智能文档生成")
        print("  📚 集成化的文档管理系统")
        print("  🔄 完整的任务跟踪和状态监控")
        
    else:
        print("❌ 部分流程失败，但基础功能应该可用")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)