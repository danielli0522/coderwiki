#!/usr/bin/env python3
"""
Claude CLI 子进程通讯客户端
基于 TypeScript 版本的 SubprocessCLITransport 实现
"""

import subprocess
import json
import os
import shutil
import asyncio
import signal
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from pathlib import Path
from dataclasses import dataclass
import threading
import queue
import time

logger = logging.getLogger(__name__)


class CLINotFoundError(Exception):
    """Claude CLI 未找到错误"""
    pass


class CLIConnectionError(Exception):
    """CLI 连接错误"""
    pass


class ProcessError(Exception):
    """进程执行错误"""
    def __init__(self, message: str, exit_code: Optional[int] = None, signal_name: Optional[str] = None):
        super().__init__(message)
        self.exit_code = exit_code
        self.signal_name = signal_name


class CLIJSONDecodeError(Exception):
    """CLI JSON 解析错误"""
    def __init__(self, message: str, raw_line: str):
        super().__init__(message)
        self.raw_line = raw_line


class AbortError(Exception):
    """查询中止错误"""
    pass


@dataclass
class ClaudeCodeOptions:
    """Claude Code 选项配置"""
    model: Optional[str] = None
    session_id: Optional[str] = None
    allowed_tools: Optional[List[str]] = None
    denied_tools: Optional[List[str]] = None
    permission_mode: Optional[str] = None  # 'bypassPermissions', 'default', 'acceptEdits'
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    mcp_server_permissions: Optional[Dict[str, Any]] = None
    config_file: Optional[str] = None
    role: Optional[str] = None
    context: Optional[List[str]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    add_directories: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    debug: bool = False
    timeout: int = 300  # 5分钟默认超时


class SubprocessCLIClient:
    """Claude CLI 子进程通讯客户端"""

    def __init__(self, prompt: str, options: Optional[ClaudeCodeOptions] = None):
        self.prompt = prompt
        self.options = options or ClaudeCodeOptions()
        self.process: Optional[subprocess.Popen] = None
        self._abort_event = threading.Event()
        self._cleanup_handlers: List[callable] = []

    def find_cli(self) -> str:
        """查找 Claude CLI 可执行文件"""

        # 1. 检查本地 Claude 安装路径
        home = Path.home()
        local_paths = [
            home / '.claude' / 'local' / 'claude',
            home / '.claude' / 'bin' / 'claude'
        ]

        for path in local_paths:
            if path.exists() and os.access(path, os.X_OK):
                return str(path)

        # 2. 在 PATH 中查找
        for name in ['claude', 'claude-code']:
            cli_path = shutil.which(name)
            if cli_path:
                return cli_path

        # 3. 检查常见安装路径
        common_paths = []

        if os.name == 'nt':  # Windows
            common_paths.extend([
                home / 'AppData' / 'Local' / 'Programs' / 'claude' / 'claude.exe',
                home / 'AppData' / 'Local' / 'Programs' / 'claude-code' / 'claude-code.exe',
                Path('C:/Program Files/claude/claude.exe'),
                Path('C:/Program Files/claude-code/claude-code.exe')
            ])
        else:  # Unix-like
            common_paths.extend([
                Path('/usr/local/bin/claude'),
                Path('/usr/local/bin/claude-code'),
                Path('/usr/bin/claude'),
                Path('/usr/bin/claude-code'),
                Path('/opt/homebrew/bin/claude'),
                Path('/opt/homebrew/bin/claude-code'),
                home / '.local' / 'bin' / 'claude',
                home / '.local' / 'bin' / 'claude-code',
                home / 'bin' / 'claude',
                home / 'bin' / 'claude-code',
                home / '.claude' / 'local' / 'claude'
            ])

        # 4. 尝试 npm 全局路径
        try:
            result = subprocess.run(
                ['npm', 'config', 'get', 'prefix'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                npm_prefix = Path(result.stdout.strip())
                common_paths.extend([
                    npm_prefix / 'bin' / 'claude',
                    npm_prefix / 'bin' / 'claude-code'
                ])
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # 5. 测试每个路径
        for path in common_paths:
            try:
                if path.exists():
                    result = subprocess.run(
                        [str(path), '--version'],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return str(path)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        raise CLINotFoundError("Claude CLI not found. Please install Claude Code.")

    def build_command(self) -> List[str]:
        """构建 CLI 命令参数"""
        args = ['--output-format', 'stream-json', '--verbose']

        # 模型选择
        if self.options.model:
            args.extend(['--model', self.options.model])

        # 会话恢复
        if self.options.session_id:
            args.extend(['--resume', self.options.session_id])

        # 工具权限
        if self.options.allowed_tools:
            args.extend(['--allowedTools', ','.join(self.options.allowed_tools)])

        if self.options.denied_tools:
            args.extend(['--disallowedTools', ','.join(self.options.denied_tools)])

        # 权限模式
        if self.options.permission_mode == 'bypassPermissions':
            args.append('--dangerously-skip-permissions')

        # MCP 配置
        if self.options.mcp_servers:
            mcp_config = {'mcpServers': self.options.mcp_servers}
            args.extend(['--mcp-config', json.dumps(mcp_config)])

        if self.options.mcp_server_permissions:
            args.extend(['--mcp-server-permissions', json.dumps(self.options.mcp_server_permissions)])

        # 配置文件
        if self.options.config_file:
            args.extend(['--config-file', self.options.config_file])

        # 角色
        if self.options.role:
            args.extend(['--role', self.options.role])

        # 上下文
        if self.options.context:
            args.extend(['--context'] + self.options.context)

        # 温度参数
        if self.options.temperature is not None:
            args.extend(['--temperature', str(self.options.temperature)])

        # 最大token数
        if self.options.max_tokens is not None:
            args.extend(['--max-tokens', str(self.options.max_tokens)])

        # 添加目录
        if self.options.add_directories:
            args.extend(['--add-dir', ' '.join(self.options.add_directories)])

        # 打印模式
        args.append('--print')

        return args

    def connect(self) -> None:
        """连接到 Claude CLI"""
        cli_path = self.find_cli()
        args = self.build_command()

        # 环境变量
        env = os.environ.copy()
        if self.options.env:
            env.update(self.options.env)
        env['CLAUDE_CODE_ENTRYPOINT'] = 'sdk-python'

        # 调试信息
        if self.options.debug:
            logger.debug(f"Running command: {cli_path} {' '.join(args)}")

        try:
            self.process = subprocess.Popen(
                [cli_path] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=self.options.cwd,
                bufsize=0  # 无缓冲
            )

            # 发送提示词
            if self.process.stdin:
                self.process.stdin.write(self.prompt)
                self.process.stdin.close()

        except Exception as e:
            raise CLIConnectionError(f"Failed to start Claude Code CLI: {e}")

    def receive_messages(self) -> AsyncGenerator[Dict[str, Any], None]:
        """接收 CLI 消息（同步生成器版本）"""
        if not self.process or not self.process.stdout:
            raise CLIConnectionError('Not connected to CLI')

        try:
            # 处理 stderr（后台线程）
            stderr_thread = None
            if self.process.stderr:
                def handle_stderr():
                    try:
                        for line in self.process.stderr:
                            if self.options.debug:
                                logger.debug(f"stderr: {line.rstrip()}")
                    except Exception:
                        pass

                stderr_thread = threading.Thread(target=handle_stderr, daemon=True)
                stderr_thread.start()

            # 处理 stdout
            for line in self.process.stdout:
                if self._abort_event.is_set():
                    raise AbortError('Query was aborted')

                trimmed_line = line.strip()
                if not trimmed_line:
                    continue

                if self.options.debug:
                    logger.debug(f"stdout: {trimmed_line}")

                # 尝试解析 JSON
                try:
                    if trimmed_line.startswith('{') or trimmed_line.startswith('['):
                        parsed = json.loads(trimmed_line)
                        yield parsed
                except json.JSONDecodeError as e:
                    if trimmed_line.startswith('{') or trimmed_line.startswith('['):
                        raise CLIJSONDecodeError(
                            f"Failed to parse CLI output: {e}",
                            trimmed_line
                        )
                    # 跳过非 JSON 行
                    continue

            # 等待进程结束
            return_code = self.process.wait(timeout=self.options.timeout)

            if return_code != 0:
                raise ProcessError(
                    f"Claude Code CLI exited with code {return_code}",
                    return_code
                )

        except subprocess.TimeoutExpired:
            self.process.kill()
            raise ProcessError("Claude Code CLI timed out", None, "SIGKILL")

        finally:
            # 清理
            if stderr_thread and stderr_thread.is_alive():
                stderr_thread.join(timeout=1)

    def disconnect(self) -> None:
        """断开连接"""
        self._abort_event.set()

        if self.process:
            if self.process.poll() is None:  # 进程仍在运行
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

            self.process = None

        # 执行清理处理器
        for handler in self._cleanup_handlers:
            try:
                handler()
            except Exception as e:
                logger.warning(f"Cleanup handler failed: {e}")

        self._cleanup_handlers.clear()

    def abort(self) -> None:
        """中止查询"""
        self._abort_event.set()
        self.disconnect()

    def add_cleanup_handler(self, handler: callable) -> None:
        """添加清理处理器"""
        self._cleanup_handlers.append(handler)


class ClaudeSubprocessSmartDocClient:
    """基于子进程通讯的 Claude 智能文档客户端"""

    def __init__(self, workspace_path: Optional[str] = None, options: Optional[ClaudeCodeOptions] = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.default_options = options or ClaudeCodeOptions(
            model='claude-3-5-sonnet-20241022',
            permission_mode='bypassPermissions',
            debug=True,
            timeout=300
        )

    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        prompt = "请简单介绍一下你的能力，用中文回答，不超过100字。"

        options = ClaudeCodeOptions(
            model='claude-3-haiku-20240307',  # 使用更快的模型进行测试
            debug=self.default_options.debug,
            timeout=30
        )

        client = SubprocessCLIClient(prompt, options)

        try:
            client.connect()

            responses = []
            for message in client.receive_messages():
                responses.append(message)

                # 如果收到完整响应，提前退出
                if message.get('type') == 'result' and 'result' in message:
                    break

            return {
                'success': True,
                'responses': responses,
                'message': 'Connection test successful'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Connection test failed'
            }

        finally:
            client.disconnect()

    def generate_smart_document(
        self,
        repo_path: str,
        doc_type: str = "技术架构分析",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成智能文档"""

        # 构建提示词
        prompt = self._build_smart_doc_prompt(repo_path, doc_type, additional_context)

        # 配置选项
        options = ClaudeCodeOptions(
            model=self.default_options.model,
            add_directories=[repo_path],
            allowed_tools=['Read', 'Write', 'Bash'],
            debug=self.default_options.debug,
            timeout=self.default_options.timeout,
            cwd=self.workspace_path
        )

        client = SubprocessCLIClient(prompt, options)

        try:
            logger.info(f"Starting document generation for: {repo_path}")
            start_time = time.time()

            client.connect()

            # 收集所有响应
            responses = []
            final_result = None

            for message in client.receive_messages():
                responses.append(message)

                if self.default_options.debug:
                    logger.debug(f"Received message: {message.get('type', 'unknown')}")

                # 检查是否是最终结果
                if message.get('type') == 'result':
                    final_result = message.get('result', '')
                    if final_result and not message.get('is_error', False):
                        break

            execution_time = time.time() - start_time

            if final_result:
                return {
                    'success': True,
                    'document': {'content': final_result},
                    'metadata': {
                        'repo_path': repo_path,
                        'doc_type': doc_type,
                        'generated_via': 'subprocess_cli',
                        'execution_time': execution_time,
                        'responses_count': len(responses)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'No valid result received',
                    'metadata': {
                        'repo_path': repo_path,
                        'doc_type': doc_type,
                        'generated_via': 'subprocess_cli',
                        'execution_time': execution_time,
                        'responses_count': len(responses)
                    }
                }

        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'repo_path': repo_path,
                    'doc_type': doc_type,
                    'generated_via': 'subprocess_cli'
                }
            }

        finally:
            client.disconnect()

    def _build_smart_doc_prompt(
        self,
        repo_path: str,
        doc_type: str,
        additional_context: Optional[str] = None
    ) -> str:
        """构建智能文档生成提示词"""

        prompt = f"""
作为一个专业的技术文档分析师，请为指定的代码仓库生成高质量的{doc_type}文档。

## 任务要求

1. **代码仓库分析**：
   - 仓库路径：{repo_path}
   - 请深入分析代码结构、架构模式、技术栈
   - 识别关键组件、服务、模块之间的关系

2. **文档类型**：{doc_type}

3. **分析步骤**：
   - 首先使用 Read 工具扫描项目结构
   - 分析主要的配置文件、依赖文件
   - 理解核心业务逻辑和数据流
   - 识别重要的设计模式和架构决策

4. **输出要求**：
   - 生成结构化的 Markdown 文档
   - 包含清晰的架构说明
   - 提供代码示例和关键实现说明
   - 包含部署和使用指南

## 特殊指令

- 请使用工具全面扫描代码仓库
- 重点关注 Flask 应用架构、API 设计、数据模型
- 分析智能文档生成相关的服务和工具
- 生成的文档应该对开发者友好且易于理解

请开始分析并生成文档。
"""

        if additional_context:
            prompt += f"\n## 额外上下文\n{additional_context}\n"

        return prompt.strip()


def main():
    """主测试函数"""
    print("🚀 Claude 子进程通讯客户端测试")
    print("=" * 60)

    # 初始化客户端
    client = ClaudeSubprocessSmartDocClient()

    # 1. 连接测试
    print("\n📡 测试连接...")
    connection_result = client.test_connection()

    if connection_result['success']:
        print("✅ 连接测试成功！")
        responses = connection_result['responses']
        print(f"📊 收到 {len(responses)} 个响应")

        # 查找最终结果
        for response in responses:
            if response.get('type') == 'result' and 'result' in response:
                result = response['result']
                print(f"📄 响应内容: {result[:200]}...")
                break
    else:
        print("❌ 连接测试失败")
        print(f"🔍 错误: {connection_result['error']}")
        return

    # 2. 智能文档生成测试
    print("\n📚 测试智能文档生成...")

    repo_path = os.path.join(os.path.dirname(__file__), "backend")
    doc_result = client.generate_smart_document(
        repo_path=repo_path,
        doc_type="项目结构快速分析",
        additional_context="这是一个 Flask 应用的快速分析测试"
    )

    if doc_result['success']:
        print("✅ 文档生成成功！")

        content = doc_result['document']['content']
        metadata = doc_result['metadata']

        print(f"⏱️ 执行时间: {metadata.get('execution_time', 0):.2f} 秒")
        print(f"📊 响应数量: {metadata.get('responses_count', 0)}")
        print(f"📄 文档长度: {len(content)} 字符")

        # 保存文档
        output_file = "subprocess_cli_generated_doc.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"💾 文档已保存到: {output_file}")

        # 显示预览
        print(f"\n📄 文档内容预览:")
        print("-" * 50)
        print(content[:500])
        if len(content) > 500:
            print("...")
        print("-" * 50)
    else:
        print("❌ 文档生成失败")
        print(f"🔍 错误: {doc_result['error']}")

    print("\n🎯 测试完成！")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
