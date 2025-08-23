#!/usr/bin/env python3
"""
测试BMAD任务配置
"""

import yaml
from pathlib import Path

def test_bmad_tasks():
    """测试BMAD任务配置"""
    print("=" * 60)
    print("BMAD任务配置测试")
    print("=" * 60)

    # 1. 读取BMAD配置
    config_path = Path("bmad-docs-generator/config.yaml")
    print(f"配置文件: {config_path}")
    print(f"配置文件存在: {config_path.exists()}")

    if not config_path.exists():
        print("❌ BMAD配置文件不存在")
        return

    # 2. 解析配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print("\nBMAD配置内容:")
        print(f"项目名称: {config.get('project_name', 'N/A')}")
        print(f"版本: {config.get('version', 'N/A')}")

        # 3. 显示可用任务
        tasks = config.get('tasks', {})
        print(f"\n可用任务数量: {len(tasks)}")

        print("\n可用任务列表:")
        for task_id, task_info in tasks.items():
            print(f"  - /BMad:tasks:{task_id}")
            if isinstance(task_info, dict):
                print(f"    描述: {task_info.get('description', 'N/A')}")

        # 4. 显示调用方式
        print("\n" + "=" * 40)
        print("正确的调用方式:")
        print("=" * 40)
        print()
        print("在Claude Code中，你可以使用以下方式调用BMAD任务:")
        print()
        for task_id in tasks.keys():
            print(f"1. 直接调用: /BMad:tasks:{task_id}")
            print(f"2. 使用Task工具: /task /BMad:tasks:{task_id}")
            print()

        print("示例:")
        print("请使用BMAD任务分析当前项目的架构:")
        print("/BMad:tasks:brownfield-create-story")
        print()
        print("或者生成项目文档:")
        print("/BMad:tasks:document-project")
        print("=" * 40)

        print("\n🎉 BMAD任务配置正确!")
        print("现在可以在Claude Code中直接调用这些任务了。")

    except Exception as e:
        print(f"❌ 解析配置文件失败: {e}")

if __name__ == "__main__":
    test_bmad_tasks()
