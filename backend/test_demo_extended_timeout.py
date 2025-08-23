#!/usr/bin/env python3
"""
使用10分钟超时时间测试demo目录的文档生成
"""
import os
import sys
import asyncio
import signal
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['CLAUDE_CODE_ENABLED'] = 'true'
os.environ['BMAD_DOCS_PATH'] = '../bmad-docs-generator/'

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("操作超时")

async def test_extended_timeout_document_generation():
    """使用10分钟超时测试文档生成"""
    print("🚀 使用10分钟超时测试demo目录文档生成...")

    try:
        from app.services.claude_code_service import ClaudeCodeService

        # 初始化服务
        service = ClaudeCodeService(bmad_docs_path="../bmad-docs-generator/")
        print("✅ ClaudeCodeService初始化成功")

        # demo目录路径
        demo_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796/demo"

        print(f"🎯 目标路径: {demo_path}")
        print(f"📂 路径存在: {os.path.exists(demo_path)}")

        # 设置超时（10分钟 = 600秒）
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(600)

        try:
            print("⏳ 开始生成技术设计文档（10分钟超时）...")
            start_time = time.time()

            result = await service.generate_technical_document(
                repository_path=demo_path,
                doc_type='technical_design',
                doc_title='Claude Code SDK Demo 扩展超时测试文档',
                additional_params={
                    'language': 'zh-CN',
                    'format': 'markdown',
                    'detailed': True,
                    'include_examples': True
                }
            )

            end_time = time.time()
            generation_time = end_time - start_time

            signal.alarm(0)  # 取消超时

            print(f"📊 生成结果状态: {'成功' if result['success'] else '失败'}")
            print(f"⏱️  实际生成时间: {generation_time:.2f} 秒")

            if result['success']:
                content = result['content']
                print(f"✅ 文档生成成功")
                print(f"📄 内容长度: {len(content)} 字符")
                print(f"📊 生成时间: {result.get('generation_time', 0):.2f} 秒")
                print(f"💰 成本估算: ${result.get('cost_estimate', 0):.4f}")

                # 保存文档
                output_file = "demo_extended_timeout_document.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 文档已保存到: {output_file}")

                # 显示预览
                preview = content[:500] + "..." if len(content) > 500 else content
                print(f"\n📝 文档预览:\n{'-'*50}")
                print(preview)
                print(f"{'-'*50}")

                # 分析文档内容
                analyze_document_content(content)

                return True
            else:
                print(f"❌ 文档生成失败: {result.get('error', 'Unknown error')}")
                print(f"   错误类型: {result.get('error_type', 'Unknown')}")
                return False

        except TimeoutError:
            print("⏰ 文档生成超时（10分钟）")
            signal.alarm(0)
            return False
        except Exception as e:
            print(f"❌ 文档生成错误: {e}")
            signal.alarm(0)
            return False

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_docs_generation():
    """测试API文档生成"""
    print("\n📋 测试API文档生成（10分钟超时）...")

    try:
        from app.services.claude_code_service import ClaudeCodeService

        # 初始化服务
        service = ClaudeCodeService(bmad_docs_path="../bmad-docs-generator/")

        # demo目录路径
        demo_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796/demo"

        # 设置超时（10分钟）
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(600)

        try:
            print("⏳ 开始生成API文档...")
            start_time = time.time()

            result = await service.generate_technical_document(
                repository_path=demo_path,
                doc_type='api_docs',
                doc_title='Claude Code SDK Demo API文档',
                additional_params={
                    'language': 'zh-CN',
                    'format': 'markdown',
                    'detailed': True
                }
            )

            end_time = time.time()
            generation_time = end_time - start_time

            signal.alarm(0)  # 取消超时

            if result['success']:
                content = result['content']
                print(f"✅ API文档生成成功")
                print(f"📄 内容长度: {len(content)} 字符")
                print(f"⏱️  生成时间: {generation_time:.2f} 秒")

                # 保存API文档
                output_file = "demo_api_docs_extended.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 API文档已保存到: {output_file}")

                return True
            else:
                print(f"❌ API文档生成失败: {result.get('error', 'Unknown error')}")
                return False

        except TimeoutError:
            print("⏰ API文档生成超时（10分钟）")
            signal.alarm(0)
            return False
        except Exception as e:
            print(f"❌ API文档生成错误: {e}")
            signal.alarm(0)
            return False

    except Exception as e:
        print(f"❌ API文档测试错误: {e}")
        return False

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
    print("🎯 开始10分钟超时测试...")
    print("⏰ 超时设置: 10分钟 (600秒)")

    # 测试技术设计文档生成
    tech_doc_success = await test_extended_timeout_document_generation()

    # 测试API文档生成
    api_doc_success = await test_api_docs_generation()

    # 总结
    print(f"\n📋 测试总结:")
    print(f"   - 技术设计文档: {'✅ 成功' if tech_doc_success else '❌ 失败'}")
    print(f"   - API文档: {'✅ 成功' if api_doc_success else '❌ 失败'}")

    if tech_doc_success or api_doc_success:
        print(f"\n✅ 扩展超时测试部分成功！")
        print(f"   超时时间增加到10分钟解决了部分问题")
    else:
        print(f"\n❌ 扩展超时测试失败")
        print(f"   即使10分钟超时仍然不够，可能需要其他解决方案")

if __name__ == "__main__":
    asyncio.run(main())
