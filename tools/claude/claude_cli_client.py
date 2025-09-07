#!/usr/bin/env python3
"""
使用 Claude Code CLI 的客户端实现
绕过 Anthropic API 配额限制
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

class ClaudeCliClient:
    """使用 Claude Code CLI 的客户端"""

    def __init__(self):
        """初始化 Claude CLI 客户端"""
        self.cli_path = self._find_claude_cli()
        if not self.cli_path:
            raise RuntimeError("Claude Code CLI not found. Please install Claude Code first.")

        print(f"✅ Found Claude CLI: {self.cli_path}")

    def _find_claude_cli(self) -> Optional[str]:
        """查找 Claude CLI 路径"""
        possible_paths = [
            'claude',  # 如果在 PATH 中
            '/usr/local/bin/claude',
            '/opt/homebrew/bin/claude',
            '~/.local/bin/claude'
        ]

        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            try:
                result = subprocess.run([expanded_path, '--version'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return expanded_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def send_message(self, content: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """发送消息给 Claude"""
        try:
            # 调用 Claude CLI，使用 --print 参数获取非交互式输出
            cmd = [
                self.cli_path,
                '--print',
                '--output-format', 'text',
                content
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                return {
                    'success': True,
                    'content': result.stdout.strip(),
                    'usage': {'estimated_tokens': len(result.stdout.split())}
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr.strip() or 'Unknown error',
                    'returncode': result.returncode
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Request timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_documentation(self, repo_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """生成文档"""
        try:
            # 构建文档生成提示
            prompt = self._build_documentation_prompt(repo_path, config)

            # 发送给 Claude
            response = self.send_message(prompt, max_tokens=4000)

            if response['success']:
                return {
                    'success': True,
                    'content': response['content'],
                    'usage': response['usage'],
                    'method': 'claude_cli'
                }
            else:
                return {
                    'success': False,
                    'error': response['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _build_documentation_prompt(self, repo_path: str, config: Dict[str, Any]) -> str:
        """构建文档生成提示"""

        # 扫描代码库结构
        structure = self._scan_repository_structure(repo_path)

        # 读取主要文件内容
        key_files = self._read_key_files(repo_path)

        prompt = f"""
请为以下代码库生成技术文档。

## 配置要求
- 分析深度: {config.get('analysis_depth', 'detailed')}
- 包含图表: {config.get('include_diagrams', True)}
- 包含故障排除: {config.get('include_troubleshooting', True)}

## 代码库结构
```
{structure}
```

## 主要文件内容
{key_files}

请生成包含以下部分的技术文档：

1. **项目概述**
   - 项目目的和功能
   - 主要特性
   - 技术栈

2. **架构设计**
   - 系统架构图（用文字描述）
   - 核心组件说明
   - 数据流程

3. **安装和配置**
   - 环境要求
   - 安装步骤
   - 配置说明

4. **API 文档**
   - 主要接口说明
   - 请求/响应格式
   - 使用示例

5. **开发指南**
   - 代码结构说明
   - 开发规范
   - 测试指南

请用 Markdown 格式输出，内容要详细且易于理解。
"""

        return prompt.strip()

    def _scan_repository_structure(self, repo_path: str, max_depth: int = 3) -> str:
        """扫描仓库结构"""
        try:
            structure_lines = []
            repo_path = Path(repo_path)

            def scan_dir(path: Path, prefix: str = "", depth: int = 0):
                if depth > max_depth:
                    return

                try:
                    items = sorted(path.iterdir())
                    for i, item in enumerate(items):
                        if item.name.startswith('.'):
                            continue

                        is_last = i == len(items) - 1
                        current_prefix = "└── " if is_last else "├── "
                        structure_lines.append(f"{prefix}{current_prefix}{item.name}")

                        if item.is_dir() and item.name not in ['__pycache__', 'node_modules', '.git', 'venv']:
                            next_prefix = prefix + ("    " if is_last else "│   ")
                            scan_dir(item, next_prefix, depth + 1)

                except PermissionError:
                    pass

            structure_lines.append(repo_path.name)
            scan_dir(repo_path)

            return "\n".join(structure_lines[:100])  # 限制行数

        except Exception as e:
            return f"无法扫描目录结构: {e}"

    def _read_key_files(self, repo_path: str) -> str:
        """读取关键文件内容"""
        repo_path = Path(repo_path)
        key_files = []

        # 定义关键文件模式
        important_files = [
            'README.md', 'README.rst', 'README.txt',
            'requirements.txt', 'package.json', 'pyproject.toml',
            'main.py', 'app.py', 'index.js', 'server.js',
            'config.py', 'settings.py', 'config.json'
        ]

        for file_pattern in important_files:
            for file_path in repo_path.rglob(file_pattern):
                if file_path.is_file() and file_path.stat().st_size < 10000:  # 限制文件大小
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            relative_path = file_path.relative_to(repo_path)
                            key_files.append(f"\n### {relative_path}\n```\n{content}\n```")
                    except (UnicodeDecodeError, PermissionError):
                        continue

        return "\n".join(key_files[:10])  # 限制文件数量

def test_claude_cli_client():
    """测试 Claude CLI 客户端"""
    print("🔍 测试 Claude CLI 客户端...")

    try:
        client = ClaudeCliClient()

        # 测试简单消息
        response = client.send_message("Hello! Please respond with 'Claude CLI is working!' to test the connection.", max_tokens=50)

        if response['success']:
            print("✅ Claude CLI 测试成功！")
            print(f"📄 响应: {response['content']}")
            return True
        else:
            print(f"❌ Claude CLI 测试失败: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Claude CLI 客户端错误: {e}")
        return False

if __name__ == "__main__":
    test_claude_cli_client()
