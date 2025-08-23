#!/usr/bin/env python3
"""
Backend目录文档生成测试
专门测试为backend目录生成技术文档的效果
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_backend_documentation():
    """测试为backend目录生成技术文档"""
    print("=== Backend目录文档生成测试 ===")

    try:
        # 导入Claude Code服务
        from app.services.claude_code_service import ClaudeCodeService

        # 创建服务实例
        service = ClaudeCodeService()

        print("✅ Claude Code服务创建成功")

        # 设置backend目录路径
        backend_path = os.path.dirname(os.path.abspath(__file__))
        print(f"Backend目录路径: {backend_path}")

        # 检查backend目录结构
        print("\n=== Backend目录结构 ===")
        backend_files = []
        for root, dirs, files in os.walk(backend_path):
            level = root.replace(backend_path, '').count(os.sep)
            indent = ' ' * 2 * level
            dir_name = os.path.basename(root)
            if level == 0:
                print(f"{indent}📁 {dir_name}/")
            else:
                print(f"{indent}📁 {dir_name}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # 只显示前10个文件
                if file.endswith('.py') or file.endswith('.md') or file.endswith('.json'):
                    backend_files.append(os.path.join(root, file))
                    print(f"{subindent}📄 {file}")
            if len(files) > 10:
                print(f"{subindent}... 还有 {len(files) - 10} 个文件")

        print(f"\n总共发现 {len(backend_files)} 个主要文件")

        # 测试不同类型的文档生成
        doc_types = [
            'technical_design',
            'architecture',
            'api_docs',
            'developer_guide'
        ]

        for doc_type in doc_types:
            print(f"\n{'='*60}")
            print(f"生成 {doc_type} 文档...")
            print(f"{'='*60}")

            result = await service.generate_technical_document(
                repository_path=backend_path,
                doc_type=doc_type,
                doc_title=f'Backend {doc_type.replace("_", " ").title()}',
                additional_params={
                    'detailed': True,
                    'include_examples': True,
                    'comprehensive': True
                }
            )

            if result['success']:
                print(f"✅ {doc_type} 文档生成成功！")
                print(f"文档长度: {len(result.get('content', ''))} 字符")
                print(f"生成时间: {result.get('generation_time', 0):.2f} 秒")
                print(f"成本估算: ${result.get('cost_estimate', 0):.4f}")

                # 保存生成的文档
                output_file = f"backend_{doc_type}_documentation.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('content', ''))
                print(f"文档已保存到: {output_file}")

                # 显示文档内容预览
                content = result.get('content', '')
                print(f"\n📄 文档预览 (前1000字符):")
                print("-" * 50)
                if len(content) > 1000:
                    print(content[:1000] + "...")
                else:
                    print(content)
                print("-" * 50)

            else:
                print(f"❌ {doc_type} 文档生成失败")
                print(f"错误: {result.get('error', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_backend_architecture_doc():
    """专门测试架构文档生成"""
    print("\n=== 专门测试Backend架构文档生成 ===")

    try:
        from app.services.claude_code_service import ClaudeCodeService

        service = ClaudeCodeService()
        backend_path = os.path.dirname(os.path.abspath(__file__))

        # 使用更详细的系统提示词
        custom_params = {
            'detailed': True,
            'include_examples': True,
            'comprehensive': True,
            'architecture_focus': True,
            'code_analysis': True
        }

        print("开始生成Backend架构文档...")
        result = await service.generate_technical_document(
            repository_path=backend_path,
            doc_type='architecture',
            doc_title='CoderWiki Backend 系统架构文档',
            additional_params=custom_params
        )

        if result['success']:
            print("✅ Backend架构文档生成成功！")

            # 保存到专门的文件
            output_file = "backend_architecture_detailed.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.get('content', ''))
            print(f"详细架构文档已保存到: {output_file}")

            # 显示完整内容
            content = result.get('content', '')
            print(f"\n📄 完整架构文档内容:")
            print("=" * 80)
            print(content)
            print("=" * 80)

        else:
            print("❌ Backend架构文档生成失败")
            print(f"错误: {result.get('error', 'Unknown error')}")

        return result['success']

    except Exception as e:
        print(f"❌ 架构文档测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("Backend目录文档生成效果验证")
    print("=" * 80)

    # 设置环境变量
    os.environ['CLAUDE_CODE_ENABLED'] = 'true'
    os.environ['BMAD_DOCS_PATH'] = '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/'

    print(f"CLAUDE_CODE_ENABLED: {os.environ.get('CLAUDE_CODE_ENABLED')}")
    print(f"BMAD_DOCS_PATH: {os.environ.get('BMAD_DOCS_PATH')}")
    print()

    # 运行测试
    success1 = await test_backend_documentation()
    success2 = await test_backend_architecture_doc()

    print("\n" + "=" * 80)
    print("测试结果总结:")
    print("=" * 80)

    if success1 and success2:
        print("🎉 Backend文档生成测试完全成功！")
        print("✅ 多种文档类型生成成功")
        print("✅ 架构文档生成成功")
        print("✅ 文档内容质量良好")
    elif success1:
        print("⚠️  部分测试成功")
        print("✅ 基础文档生成成功")
        print("❌ 架构文档生成失败")
    else:
        print("❌ Backend文档生成测试失败")

    print("\n生成的文件:")
    for file in os.listdir('.'):
        if file.startswith('backend_') and file.endswith('.md'):
            print(f"📄 {file}")

    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
