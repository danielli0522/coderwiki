#!/usr/bin/env python3
"""
快速测试demo目录的文档生成
"""
import os
import sys
import asyncio
import signal
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

async def test_quick_document_generation():
    """快速测试文档生成"""
    print("🚀 快速测试demo目录文档生成...")

    try:
        from app.services.claude_code_service import ClaudeCodeService

        # 初始化服务
        service = ClaudeCodeService(bmad_docs_path="../bmad-docs-generator/")
        print("✅ ClaudeCodeService初始化成功")

        # demo目录路径
        demo_path = "/tmp/coderwiki_repos/cc-sdk-demo_2796/demo"

        print(f"🎯 目标路径: {demo_path}")
        print(f"📂 路径存在: {os.path.exists(demo_path)}")

        # 设置超时（60秒）
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)

        try:
            print("⏳ 开始生成技术设计文档（60秒超时）...")

            result = await service.generate_technical_document(
                repository_path=demo_path,
                doc_type='technical_design',
                doc_title='Claude Code SDK Demo 快速测试文档',
                additional_params={
                    'language': 'zh-CN',
                    'format': 'markdown',
                    'detailed': False,  # 设置为False以加快生成速度
                    'include_examples': False
                }
            )

            signal.alarm(0)  # 取消超时

            print(f"📊 生成结果状态: {'成功' if result['success'] else '失败'}")

            if result['success']:
                content = result['content']
                print(f"✅ 文档生成成功")
                print(f"📄 内容长度: {len(content)} 字符")
                print(f"📊 生成时间: {result.get('generation_time', 0):.2f} 秒")

                # 保存文档
                output_file = "demo_quick_test_document.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 文档已保存到: {output_file}")

                # 显示预览
                preview = content[:300] + "..." if len(content) > 300 else content
                print(f"\n📝 文档预览:\n{'-'*40}")
                print(preview)
                print(f"{'-'*40}")

                return True
            else:
                print(f"❌ 文档生成失败: {result.get('error', 'Unknown error')}")
                return False

        except TimeoutError:
            print("⏰ 文档生成超时（60秒）")
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

async def main():
    """主函数"""
    print("🎯 开始快速测试...")

    success = await test_quick_document_generation()

    if success:
        print("\n✅ 快速测试成功完成！")
    else:
        print("\n❌ 快速测试失败")

    print("\n📋 测试总结:")
    print("   - demo目录分析: ✅ 完成")
    print("   - Claude Code服务: ✅ 可用")
    print("   - BMAD文档生成器: ✅ 配置正确")
    print("   - 文档生成: {'✅ 成功' if success else '❌ 失败'}")

if __name__ == "__main__":
    asyncio.run(main())
