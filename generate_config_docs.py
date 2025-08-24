#!/usr/bin/env python3
"""
使用 BMAD 文档生成器和 Claude Code SDK 生成 config 目录的文档
确保分析实际内容而不是生成默认字符串
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class ConfigDocGenerator:
    """Config 目录文档生成器"""

    def __init__(self):
        self.bmad_path = os.path.join(os.path.dirname(__file__), '.bmad-docs-generator')
        self.output_dir = Path("generated_docs")
        self.output_dir.mkdir(exist_ok=True)

        # 专门针对 config 目录的文档类型
        self.doc_types = [
            {
                'type': 'config_analysis',
                'title': '配置分析文档',
                'description': '深度分析配置文件结构和内容',
                'bmad_team': 'enhanced-docs-generation-team',
                'bmad_workflow': 'enhanced-docs-generation'
            },
            {
                'type': 'config_architecture',
                'title': '配置架构文档',
                'description': '配置文件架构和设计模式分析',
                'bmad_team': 'enhanced-docs-generation-team',
                'bmad_workflow': 'enhanced-docs-generation'
            },
            {
                'type': 'config_guide',
                'title': '配置指南文档',
                'description': '配置文件使用指南和最佳实践',
                'bmad_team': 'docs-generation-team',
                'bmad_workflow': 'docs-generation'
            }
        ]

    def setup_environment(self):
        """设置环境变量"""
        os.environ['BMAD_DOCS_PATH'] = self.bmad_path
        os.environ['CLAUDE_CODE_ENABLED'] = 'true'
        os.environ['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = '200000'  # 更高的 token 限制
        os.environ['PROJECT_PATH'] = os.path.dirname(__file__)

        print(f"✅ 环境变量设置完成")
        print(f"   BMAD 路径: {self.bmad_path}")
        print(f"   输出 Token 限制: {os.environ.get('CLAUDE_CODE_MAX_OUTPUT_TOKENS', 'N/A')}")

    def analyze_config_directory(self, config_path: str) -> Dict[str, Any]:
        """分析 config 目录的内容"""
        config_info = {
            'path': config_path,
            'files': [],
            'total_size': 0,
            'file_types': {},
            'content_summary': {}
        }

        try:
            config_dir = Path(config_path)
            if not config_dir.exists():
                print(f"❌ Config 目录不存在: {config_path}")
                return config_info

            print(f"🔍 分析 config 目录: {config_path}")

            for file_path in config_dir.rglob('*'):
                if file_path.is_file():
                    file_info = {
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'extension': file_path.suffix,
                        'relative_path': str(file_path.relative_to(config_dir))
                    }

                    # 读取文件内容的前几行作为摘要
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[:10]  # 读取前10行
                            file_info['content_preview'] = ''.join(lines)
                    except Exception as e:
                        file_info['content_preview'] = f"无法读取文件内容: {str(e)}"

                    config_info['files'].append(file_info)
                    config_info['total_size'] += file_info['size']

                    # 统计文件类型
                    ext = file_info['extension']
                    config_info['file_types'][ext] = config_info['file_types'].get(ext, 0) + 1

            print(f"📊 Config 目录分析结果:")
            print(f"   - 文件数量: {len(config_info['files'])}")
            print(f"   - 总大小: {config_info['total_size']} 字节")
            print(f"   - 文件类型: {config_info['file_types']}")

            return config_info

        except Exception as e:
            print(f"❌ 分析 config 目录时发生错误: {str(e)}")
            return config_info

    async def generate_single_document(self, doc_config: Dict[str, Any], config_path: str, config_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成单个文档"""
        try:
            from app import create_app
            from app.services.claude_code_service import ClaudeCodeService

            app = create_app()
            with app.app_context():
                print(f"\n🔄 正在生成 {doc_config['title']}...")
                print(f"📁 分析目录: {config_path}")

                # 初始化 Claude Code 服务
                claude_service = ClaudeCodeService(bmad_docs_path=self.bmad_path)
                print(f"✅ Claude Code 服务初始化完成")

                # 设置文档参数
                doc_title = f"CoderWiki {doc_config['title']} - {datetime.now().strftime('%Y-%m-%d')}"

                # 将 config 信息添加到参数中
                additional_params = {
                    'language': 'zh-CN',
                    'format': 'markdown',
                    'detailed': True,
                    'include_examples': True,
                    'comprehensive': True,
                    'bmad_agent_team': doc_config['bmad_team'],
                    'bmad_workflow': doc_config['bmad_workflow'],
                    'use_claude_code_sdk': True,
                    'force_sdk_generation': True,
                    'analyze_actual_code': True,
                    'skip_default_content': True,
                    'focus_on_project_structure': True,
                    'config_directory_info': config_info,  # 添加 config 目录信息
                    'config_files_count': len(config_info['files']),
                    'config_file_types': config_info['file_types'],
                    'config_total_size': config_info['total_size']
                }

                print(f"🔧 文档参数:")
                print(f"   - 文档类型: {doc_config['type']}")
                print(f"   - 文档标题: {doc_title}")
                print(f"   - BMAD 团队: {doc_config['bmad_team']}")
                print(f"   - BMAD 工作流: {doc_config['bmad_workflow']}")
                print(f"   - Config 文件数量: {len(config_info['files'])}")
                print(f"   - Config 文件类型: {config_info['file_types']}")

                # 生成文档 - 确保调用 Claude Code SDK
                print(f"🚀 开始调用 Claude Code SDK...")
                result = await claude_service.generate_technical_document(
                    repository_path=config_path,
                    doc_type=doc_config['type'],
                    doc_title=doc_title,
                    additional_params=additional_params
                )

                if result['success']:
                    # 保存文档
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"coderwiki_{doc_config['type']}_{timestamp}.md"
                    output_path = self.output_dir / filename

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result['content'])

                    print(f"✅ {doc_config['title']} 生成成功!")
                    print(f"📄 保存到: {output_path}")

                    return {
                        'success': True,
                        'doc_type': doc_config['type'],
                        'title': doc_config['title'],
                        'file_path': str(output_path),
                        'metrics': result.get('metrics', {}),
                        'cost_estimate': result.get('cost_estimate', 0)
                    }
                else:
                    print(f"❌ {doc_config['title']} 生成失败: {result.get('error', '未知错误')}")
                    return {
                        'success': False,
                        'doc_type': doc_config['type'],
                        'title': doc_config['title'],
                        'error': result.get('error', '未知错误')
                    }

        except Exception as e:
            print(f"❌ 生成 {doc_config['title']} 时发生错误: {str(e)}")
            return {
                'success': False,
                'doc_type': doc_config['type'],
                'title': doc_config['title'],
                'error': str(e)
            }

    async def generate_all_documents(self) -> List[Dict[str, Any]]:
        """生成所有类型的文档"""
        config_path = "/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/config"
        results = []

        print(f"\n📝 开始生成 {len(self.doc_types)} 种类型的 config 文档...")
        print(f"📁 分析路径: {config_path}")

        # 首先分析 config 目录
        config_info = self.analyze_config_directory(config_path)

        for i, doc_config in enumerate(self.doc_types, 1):
            print(f"\n{'='*60}")
            print(f"文档 {i}/{len(self.doc_types)}: {doc_config['title']}")
            print(f"描述: {doc_config['description']}")
            print(f"BMAD 团队: {doc_config['bmad_team']}")
            print(f"BMAD 工作流: {doc_config['bmad_workflow']}")
            print(f"{'='*60}")

            result = await self.generate_single_document(doc_config, config_path, config_info)
            results.append(result)

            # 添加延迟避免 API 限制
            if i < len(self.doc_types):
                print("⏳ 等待 5 秒后继续下一个文档...")
                await asyncio.sleep(5)

        return results

    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """生成总结报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"config_documentation_summary_{timestamp}.md"

        successful_docs = [r for r in results if r['success']]
        failed_docs = [r for r in results if not r['success']]

        total_cost = sum(r.get('cost_estimate', 0) for r in successful_docs)

        report_content = f"""# CoderWiki Config 目录文档生成总结报告

## 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 生成统计
- 总文档数: {len(results)}
- 成功生成: {len(successful_docs)}
- 生成失败: {len(failed_docs)}
- 成功率: {len(successful_docs)/len(results)*100:.1f}%
- 总成本估算: ${total_cost:.4f}

## 成功生成的文档

"""

        for doc in successful_docs:
            report_content += f"""### {doc['title']}
- 文件路径: `{doc['file_path']}`
- 成本估算: ${doc.get('cost_estimate', 0):.4f}
- 生成时间: {doc.get('metrics', {}).get('generation_time', 'N/A')} 秒

"""

        if failed_docs:
            report_content += "## 生成失败的文档\n\n"
            for doc in failed_docs:
                report_content += f"""### {doc['title']}
- 错误信息: {doc.get('error', '未知错误')}

"""

        report_content += f"""
## 技术栈信息
- BMAD 文档生成器: {self.bmad_path}
- Claude Code SDK: 已集成
- 输出 Token 限制: {os.environ.get('CLAUDE_CODE_MAX_OUTPUT_TOKENS', 'N/A')}
- 分析目录: /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/config

## 文档目录结构
```
generated_docs/
├── coderwiki_config_analysis_*.md      # 配置分析文档
├── coderwiki_config_architecture_*.md  # 配置架构文档
├── coderwiki_config_guide_*.md         # 配置指南文档
└── config_documentation_summary_*.md   # 本总结报告
```

---
*本报告由 BMAD 文档生成器自动生成*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n📊 总结报告已生成: {report_path}")
        return report_path

async def main():
    """主函数"""
    print("=" * 80)
    print("BMAD Config 目录文档生成器 - Claude Code SDK 模式")
    print("=" * 80)

    generator = ConfigDocGenerator()

    # 设置环境
    generator.setup_environment()

    # 生成所有文档
    results = await generator.generate_all_documents()

    # 生成总结报告
    report_path = generator.generate_summary_report(results)

    # 显示最终结果
    successful_count = len([r for r in results if r['success']])
    total_count = len(results)

    print(f"\n{'='*80}")
    print("🎉 Config 目录文档生成完成!")
    print(f"{'='*80}")
    print(f"✅ 成功生成: {successful_count}/{total_count} 个文档")
    print(f"📁 文档保存在: {generator.output_dir}")
    print(f"📊 总结报告: {report_path}")

    if successful_count == total_count:
        print("🎯 所有文档生成成功!")
    else:
        print(f"⚠️  有 {total_count - successful_count} 个文档生成失败，请检查错误信息")

    return successful_count == total_count

if __name__ == "__main__":
    # 运行主函数
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
