#!/usr/bin/env python3
"""
验证Claude Code标准子代理配置
"""

import os
import json
import yaml
from pathlib import Path

def test_claude_subagents():
    """测试Claude Code标准子代理配置"""
    print("🎯 Claude Code标准子代理验证")
    print("=" * 60)

    # 1. 检查.claude/agents目录
    print("\n📁 检查子代理目录:")
    agents_dir = Path(".claude/agents")
    if agents_dir.exists():
        print(f"  ✅ 子代理目录存在: {agents_dir}")

        # 列出所有子代理文件
        agent_files = list(agents_dir.glob("*.md"))
        print(f"  📋 发现 {len(agent_files)} 个子代理文件:")

        for agent_file in agent_files:
            print(f"    - {agent_file.name}")
    else:
        print(f"  ❌ 子代理目录不存在: {agents_dir}")
        return False

    # 2. 验证子代理文件格式
    print("\n📄 验证子代理文件格式:")

    required_agents = [
        "code-analyst.md",
        "tech-architect.md",
        "flow-analyst.md",
        "problem-solver.md",
        "doc-engineer.md",
        "bmad-docs-team.md"
    ]

    all_valid = True
    for agent_name in required_agents:
        agent_file = agents_dir / agent_name
        if agent_file.exists():
            print(f"  ✅ {agent_name}")

            # 检查YAML前言格式
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查是否有YAML前言
                if content.startswith('---'):
                    print(f"    ✅ YAML前言格式正确")

                    # 解析YAML前言
                    lines = content.split('\n')
                    yaml_lines = []
                    in_yaml = False

                    for line in lines:
                        if line.strip() == '---':
                            if not in_yaml:
                                in_yaml = True
                            else:
                                break
                        elif in_yaml:
                            yaml_lines.append(line)

                    if yaml_lines:
                        yaml_content = '\n'.join(yaml_lines)
                        try:
                            config = yaml.safe_load(yaml_content)

                            # 检查必需字段
                            required_fields = ['name', 'description']
                            for field in required_fields:
                                if field in config:
                                    print(f"    ✅ {field}: {config[field]}")
                                else:
                                    print(f"    ❌ 缺少字段: {field}")
                                    all_valid = False

                            # 检查工具配置
                            if 'tools' in config:
                                print(f"    ✅ tools: {config['tools']}")
                            else:
                                print(f"    ℹ️  tools: 继承所有工具")

                        except yaml.YAMLError as e:
                            print(f"    ❌ YAML解析失败: {e}")
                            all_valid = False
                    else:
                        print(f"    ❌ 未找到YAML前言")
                        all_valid = False
                else:
                    print(f"    ❌ 缺少YAML前言")
                    all_valid = False

            except Exception as e:
                print(f"    ❌ 文件读取失败: {e}")
                all_valid = False
        else:
            print(f"  ❌ {agent_name} - 文件不存在")
            all_valid = False

    # 3. 检查Claude Code配置
    print("\n🔧 检查Claude Code配置:")
    claude_config = Path(".claude/settings.json")
    if claude_config.exists():
        with open(claude_config, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print("  ✅ Claude Code配置存在")
        print(f"  工作目录: {config.get('cwd', 'N/A')}")
        print(f"  添加目录: {config.get('add_dirs', [])}")
        print(f"  允许工具: {config.get('allowed_tools', [])}")

        # 检查BMAD路径
        add_dirs = config.get('add_dirs', [])
        bmad_path = "/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/.bmad-docs-generator"

        if bmad_path in add_dirs:
            print(f"  ✅ BMAD路径已配置: {bmad_path}")
        else:
            print(f"  ❌ BMAD路径未配置")
            all_valid = False
    else:
        print("  ❌ Claude Code配置不存在")
        all_valid = False

    # 4. 显示使用说明
    print("\n" + "=" * 50)
    print("🎉 Claude Code标准子代理配置完成!")
    print("=" * 50)

    print("\n📋 现在你可以使用以下方式调用子代理:")
    print()
    print("🚀 启动Claude Code:")
    print("   cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki")
    print("   claude")
    print()
    print("🎯 调用子代理:")
    print()
    print("1. 使用/agents命令查看所有子代理:")
    print("   /agents")
    print()
    print("2. 显式调用特定子代理:")
    print("   使用代码分析专家: 让代码分析专家分析当前项目")
    print("   使用技术架构专家: 请技术架构专家评估系统架构")
    print("   使用流程分析专家: 让流程分析专家分析数据流")
    print("   使用问题诊断专家: 请问题诊断专家分析这个错误")
    print("   使用文档工程师: 让文档工程师创建技术文档")
    print("   使用BMAD文档团队: 请BMAD文档团队生成完整文档")
    print()
    print("3. 自动委托:")
    print("   Claude Code会根据任务描述自动选择合适的子代理")
    print("   在子代理描述中包含'主动使用'或'必须使用'等短语")
    print("=" * 50)

    print("\n💡 子代理优势:")
    print("- 上下文保护: 每个子代理有独立的上下文窗口")
    print("- 专业知识: 针对特定任务优化的专业能力")
    print("- 可重用性: 可在不同项目中重复使用")
    print("- 灵活权限: 每个子代理可配置不同的工具访问权限")

    if all_valid:
        print("\n✅ 所有子代理配置验证成功!")
        print("现在可以在Claude Code中使用标准子代理了。")
        return True
    else:
        print("\n❌ 子代理配置验证失败!")
        print("请检查配置并修复问题。")
        return False

if __name__ == "__main__":
    success = test_claude_subagents()
    exit(0 if success else 1)
