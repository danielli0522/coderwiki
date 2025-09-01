#!/usr/bin/env python3
"""
生成 deepwiki-open 项目文档
使用 Claude 交互模式分析项目并生成 MkDocs 站点
"""

import os
import sys
import json
import time
import yaml
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

from claude_interactive_client import ClaudeInteractiveClient

def main():
    """主函数：生成 deepwiki-open 项目文档"""
    print("🚀 开始生成 deepwiki-open 项目文档")
    print("=" * 60)
    
    # 设置项目路径
    project_path = "backend/repos/deepwiki-open"
    
    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在: {project_path}")
        return False
    
    print(f"📁 项目路径: {project_path}")
    
    # 初始化 Claude 客户端
    client = ClaudeInteractiveClient(workspace_path=os.getcwd())
    
    print("🤖 开始使用 Claude 交互模式分析项目...")
    
    # 生成项目分析
    analysis_result = client.generate_project_analysis(project_path)
    
    if not analysis_result['success']:
        print(f"❌ 项目分析失败: {analysis_result['error']}")
        return False
    
    print("✅ 项目分析成功！")
    
    # 保存分析结果
    docs_dir = "backend/coderwiki-output-docs/deepwiki-open"
    os.makedirs(docs_dir, exist_ok=True)
    
    analysis_file = os.path.join(docs_dir, "project_analysis.md")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write(analysis_result['analysis'])
    
    print(f"📄 项目分析报告已保存: {analysis_file}")
    
    # 生成更详细的技术文档
    print("\n📚 生成详细技术文档...")
    
    detailed_questions = [
        f"请详细分析 {project_path} 项目的架构设计，包括主要模块和组件",
        f"分析 {project_path} 项目的API设计和数据流",
        f"总结 {project_path} 项目的安装和使用方法",
        f"为 {project_path} 项目生成完整的技术文档大纲"
    ]
    
    detailed_docs = []
    
    for i, question in enumerate(detailed_questions, 1):
        print(f"📝 生成详细文档 {i}/{len(detailed_questions)}...")
        
        response = client.send_interactive_message(question, timeout=60)
        
        if response['success']:
            detailed_docs.append({
                'section': f"section_{i}",
                'question': question,
                'content': response['response']
            })
            print(f"✅ 第 {i} 部分完成")
        else:
            print(f"❌ 第 {i} 部分失败: {response['error']}")
    
    # 生成完整的技术文档
    if detailed_docs:
        print("\n📖 合成完整技术文档...")
        
        full_doc_parts = []
        full_doc_parts.append("# DeepWiki-Open 项目技术文档")
        full_doc_parts.append(f"\n> 基于 Claude 交互模式自动生成")
        full_doc_parts.append(f"\n> 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 添加项目概述
        full_doc_parts.append("\n## 项目概述")
        if analysis_result.get('step_results', {}).get('project_type', {}).get('success'):
            full_doc_parts.append(f"\n{analysis_result['step_results']['project_type']['answer']}")
        
        # 添加技术栈
        full_doc_parts.append("\n## 技术栈")
        if analysis_result.get('step_results', {}).get('tech_stack', {}).get('success'):
            full_doc_parts.append(f"\n{analysis_result['step_results']['tech_stack']['answer']}")
        
        # 添加核心功能
        full_doc_parts.append("\n## 核心功能")
        if analysis_result.get('step_results', {}).get('main_function', {}).get('success'):
            full_doc_parts.append(f"\n{analysis_result['step_results']['main_function']['answer']}")
        
        # 添加详细分析
        for i, doc in enumerate(detailed_docs, 1):
            full_doc_parts.append(f"\n## 详细分析 {i}")
            full_doc_parts.append(f"\n**分析问题**: {doc['question']}")
            full_doc_parts.append(f"\n{doc['content']}")
            full_doc_parts.append("\n---")
        
        full_doc_content = "\n".join(full_doc_parts)
        
        # 保存完整文档
        full_doc_file = os.path.join(docs_dir, "README.md")
        with open(full_doc_file, 'w', encoding='utf-8') as f:
            f.write(full_doc_content)
        
        print(f"📚 完整技术文档已保存: {full_doc_file}")
        
        # 创建 MkDocs 配置
        print("\n🏗️ 创建 MkDocs 配置...")
        
        mkdocs_config = {
            'site_name': 'DeepWiki-Open 技术文档',
            'site_description': 'DeepWiki-Open 项目的完整技术文档',
            'theme': {
                'name': 'material',
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'toc.follow',
                    'search.suggest',
                    'search.highlight'
                ]
            },
            'nav': [
                {'首页': 'README.md'},
                {'项目分析': 'project_analysis.md'}
            ]
        }
        
        # 保存 MkDocs 配置
        mkdocs_config_file = os.path.join(docs_dir, "mkdocs.yml")
        with open(mkdocs_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(mkdocs_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"⚙️ MkDocs 配置已保存: {mkdocs_config_file}")
        
        # 构建 MkDocs 站点
        print("\n🔨 构建 MkDocs 站点...")
        
        import subprocess
        
        try:
            # 构建命令
            build_result = subprocess.run(
                ['mkdocs', 'build', '--clean'],
                cwd=docs_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if build_result.returncode == 0:
                print("✅ MkDocs 站点构建成功！")
                
                site_dir = os.path.join(docs_dir, "site")
                print(f"🌐 站点文件位置: {site_dir}")
                
                # 启动本地服务器
                print("\n🚀 启动 MkDocs 本地服务器...")
                
                serve_cmd = ['mkdocs', 'serve', '--dev-addr', '0.0.0.0:8080']
                print(f"🌍 MkDocs 服务器将在 http://localhost:8080 启动")
                print("📋 使用以下命令手动启动:")
                print(f"   cd {docs_dir}")
                print(f"   mkdocs serve")
                
                return True
                
            else:
                print("❌ MkDocs 构建失败")
                print(f"错误输出: {build_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ MkDocs 构建超时")
            return False
        except FileNotFoundError:
            print("❌ MkDocs 命令未找到，请先安装 MkDocs:")
            print("   pip install mkdocs mkdocs-material")
            return False
    
    else:
        print("❌ 没有生成详细文档内容")
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 60)
    print("📋 生成总结")
    print("=" * 60)
    
    if success:
        print("🎉 deepwiki-open 项目文档生成完成！")
        print("\n📁 生成的文件:")
        print("  - backend/coderwiki-output-docs/deepwiki-open/README.md")
        print("  - backend/coderwiki-output-docs/deepwiki-open/project_analysis.md") 
        print("  - backend/coderwiki-output-docs/deepwiki-open/mkdocs.yml")
        print("  - backend/coderwiki-output-docs/deepwiki-open/site/ (MkDocs站点)")
        
        print("\n🌐 访问方式:")
        print("  1. 直接查看 Markdown 文件")
        print("  2. 启动 MkDocs 服务器:")
        print("     cd backend/coderwiki-output-docs/deepwiki-open")
        print("     mkdocs serve")
        print("     然后访问 http://localhost:8000")
        
        print("\n💡 特色:")
        print("  ✅ 使用 Claude 交互模式，绕过 API 配额限制")
        print("  ✅ 完整的项目分析和技术文档")
        print("  ✅ 自动生成 MkDocs 站点")
        print("  ✅ 职责分离的服务架构")
        
    else:
        print("❌ 文档生成过程中出现错误")
        print("💡 请检查:")
        print("  1. Claude CLI 是否正确安装")
        print("  2. 项目路径是否存在")
        print("  3. MkDocs 是否正确安装")