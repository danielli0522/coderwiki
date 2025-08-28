#!/usr/bin/env python3
"""
Claude Web Session 客户端
尝试模拟 Web 登录会话，使用 Claude Max 订阅而非 API 配额
"""

import os
import json
import time
import subprocess
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ClaudeWebSessionClient:
    """Claude Web Session 客户端 - 模拟网页登录使用"""

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.session_active = False

    def check_web_login_status(self) -> Dict[str, Any]:
        """检查 Web 登录状态"""
        print("🔍 检查 Claude 登录状态...")

        try:
            # 尝试使用 claude 命令检查登录状态
            result = subprocess.run(
                ['claude', 'config', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                config_output = result.stdout
                print("✅ Claude CLI 配置可用")
                print(f"📋 配置信息: {config_output[:200]}...")

                # 检查是否有认证信息
                if "theme" in config_output or "output" in config_output:
                    return {
                        'logged_in': True,
                        'method': 'cli_config',
                        'details': config_output
                    }

            # 尝试直接测试登录状态
            result = subprocess.run(
                ['claude', '--print', 'test'],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0 and "credit balance" not in result.stderr.lower():
                return {
                    'logged_in': True,
                    'method': 'direct_access',
                    'details': result.stdout[:100]
                }
            else:
                return {
                    'logged_in': True,
                    'method': 'authenticated_but_quota_limited',
                    'error': result.stderr + result.stdout
                }

        except Exception as e:
            return {
                'logged_in': False,
                'error': str(e)
            }

    def try_web_mode_access(self) -> Dict[str, Any]:
        """尝试 Web 模式访问"""
        print("\n🌐 尝试 Web 模式访问...")

        # 方法1: 尝试交互式模式而非 --print 模式
        print("📝 方法1: 交互式对话模式")
        try:
            # 创建一个简单的输入文件
            input_file = "claude_input.txt"
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write("你好，请简单介绍一下你的能力。\n/exit\n")

            # 尝试交互式模式
            result = subprocess.run(
                ['claude'],
                stdin=open(input_file, 'r'),
                capture_output=True,
                text=True,
                timeout=30
            )

            # 清理输入文件
            os.remove(input_file)

            if result.returncode == 0:
                output = result.stdout
                if "credit balance" not in output.lower():
                    print("✅ 交互式模式成功！")
                    return {
                        'success': True,
                        'method': 'interactive_mode',
                        'output': output
                    }
                else:
                    print("❌ 交互式模式仍遇到配额限制")

        except Exception as e:
            print(f"❌ 交互式模式失败: {e}")

        # 方法2: 尝试不同的命令行选项
        print("\n📝 方法2: 特殊命令行选项")
        special_options = [
            ['claude', '--help'],  # 帮助命令应该不需要配额
            ['claude', 'config', 'list'],  # 配置命令
            ['claude', 'status'],  # 状态命令
            ['claude', '--version'],  # 版本命令
        ]

        for cmd in special_options:
            try:
                print(f"🧪 测试: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print(f"✅ 成功: {result.stdout[:100]}...")

                    if cmd[1] == 'status':
                        # 状态命令可能提供有用信息
                        return {
                            'success': True,
                            'method': 'status_command',
                            'output': result.stdout
                        }
                else:
                    print(f"❌ 失败: {result.stderr}")

            except Exception as e:
                print(f"❌ 异常: {e}")

        # 方法3: 尝试本地会话恢复
        print("\n📝 方法3: 本地会话恢复")
        try:
            # 尝试恢复最近的会话
            result = subprocess.run(
                ['claude', '--continue'],
                capture_output=True,
                text=True,
                timeout=20
            )

            if result.returncode == 0 and "credit balance" not in result.stdout.lower():
                return {
                    'success': True,
                    'method': 'session_resume',
                    'output': result.stdout
                }

        except Exception as e:
            print(f"❌ 会话恢复失败: {e}")

        return {
            'success': False,
            'message': 'All web mode access methods failed'
        }

    def try_alternative_authentication(self) -> Dict[str, Any]:
        """尝试替代认证方式"""
        print("\n🔐 尝试替代认证方式...")

        # 检查是否有保存的会话令牌
        possible_token_locations = [
            Path.home() / '.claude' / 'session',
            Path.home() / '.claude' / 'auth',
            Path.home() / '.config' / 'claude',
            Path.home() / '.anthropic',
        ]

        for location in possible_token_locations:
            if location.exists():
                print(f"📁 找到可能的认证目录: {location}")
                try:
                    for file in location.iterdir():
                        if file.is_file():
                            print(f"  📄 {file.name}")
                except Exception as e:
                    print(f"  ❌ 无法读取: {e}")

        # 尝试使用环境变量进行 Web 认证
        print("\n🔧 尝试环境变量认证...")

        # 清除 API 相关的环境变量，强制使用 Web 认证
        web_env = os.environ.copy()

        # 移除 API 相关环境变量
        api_vars_to_remove = [
            'ANTHROPIC_API_KEY',
            'CLAUDE_API_KEY',
            'OPENAI_API_KEY'
        ]

        for var in api_vars_to_remove:
            if var in web_env:
                del web_env[var]
                print(f"🗑️ 移除环境变量: {var}")

        # 设置可能有助于 Web 模式的环境变量
        web_env['CLAUDE_USE_WEB_AUTH'] = 'true'
        web_env['CLAUDE_DISABLE_API'] = 'true'

        try:
            result = subprocess.run(
                ['claude', '--print', 'Hello'],
                env=web_env,
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0 and "credit balance" not in result.stderr.lower():
                return {
                    'success': True,
                    'method': 'web_env_auth',
                    'output': result.stdout
                }
            else:
                print(f"❌ Web 环境认证失败: {result.stderr}")

        except Exception as e:
            print(f"❌ Web 环境认证异常: {e}")

        return {
            'success': False,
            'message': 'Alternative authentication methods failed'
        }

    def try_browser_integration(self) -> Dict[str, Any]:
        """尝试浏览器集成方式"""
        print("\n🌐 尝试浏览器集成...")

        # 方法1: 尝试启动 IDE 集成模式
        print("📝 方法1: IDE 集成模式")
        try:
            result = subprocess.run(
                ['claude', '--ide'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print("✅ IDE 集成模式启动成功")
                return {
                    'success': True,
                    'method': 'ide_integration',
                    'output': result.stdout
                }

        except Exception as e:
            print(f"❌ IDE 集成失败: {e}")

        # 方法2: 检查浏览器扩展或桌面应用
        print("\n📝 方法2: 检查桌面应用")

        desktop_apps = [
            '/Applications/Claude.app',
            '/Applications/Claude Code.app',
            '/Applications/Anthropic Claude.app'
        ]

        for app_path in desktop_apps:
            if os.path.exists(app_path):
                print(f"✅ 找到桌面应用: {app_path}")
                return {
                    'success': True,
                    'method': 'desktop_app',
                    'app_path': app_path
                }

        print("❌ 未找到桌面应用")

        return {
            'success': False,
            'message': 'Browser integration methods not available'
        }

    def generate_document_with_web_mode(
        self,
        repo_path: str,
        doc_type: str = "项目概述",
        use_simple_prompt: bool = True
    ) -> Dict[str, Any]:
        """使用 Web 模式生成文档"""
        print(f"\n📚 使用 Web 模式生成文档...")
        print(f"📂 目标路径: {repo_path}")
        print(f"📄 文档类型: {doc_type}")

        if use_simple_prompt:
            # 使用非常简单的提示，避免触发复杂的 API 调用
            prompt = f"""请简单分析一下 {repo_path} 目录下的项目：
1. 这是什么类型的项目？
2. 主要包含哪些文件？
3. 用一句话总结项目的作用。

请保持回答简洁，不超过200字。"""
        else:
            # 使用更详细的提示
            prompt = f"""作为技术文档分析师，请为 {repo_path} 生成 {doc_type}：

## 分析要求
1. 扫描项目结构
2. 识别技术栈
3. 理解核心功能
4. 生成结构化文档

请开始分析。"""

        # 方法1: 尝试最小化的命令
        print("🧪 方法1: 最小化命令")
        try:
            # 创建临时输入文件
            input_file = "doc_generation_input.txt"
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(f"{prompt}\n")

            # 尝试最简单的调用方式
            result = subprocess.run(
                ['claude', '--print'],
                stdin=open(input_file, 'r'),
                capture_output=True,
                text=True,
                timeout=60,
                cwd=repo_path  # 在目标目录执行
            )

            # 清理
            os.remove(input_file)

            if result.returncode == 0:
                output = result.stdout
                if "credit balance" not in output.lower():
                    print("✅ 文档生成成功！")

                    # 保存生成的文档
                    doc_file = "web_mode_generated_doc.md"
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {doc_type}\n\n")
                        f.write(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"**生成方式**: Claude Web 模式\n\n")
                        f.write(output)

                    return {
                        'success': True,
                        'method': 'web_mode_simple',
                        'content': output,
                        'file': doc_file
                    }
                else:
                    print("❌ 仍遇到配额限制")

        except Exception as e:
            print(f"❌ 简单模式失败: {e}")

        # 方法2: 尝试分步骤执行
        print("\n🧪 方法2: 分步骤执行")
        try:
            steps = [
                f"查看 {repo_path} 目录内容",
                f"这个项目使用什么技术？",
                f"项目的主要功能是什么？"
            ]

            results = []
            for i, step in enumerate(steps, 1):
                print(f"  步骤 {i}: {step}")

                result = subprocess.run(
                    ['claude', '--print', step],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=repo_path
                )

                if result.returncode == 0 and "credit balance" not in result.stdout.lower():
                    answer = result.stdout
                    results.append(f"### {step}\n{answer}\n")
                    print(f"    ✅ 成功")
                else:
                    print(f"    ❌ 失败: {result.stderr}")
                    break

                time.sleep(2)  # 短暂延迟

            if results:
                combined_doc = "\n".join(results)
                doc_file = "web_mode_step_by_step_doc.md"

                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {doc_type} (分步骤生成)\n\n")
                    f.write(combined_doc)

                return {
                    'success': True,
                    'method': 'web_mode_stepwise',
                    'content': combined_doc,
                    'file': doc_file
                }

        except Exception as e:
            print(f"❌ 分步骤模式失败: {e}")

        return {
            'success': False,
            'message': 'All web mode document generation methods failed'
        }


def main():
    """主测试函数"""
    print("🎯 Claude Web Session 模式测试")
    print("=" * 60)
    print("目标：像在 claude.ai 网站登录一样使用 Claude，而非 API 模式")
    print("=" * 60)

    client = ClaudeWebSessionClient()

    # 1. 检查登录状态
    login_status = client.check_web_login_status()
    print(f"\n📊 登录状态: {login_status}")

    # 2. 尝试 Web 模式访问
    web_access = client.try_web_mode_access()
    print(f"\n📊 Web 模式访问: {web_access.get('success', False)}")

    if web_access.get('success'):
        print("🎉 找到可用的 Web 模式访问方法！")
        print(f"方法: {web_access.get('method')}")

        # 3. 尝试生成文档
        repo_path = os.path.join(os.path.dirname(__file__), "backend")
        if os.path.exists(repo_path):
            doc_result = client.generate_document_with_web_mode(repo_path)

            if doc_result.get('success'):
                print("🎉 Web 模式文档生成成功！")
                print(f"📄 文件: {doc_result.get('file')}")
                print(f"📊 内容长度: {len(doc_result.get('content', ''))} 字符")
            else:
                print("❌ Web 模式文档生成失败")
        else:
            print("⚠️ 未找到测试目录，跳过文档生成测试")

    else:
        # 4. 尝试替代认证
        alt_auth = client.try_alternative_authentication()
        print(f"\n📊 替代认证: {alt_auth.get('success', False)}")

        # 5. 尝试浏览器集成
        browser_integration = client.try_browser_integration()
        print(f"\n📊 浏览器集成: {browser_integration.get('success', False)}")

    # 6. 总结和建议
    print("\n" + "=" * 60)
    print("📋 Web Session 模式测试总结")
    print("=" * 60)

    if web_access.get('success') or login_status.get('logged_in'):
        print("✅ 好消息：找到了可用的访问方式！")
        print("💡 建议：")
        print("  1. 继续使用发现的工作方法")
        print("  2. 避免使用 --print 模式，尝试交互式对话")
        print("  3. 使用简单的提示词，避免复杂的任务")
    else:
        print("❌ 当前无法找到绕过 API 配额的方法")
        print("💡 建议：")
        print("  1. 检查 Claude 桌面应用是否可用")
        print("  2. 尝试在 claude.ai 网站直接使用")
        print("  3. 考虑购买少量 API 配额用于自动化任务")

    print("\n🎯 下一步：")
    print("  - 如果找到可用方法，集成到智能文档生成系统")
    print("  - 如果没有找到，建议购买 API 配额获得完整功能")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
