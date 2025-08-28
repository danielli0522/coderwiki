"""
Claude Code SDK 客户端
用于与 Claude Code API 进行交互
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeCodeClient:
    """Claude Code SDK 客户端"""

    def __init__(self, api_key: str, workspace_id: Optional[str] = None):
        """
        初始化 Claude Code 客户端

        Args:
            api_key: Anthropic API 密钥
            workspace_id: Claude Code 工作空间 ID（可选）
        """
        if not api_key:
            raise ValueError("API Key is required for Claude Code client")

        self.client = Anthropic(api_key=api_key)
        self.workspace_id = workspace_id
        self.session = None

        logger.info(f"Initialized Claude Code client with API key: {api_key[:20]}...")

    def create_session(self) -> Dict[str, Any]:
        """
        创建 Claude Code 会话

        Returns:
            会话信息字典
        """
        try:
            session = self.client.beta.workspaces.sessions.create(
                workspace_id=self.workspace_id
            )
            self.session = session
            logger.info(f"Created Claude Code session: {session.id}")
            return {
                'session_id': session.id,
                'workspace_id': session.workspace_id,
                'created_at': session.created_at
            }
        except Exception as e:
            logger.error(f"Failed to create Claude Code session: {e}")
            raise

    def configure_bmad_agents(self, session_id: str, config: Dict[str, Any]) -> bool:
        """
        配置 BMAD 代理团队

        Args:
            session_id: 会话 ID
            config: 配置信息

        Returns:
            配置是否成功
        """
        try:
            # 上传代理团队配置文件
            self.client.beta.workspaces.sessions.files.create(
                session_id=session_id,
                file_path="bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml"
            )

            # 上传工作流配置文件
            self.client.beta.workspaces.sessions.files.create(
                session_id=session_id,
                file_path="bmad-docs-generator/workflows/enhanced-docs-generation.yaml"
            )

            logger.info(f"Configured BMAD agents for session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to configure BMAD agents: {e}")
            return False

    def upload_codebase(self, session_id: str, repo_path: str) -> bool:
        """
        上传代码库到 Claude Code

        Args:
            session_id: 会话 ID
            repo_path: 代码库路径

        Returns:
            上传是否成功
        """
        try:
            uploaded_files = 0

            for root, dirs, files in os.walk(repo_path):
                # 跳过隐藏目录和虚拟环境
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]

                for file in files:
                    if self._should_upload_file(file):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, repo_path)

                        try:
                            self.client.beta.workspaces.sessions.files.create(
                                session_id=session_id,
                                file_path=relative_path
                            )
                            uploaded_files += 1
                        except Exception as e:
                            logger.warning(f"Failed to upload file {relative_path}: {e}")
                            continue

            logger.info(f"Uploaded {uploaded_files} files to session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload codebase: {e}")
            return False

    def trigger_bmad_workflow(self, session_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        触发 BMAD 工作流执行

        Args:
            session_id: 会话 ID
            config: 工作流配置

        Returns:
            触发结果
        """
        try:
            # 构建工作流触发消息
            workflow_message = self._build_workflow_message(config)

            message = self.client.beta.workspaces.sessions.messages.create(
                session_id=session_id,
                content=workflow_message
            )

            logger.info(f"Triggered BMAD workflow for session: {session_id}")
            return {
                'message_id': message.id,
                'session_id': session_id,
                'status': 'triggered'
            }

        except Exception as e:
            logger.error(f"Failed to trigger BMAD workflow: {e}")
            raise

    def get_workflow_results(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取工作流执行结果

        Args:
            session_id: 会话 ID

        Returns:
            消息列表
        """
        try:
            messages = self.client.beta.workspaces.sessions.messages.list(
                session_id=session_id
            )

            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'role': msg.role,
                    'created_at': msg.created_at
                }
                for msg in messages.data
            ]

        except Exception as e:
            logger.error(f"Failed to get workflow results: {e}")
            return []

    def monitor_execution(self, session_id: str, timeout: int = 300) -> Dict[str, Any]:
        """
        监控工作流执行进度

        Args:
            session_id: 会话 ID
            timeout: 超时时间（秒）

        Returns:
            执行结果
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            messages = self.get_workflow_results(session_id)

            if self._is_workflow_complete(messages):
                return {
                    'status': 'completed',
                    'messages': messages,
                    'execution_time': time.time() - start_time
                }

            time.sleep(10)  # 每10秒检查一次

        raise TimeoutError(f"BMAD workflow execution timeout after {timeout} seconds")

    def _should_upload_file(self, filename: str) -> bool:
        """
        判断文件是否应该上传

        Args:
            filename: 文件名

        Returns:
            是否应该上传
        """
        # 排除的文件和目录
        exclude_patterns = [
            '__pycache__', '.git', '.env', '.DS_Store', 'venv', 'node_modules',
            '.pytest_cache', '.coverage', 'htmlcov', '.vscode', '.idea'
        ]

        # 检查是否包含排除模式
        for pattern in exclude_patterns:
            if pattern in filename:
                return False

        # 代码文件扩展名
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
            '.html', '.css', '.scss', '.sass', '.vue', '.jsx', '.tsx',
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.md', '.txt', '.sql', '.sh', '.bat', '.ps1'
        }

        # 配置文件
        config_files = {
            'package.json', 'requirements.txt', 'pom.xml', 'build.gradle',
            'Dockerfile', 'docker-compose.yml', 'README.md',
            'Makefile', 'CMakeLists.txt', 'setup.py', 'pyproject.toml'
        }

        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in code_extensions or filename in config_files

    def _build_workflow_message(self, config: Dict[str, Any]) -> str:
        """
        构建工作流触发消息

        Args:
            config: 工作流配置

        Returns:
            触发消息
        """
        analysis_depth = config.get('analysis_depth', 'detailed')
        include_diagrams = config.get('include_diagrams', True)
        include_troubleshooting = config.get('include_troubleshooting', True)

        message = f"""
Execute the enhanced-docs-generation workflow with BMAD agents.

Configuration:
- Analysis Depth: {analysis_depth}
- Include Diagrams: {include_diagrams}
- Include Troubleshooting: {include_troubleshooting}

Please follow the workflow defined in enhanced-docs-generation.yaml and coordinate with all BMAD agents:
1. Code Analyst (Alex) - for codebase scanning and analysis
2. Architecture Analyst - for architecture pattern recognition
3. Flow Analyst (Jordan) - for complex flow analysis
4. Problem Solver (Dr. Morgan) - for problem diagnosis
5. Doc Engineer (Maya) - for final documentation generation

Generate comprehensive technical documentation that enables 3-day project understanding.
"""
        return message.strip()

    def _is_workflow_complete(self, messages: List[Dict[str, Any]]) -> bool:
        """
        判断工作流是否完成

        Args:
            messages: 消息列表

        Returns:
            是否完成
        """
        if not messages:
            return False

        # 检查最后一条消息是否包含完成标识
        last_message = messages[-1]
        content = last_message.get('content', '')

        completion_indicators = [
            'workflow completed',
            'documentation generated',
            'final documentation',
            'executive summary',
            'quality validation passed'
        ]

        return any(indicator in content.lower() for indicator in completion_indicators)

    def extract_agent_output(self, messages: List[Dict[str, Any]], agent_name: str) -> Optional[str]:
        """
        提取指定代理的输出

        Args:
            messages: 消息列表
            agent_name: 代理名称

        Returns:
            代理输出内容
        """
        for message in messages:
            content = message.get('content', '')
            if agent_name.lower() in content.lower():
                return content

        return None
