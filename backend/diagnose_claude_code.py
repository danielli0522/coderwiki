#!/usr/bin/env python3
"""
Claude Code诊断脚本
"""

import asyncio
import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnose_claude_code():
    """诊断Claude Code状态"""
    print("=" * 60)
    print("Claude Code诊断报告")
    print("=" * 60)

    # 1. 检查Claude Code CLI是否安装
    print("\n1. 检查Claude Code CLI...")
    try:
        result = subprocess.run(['claude-code', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Claude Code CLI已安装")
            print(f"  版本信息: {result.stdout.strip()}")
        else:
            print(f"❌ Claude Code CLI返回错误: {result.stderr}")
    except FileNotFoundError:
        print("❌ Claude Code CLI未找到，请确保已安装")
    except subprocess.TimeoutExpired:
        print("❌ Claude Code CLI响应超时")
    except Exception as e:
        print(f"❌ 检查Claude Code CLI时出错: {e}")

    # 2. 检查Claude Code SDK
    print("\n2. 检查Claude Code SDK...")
    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        print("✅ Claude Code SDK导入成功")

        # 检查SDK版本
        import claude_code_sdk
        print(f"  SDK版本: {getattr(claude_code_sdk, '__version__', 'unknown')}")

    except ImportError as e:
        print(f"❌ Claude Code SDK导入失败: {e}")
        return

    # 3. 检查BMAD文档生成器
    print("\n3. 检查BMAD文档生成器...")
    from app.services.claude_code_service import ClaudeCodeService

    service = ClaudeCodeService()
    bmad_check = service.check_bmad_docs_generator()

    if bmad_check['available']:
        print("✅ BMAD文档生成器可用")
        print(f"  路径: {bmad_check['bmad_docs_path']}")
        print(f"  团队数量: {bmad_check['teams_count']}")
        print(f"  代理数量: {bmad_check['agents_count']}")
    else:
        print(f"❌ BMAD文档生成器不可用: {bmad_check['error']}")

    # 4. 测试Claude Code连接
    print("\n4. 测试Claude Code连接...")
    try:
        from pathlib import Path

        # 获取BMAD文档生成器的绝对路径
        bmad_docs_abs_path = Path(service.bmad_docs_path).resolve()

        # 配置Claude Code选项
        options = ClaudeCodeOptions(
            system_prompt="你是一个诊断助手。",
            max_turns=2,
            allowed_tools=["Read"],
            add_dirs=[bmad_docs_abs_path],
            cwd=bmad_docs_abs_path
        )

        print("✅ Claude Code选项配置成功")

        # 测试连接
        print("  正在测试连接...")
        async with ClaudeSDKClient(options=options) as client:
            print("  ✅ ClaudeSDKClient创建成功")

            # 发送简单查询
            await client.query("请回复'连接测试成功'")
            print("  ✅ 查询发送成功")

            # 接收响应
            response_received = False
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text_content = block.text
                            if text_content and text_content.strip():
                                print(f"  ✅ 收到响应: {text_content[:100]}...")
                                response_received = True
                                break
                    if response_received:
                        break
                break

            if not response_received:
                print("  ⚠️  未收到响应，但连接可能正常")

    except Exception as e:
        print(f"❌ Claude Code连接测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 5. 检查环境变量
    print("\n5. 检查环境变量...")
    env_vars = [
        'CLAUDE_CODE_ENABLED',
        'BMAD_DOCS_PATH',
        'CLAUDE_CODE_PATH'
    ]

    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未设置")

    # 6. 检查文件权限
    print("\n6. 检查文件权限...")
    try:
        bmad_path = Path(service.bmad_docs_path).resolve()
        print(f"  BMAD路径: {bmad_path}")
        print(f"  路径存在: {bmad_path.exists()}")
        print(f"  可读: {os.access(bmad_path, os.R_OK)}")
        print(f"  可写: {os.access(bmad_path, os.W_OK)}")
        print(f"  可执行: {os.access(bmad_path, os.X_OK)}")
    except Exception as e:
        print(f"  检查文件权限时出错: {e}")

    print("\n" + "=" * 60)
    print("诊断完成!")
    print("=" * 60)

async def test_subagent_discovery():
    """测试子代理发现"""
    print("\n" + "=" * 60)
    print("子代理发现测试")
    print("=" * 60)

    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        from pathlib import Path
        from app.services.claude_code_service import ClaudeCodeService

        service = ClaudeCodeService()
        bmad_docs_abs_path = Path(service.bmad_docs_path).resolve()

        # 配置选项
        options = ClaudeCodeOptions(
            system_prompt="你是一个文档生成专家。请检查可用的子代理和工具。",
            max_turns=5,
            allowed_tools=["Read", "Grep", "WebSearch", "Task"],
            add_dirs=[bmad_docs_abs_path],
            cwd=bmad_docs_abs_path
        )

        print("✅ 配置选项设置完成")

        # 测试子代理发现
        async with ClaudeSDKClient(options=options) as client:
            await client.query("请列出当前工作目录中的文件，特别是agent-teams和agents目录")

            response_count = 0
            async for message in client.receive_response():
                response_count += 1
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text_content = block.text
                            if text_content and text_content.strip():
                                print(f"响应 {response_count}: {text_content[:300]}...")
                                break

                if response_count >= 3:
                    break

    except Exception as e:
        print(f"❌ 子代理发现测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    try:
        await diagnose_claude_code()
        await test_subagent_discovery()

    except Exception as e:
        print(f"\n诊断过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
