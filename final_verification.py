#!/usr/bin/env python3
"""
最终BMAD子代理验证
"""

import json
import yaml
from pathlib import Path

def final_verification():
    """最终验证"""
    print("🎯 BMAD子代理最终验证")
    print("=" * 60)

    # 1. 验证Claude Code配置
    print("\n🔧 Claude Code配置验证:")
    claude_config = Path(".claude/settings.json")

    if not claude_config.exists():
        print("❌ Claude Code配置不存在")
        return False

    with open(claude_config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 检查关键配置项
    required_keys = ['cwd', 'add_dirs', 'allowed_tools']
    for key in required_keys:
        if key not in config:
            print(f"❌ 缺少配置项: {key}")
            return False

    print("✅ Claude Code配置完整")

    # 检查BMAD路径
    add_dirs = config.get('add_dirs', [])
    bmad_path = "/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/.bmad-docs-generator"

    if bmad_path in add_dirs:
        print("✅ BMAD路径已配置")
    else:
        print(f"❌ BMAD路径未配置: {bmad_path}")
        return False

    # 2. 验证BMAD扩展包
    print("\n📦 BMAD扩展包验证:")
    bmad_dir = Path(".bmad-docs-generator")

    if not bmad_dir.exists():
        print("❌ BMAD扩展包目录不存在")
        return False

    print("✅ BMAD扩展包目录存在")

    # 检查关键文件
    required_files = [
        "agent-teams/enhanced-docs-generation-team.yaml",
        "agents/code-analyst.md",
        "workflows/enhanced-docs-generation.yaml",
        "config.yaml"
    ]

    for file_path in required_files:
        full_path = bmad_dir / file_path
        if not full_path.exists():
            print(f"❌ 关键文件缺失: {file_path}")
            return False
        print(f"✅ {file_path}")

    # 3. 验证YAML文件
    print("\n📄 YAML文件验证:")

    yaml_files = [
        "agent-teams/enhanced-docs-generation-team.yaml",
        "workflows/enhanced-docs-generation.yaml",
        "config.yaml"
    ]

    for yaml_file in yaml_files:
        full_path = bmad_dir / yaml_file
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"✅ {yaml_file} - YAML解析成功")
        except Exception as e:
            print(f"❌ {yaml_file} - YAML解析失败: {e}")
            return False

    # 4. 显示最终状态
    print("\n" + "=" * 50)
    print("🎉 验证完成 - 所有配置正确!")
    print("=" * 50)

    print("\n📋 现在你可以使用以下命令:")
    print()
    print("🚀 启动Claude Code:")
    print("   cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki")
    print("   claude")
    print()
    print("🎯 调用BMAD子代理:")
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
    print("4. 工作流程:")
    print("   /task .bmad-docs-generator/workflows/enhanced-docs-generation.yaml")
    print()
    print("5. 查看配置:")
    print("   /read .bmad-docs-generator/config.yaml")
    print("=" * 50)

    print("\n💡 如果子代理仍然不可见:")
    print("1. 重启Claude Code")
    print("2. 确保在项目根目录启动")
    print("3. 检查Claude Code版本")
    print("4. 查看错误信息")

    return True

if __name__ == "__main__":
    success = final_verification()
    if success:
        print("\n✅ BMAD子代理配置验证成功!")
        print("现在可以在Claude Code中调用BMAD子代理了。")
    else:
        print("\n❌ BMAD子代理配置验证失败!")
        print("请检查配置并重新安装。")
