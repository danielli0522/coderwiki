#!/usr/bin/env python3
"""
Claude 无头模式运行器使用示例

演示如何使用 ClaudeHeadlessRunner 进行各种自动化任务
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径以导入我们的模块
sys.path.insert(0, str(Path(__file__).parent))

from claude_headless_runner import ClaudeHeadlessRunner, ClaudeHeadlessOptions


def example_list_project_structure():
    """示例：列出项目目录结构"""
    print("🔍 示例1: 列出项目目录结构")
    print("-" * 50)

    options = ClaudeHeadlessOptions(
        prompt="请列出该项目目录结构，重点关注Python文件和配置文件",
        allowed_tools=["Bash", "Read"],
        permission_mode="acceptEdits",
        cwd=str(Path(__file__).parent),
        timeout=120
    )

    runner = ClaudeHeadlessRunner(options)
    result = runner.run()

    if result['success']:
        print("✅ 执行成功!")
        print(f"⏱️  执行时间: {result['execution_time']:.2f}秒")
        print("\n📋 结果:")
        print(result['output'])
    else:
        print("❌ 执行失败!")
        print(f"错误: {result['error']}")

    return result


def example_analyze_code_architecture():
    """示例：分析代码架构"""
    print("\n\n🏗️  示例2: 分析代码架构")
    print("-" * 50)

    options = ClaudeHeadlessOptions(
        prompt="""
        请分析这个项目的代码架构，包括：
        1. 主要模块和组件
        2. 依赖关系
        3. 设计模式的使用
        4. 改进建议

        重点分析backend目录下的Python代码。
        """,
        allowed_tools=["Read", "Grep", "Bash"],
        permission_mode="acceptEdits",
        cwd=str(Path(__file__).parent),
        timeout=300
    )

    runner = ClaudeHeadlessRunner(options)
    result = runner.run()

    if result['success']:
        print("✅ 执行成功!")
        print(f"⏱️  执行时间: {result['execution_time']:.2f}秒")
        print("\n📋 架构分析结果:")
        print(result['output'])
    else:
        print("❌ 执行失败!")
        print(f"错误: {result['error']}")

    return result


def example_generate_documentation():
    """示例：生成文档"""
    print("\n\n📚 示例3: 生成项目文档")
    print("-" * 50)

    options = ClaudeHeadlessOptions(
        prompt="""
        请为这个CoderWiki项目生成一份完整的技术文档，包括：
        1. 项目概述和功能介绍
        2. 技术栈说明
        3. 安装和配置指南
        4. API文档概览
        5. 开发者指南

        请基于实际代码内容生成，确保准确性。
        """,
        allowed_tools=["Read", "Write", "Grep"],
        permission_mode="acceptEdits",
        cwd=str(Path(__file__).parent),
        timeout=600,
        max_tokens=4000
    )

    runner = ClaudeHeadlessRunner(options)
    result = runner.run()

    if result['success']:
        print("✅ 执行成功!")
        print(f"⏱️  执行时间: {result['execution_time']:.2f}秒")
        print("\n📋 文档生成结果:")
        print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])
    else:
        print("❌ 执行失败!")
        print(f"错误: {result['error']}")

    return result


def example_debug_mode():
    """示例：调试模式运行"""
    print("\n\n🐛 示例4: 调试模式运行")
    print("-" * 50)

    options = ClaudeHeadlessOptions(
        prompt="请简要说明这个项目的主要功能",
        allowed_tools=["Read"],
        permission_mode="acceptEdits",
        cwd=str(Path(__file__).parent),
        timeout=60,
        debug=True  # 启用调试模式
    )

    runner = ClaudeHeadlessRunner(options)
    result = runner.run()

    if result['success']:
        print("✅ 执行成功!")
        print(f"⏱️  执行时间: {result['execution_time']:.2f}秒")
        print("\n📋 结果:")
        print(result['output'])
    else:
        print("❌ 执行失败!")
        print(f"错误: {result['error']}")

    return result


def example_custom_model():
    """示例：使用自定义模型"""
    print("\n\n🤖 示例5: 使用自定义模型和参数")
    print("-" * 50)

    options = ClaudeHeadlessOptions(
        prompt="请用一句话总结这个项目是做什么的",
        allowed_tools=["Read"],
        permission_mode="acceptEdits",
        cwd=str(Path(__file__).parent),
        model="claude-3-haiku-20240307",  # 使用更快的模型
        temperature=0.3,  # 降低随机性
        max_tokens=100,   # 限制输出长度
        timeout=60
    )

    runner = ClaudeHeadlessRunner(options)
    result = runner.run()

    if result['success']:
        print("✅ 执行成功!")
        print(f"⏱️  执行时间: {result['execution_time']:.2f}秒")
        print("\n📋 结果:")
        print(result['output'])
    else:
        print("❌ 执行失败!")
        print(f"错误: {result['error']}")

    return result


def main():
    """主函数 - 运行所有示例"""
    print("🚀 Claude 无头模式运行器示例")
    print("=" * 60)

    # 检查当前目录
    current_dir = Path(__file__).parent
    print(f"📁 当前工作目录: {current_dir}")

    # 运行示例（按顺序）
    examples = [
        ("列出项目结构", example_list_project_structure),
        ("分析代码架构", example_analyze_code_architecture),
        ("生成项目文档", example_generate_documentation),
        ("调试模式运行", example_debug_mode),
        ("自定义模型参数", example_custom_model),
    ]

    results = []

    for name, example_func in examples:
        try:
            print(f"\n🎯 开始执行: {name}")
            result = example_func()
            results.append((name, result))

            # 如果失败，询问是否继续
            if not result['success']:
                user_input = input(f"\n⚠️  '{name}' 执行失败，是否继续下一个示例？ (y/n): ")
                if user_input.lower() != 'y':
                    break

        except KeyboardInterrupt:
            print("\n\n⏹️  用户中断执行")
            break
        except Exception as e:
            print(f"\n💥 执行 '{name}' 时发生意外错误: {e}")
            user_input = input(f"是否继续下一个示例？ (y/n): ")
            if user_input.lower() != 'y':
                break

    # 总结报告
    print("\n\n📊 执行总结")
    print("=" * 60)

    success_count = sum(1 for _, result in results if result['success'])
    total_count = len(results)
    total_time = sum(result['execution_time'] for _, result in results)

    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"⏱️  总耗时: {total_time:.2f}秒")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "📈 成功率: N/A")

    for name, result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {name}: {result['execution_time']:.2f}s")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        sys.exit(1)

