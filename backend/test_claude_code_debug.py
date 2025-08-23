#!/usr/bin/env python3
"""
Claude Code SDK调试测试
诊断响应处理问题
"""

import os
import sys
import asyncio
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_claude_code_response():
    """调试Claude Code SDK响应"""
    print("=== Claude Code SDK响应调试 ===")

    try:
        # 导入Claude Code SDK
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

        print("✅ Claude Code SDK导入成功")

        # 简单的系统提示词
        system_prompt = """你是一个技术文档生成专家。请分析代码仓库并生成详细的技术文档。
要求：
1. 使用中文编写
2. 使用Markdown格式
3. 包含详细的代码分析
4. 生成至少2000字的文档
5. 包含目录结构、架构说明、API文档等"""

        query_content = """请分析这个Flask后端项目并生成详细的技术文档。
项目路径: /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/backend
请生成包含以下内容的文档：
1. 项目概述
2. 目录结构分析
3. 核心模块说明
4. API接口文档
5. 数据库设计
6. 部署说明"""

        print("开始调用Claude Code SDK...")
        start_time = time.time()

        async with ClaudeSDKClient(
            options=ClaudeCodeOptions(
                system_prompt=system_prompt,
                max_turns=5,  # 增加轮次
                allowed_tools=["Read", "Grep", "WebSearch"]
            )
        ) as client:
            print("✅ ClaudeSDKClient创建成功")

            # 发送查询
            print("发送查询...")
            await client.query(query_content)
            print("✅ 查询发送成功")

            # 收集响应
            print("开始接收响应...")
            content_parts = []
            message_count = 0
            cost_estimate = 0.0
            tokens_used = 0

            async for message in client.receive_response():
                message_count += 1
                print(f"收到消息 #{message_count}: {type(message).__name__}")

                # 打印消息的详细信息
                print(f"  消息属性: {dir(message)}")

                if hasattr(message, 'content'):
                    print(f"  有content属性，长度: {len(message.content) if message.content else 0}")
                    if message.content:
                        for i, block in enumerate(message.content):
                            print(f"    块 #{i}: {type(block).__name__}")
                            if hasattr(block, 'text'):
                                text_content = block.text
                                print(f"      文本长度: {len(text_content) if text_content else 0}")
                                if text_content:
                                    content_parts.append(text_content)
                                    print(f"      文本预览: {text_content[:100]}...")

                # 获取成本信息
                if type(message).__name__ == "ResultMessage":
                    cost_estimate = getattr(message, 'total_cost_usd', 0.0)
                    tokens_used = getattr(message, 'total_tokens', 0)
                    print(f"  成本信息: ${cost_estimate}, 令牌: {tokens_used}")

                print()

            print(f"总共收到 {message_count} 条消息")
            print(f"收集到的内容块数量: {len(content_parts)}")

            # 合并内容
            final_content = ''.join(content_parts)
            print(f"最终内容长度: {len(final_content)} 字符")

            if final_content:
                print("内容预览:")
                print("-" * 50)
                print(final_content[:500])
                if len(final_content) > 500:
                    print("...")
                print("-" * 50)

                # 保存完整内容
                with open("debug_claude_response.md", "w", encoding="utf-8") as f:
                    f.write(final_content)
                print("完整响应已保存到: debug_claude_response.md")
            else:
                print("❌ 没有收集到任何内容")

            response_time = time.time() - start_time
            print(f"总耗时: {response_time:.2f} 秒")

            return {
                'success': True,
                'content': final_content,
                'message_count': message_count,
                'content_parts_count': len(content_parts),
                'cost_estimate': cost_estimate,
                'tokens_used': tokens_used,
                'response_time': response_time
            }

    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

async def test_simple_query():
    """测试简单查询"""
    print("\n=== 简单查询测试 ===")

    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

        system_prompt = "你是一个助手，请用中文回答。"
        query_content = "请介绍一下Flask框架的主要特点。"

        print("开始简单查询...")

        async with ClaudeSDKClient(
            options=ClaudeCodeOptions(
                system_prompt=system_prompt,
                max_turns=2
            )
        ) as client:
            await client.query(query_content)

            content_parts = []
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            content_parts.append(block.text)

            final_content = ''.join(content_parts)
            print(f"简单查询响应长度: {len(final_content)} 字符")
            print("响应内容:")
            print(final_content)

            return len(final_content) > 0

    except Exception as e:
        print(f"简单查询失败: {e}")
        return False

async def main():
    """主函数"""
    print("Claude Code SDK响应调试")
    print("=" * 60)

    # 设置环境变量
    os.environ['CLAUDE_CODE_ENABLED'] = 'true'

    # 测试简单查询
    simple_success = await test_simple_query()

    if simple_success:
        print("✅ 简单查询成功，继续调试复杂查询...")
        # 测试复杂查询
        result = await debug_claude_code_response()

        print("\n" + "=" * 60)
        print("调试结果总结:")
        print("=" * 60)

        if result['success']:
            print("✅ 调试成功")
            print(f"消息数量: {result['message_count']}")
            print(f"内容块数量: {result['content_parts_count']}")
            print(f"最终内容长度: {len(result['content'])} 字符")
            print(f"响应时间: {result['response_time']:.2f} 秒")
            print(f"成本估算: ${result['cost_estimate']:.4f}")
            print(f"令牌使用: {result['tokens_used']}")
        else:
            print("❌ 调试失败")
            print(f"错误: {result.get('error', 'Unknown error')}")
    else:
        print("❌ 简单查询失败，可能存在SDK问题")

if __name__ == "__main__":
    asyncio.run(main())
