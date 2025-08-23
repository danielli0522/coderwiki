#!/usr/bin/env python3
"""
简化的BMAD子代理测试
"""

import os
import json
from pathlib import Path

def test_simple_subagent():
    """简化的子代理测试"""
    print("=" * 50)
    print("简化BMAD子代理测试")
    print("=" * 50)

    # 1. 检查基本配置
    print("\n🔧 基本配置检查:")

    # Claude配置
    claude_config = Path(".claude/settings.json")
    if claude_config.exists():
        print("  ✅ Claude Code配置存在")
    else:
        print("  ❌ Claude Code配置不存在")
        return

    # BMAD扩展包
    bmad_dir = Path(".bmad-docs-generator")
    if bmad_dir.exists():
        print("  ✅ BMAD扩展包存在")
    else:
        print("  ❌ BMAD扩展包不存在")
        return

    # 2. 检查关键文件
    print("\n📋 关键文件检查:")

    key_files = [
        ".bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml",
        ".bmad-docs-generator/agents/code-analyst.md",
        ".bmad-docs-generator/workflows/enhanced-docs-generation.yaml"
    ]

    all_files_exist = True
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            all_files_exist = False

    if not all_files_exist:
        print("\n❌ 关键文件缺失，请重新安装BMAD扩展包")
        return

    # 3. 显示调用命令
    print("\n" + "=" * 40)
    print("现在可以使用的命令:")
    print("=" * 40)
    print()
    print("🚀 启动Claude Code:")
    print("   cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki")
    print("   claude")
    print()
    print("📋 调用子代理:")
    print()
    print("1. 增强文档生成团队:")
    print("   /task .bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml")
    print()
    print("2. 代码分析代理:")
    print("   /task .bmad-docs-generator/agents/code-analyst.md")
    print()
    print("3. 技术架构代理:")
    print("   /task .bmad-docs-generator/agents/tech-architect.md")
    print()
    print("4. 流程分析代理:")
    print("   /task .bmad-docs-generator/agents/flow-analyst.md")
    print()
    print("5. 问题诊断代理:")
    print("   /task .bmad-docs-generator/agents/problem-solver.md")
    print()
    print("6. 文档工程师代理:")
    print("   /task .bmad-docs-generator/agents/doc-engineer.md")
    print()
    print("7. 工作流程:")
    print("   /task .bmad-docs-generator/workflows/enhanced-docs-generation.yaml")
    print()
    print("8. 查看配置:")
    print("   /read .bmad-docs-generator/config.yaml")
    print("=" * 40)

    # 4. 故障排除建议
    print("\n💡 如果子代理仍然不可见:")
    print("-" * 30)
    print("1. 确保在项目根目录启动Claude Code")
    print("2. 重启Claude Code")
    print("3. 检查Claude Code版本")
    print("4. 尝试使用绝对路径")
    print("5. 查看Claude Code错误信息")

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    test_simple_subagent()
