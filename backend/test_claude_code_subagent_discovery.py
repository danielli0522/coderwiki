#!/usr/bin/env python3
"""
测试Claude Code子代理发现功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.claude_code_service import ClaudeCodeService
from app.services.bmad_subagent_config import BMADSubagentConfig

async def test_subagent_discovery():
    """测试子代理发现功能"""
    print("=" * 60)
    print("Claude Code子代理发现测试")
    print("=" * 60)

    # 创建服务实例
    service = ClaudeCodeService()

    # 测试系统提示词生成
    print("\n1. 测试系统提示词生成...")
    system_prompt = service._prepare_system_prompt(
        doc_type="technical_design",
        doc_title="测试技术设计文档",
        additional_params={"detailed": True}
    )

    print(f"系统提示词长度: {len(system_prompt)} 字符")
    print("\n系统提示词预览 (前800字符):")
    print("-" * 40)
    print(system_prompt[:800] + "...")
    print("-" * 40)

    # 测试Claude Code SDK配置
    print("\n2. 测试Claude Code SDK配置...")
    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        from pathlib import Path

        # 获取BMAD文档生成器的绝对路径
        bmad_docs_abs_path = Path(service.bmad_docs_path).resolve()
        print(f"BMAD文档生成器绝对路径: {bmad_docs_abs_path}")
        print(f"路径存在: {bmad_docs_abs_path.exists()}")

        # 配置Claude Code选项
        options = ClaudeCodeOptions(
            system_prompt="测试系统提示词",
            max_turns=5,
            allowed_tools=["Read", "Grep", "WebSearch", "Task"],
            add_dirs=[bmad_docs_abs_path],
            cwd=bmad_docs_abs_path
        )

        print(f"Claude Code选项配置成功:")
        print(f"  - add_dirs: {options.add_dirs}")
        print(f"  - cwd: {options.cwd}")
        print(f"  - allowed_tools: {options.allowed_tools}")

    except Exception as e:
        print(f"配置测试失败: {e}")
        return

    # 测试简单的Claude Code查询
    print("\n3. 测试Claude Code查询...")
    try:
        async with ClaudeSDKClient(options=options) as client:
            # 发送一个简单的查询来测试连接
            await client.query("请列出当前工作目录中的文件")

            # 接收响应
            response_count = 0
            async for message in client.receive_response():
                response_count += 1
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text_content = block.text
                            if text_content and text_content.strip():
                                print(f"响应 {response_count}: {text_content[:200]}...")
                                break

                # 限制响应数量
                if response_count >= 3:
                    break

    except Exception as e:
        print(f"Claude Code查询测试失败: {e}")
        return

    print("\n4. 测试BMAD子代理配置...")
    bmad_config = service.bmad_config

    # 验证团队配置
    teams = bmad_config.get_subagent_teams()
    print(f"可用团队数量: {len(teams)}")
    for team in teams:
        print(f"  - {team['name']} ({team['id']})")
        print(f"    路径: {team['path']}")

        # 检查团队文件是否存在
        team_file_path = os.path.join(service.bmad_docs_path, team['path'])
        print(f"    文件存在: {os.path.exists(team_file_path)}")

    # 验证代理配置
    agents = bmad_config.get_subagent_agents()
    print(f"\n可用代理数量: {len(agents)}")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['role']})")
        print(f"    路径: {agent['path']}")

        # 检查代理文件是否存在
        agent_file_path = os.path.join(service.bmad_docs_path, agent['path'])
        print(f"    文件存在: {os.path.exists(agent_file_path)}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

async def test_subagent_call():
    """测试子代理调用功能"""
    print("\n" + "=" * 60)
    print("子代理调用测试")
    print("=" * 60)

    # 创建服务实例
    service = ClaudeCodeService()

    # 测试文档生成
    print("\n1. 测试文档生成...")
    try:
        # 使用当前目录作为测试仓库
        test_repo_path = os.getcwd()

        result = await service.generate_technical_document(
            repository_path=test_repo_path,
            doc_type="technical_design",
            doc_title="测试技术设计文档",
            additional_params={"detailed": True}
        )

        if result['success']:
            print("✅ 文档生成成功!")
            print(f"  内容长度: {len(result.get('content', ''))} 字符")
            print(f"  生成时间: {result.get('generation_time', 0):.2f} 秒")
            print(f"  成本估算: ${result.get('cost_estimate', 0):.4f}")

            # 显示内容预览
            content = result.get('content', '')
            if content:
                print("\n内容预览 (前500字符):")
                print("-" * 40)
                print(content[:500] + "...")
                print("-" * 40)
        else:
            print("❌ 文档生成失败!")
            print(f"  错误: {result.get('error', 'Unknown error')}")
            print(f"  错误类型: {result.get('error_type', 'unknown')}")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    try:
        await test_subagent_discovery()
        await test_subagent_call()

    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
