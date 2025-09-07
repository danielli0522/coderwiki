#!/usr/bin/env python3
"""
Claude Code SDK 无头模式运行器

基于Claude Code CLI的无头模式运行脚本，等待最终反馈后返回成功状态。
参考命令格式：
claude -p "请列出该项目目录结构" \
  --allowedTools "Bash,Read" \
  --permission-mode acceptEdits \
  --cwd /path/to/project
"""

import os
import subprocess
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('claude_headless.log')
    ]
)
logger = logging.getLogger(__name__)


class ClaudeCliNotFoundError(Exception):
    """Claude CLI 未找到异常"""
    pass


class ClaudeExecutionError(Exception):
    """Claude 执行异常"""
    pass


@dataclass
class ClaudeHeadlessOptions:
    """Claude 无头模式选项配置"""
    prompt: str                                 # 提示内容
    allowed_tools: Optional[List[str]] = None   # 允许的工具
    denied_tools: Optional[List[str]] = None    # 禁止的工具
    permission_mode: str = "acceptEdits"        # 权限模式
    cwd: Optional[str] = None                   # 工作目录
    model: Optional[str] = None                 # 模型名称
    max_tokens: Optional[int] = None            # 最大token数
    temperature: Optional[float] = None         # 温度参数
    timeout: int = 300                          # 超时时间（秒）
    output_format: str = "text"                 # 输出格式
    session_id: Optional[str] = None            # 会话ID
    debug: bool = False                         # 调试模式


class ClaudeHeadlessRunner:
    """Claude Code SDK 无头模式运行器"""

    def __init__(self, options: ClaudeHeadlessOptions):
        """
        初始化无头模式运行器

        Args:
            options: Claude 无头模式选项配置
        """
        self.options = options
        self.cli_path = self._find_claude_cli()

        if not self.cli_path:
            raise ClaudeCliNotFoundError(
                "Claude Code CLI not found. Please install Claude Code first."
            )

        logger.info(f"✅ Found Claude CLI: {self.cli_path}")

    def _find_claude_cli(self) -> Optional[str]:
        """
        查找 Claude CLI 可执行文件路径

        Returns:
            Claude CLI 路径，如果未找到则返回 None
        """
        # 优先级顺序的可能路径
        possible_paths = [
            'claude',                           # PATH 中
            '/usr/local/bin/claude',           # 系统安装
            '/opt/homebrew/bin/claude',        # Homebrew (Apple Silicon)
            '/usr/bin/claude',                 # 系统 bin
            str(Path.home() / '.local/bin/claude'),  # 用户本地安装
            str(Path.home() / '.claude/bin/claude'), # Claude 专用目录
        ]

        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            try:
                # 测试 Claude CLI 是否可用
                result = subprocess.run(
                    [expanded_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.debug(f"Found Claude CLI at: {expanded_path}")
                    return expanded_path

            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
                continue

        return None

    def _build_command(self) -> List[str]:
        """
        构建 Claude CLI 命令

        Returns:
            完整的命令参数列表
        """
        cmd = [self.cli_path]

        # 添加提示内容
        cmd.extend(['-p', self.options.prompt])

        # 允许的工具
        if self.options.allowed_tools:
            tools_str = ','.join(self.options.allowed_tools)
            cmd.extend(['--allowedTools', tools_str])

        # 禁止的工具
        if self.options.denied_tools:
            denied_tools_str = ','.join(self.options.denied_tools)
            cmd.extend(['--deniedTools', denied_tools_str])

        # 权限模式
        cmd.extend(['--permission-mode', self.options.permission_mode])

        # 工作目录（使用 --add-dir 参数）
        if self.options.cwd:
            cmd.extend(['--add-dir', self.options.cwd])

        # 模型
        if self.options.model:
            cmd.extend(['--model', self.options.model])

        # 最大token数
        if self.options.max_tokens:
            cmd.extend(['--max-tokens', str(self.options.max_tokens)])

        # 温度参数
        if self.options.temperature is not None:
            cmd.extend(['--temperature', str(self.options.temperature)])

        # 会话ID
        if self.options.session_id:
            cmd.extend(['--session-id', self.options.session_id])

        # 输出格式
        cmd.extend(['--output-format', self.options.output_format])

        # 调试模式
        if self.options.debug:
            cmd.append('--debug')

        return cmd

    def run(self) -> Dict[str, Any]:
        """
        运行 Claude 无头模式命令，等待最终反馈

        Returns:
            包含执行结果的字典，格式：
            {
                'success': bool,
                'output': str,
                'error': str,
                'execution_time': float,
                'exit_code': int
            }
        """
        start_time = time.time()

        try:
            # 构建命令
            cmd = self._build_command()

            if self.options.debug:
                logger.debug(f"Executing command: {' '.join(cmd)}")

            logger.info(f"🚀 Starting Claude headless execution...")
            logger.info(f"📝 Prompt: {self.options.prompt[:100]}...")
            logger.info(f"🛠️  Tools: {self.options.allowed_tools}")
            logger.info(f"📁 Working directory: {self.options.cwd}")

            # 执行命令
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.options.timeout,
                cwd=self.options.cwd
            )

            execution_time = time.time() - start_time

            # 处理执行结果
            if process.returncode == 0:
                logger.info(f"✅ Claude execution completed successfully!")
                logger.info(f"⏱️  Execution time: {execution_time:.2f} seconds")

                return {
                    'success': True,
                    'output': process.stdout.strip(),
                    'error': '',
                    'execution_time': execution_time,
                    'exit_code': process.returncode
                }
            else:
                logger.error(f"❌ Claude execution failed with exit code {process.returncode}")
                logger.error(f"Error output: {process.stderr}")

                return {
                    'success': False,
                    'output': process.stdout.strip(),
                    'error': process.stderr.strip(),
                    'execution_time': execution_time,
                    'exit_code': process.returncode
                }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            error_msg = f"Claude execution timed out after {self.options.timeout} seconds"
            logger.error(f"⏰ {error_msg}")

            return {
                'success': False,
                'output': '',
                'error': error_msg,
                'execution_time': execution_time,
                'exit_code': -1
            }

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Unexpected error during Claude execution: {str(e)}"
            logger.error(f"💥 {error_msg}")

            return {
                'success': False,
                'output': '',
                'error': error_msg,
                'execution_time': execution_time,
                'exit_code': -2
            }

    def run_async(self) -> subprocess.Popen:
        """
        异步运行 Claude 无头模式命令

        Returns:
            subprocess.Popen 对象，可用于监控进程状态
        """
        cmd = self._build_command()

        if self.options.debug:
            logger.debug(f"Executing async command: {' '.join(cmd)}")

        logger.info(f"🚀 Starting Claude headless execution (async)...")

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.options.cwd
        )


def main():
    """主函数 - 命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Code SDK 无头模式运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python claude_headless_runner.py -p "请列出该项目目录结构" --tools "Bash,Read" --cwd /path/to/project
  python claude_headless_runner.py -p "分析代码架构" --tools "Read,Grep" --permission-mode acceptEdits
  python claude_headless_runner.py -p "生成文档" --tools "Read,Write" --timeout 600 --debug
        """
    )

    parser.add_argument('-p', '--prompt', required=True, help='提示内容')
    parser.add_argument('--tools', '--allowedTools', help='允许的工具列表，逗号分隔')
    parser.add_argument('--denied-tools', help='禁止的工具列表，逗号分隔')
    parser.add_argument('--permission-mode', default='acceptEdits',
                       choices=['acceptEdits', 'bypassPermissions', 'default'],
                       help='权限模式')
    parser.add_argument('--cwd', help='工作目录')
    parser.add_argument('--model', help='使用的模型')
    parser.add_argument('--max-tokens', type=int, help='最大token数')
    parser.add_argument('--temperature', type=float, help='温度参数')
    parser.add_argument('--timeout', type=int, default=300, help='超时时间（秒）')
    parser.add_argument('--session-id', help='会话ID')
    parser.add_argument('--output-format', default='text', help='输出格式')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--json-output', action='store_true', help='以JSON格式输出结果')

    args = parser.parse_args()

    # 构建选项
    options = ClaudeHeadlessOptions(
        prompt=args.prompt,
        allowed_tools=args.tools.split(',') if args.tools else None,
        denied_tools=args.denied_tools.split(',') if args.denied_tools else None,
        permission_mode=args.permission_mode,
        cwd=args.cwd,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        timeout=args.timeout,
        session_id=args.session_id,
        output_format=args.output_format,
        debug=args.debug
    )

    try:
        # 创建运行器并执行
        runner = ClaudeHeadlessRunner(options)
        result = runner.run()

        if args.json_output:
            # JSON 输出
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 人类可读输出
            if result['success']:
                print(f"\n✅ 执行成功! (耗时: {result['execution_time']:.2f}s)")
                print("\n" + "="*50)
                print("输出结果:")
                print("="*50)
                print(result['output'])
            else:
                print(f"\n❌ 执行失败! (耗时: {result['execution_time']:.2f}s)")
                print(f"错误信息: {result['error']}")
                if result['output']:
                    print(f"部分输出: {result['output']}")
                sys.exit(result['exit_code'] if result['exit_code'] > 0 else 1)

    except ClaudeCliNotFoundError as e:
        logger.error(f"❌ {e}")
        print("请先安装 Claude Code CLI: https://claude.ai/")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
