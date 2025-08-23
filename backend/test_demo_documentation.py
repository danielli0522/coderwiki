#!/usr/bin/env python3
"""
测试使用cc-sdk-demo目录下的demo目录生成文档的效果
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

def analyze_demo_directory():
    """分析demo目录的内容"""
    print("🔍 分析demo目录内容...")

    demo_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796/demo"

    if not os.path.exists(demo_path):
        print("❌ demo目录不存在")
        return False

    print(f"📂 demo目录路径: {demo_path}")

    # 列出所有文件
    files = os.listdir(demo_path)
    print(f"📄 包含 {len(files)} 个文件:")

    for file in files:
        file_path = os.path.join(demo_path, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size} bytes)")
        else:
            print(f"   📁 {file}/")

    # 分析关键文件
    print("\n🔍 分析关键文件:")

    # 检查index.html
    index_path = os.path.join(demo_path, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   📄 index.html: {len(content)} 字符")
        print(f"      - 包含HTML结构")
        if 'claude' in content.lower():
            print(f"      - 包含Claude相关代码")

    # 检查app.js
    app_js_path = os.path.join(demo_path, 'app.js')
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   📄 app.js: {len(content)} 字符")
        print(f"      - 包含JavaScript应用逻辑")
        if 'claude' in content.lower():
            print(f"      - 包含Claude SDK集成")

    # 检查claude-browser-sdk.js
    sdk_path = os.path.join(demo_path, 'claude-browser-sdk.js')
    if os.path.exists(sdk_path):
        with open(sdk_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   📄 claude-browser-sdk.js: {len(content)} 字符")
        print(f"      - 包含Claude浏览器SDK")

    # 检查styles.css
    css_path = os.path.join(demo_path, 'styles.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   📄 styles.css: {len(content)} 字符")
        print(f"      - 包含样式定义")

    return True

async def test_demo_documentation_generation():
    """测试demo目录的文档生成"""
    print("\n🤖 测试demo目录文档生成...")

    try:
        from app.services.claude_code_service import ClaudeCodeService

        # 初始化服务
        service = ClaudeCodeService(bmad_docs_path="../bmad-docs-generator/")
        print("✅ ClaudeCodeService初始化成功")

        # demo目录路径
        demo_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796/demo"

        # 测试生成技术设计文档
        print(f"\n📋 生成技术设计文档，路径: {demo_path}")

        result = await service.generate_technical_document(
            repository_path=demo_path,
            doc_type='technical_design',
            doc_title='Claude Code SDK Demo 技术设计文档',
            additional_params={
                'language': 'zh-CN',
                'format': 'markdown',
                'detailed': True,
                'include_examples': True
            }
        )

        print(f"📊 生成结果状态: {'成功' if result['success'] else '失败'}")

        if result['success']:
            content = result['content']
            print(f"✅ 文档生成成功")
            print(f"📄 内容长度: {len(content)} 字符")
            print(f"📊 生成时间: {result.get('generation_time', 0):.2f} 秒")
            print(f"💰 成本估算: ${result.get('cost_estimate', 0):.4f}")

            # 显示文档预览
            preview = content[:500] + "..." if len(content) > 500 else content
            print(f"\n📝 文档预览:\n{'-'*50}")
            print(preview)
            print(f"{'-'*50}")

            # 保存完整文档
            output_file = "demo_technical_design.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 完整文档已保存到: {output_file}")

            # 分析文档内容
            analyze_document_content(content)

        else:
            print(f"❌ 文档生成失败: {result.get('error', 'Unknown error')}")
            print(f"   错误类型: {result.get('error_type', 'Unknown')}")

        # 测试生成API文档
        print(f"\n📋 生成API文档，路径: {demo_path}")

        api_result = await service.generate_technical_document(
            repository_path=demo_path,
            doc_type='api_docs',
            doc_title='Claude Code SDK Demo API文档',
            additional_params={
                'language': 'zh-CN',
                'format': 'markdown',
                'detailed': True
            }
        )

        if api_result['success']:
            api_content = api_result['content']
            print(f"✅ API文档生成成功")
            print(f"📄 内容长度: {len(api_content)} 字符")

            # 保存API文档
            api_output_file = "demo_api_docs.md"
            with open(api_output_file, 'w', encoding='utf-8') as f:
                f.write(api_content)
            print(f"💾 API文档已保存到: {api_output_file}")

        else:
            print(f"❌ API文档生成失败: {api_result.get('error', 'Unknown error')}")

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   可能需要安装Claude Code SDK: pip install claude-code-sdk")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def analyze_document_content(content):
    """分析生成的文档内容"""
    print(f"\n📊 文档内容分析:")

    # 统计章节
    sections = content.count('# ')
    print(f"   📑 章节数量: {sections}")

    # 统计代码块
    code_blocks = content.count('```')
    print(f"   💻 代码块数量: {code_blocks // 2}")

    # 统计列表项
    list_items = content.count('- ')
    print(f"   📝 列表项数量: {list_items}")

    # 检查关键内容
    if 'claude' in content.lower():
        print(f"   ✅ 包含Claude相关内容")
    if 'sdk' in content.lower():
        print(f"   ✅ 包含SDK相关内容")
    if 'demo' in content.lower():
        print(f"   ✅ 包含Demo相关内容")
    if 'api' in content.lower():
        print(f"   ✅ 包含API相关内容")

    # 检查文档结构
    if '# ' in content:
        print(f"   ✅ 包含标题结构")
    if '```' in content:
        print(f"   ✅ 包含代码示例")
    if '## ' in content:
        print(f"   ✅ 包含子章节")

async def main():
    """主函数"""
    print("🚀 开始测试demo目录文档生成...")

    # 分析demo目录
    if analyze_demo_directory():
        # 测试文档生成
        await test_demo_documentation_generation()
    else:
        print("❌ demo目录分析失败，跳过文档生成测试")

    print("\n✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main())
