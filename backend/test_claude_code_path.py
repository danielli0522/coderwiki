#!/usr/bin/env python3
"""
测试Claude Code SDK能否读取指定路径的代码
"""
import os
import sys
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['CLAUDE_CODE_ENABLED'] = 'true'
os.environ['BMAD_DOCS_PATH'] = '../bmad-docs-generator/'

def test_path_verification():
    """测试路径验证"""
    print("🔍 验证Claude Code路径配置...")

    # 目标路径
    target_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796"

    print(f"📂 目标路径: {target_path}")

    # 检查路径是否存在
    if os.path.exists(target_path):
        print("✅ 路径存在")

        # 列出目录内容
        try:
            files = os.listdir(target_path)
            print(f"📄 目录包含 {len(files)} 个文件/目录")

            # 显示关键文件
            key_files = []
            for file in files:
                if file in ['package.json', 'README.md', 'tsconfig.json', 'src']:
                    key_files.append(file)
                elif file.endswith('.md'):
                    key_files.append(file)

            if key_files:
                print(f"🔑 关键文件: {key_files}")

            # 检查是否有package.json
            package_json = os.path.join(target_path, 'package.json')
            if os.path.exists(package_json):
                print("📦 这是一个Node.js项目")
                try:
                    import json
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                    print(f"   项目名: {package_data.get('name', 'Unknown')}")
                    print(f"   版本: {package_data.get('version', 'Unknown')}")
                    print(f"   描述: {package_data.get('description', 'No description')}")
                except Exception as e:
                    print(f"   ❌ 无法读取package.json: {e}")

            # 检查README.md
            readme_path = os.path.join(target_path, 'README.md')
            if os.path.exists(readme_path):
                print("📝 README.md存在")
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"   大小: {len(content)} 字符")
                    lines = content.split('\n')
                    if lines:
                        print(f"   第一行: {lines[0][:100]}...")
                except Exception as e:
                    print(f"   ❌ 无法读取README.md: {e}")

        except Exception as e:
            print(f"❌ 无法列出目录内容: {e}")
    else:
        print("❌ 路径不存在")
        return False

    return True

async def test_claude_code_service():
    """测试Claude Code Service"""
    print("\n🤖 测试Claude Code Service...")

    try:
        from app.services.claude_code_service import ClaudeCodeService

        # 初始化服务
        service = ClaudeCodeService(bmad_docs_path="../bmad-docs-generator/")
        print("✅ ClaudeCodeService初始化成功")

        # 检查Claude Code可用性
        availability = service.check_claude_code_availability()
        print(f"📊 Claude Code可用性: {availability}")

        # 检查BMAD文档生成器
        bmad_status = service.check_bmad_docs_generator()
        print(f"📊 BMAD文档生成器状态: {bmad_status}")

        # 测试文档生成
        target_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796"
        print(f"\n📋 测试生成文档，路径: {target_path}")

        result = await service.generate_technical_document(
            repository_path=target_path,
            doc_type='technical_design',
            doc_title='cc-sdk-demo技术设计文档',
            additional_params={
                'language': 'zh-CN',
                'format': 'markdown',
                'detailed': True
            }
        )

        print(f"📊 生成结果: {result}")

        if result['success']:
            content = result['content']
            print(f"✅ 文档生成成功")
            print(f"📄 内容长度: {len(content)} 字符")
            print(f"📊 生成时间: {result.get('generation_time', 0)} 秒")

            # 显示文档前100字符
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"📝 内容预览:\n{preview}")

            # 保存到文件
            output_file = "test_claude_code_output.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 完整内容已保存到: {output_file}")

        else:
            print(f"❌ 文档生成失败: {result.get('error', 'Unknown error')}")

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   可能需要安装Claude Code SDK: pip install claude-code-sdk")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    print("🚀 开始Claude Code路径验证测试...")

    # 测试路径
    if test_path_verification():
        # 测试Claude Code服务
        await test_claude_code_service()
    else:
        print("❌ 路径验证失败，跳过Claude Code测试")

    print("\n✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main())
