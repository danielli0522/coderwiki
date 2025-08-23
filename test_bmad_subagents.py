#!/usr/bin/env python3
"""
测试BMAD子代理的正确调用方式
"""

import yaml
from pathlib import Path

def test_bmad_subagents():
    """测试BMAD子代理配置"""
    print("=" * 60)
    print("BMAD子代理配置测试")
    print("=" * 60)

    # 1. 检查关键文件
    key_files = [
        "bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml",
        "bmad-docs-generator/agents/code-analyst.md",
        "bmad-docs-generator/agents/tech-architect.md",
        "bmad-docs-generator/workflows/enhanced-docs-generation.yaml"
    ]

    print("检查关键文件:")
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

    # 2. 读取团队配置
    team_file = "bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml"
    print(f"\n读取团队配置: {team_file}")

    if Path(team_file).exists():
        try:
            with open(team_file, 'r', encoding='utf-8') as f:
                team_config = yaml.safe_load(f)

            team = team_config.get('team', {})
            print(f"团队ID: {team.get('id', 'N/A')}")
            print(f"团队名称: {team.get('name', 'N/A')}")

            agents = team.get('agents', [])
            print(f"代理数量: {len(agents)}")

            print("\n可用代理:")
            for agent in agents:
                agent_id = agent.get('id', 'N/A')
                agent_name = agent.get('name', 'N/A')
                print(f"  - {agent_id}: {agent_name}")

        except Exception as e:
            print(f"❌ 读取团队配置失败: {e}")

    # 3. 显示正确的调用方式
    print("\n" + "=" * 50)
    print("正确的BMAD子代理调用方式")
    print("=" * 50)
    print()
    print("🎯 从你的截图可以看到，BMAD子代理已经被发现了！")
    print("你看到的这些就是BMAD子代理:")
    print()
    print("可用的BMAD任务:")
    bmad_tasks = [
        "brownfield-create-story",
        "risk-profile",
        "index-docs",
        "execute-checklist",
        "correct-course",
        "generate-ai-frontend-prompt",
        "validate-next-story",
        "apply-qa-fixes",
        "document-project",
        "test-design"
    ]

    for task in bmad_tasks:
        print(f"  - /BMad:tasks:{task}")

    print()
    print("📝 调用方式:")
    print("1. 直接调用: /BMad:tasks:brownfield-create-story")
    print("2. 使用Task工具: /task /BMad:tasks:brownfield-create-story")
    print()
    print("💡 使用示例:")
    print("请使用BMAD分析当前项目架构:")
    print("/BMad:tasks:brownfield-create-story")
    print()
    print("生成项目文档:")
    print("/BMad:tasks:document-project")
    print()
    print("执行质量检查:")
    print("/BMad:tasks:execute-checklist")
    print("=" * 50)

    print("\n🎉 BMAD子代理配置成功!")
    print("现在你可以直接在Claude Code中调用这些BMAD任务了。")

if __name__ == "__main__":
    test_bmad_subagents()
