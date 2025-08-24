#!/usr/bin/env python3
"""
技术架构文档生成器
使用 bmad-docs-generator 和 Claude Code SDK 生成技术架构文档
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入Claude Code服务
from backend.app.services.claude_code_service import ClaudeCodeService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('technical_architecture_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TechnicalArchitectureDocGenerator:
    """技术架构文档生成器"""

    def __init__(self, project_path: str = None, bmad_docs_path: str = None):
        """
        初始化文档生成器

        Args:
            project_path: 项目路径，默认为当前目录
            bmad_docs_path: BMAD文档生成器路径
        """
        self.project_path = project_path or str(project_root)
        self.bmad_docs_path = bmad_docs_path or "bmad-docs-generator"

        # 初始化Claude Code服务
        self.claude_service = ClaudeCodeService(bmad_docs_path=self.bmad_docs_path)

        # 输出目录
        self.output_dir = Path(self.project_path) / "generated_docs"
        self.output_dir.mkdir(exist_ok=True)

        logger.info(f"初始化技术架构文档生成器")
        logger.info(f"项目路径: {self.project_path}")
        logger.info(f"BMAD文档生成器路径: {self.bmad_docs_path}")
        logger.info(f"输出目录: {self.output_dir}")

    async def generate_technical_architecture_doc(self,
                                                 doc_title: str = None,
                                                 include_diagrams: bool = True,
                                                 comprehensive: bool = True) -> Dict[str, Any]:
        """
        生成技术架构文档

        Args:
            doc_title: 文档标题
            include_diagrams: 是否包含架构图
            comprehensive: 是否生成全面文档

        Returns:
            生成结果字典
        """
        try:
            # 生成文档标题
            if not doc_title:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                doc_title = f"CoderWiki_Technical_Architecture_{timestamp}"

            logger.info(f"开始生成技术架构文档: {doc_title}")

            # 准备额外参数
            additional_params = {
                'comprehensive': comprehensive,
                'include_diagrams': include_diagrams,
                'doc_type': 'technical_architecture',
                'project_name': 'CoderWiki',
                'architecture_focus': True
            }

            # 调用Claude Code服务生成文档
            result = await self.claude_service.generate_technical_document(
                repository_path=self.project_path,
                doc_type='technical_architecture',
                doc_title=doc_title,
                additional_params=additional_params
            )

            if result['success']:
                # 保存生成的文档
                doc_filename = f"{doc_title}.md"
                doc_path = self.output_dir / doc_filename

                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])

                # 保存元数据
                metadata_filename = f"{doc_title}_metadata.json"
                metadata_path = self.output_dir / metadata_filename

                metadata = {
                    'doc_title': doc_title,
                    'generation_time': result.get('generation_time', 0),
                    'metrics': result.get('metrics', {}),
                    'doc_path': str(doc_path),
                    'metadata_path': str(metadata_path),
                    'additional_params': additional_params,
                    'generated_at': datetime.now().isoformat()
                }

                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                logger.info(f"技术架构文档生成成功")
                logger.info(f"文档路径: {doc_path}")
                logger.info(f"元数据路径: {metadata_path}")
                logger.info(f"生成时间: {result.get('generation_time', 0):.2f}秒")

                return {
                    'success': True,
                    'doc_path': str(doc_path),
                    'metadata_path': str(metadata_path),
                    'content': result['content'],
                    'metrics': result.get('metrics', {}),
                    'generation_time': result.get('generation_time', 0)
                }
            else:
                logger.error(f"文档生成失败: {result.get('error', 'Unknown error')}")
                return result

        except Exception as e:
            logger.error(f"生成技术架构文档时发生错误: {str(e)}")
            return {
                'success': False,
                'error': f'Document generation error: {str(e)}',
                'error_type': 'generation_error'
            }

    async def generate_comprehensive_architecture_doc(self) -> Dict[str, Any]:
        """生成全面的技术架构文档"""
        logger.info("生成全面的技术架构文档")

        return await self.generate_technical_architecture_doc(
            doc_title="CoderWiki_Comprehensive_Technical_Architecture",
            include_diagrams=True,
            comprehensive=True
        )

    async def generate_summary_architecture_doc(self) -> Dict[str, Any]:
        """生成简洁的技术架构概览文档"""
        logger.info("生成简洁的技术架构概览文档")

        return await self.generate_technical_architecture_doc(
            doc_title="CoderWiki_Technical_Architecture_Summary",
            include_diagrams=False,
            comprehensive=False
        )

    def list_generated_docs(self) -> List[str]:
        """列出已生成的文档"""
        docs = []
        for file in self.output_dir.glob("*.md"):
            docs.append(file.name)
        return sorted(docs)

    def get_doc_content(self, doc_filename: str) -> Optional[str]:
        """获取指定文档的内容"""
        doc_path = self.output_dir / doc_filename
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

async def main():
    """主函数"""
    print("🚀 CoderWiki 技术架构文档生成器")
    print("=" * 50)

    # 初始化生成器
    generator = TechnicalArchitectureDocGenerator()

    # 生成全面的技术架构文档
    print("\n📋 生成全面的技术架构文档...")
    result = await generator.generate_comprehensive_architecture_doc()

    if result['success']:
        print(f"✅ 文档生成成功!")
        print(f"📄 文档路径: {result['doc_path']}")
        print(f"⏱️  生成时间: {result['generation_time']:.2f}秒")

        # 显示文档内容预览
        content = result['content']
        preview_lines = content.split('\n')[:20]
        print(f"\n📖 文档预览 (前20行):")
        print("-" * 40)
        for line in preview_lines:
            print(line)
        if len(content.split('\n')) > 20:
            print("...")
    else:
        print(f"❌ 文档生成失败: {result.get('error', 'Unknown error')}")

    # 列出所有生成的文档
    print(f"\n📚 已生成的文档列表:")
    docs = generator.list_generated_docs()
    for i, doc in enumerate(docs, 1):
        print(f"  {i}. {doc}")

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
