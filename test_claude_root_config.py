#!/usr/bin/env python3
"""
测试根目录的Claude Code配置
"""

import os
import sys
from pathlib import Path

def test_root_config():
    """测试根目录配置"""
    print("=" * 60)
    print("根目录Claude Code配置测试")
    print("=" * 60)

    # 1. 检查当前目录
    current_dir = Path.cwd()
    print(f"当前目录: {current_dir}")

    # 2. 检查BMAD文档生成器路径
    bmad_path = current_dir / "bmad-docs-generator"
    print(f"BMAD路径: {bmad_path}")
    print(f"BMAD路径存在: {bmad_path.exists()}")

    # 3. 检查关键文件
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

    print("\n检查关键文件:")
    all_files_exist = True
    for file_path in key_files:
        full_path = bmad_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_files_exist = False

    # 4. 检查.claude配置
    claude_config = current_dir / ".claude" / "settings.json"
    print(f"\nClaude配置: {claude_config}")
    print(f"Claude配置存在: {claude_config.exists()}")

    if claude_config.exists():
        print("✅ Claude Code配置文件存在")
    else:
        print("❌ Claude Code配置文件不存在")

    # 5. 显示正确的调用命令
    print("\n" + "=" * 40)
    print("正确的调用命令:")
    print("=" * 40)
    print()
    print("在项目根目录启动Claude Code:")
    print("cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki")
    print("claude")
    print()
    print("然后使用以下命令:")
    print("/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml")
    print()
    print("或者查看配置:")
    print("/read bmad-docs-generator/config.yaml")
    print("/read bmad-docs-generator/workflows/enhanced-docs-generation.yaml")
    print("=" * 40)

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

    if all_files_exist and claude_config.exists():
        print("🎉 根目录配置正确!")
        print("现在可以在项目根目录启动Claude Code并调用BMAD子代理了。")
    else:
        print("⚠️  请检查缺失的文件或配置。")

if __name__ == "__main__":
    test_root_config()
