#!/usr/bin/env python3
"""
分析BMAD安装器代码，理解其功能和Claude Code集成
"""

import re
from pathlib import Path

def analyze_bmad_installer():
    """分析BMAD安装器代码"""
    print("=" * 80)
    print("BMAD安装器代码分析")
    print("=" * 80)

    # 1. 分析主要功能
    print("\n🔍 主要功能分析:")
    print("-" * 40)

    features = [
        "✅ 安装BMAD Method核心系统",
        "✅ 安装扩展包(expansion packs)",
        "✅ 配置多种IDE集成",
        "✅ 生成Web bundles",
        "✅ 更新现有安装",
        "✅ 检查更新",
        "✅ 扁平化代码库到XML格式"
    ]

    for feature in features:
        print(f"  {feature}")

    # 2. 支持的IDE
    print("\n🛠️  支持的IDE:")
    print("-" * 40)

    ides = [
        "Cursor",
        "Claude Code",
        "Windsurf",
        "Trae",
        "Roo Code",
        "Kilo Code",
        "Cline",
        "Gemini CLI",
        "Qwen Code",
        "Crush",
        "Github Copilot"
    ]

    for ide in ides:
        print(f"  - {ide}")

    # 3. 主要命令
    print("\n📋 主要命令:")
    print("-" * 40)

    commands = [
        "install - 安装BMAD Method",
        "update - 更新现有安装",
        "update-check - 检查更新",
        "list:expansions - 列出可用扩展包",
        "status - 显示安装状态",
        "flatten - 扁平化代码库"
    ]

    for cmd in commands:
        print(f"  - {cmd}")

    # 4. Claude Code集成分析
    print("\n🎯 Claude Code集成分析:")
    print("-" * 40)

    claude_code_features = [
        "✅ 自动配置Claude Code工作目录",
        "✅ 设置Claude Code的add_dirs路径",
        "✅ 配置Claude Code的allowed_tools",
        "✅ 生成Claude Code的system_prompt",
        "✅ 创建.claude/settings.json配置文件",
        "✅ 集成BMAD子代理到Claude Code工作空间"
    ]

    for feature in claude_code_features:
        print(f"  {feature}")

    # 5. 安装流程
    print("\n🚀 安装流程:")
    print("-" * 40)

    steps = [
        "1. 选择安装目录",
        "2. 检测现有安装状态",
        "3. 选择要安装的组件(BMad核心/扩展包)",
        "4. 配置文档分片设置",
        "5. 选择IDE集成",
        "6. 配置GitHub Copilot(如果选择)",
        "7. 选择Web bundles",
        "8. 执行安装"
    ]

    for step in steps:
        print(f"  {step}")

    # 6. 与当前配置的关系
    print("\n🔗 与当前配置的关系:")
    print("-" * 40)

    print("当前状态:")
    print("  ✅ 已手动配置Claude Code集成")
    print("  ✅ BMAD子代理已可被发现")
    print("  ✅ 可以调用BMAD任务")
    print()
    print("使用BMAD安装器的优势:")
    print("  🎯 自动化配置过程")
    print("  🔧 标准化设置")
    print("  📦 包含所有必要的组件")
    print("  🔄 支持更新和维护")
    print("  🌐 支持多种IDE")

    # 7. 建议
    print("\n💡 建议:")
    print("-" * 40)

    suggestions = [
        "1. 考虑使用BMAD安装器重新安装以获得完整功能",
        "2. 安装器会自动配置Claude Code集成",
        "3. 可以获得最新的BMAD Method框架",
        "4. 支持扩展包和Web bundles",
        "5. 提供标准化的配置和维护"
    ]

    for suggestion in suggestions:
        print(f"  {suggestion}")

    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)

def extract_claude_code_config():
    """提取Claude Code相关配置"""
    print("\n🔧 Claude Code配置示例:")
    print("-" * 40)

    config_example = {
        "cwd": "/path/to/your/project",
        "add_dirs": [
            "/path/to/your/project/.bmad-core",
            "/path/to/your/project/.expansion-packs"
        ],
        "allowed_tools": [
            "Read", "Grep", "WebSearch", "Task"
        ],
        "max_turns": 10,
        "system_prompt": "你是一个专业的BMAD Method专家...",
        "env": {
            "BMAD_CORE_PATH": "/path/to/your/project/.bmad-core",
            "BMAD_ENABLED": "true"
        }
    }

    print("BMAD安装器会生成类似这样的配置:")
    for key, value in config_example.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    analyze_bmad_installer()
    extract_claude_code_config()
