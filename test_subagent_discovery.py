#!/usr/bin/env python3
"""
测试BMAD子代理发现功能
"""

import os
import json
import yaml
from pathlib import Path

def test_subagent_discovery():
    """测试子代理发现功能"""
    print("=" * 60)
    print("BMAD子代理发现测试")
    print("=" * 60)

    # 1. 检查Claude Code配置
    print("\n🔧 检查Claude Code配置:")
    claude_config = Path(".claude/settings.json")
    if claude_config.exists():
        with open(claude_config, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"  ✅ Claude配置存在")
        print(f"  工作目录: {config.get('cwd', 'N/A')}")
        print(f"  添加目录: {config.get('add_dirs', [])}")
        print(f"  允许工具: {config.get('allowed_tools', [])}")

        # 检查add_dirs中的BMAD路径
        add_dirs = config.get('add_dirs', [])
        bmad_paths = [path for path in add_dirs if 'bmad' in path.lower()]
        print(f"  BMAD路径: {bmad_paths}")

        for path in bmad_paths:
            if Path(path).exists():
                print(f"    ✅ 路径存在: {path}")
            else:
                print(f"    ❌ 路径不存在: {path}")
    else:
        print("  ❌ Claude配置不存在")

    # 2. 检查BMAD扩展包
    print("\n📦 检查BMAD扩展包:")
    bmad_dir = Path(".bmad-docs-generator")
    if bmad_dir.exists():
        print(f"  ✅ BMAD扩展包目录存在: {bmad_dir}")

        # 检查关键文件
        key_files = [
            "agent-teams/enhanced-docs-generation-team.yaml",
            "agent-teams/docs-generation-team.yaml",
            "agents/code-analyst.md",
            "agents/tech-architect.md",
            "workflows/enhanced-docs-generation.yaml",
            "config.yaml"
        ]

        print("\n  检查关键文件:")
        for file_path in key_files:
            full_path = bmad_dir / file_path
            if full_path.exists():
                print(f"    ✅ {file_path}")

                # 检查文件内容
                if file_path.endswith('.yaml'):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = yaml.safe_load(f)
                        print(f"      📄 YAML解析成功")
                    except Exception as e:
                        print(f"      ❌ YAML解析失败: {e}")
            else:
                print(f"    ❌ {file_path}")
    else:
        print(f"  ❌ BMAD扩展包目录不存在: {bmad_dir}")

    # 3. 测试子代理调用路径
    print("\n🎯 测试子代理调用路径:")

    test_paths = [
        ".bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml",
        ".bmad-docs-generator/agents/code-analyst.md",
        ".bmad-docs-generator/workflows/enhanced-docs-generation.yaml"
    ]

    for test_path in test_paths:
        if Path(test_path).exists():
            print(f"  ✅ 可调用: /task {test_path}")
        else:
            print(f"  ❌ 不可调用: /task {test_path}")

    # 4. 显示正确的调用命令
    print("\n" + "=" * 50)
    print("正确的调用命令:")
    print("=" * 50)
    print()
    print("在Claude Code中使用以下命令:")
    print()
    print("1. 调用增强文档生成团队:")
    print("   /task .bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml")
    print()
    print("2. 调用代码分析代理:")
    print("   /task .bmad-docs-generator/agents/code-analyst.md")
    print()
    print("3. 调用技术架构代理:")
    print("   /task .bmad-docs-generator/agents/tech-architect.md")
    print()
    print("4. 调用工作流程:")
    print("   /task .bmad-docs-generator/workflows/enhanced-docs-generation.yaml")
    print()
    print("5. 查看配置:")
    print("   /read .bmad-docs-generator/config.yaml")
    print("=" * 50)

    # 5. 诊断建议
    print("\n💡 诊断建议:")
    print("-" * 30)

    if claude_config.exists() and bmad_dir.exists():
        print("✅ 配置看起来正确")
        print("💡 尝试重启Claude Code")
        print("💡 确保在项目根目录启动Claude Code")
        print("💡 使用绝对路径调用子代理")
    else:
        print("❌ 配置有问题")
        if not claude_config.exists():
            print("  - Claude Code配置缺失")
        if not bmad_dir.exists():
            print("  - BMAD扩展包未安装")
        print("💡 重新运行安装脚本")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_subagent_discovery()
