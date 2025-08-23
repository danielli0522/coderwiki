#!/usr/bin/env python3
"""
简化的Claude Code测试
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_claude_code_simple():
    """简化的Claude Code测试"""
    print("=== 简化Claude Code测试 ===")
    
    try:
        # 导入Claude Code服务
        from app.services.claude_code_service import ClaudeCodeService
        
        # 创建服务实例
        service = ClaudeCodeService()
        
        print("✅ Claude Code服务创建成功")
        
        # 测试SDK可用性
        availability = service.check_claude_code_availability()
        print(f"SDK可用性: {availability['success']}")
        
        # 测试BMAD文档生成器
        bmad_status = service.check_bmad_docs_generator()
        print(f"BMAD文档生成器状态: {bmad_status['success']}")
        
        # 测试支持的文档类型
        doc_types = service.get_supported_doc_types()
        print(f"支持的文档类型: {len(doc_types.get('doc_types', []))} 个")
        
        # 测试文档生成（使用当前目录作为测试仓库）
        test_repo_path = os.path.dirname(os.path.abspath(__file__))
        print(f"测试仓库路径: {test_repo_path}")
        
        print("\n开始生成测试文档...")
        result = await service.generate_technical_document(
            repository_path=test_repo_path,
            doc_type='technical_design',
            doc_title='简化测试技术设计文档',
            additional_params={
                'detailed': True,
                'include_examples': True
            }
        )
        
        if result['success']:
            print("✅ 文档生成成功！")
            print(f"文档长度: {len(result.get('content', ''))} 字符")
            print(f"生成时间: {result.get('generation_time', 0):.2f} 秒")
            print(f"成本估算: ${result.get('cost_estimate', 0):.4f}")
            
            # 保存生成的文档
            output_file = "simple_test_document.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.get('content', ''))
            print(f"文档已保存到: {output_file}")
            
            # 显示文档前500字符
            content = result.get('content', '')
            if len(content) > 500:
                print(f"文档预览:\n{content[:500]}...")
            else:
                print(f"文档内容:\n{content}")
        else:
            print("❌ 文档生成失败")
            print(f"错误: {result.get('error', 'Unknown error')}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("简化Claude Code测试")
    print("=" * 50)
    
    # 设置环境变量
    os.environ['CLAUDE_CODE_ENABLED'] = 'true'
    os.environ['BMAD_DOCS_PATH'] = '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/'
    
    print(f"CLAUDE_CODE_ENABLED: {os.environ.get('CLAUDE_CODE_ENABLED')}")
    print(f"BMAD_DOCS_PATH: {os.environ.get('BMAD_DOCS_PATH')}")
    print()
    
    # 运行测试
    success = await test_claude_code_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 简化Claude Code测试成功！")
    else:
        print("⚠️  简化Claude Code测试失败")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
