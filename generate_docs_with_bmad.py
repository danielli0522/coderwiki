#!/usr/bin/env python3
"""
使用 BMAD 文档生成器和 Claude Code SDK 生成文档
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def setup_environment():
    """设置环境变量"""
    # BMAD 文档生成器路径
    bmad_path = os.path.join(os.path.dirname(__file__), '.bmad-docs-generator')
    os.environ['BMAD_DOCS_PATH'] = bmad_path

    # Claude Code 配置
    os.environ['CLAUDE_CODE_ENABLED'] = 'true'

    # 项目路径
    project_path = os.path.dirname(__file__)
    os.environ['PROJECT_PATH'] = project_path

    print(f"✅ 环境变量设置完成")
    print(f"   BMAD 路径: {bmad_path}")
    print(f"   项目路径: {project_path}")

    return bmad_path

async def generate_documentation(bmad_path: str):
    """生成文档"""
    try:
        from app import create_app
        from app.services.claude_code_service import ClaudeCodeService
        from app.services.document_generator import DocumentGenerator

        # 创建应用上下文
        app = create_app()
        with app.app_context():
            print("🚀 开始生成文档...")

            # 初始化 Claude Code 服务，传入正确的 BMAD 路径
            claude_service = ClaudeCodeService(bmad_docs_path=bmad_path)

            print("✅ Claude Code 服务初始化完成")

            # 设置文档生成参数
            repository_path = os.path.dirname(__file__)  # 当前项目路径
            doc_type = 'technical_design'
            doc_title = f"CoderWiki 技术设计文档 - {datetime.now().strftime('%Y-%m-%d')}"

            additional_params = {
                'language': 'zh-CN',
                'format': 'markdown',
                'detailed': True,
                'include_examples': True,
                'comprehensive': True,
                'bmad_agent_team': 'enhanced-docs-generation-team',
                'bmad_workflow': 'enhanced-docs-generation'
            }

            print(f"📝 生成文档参数:")
            print(f"   仓库路径: {repository_path}")
            print(f"   文档类型: {doc_type}")
            print(f"   文档标题: {doc_title}")
            print(f"   BMAD 团队: {additional_params['bmad_agent_team']}")
            print(f"   BMAD 工作流: {additional_params['bmad_workflow']}")

            # 生成文档
            print("\n🔄 正在生成文档...")
            result = await claude_service.generate_technical_document(
                repository_path=repository_path,
                doc_type=doc_type,
                doc_title=doc_title,
                additional_params=additional_params
            )

            if result['success']:
                print("✅ 文档生成成功!")

                # 保存文档
                output_dir = Path("generated_docs")
                output_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"coderwiki_technical_design_{timestamp}.md"
                output_path = output_dir / filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])

                print(f"📄 文档已保存到: {output_path}")

                # 显示生成统计
                if 'metrics' in result:
                    metrics = result['metrics']
                    print(f"\n📊 生成统计:")
                    print(f"   生成时间: {metrics.get('generation_time', 'N/A')} 秒")
                    print(f"   成本估算: {metrics.get('cost_estimate', 'N/A')}")
                    print(f"   使用的 Token: {metrics.get('tokens_used', 'N/A')}")

                return True
            else:
                print(f"❌ 文档生成失败: {result.get('error', '未知错误')}")
                return False

    except Exception as e:
        print(f"❌ 生成文档时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_bmad_configuration():
    """检查 BMAD 配置"""
    print("🔍 检查 BMAD 配置...")

    # 检查 BMAD 文档生成器路径
    bmad_path = Path(".bmad-docs-generator")
    if not bmad_path.exists():
        print(f"❌ BMAD 文档生成器路径不存在: {bmad_path}")
        return False

    print(f"✅ BMAD 文档生成器路径存在: {bmad_path}")

    # 检查配置文件
    config_file = bmad_path / "config.yaml"
    if not config_file.exists():
        print(f"❌ BMAD 配置文件不存在: {config_file}")
        return False

    print(f"✅ BMAD 配置文件存在: {config_file}")

    # 检查工作流
    workflows_dir = bmad_path / "workflows"
    if not workflows_dir.exists():
        print(f"❌ BMAD 工作流目录不存在: {workflows_dir}")
        return False

    print(f"✅ BMAD 工作流目录存在: {workflows_dir}")

    # 检查代理团队
    teams_dir = bmad_path / "agent-teams"
    if not teams_dir.exists():
        print(f"❌ BMAD 代理团队目录不存在: {teams_dir}")
        return False

    print(f"✅ BMAD 代理团队目录存在: {teams_dir}")

    return True

def check_claude_code_configuration():
    """检查 Claude Code 配置"""
    print("🔍 检查 Claude Code 配置...")

    try:
        # 检查环境变量
        claude_enabled = os.environ.get('CLAUDE_CODE_ENABLED', 'false').lower() == 'true'
        if not claude_enabled:
            print("⚠️  Claude Code 未启用，请设置 CLAUDE_CODE_ENABLED=true")
            return False

        print("✅ Claude Code 已启用")

        # 检查 Claude Code SDK
        try:
            import claude_code_sdk
            print("✅ Claude Code SDK 已安装")
        except ImportError:
            print("❌ Claude Code SDK 未安装，请运行: pip install claude-code-sdk")
            return False

        return True

    except Exception as e:
        print(f"❌ 检查 Claude Code 配置时发生错误: {str(e)}")
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("BMAD 文档生成器 - Claude Code SDK 模式")
    print("=" * 60)

    # 设置环境
    bmad_path = setup_environment()

    # 检查配置
    if not check_bmad_configuration():
        print("❌ BMAD 配置检查失败")
        return False

    if not check_claude_code_configuration():
        print("❌ Claude Code 配置检查失败")
        return False

    print("\n" + "=" * 60)
    print("开始生成文档...")
    print("=" * 60)

    # 生成文档
    success = await generate_documentation(bmad_path)

    if success:
        print("\n🎉 文档生成完成!")
        print("📁 生成的文档保存在 generated_docs/ 目录中")
    else:
        print("\n❌ 文档生成失败")

    return success

if __name__ == "__main__":
    # 运行主函数
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
