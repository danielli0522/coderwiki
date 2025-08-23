#!/usr/bin/env python3
"""
简单的Claude Code子代理配置测试
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.claude_code_service import ClaudeCodeService
from app.services.bmad_subagent_config import BMADSubagentConfig

async def test_basic_config():
    """测试基本配置"""
    print("=" * 60)
    print("Claude Code子代理基本配置测试")
    print("=" * 60)

    # 创建服务实例
    service = ClaudeCodeService()

    # 1. 测试BMAD配置
    print("\n1. 测试BMAD配置...")
    bmad_config = service.bmad_config

    # 验证配置
    validation = bmad_config.validate_configuration()
    print(f"配置验证结果: {'成功' if validation['success'] else '失败'}")

    if not validation['success']:
        print("错误:")
        for error in validation['errors']:
            print(f"  - {error}")

    if validation['warnings']:
        print("警告:")
        for warning in validation['warnings']:
            print(f"  - {warning}")

    # 2. 测试子代理信息
    print("\n2. 测试子代理信息...")
    subagent_info = service.get_bmad_subagent_info()
    if subagent_info['success']:
        print(f"✅ 子代理信息获取成功")
        print(f"  团队数量: {subagent_info['teams_count']}")
        print(f"  代理数量: {subagent_info['agents_count']}")
        print(f"  配置路径: {subagent_info['config_path']}")
    else:
        print(f"❌ 子代理信息获取失败: {subagent_info['error']}")

    # 3. 测试系统提示词生成
    print("\n3. 测试系统提示词生成...")
    try:
        system_prompt = service._prepare_system_prompt(
            doc_type="technical_design",
            doc_title="测试技术设计文档",
            additional_params={"detailed": True}
        )
        print(f"✅ 系统提示词生成成功")
        print(f"  长度: {len(system_prompt)} 字符")

        # 检查是否包含BMAD相关信息
        if "BMAD" in system_prompt:
            print("✅ 包含BMAD相关信息")
        else:
            print("❌ 缺少BMAD相关信息")

    except Exception as e:
        print(f"❌ 系统提示词生成失败: {e}")

    # 4. 测试Claude Code SDK可用性
    print("\n4. 测试Claude Code SDK可用性...")
    sdk_check = service.check_claude_code_availability()
    if sdk_check['available']:
        print("✅ Claude Code SDK可用")
    else:
        print(f"❌ Claude Code SDK不可用: {sdk_check['error']}")

    # 5. 测试BMAD文档生成器可用性
    print("\n5. 测试BMAD文档生成器可用性...")
    bmad_check = service.check_bmad_docs_generator()
    if bmad_check['available']:
        print("✅ BMAD文档生成器可用")
        print(f"  团队数量: {bmad_check['teams_count']}")
        print(f"  代理数量: {bmad_check['agents_count']}")
    else:
        print(f"❌ BMAD文档生成器不可用: {bmad_check['error']}")

async def test_claude_code_connection():
    """测试Claude Code连接"""
    print("\n" + "=" * 60)
    print("Claude Code连接测试")
    print("=" * 60)

    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        from pathlib import Path

        # 创建服务实例
        service = ClaudeCodeService()

        # 获取BMAD文档生成器的绝对路径
        bmad_docs_abs_path = Path(service.bmad_docs_path).resolve()
        print(f"BMAD文档生成器路径: {bmad_docs_abs_path}")
        print(f"路径存在: {bmad_docs_abs_path.exists()}")

        # 配置Claude Code选项
        options = ClaudeCodeOptions(
            system_prompt="你是一个测试助手，请简单回答我的问题。",
            max_turns=3,
            allowed_tools=["Read"],
            add_dirs=[bmad_docs_abs_path],
            cwd=bmad_docs_abs_path
        )

        print("✅ Claude Code选项配置成功")

        # 测试简单连接
        print("\n测试简单连接...")
        async with ClaudeSDKClient(options=options) as client:
            await client.query("请说'Hello World'")

            # 接收响应
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text_content = block.text
                            if text_content and text_content.strip():
                                print(f"✅ 收到响应: {text_content[:100]}...")
                                return  # 成功收到响应，退出测试
                                break
                break

        print("❌ 未收到有效响应")

    except Exception as e:
        print(f"❌ Claude Code连接测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    try:
        await test_basic_config()
        await test_claude_code_connection()

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
