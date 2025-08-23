#!/usr/bin/env python3
"""
文档生成器集成测试
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_document_generator():
    """测试文档生成器集成"""
    print("=== 测试文档生成器集成 ===")

    try:
        # 导入文档生成器
        from app.services.document_generator import DocumentGenerator

        # 创建文档生成器实例
        doc_generator = DocumentGenerator(use_claude_code=True)

        print("✅ 文档生成器创建成功")
        print(f"使用Claude Code: {doc_generator.use_claude_code}")
        print(f"使用MCP: {doc_generator.use_mcp}")

        # 测试Claude Code服务状态
        claude_status = doc_generator.check_claude_code_service_status()
        print(f"Claude Code服务状态: {claude_status}")

        # 测试MCP服务状态
        mcp_status = doc_generator.check_mcp_service_status()
        print(f"MCP服务状态: {mcp_status}")

        # 测试获取文档类型
        doc_types = doc_generator.get_available_doc_types()
        print(f"可用文档类型: {doc_types}")

        # 测试文档生成（模拟）
        print("\n开始测试文档生成...")

        # 创建一个模拟的仓库对象
        class MockRepository:
            def __init__(self, path):
                self.local_path = path
                self.name = "test-repo"
                self.id = 1

        # 创建一个模拟的LLM配置对象
        class MockLLMConfig:
            def __init__(self):
                self.id = 1
                self.max_tokens = 4000
                self.temperature = 0.7

        # 创建一个模拟的任务服务
        class MockTaskService:
            def create_task(self, user_id, task_type, repository_id, status, metadata):
                class MockTask:
                    def __init__(self):
                        self.id = 1
                return MockTask()

            def update_task_status(self, task_id, status, message):
                print(f"任务状态更新: {task_id} -> {status}: {message}")

        # 替换任务服务
        doc_generator.task_service = MockTaskService()

        # 测试文档生成
        test_repo = MockRepository(os.path.dirname(os.path.abspath(__file__)))
        test_llm_config = MockLLMConfig()

        result = doc_generator.generate_document(
            repository_id=1,
            user_id=1,
            llm_config_id=1,
            doc_type='technical_design',
            doc_title='集成测试技术设计文档'
        )

        print(f"文档生成结果: {result}")

        if result.get('success'):
            print("✅ 文档生成成功！")
            print(f"文档ID: {result.get('document_id')}")
            print(f"任务ID: {result.get('task_id')}")

            if 'document' in result:
                doc = result['document']
                print(f"文档标题: {doc.get('title')}")
                print(f"文档状态: {doc.get('status')}")
                print(f"文档内容长度: {len(doc.get('content', ''))} 字符")

            if 'generation_stats' in result:
                stats = result['generation_stats']
                print(f"生成时间: {stats.get('generation_time', 0):.2f} 秒")
                print(f"成本估算: ${stats.get('cost_estimate', 0):.4f}")
                print(f"Token使用量: {stats.get('tokens_used', 0)}")
        else:
            print("❌ 文档生成失败")
            print(f"错误: {result.get('error', 'Unknown error')}")

        return result.get('success', False)

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("文档生成器集成测试")
    print("=" * 50)

    # 设置环境变量
    os.environ['CLAUDE_CODE_ENABLED'] = 'true'
    os.environ['BMAD_DOCS_PATH'] = '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/'

    print(f"CLAUDE_CODE_ENABLED: {os.environ.get('CLAUDE_CODE_ENABLED')}")
    print(f"BMAD_DOCS_PATH: {os.environ.get('BMAD_DOCS_PATH')}")
    print()

    # 运行测试
    success = await test_document_generator()

    print("\n" + "=" * 50)
    if success:
        print("🎉 文档生成器集成测试成功！")
    else:
        print("⚠️  文档生成器集成测试失败")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
