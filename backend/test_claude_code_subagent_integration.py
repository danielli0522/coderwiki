#!/usr/bin/env python3
"""
测试Claude Code中的BMAD子代理集成
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.claude_code_service import ClaudeCodeService
from app.services.bmad_subagent_config import BMADSubagentConfig

async def test_claude_code_subagent_integration():
    """测试Claude Code中的BMAD子代理集成"""
    print("=" * 60)
    print("Claude Code BMAD子代理集成测试")
    print("=" * 60)

    # 创建服务实例
    service = ClaudeCodeService()

    # 1. 验证BMAD配置
    print("\n1. 验证BMAD配置...")
    bmad_config = service.bmad_config
    validation = bmad_config.validate_configuration()

    if validation['success']:
        print("✅ BMAD配置验证成功")
    else:
        print("❌ BMAD配置验证失败")
        for error in validation['errors']:
            print(f"  - {error}")
        return

    # 2. 获取子代理信息
    print("\n2. 获取子代理信息...")
    subagent_info = service.get_bmad_subagent_info()

    if subagent_info['success']:
        print("✅ 子代理信息获取成功")
        print(f"  团队数量: {subagent_info['teams_count']}")
        print(f"  代理数量: {subagent_info['agents_count']}")

        # 显示团队信息
        teams = subagent_info['teams']
        for team in teams:
            print(f"  - {team['name']} ({team['id']})")
            print(f"    路径: {team['path']}")
            print(f"    代理: {', '.join(team['agents'])}")
    else:
        print(f"❌ 子代理信息获取失败: {subagent_info['error']}")
        return

    # 3. 测试Claude Code SDK配置
    print("\n3. 测试Claude Code SDK配置...")
    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        from pathlib import Path

        # 获取BMAD文档生成器的绝对路径
        bmad_docs_abs_path = Path(service.bmad_docs_path).resolve()

        # 配置Claude Code选项
        options = ClaudeCodeOptions(
            system_prompt="你是一个文档生成专家，可以使用BMAD子代理。",
            max_turns=5,
            allowed_tools=["Read", "Grep", "WebSearch", "Task"],
            add_dirs=[bmad_docs_abs_path],
            cwd=bmad_docs_abs_path
        )

        print("✅ Claude Code选项配置成功")
        print(f"  工作目录: {options.cwd}")
        print(f"  添加目录: {options.add_dirs}")
        print(f"  允许工具: {options.allowed_tools}")

    except Exception as e:
        print(f"❌ Claude Code SDK配置失败: {e}")
        return

    # 4. 生成调用指令
    print("\n4. 生成调用指令...")
    call_instructions = bmad_config.get_subagent_call_instructions()
    print("✅ 调用指令生成成功")
    print(f"  指令长度: {len(call_instructions)} 字符")

    # 5. 显示关键调用命令
    print("\n5. 关键调用命令:")
    print("=" * 40)
    print("在Claude Code中使用以下命令:")
    print()
    print("激活增强文档生成团队:")
    print("/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml")
    print()
    print("查看BMAD配置:")
    print("/read bmad-docs-generator/config.yaml")
    print()
    print("查看工作流程:")
    print("/read bmad-docs-generator/workflows/enhanced-docs-generation.yaml")
    print()
    print("调用单个代理:")
    print("/task bmad-docs-generator/agents/code-analyst.md")
    print("/task bmad-docs-generator/agents/tech-architect.md")
    print("/task bmad-docs-generator/agents/flow-analyst.md")
    print("/task bmad-docs-generator/agents/problem-solver.md")
    print("/task bmad-docs-generator/agents/doc-engineer.md")
    print("=" * 40)

    # 6. 验证文件存在性
    print("\n6. 验证文件存在性...")
    bmad_path = Path(service.bmad_docs_path).resolve()

    key_files = [
        "agent-teams/enhanced-docs-generation-team.yaml",
        "agent-teams/docs-generation-team.yaml",
        "agents/code-analyst.md",
        "agents/tech-architect.md",
        "agents/flow-analyst.md",
        "agents/problem-solver.md",
        "agents/doc-engineer.md",
        "workflows/enhanced-docs-generation.yaml",
        "config.yaml"
    ]

    all_files_exist = True
    for file_path in key_files:
        full_path = bmad_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_files_exist = False

    if all_files_exist:
        print("✅ 所有关键文件都存在")
    else:
        print("❌ 部分关键文件缺失")

    print("\n" + "=" * 60)
    print("集成测试完成!")
    print("=" * 60)

    if all_files_exist:
        print("🎉 BMAD子代理已成功配置到Claude Code!")
        print("现在你可以在Claude Code中使用BMAD子代理生成技术文档了。")
    else:
        print("⚠️  请检查缺失的文件，确保BMAD子代理配置完整。")

async def main():
    """主函数"""
    try:
        await test_claude_code_subagent_integration()

    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
