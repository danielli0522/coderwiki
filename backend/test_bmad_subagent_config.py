#!/usr/bin/env python3
"""
BMAD子代理配置测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.claude_code_service import ClaudeCodeService
from app.services.bmad_subagent_config import BMADSubagentConfig

def test_bmad_config():
    """测试BMAD配置"""
    print("=" * 60)
    print("BMAD子代理配置测试")
    print("=" * 60)

    # 测试BMAD配置类
    print("\n1. 测试BMAD配置类...")
    bmad_config = BMADSubagentConfig()

    # 验证配置
    validation = bmad_config.validate_configuration()
    print(f"配置验证结果: {'成功' if validation['success'] else '失败'}")

    if not validation['success']:
        print("错误:")
        for error in validation['errors']:
            print(f"  - {error}")

    if validation['warnings']:
        print("警告:")
        for warning in validation['warnings']:
            print(f"  - {warning}")

    # 获取团队信息
    teams = bmad_config.get_subagent_teams()
    print(f"\n可用团队数量: {len(teams)}")
    for team in teams:
        print(f"  - {team['name']} ({team['id']})")
        print(f"    路径: {team['path']}")
        print(f"    代理: {', '.join(team['agents'])}")

    # 获取代理信息
    agents = bmad_config.get_subagent_agents()
    print(f"\n可用代理数量: {len(agents)}")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['role']})")
        print(f"    路径: {agent['path']}")
        print(f"    能力: {', '.join(agent['capabilities'][:3])}...")

    # 获取调用指令
    instructions = bmad_config.get_subagent_call_instructions()
    print(f"\n调用指令长度: {len(instructions)} 字符")

def test_claude_code_service():
    """测试Claude Code服务"""
    print("\n" + "=" * 60)
    print("Claude Code服务测试")
    print("=" * 60)

    # 创建服务实例
    service = ClaudeCodeService()

    # 检查Claude Code SDK
    print("\n1. 检查Claude Code SDK...")
    sdk_check = service.check_claude_code_availability()
    print(f"SDK可用性: {'是' if sdk_check['available'] else '否'}")
    if not sdk_check['available']:
        print(f"错误: {sdk_check['error']}")

    # 检查BMAD文档生成器
    print("\n2. 检查BMAD文档生成器...")
    bmad_check = service.check_bmad_docs_generator()
    print(f"BMAD可用性: {'是' if bmad_check['available'] else '否'}")

    if bmad_check['available']:
        print(f"团队数量: {bmad_check['teams_count']}")
        print(f"代理数量: {bmad_check['agents_count']}")

        if bmad_check['warnings']:
            print("警告:")
            for warning in bmad_check['warnings']:
                print(f"  - {warning}")
    else:
        print(f"错误: {bmad_check['error']}")

    # 获取BMAD子代理信息
    print("\n3. 获取BMAD子代理信息...")
    subagent_info = service.get_bmad_subagent_info()
    if subagent_info['success']:
        print(f"配置路径: {subagent_info['config_path']}")
        print(f"团队数量: {subagent_info['teams_count']}")
        print(f"代理数量: {subagent_info['agents_count']}")
    else:
        print(f"错误: {subagent_info['error']}")

    # 获取工作流程配置
    print("\n4. 获取工作流程配置...")
    workflow_config = service.get_bmad_workflow_config()
    if workflow_config['success']:
        print(f"工作流程: {workflow_config['workflow_name']}")
        workflow = workflow_config['config']['workflow']
        print(f"版本: {workflow['version']}")
        print(f"阶段数量: {len(workflow['phases'])}")
    else:
        print(f"错误: {workflow_config['error']}")

    # 获取支持的文档类型
    print("\n5. 获取支持的文档类型...")
    doc_types = service.get_supported_doc_types()
    if doc_types['success']:
        print(f"文档类型数量: {len(doc_types['doc_types'])}")
        for doc_type in doc_types['doc_types']:
            print(f"  - {doc_type}")

def test_system_prompt():
    """测试系统提示词生成"""
    print("\n" + "=" * 60)
    print("系统提示词测试")
    print("=" * 60)

    service = ClaudeCodeService()

    # 生成系统提示词
    system_prompt = service._prepare_system_prompt(
        doc_type="technical_design",
        doc_title="测试技术设计文档",
        additional_params={"detailed": True}
    )

    print(f"系统提示词长度: {len(system_prompt)} 字符")
    print("\n系统提示词预览 (前500字符):")
    print("-" * 40)
    print(system_prompt[:500] + "...")
    print("-" * 40)

def main():
    """主函数"""
    try:
        test_bmad_config()
        test_claude_code_service()
        test_system_prompt()

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
