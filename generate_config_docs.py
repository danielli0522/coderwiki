#!/usr/bin/env python3
"""
使用BMAD文档生成器生成Config项目技术文档
"""

import os
import json
from pathlib import Path

def generate_config_documentation():
    """生成Config项目技术文档"""
    print("🚀 使用BMAD文档生成器生成Config项目技术文档")
    print("=" * 70)

    # 1. 项目信息
    print("\n📋 项目信息:")
    project_name = "Config"
    project_description = "配置管理系统，支持多种配置格式和环境管理"
    project_root = Path.cwd()

    print(f"  项目名称: {project_name}")
    print(f"  项目描述: {project_description}")
    print(f"  项目根目录: {project_root}")

    # 2. 检查BMAD子代理配置
    print("\n🔧 检查BMAD子代理配置:")
    agents_dir = Path(".claude/agents")
    if agents_dir.exists():
        agent_files = list(agents_dir.glob("*.md"))
        print(f"  ✅ 发现 {len(agent_files)} 个BMAD子代理:")
        for agent_file in agent_files:
            print(f"    - {agent_file.stem}")
    else:
        print("  ❌ BMAD子代理目录不存在")
        return

    # 3. 项目结构分析
    print("\n📁 项目结构分析:")
    key_directories = [
        "backend",
        "frontend",
        "config",
        "database",
        "docs",
        "bmad-docs-generator"
    ]

    for directory in key_directories:
        if Path(directory).exists():
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ - 不存在")

    # 4. 技术栈分析
    print("\n🛠️  技术栈分析:")
    tech_stack = {
        "后端": ["Python", "Flask", "SQLAlchemy", "MySQL"],
        "前端": ["HTML", "CSS", "JavaScript", "Bootstrap"],
        "配置管理": ["YAML", "JSON", "环境变量"],
        "文档生成": ["BMAD-Method", "Markdown", "Mermaid"],
        "开发工具": ["Claude Code", "Git", "Docker"]
    }

    for category, technologies in tech_stack.items():
        print(f"  {category}: {', '.join(technologies)}")

    # 5. 文档生成计划
    print("\n📝 文档生成计划:")
    documentation_plan = [
        "1. 项目概述和技术架构",
        "2. 代码库结构和组织",
        "3. 配置管理系统设计",
        "4. API接口文档",
        "5. 数据库设计文档",
        "6. 部署和运维指南",
        "7. 开发指南和最佳实践"
    ]

    for item in documentation_plan:
        print(f"  {item}")

    # 6. BMAD子代理调用指南
    print("\n🎯 BMAD子代理调用指南:")
    print("=" * 50)
    print()
    print("在Claude Code中使用以下命令生成Config项目文档:")
    print()
    print("1. 启动Claude Code:")
    print("   cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki")
    print("   claude")
    print()
    print("2. 调用BMAD文档团队:")
    print("   请BMAD文档团队为Config项目生成完整的技术文档，包括：")
    print("   - 项目架构分析")
    print("   - 技术栈评估")
    print("   - 代码结构分析")
    print("   - 配置管理系统设计")
    print("   - API接口文档")
    print("   - 数据库设计文档")
    print("   - 部署和运维指南")
    print()
    print("3. 或者调用特定子代理:")
    print("   让代码分析专家分析Config项目的代码结构和组织")
    print("   请技术架构专家评估Config项目的系统架构")
    print("   让流程分析专家分析Config项目的配置管理流程")
    print("   请问题诊断专家分析Config项目的潜在问题")
    print("   让文档工程师为Config项目创建技术文档")
    print()
    print("4. 查看所有可用子代理:")
    print("   /agents")
    print("=" * 50)

    # 7. 预期输出
    print("\n📊 预期文档输出:")
    expected_outputs = [
        "Config项目技术概述.md",
        "Config项目架构设计.md",
        "Config项目代码分析报告.md",
        "Config项目API文档.md",
        "Config项目数据库设计.md",
        "Config项目部署指南.md",
        "Config项目开发指南.md"
    ]

    for output in expected_outputs:
        print(f"  📄 {output}")

    print("\n" + "=" * 70)
    print("🎉 BMAD文档生成器已准备就绪!")
    print("现在可以在Claude Code中调用BMAD子代理生成Config项目技术文档。")
    print("=" * 70)

def show_bmad_workflow():
    """显示BMAD工作流程"""
    print("\n🔄 BMAD-Method工作流程:")
    print("-" * 40)

    workflow_steps = [
        "1. 代码分析阶段 - 扫描代码库结构和模式",
        "2. 架构分析阶段 - 评估系统架构和技术选择",
        "3. 流程分析阶段 - 分析工作流程和过程",
        "4. 问题诊断阶段 - 识别潜在问题和解决方案",
        "5. 文档生成阶段 - 创建综合技术文档"
    ]

    for step in workflow_steps:
        print(f"  {step}")

    print("\n💡 每个阶段都由专门的BMAD子代理执行，确保专业性和完整性。")

if __name__ == "__main__":
    generate_config_documentation()
    show_bmad_workflow()
