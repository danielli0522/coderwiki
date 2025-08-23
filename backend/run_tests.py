#!/usr/bin/env python3
"""
测试运行脚本
运行 Claude Code SDK 和 BMAD 代理集成的单元测试
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_tests(test_pattern=None, verbose=False):
    """运行测试"""
    # 设置测试目录
    test_dir = project_root / 'tests'

    if not test_dir.exists():
        print(f"测试目录不存在: {test_dir}")
        return False

    # 发现测试
    if test_pattern:
        # 运行特定测试
        loader = unittest.TestLoader()
        suite = loader.discover(str(test_dir), pattern=test_pattern)
    else:
        # 运行所有测试
        loader = unittest.TestLoader()
        suite = loader.discover(str(test_dir), pattern='test_*.py')

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    return result.wasSuccessful()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行 Claude Code SDK 和 BMAD 代理集成测试')
    parser.add_argument('--test', '-t', help='运行特定测试文件 (例如: test_claude_bmad_integration.py)')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--config-only', action='store_true', help='只运行 Config 文档生成测试')

    args = parser.parse_args()

    print("=" * 60)
    print("Claude Code SDK 和 BMAD 代理集成测试")
    print("=" * 60)

    # 检查环境
    print("检查测试环境...")

    # 检查必要的目录
    required_dirs = ['app', 'tests']
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"❌ 缺少必要目录: {dir_name}")
            return False
        else:
            print(f"✅ 找到目录: {dir_name}")

    # 检查 bmad-docs-generator 目录（在上级目录）
    bmad_dir = project_root.parent / 'bmad-docs-generator'
    if not bmad_dir.exists():
        print(f"❌ 缺少必要目录: bmad-docs-generator (在 {bmad_dir})")
        return False
    else:
        print(f"✅ 找到目录: bmad-docs-generator")

    # 检查必要的文件
    required_files = [
        'app/utils/claude_client.py',
        'app/utils/bmad_orchestrator.py',
        'app/services/smart_doc_service.py'
    ]

    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ 缺少必要文件: {file_path}")
            return False
        else:
            print(f"✅ 找到文件: {file_path}")

    print("\n开始运行测试...")

    # 确定要运行的测试
    if args.config_only:
        test_pattern = 'test_config_docs.py'
        print("运行 Config 文档生成测试...")
    elif args.test:
        test_pattern = args.test
        print(f"运行特定测试: {args.test}")
    else:
        test_pattern = None
        print("运行所有测试...")

    # 运行测试
    success = run_tests(test_pattern, args.verbose)

    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败!")
    print("=" * 60)

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
