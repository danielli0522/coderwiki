"""
Claude Code SDK 和 BMAD 代理集成测试
测试通过 Claude Code SDK 调用 BMAD-Docs-Generator 子代理功能
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.claude_client import ClaudeCodeClient
from app.utils.bmad_orchestrator import BMADOrchestrator
from app.services.smart_doc_service import SmartDocumentService


class TestClaudeBMADIntegration(unittest.TestCase):
    """Claude Code SDK 和 BMAD 代理集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.test_api_key = "test-claude-api-key"
        self.test_workspace_id = "test-workspace-id"
        self.test_session_id = "test-session-id"

        # 创建临时目录作为测试仓库
        self.temp_dir = tempfile.mkdtemp()
        self.create_test_config_directory()

        # 模拟 Claude Code 客户端
        self.mock_claude_client = Mock(spec=ClaudeCodeClient)
        self.mock_claude_client.api_key = self.test_api_key
        self.mock_claude_client.workspace_id = self.test_workspace_id

        # 创建 BMAD 编排器
        self.bmad_orchestrator = BMADOrchestrator(self.mock_claude_client)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_config_directory(self):
        """创建测试用的 Config 目录结构"""
        config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)

        # 创建配置文件
        config_files = {
            "database.py": """
# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'coderwiki',
    'username': 'user',
    'password': 'password'
}
""",
            "app.py": """
# 应用配置
class Config:
    SECRET_KEY = 'your-secret-key'
    DEBUG = True
    DATABASE_URL = 'mysql://localhost/coderwiki'
""",
            "claude_config.py": """
# Claude Code 配置
CLAUDE_API_KEY = 'your-claude-api-key'
CLAUDE_WORKSPACE_ID = 'your-workspace-id'
BMAD_AGENTS_PATH = 'bmad-docs-generator'
""",
            "settings.py": """
# 系统设置
SYSTEM_SETTINGS = {
    'max_file_size': 10485760,
    'max_files_per_repo': 1000,
    'workflow_timeout': 300
}
"""
        }

        for filename, content in config_files.items():
            file_path = os.path.join(config_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # 创建 README 文件
        readme_path = os.path.join(self.temp_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""
# 测试项目

这是一个用于测试 Claude Code SDK 和 BMAD 代理集成的项目。

## 目录结构

- `config/` - 配置文件目录
  - `database.py` - 数据库配置
  - `app.py` - 应用配置
  - `claude_config.py` - Claude Code 配置
  - `settings.py` - 系统设置

## 技术栈

- Python 3.8+
- Flask
- MySQL
- Claude Code SDK
- BMAD 代理系统
""")

    @patch('app.utils.claude_client.Anthropic')
    def test_claude_client_initialization(self, mock_anthropic):
        """测试 Claude Code 客户端初始化"""
        # 模拟 Anthropic 客户端
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # 创建客户端实例
        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)

        # 验证初始化
        self.assertEqual(client.api_key, self.test_api_key)
        self.assertEqual(client.workspace_id, self.test_workspace_id)
        self.assertIsNotNone(client.client)

    @patch('app.utils.claude_client.Anthropic')
    def test_create_session(self, mock_anthropic):
        """测试创建 Claude Code 会话"""
        # 模拟会话创建
        mock_session = Mock()
        mock_session.id = self.test_session_id
        mock_session.workspace_id = self.test_workspace_id
        mock_session.created_at = "2024-01-01T00:00:00Z"

        mock_client = Mock()
        mock_client.beta.workspaces.sessions.create.return_value = mock_session
        mock_anthropic.return_value = mock_client

        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)
        session_info = client.create_session()

        # 验证会话创建
        self.assertEqual(session_info['session_id'], self.test_session_id)
        self.assertEqual(session_info['workspace_id'], self.test_workspace_id)
        mock_client.beta.workspaces.sessions.create.assert_called_once()

    @patch('app.utils.claude_client.Anthropic')
    def test_configure_bmad_agents(self, mock_anthropic):
        """测试配置 BMAD 代理"""
        # 模拟文件上传
        mock_client = Mock()
        mock_client.beta.workspaces.sessions.files.create.return_value = Mock()
        mock_anthropic.return_value = mock_client

        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)
        config = {'analysis_depth': 'detailed'}

        result = client.configure_bmad_agents(self.test_session_id, config)

        # 验证配置成功
        self.assertTrue(result)
        # 验证文件上传调用次数（代理团队配置 + 工作流配置）
        self.assertEqual(mock_client.beta.workspaces.sessions.files.create.call_count, 2)

    @patch('app.utils.claude_client.Anthropic')
    def test_upload_codebase(self, mock_anthropic):
        """测试上传代码库"""
        # 模拟文件上传
        mock_client = Mock()
        mock_client.beta.workspaces.sessions.files.create.return_value = Mock()
        mock_anthropic.return_value = mock_client

        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)

        result = client.upload_codebase(self.test_session_id, self.temp_dir)

        # 验证上传成功
        self.assertTrue(result)
        # 验证至少上传了配置文件
        self.assertGreater(mock_client.beta.workspaces.sessions.files.create.call_count, 0)

    @patch('app.utils.claude_client.Anthropic')
    def test_trigger_bmad_workflow(self, mock_anthropic):
        """测试触发 BMAD 工作流"""
        # 模拟消息创建
        mock_message = Mock()
        mock_message.id = "test-message-id"

        mock_client = Mock()
        mock_client.beta.workspaces.sessions.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)
        config = {
            'analysis_depth': 'detailed',
            'include_diagrams': True,
            'include_troubleshooting': True
        }

        result = client.trigger_bmad_workflow(self.test_session_id, config)

        # 验证触发成功
        self.assertEqual(result['message_id'], "test-message-id")
        self.assertEqual(result['session_id'], self.test_session_id)
        self.assertEqual(result['status'], 'triggered')

    def test_bmad_orchestrator_initialization(self):
        """测试 BMAD 编排器初始化"""
        # 验证代理配置
        self.assertIn('code-analyst', self.bmad_orchestrator.agents)
        self.assertIn('architecture-analyst', self.bmad_orchestrator.agents)
        self.assertIn('flow-analyst', self.bmad_orchestrator.agents)
        self.assertIn('problem-solver', self.bmad_orchestrator.agents)
        self.assertIn('doc-engineer', self.bmad_orchestrator.agents)

        # 验证代理信息
        code_analyst = self.bmad_orchestrator.agents['code-analyst']
        self.assertEqual(code_analyst['name'], 'Alex')
        self.assertEqual(code_analyst['role'], 'Code Analyst')

    @patch('app.utils.claude_client.Anthropic')
    def test_bmad_workflow_execution(self, mock_anthropic):
        """测试 BMAD 工作流执行"""
        # 模拟完整的 Claude Code 交互
        mock_session = Mock()
        mock_session.id = self.test_session_id
        mock_session.workspace_id = self.test_workspace_id
        mock_session.created_at = "2024-01-01T00:00:00Z"

        mock_message = Mock()
        mock_message.id = "test-message-id"

        mock_client = Mock()
        mock_client.beta.workspaces.sessions.create.return_value = mock_session
        mock_client.beta.workspaces.sessions.files.create.return_value = Mock()
        mock_client.beta.workspaces.sessions.messages.create.return_value = mock_message
        mock_client.beta.workspaces.sessions.messages.list.return_value = Mock(
            data=[
                Mock(
                    id="msg-1",
                    content="Code Analyst (Alex) completed codebase analysis",
                    role="assistant",
                    created_at="2024-01-01T00:01:00Z"
                ),
                Mock(
                    id="msg-2",
                    content="Architecture Analyst completed architecture analysis",
                    role="assistant",
                    created_at="2024-01-01T00:02:00Z"
                ),
                Mock(
                    id="msg-3",
                    content="Documentation generation completed successfully",
                    role="assistant",
                    created_at="2024-01-01T00:03:00Z"
                )
            ]
        )
        mock_anthropic.return_value = mock_client

        # 创建真实的 Claude Code 客户端
        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)
        orchestrator = BMADOrchestrator(client)

        config = {
            'analysis_depth': 'detailed',
            'include_diagrams': True,
            'include_troubleshooting': True,
            'doc_type': 'complete'
        }

        # 执行工作流
        result = orchestrator.execute_workflow(self.temp_dir, config)

        # 验证执行结果
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['session_id'], self.test_session_id)
        self.assertIn('document', result)
        self.assertIn('agent_outputs', result)

        # 验证文档内容
        document = result['document']
        self.assertEqual(document['title'], 'Technical Documentation Generated by BMAD Agents')
        self.assertIn('config', document['agents_used'])

        # 验证代理输出
        agent_outputs = result['agent_outputs']
        self.assertIn('code-analyst', agent_outputs)
        self.assertIn('architecture-analyst', agent_outputs)

    def test_agent_output_extraction(self):
        """测试代理输出提取"""
        # 模拟消息列表
        messages = [
            {
                'id': 'msg-1',
                'content': 'Code Analyst (Alex) completed codebase scanning and analysis',
                'role': 'assistant',
                'created_at': '2024-01-01T00:01:00Z'
            },
            {
                'id': 'msg-2',
                'content': 'Architecture Analyst identified architectural patterns',
                'role': 'assistant',
                'created_at': '2024-01-01T00:02:00Z'
            },
            {
                'id': 'msg-3',
                'content': 'Flow Analyst (Jordan) analyzed complex business flows',
                'role': 'assistant',
                'created_at': '2024-01-01T00:03:00Z'
            }
        ]

        # 提取代理输出
        agent_outputs = self.bmad_orchestrator._extract_agent_outputs(messages)

        # 验证代理输出
        self.assertIn('code-analyst', agent_outputs)
        self.assertIn('architecture-analyst', agent_outputs)
        self.assertIn('flow-analyst', agent_outputs)

        # 验证代码分析师输出
        code_analyst = agent_outputs['code-analyst']
        self.assertEqual(code_analyst['status'], 'completed')
        self.assertIn('Alex', code_analyst['content'])

    def test_workflow_progress_calculation(self):
        """测试工作流进度计算"""
        # 模拟部分完成的代理输出
        agent_outputs = {
            'code-analyst': {'status': 'completed'},
            'architecture-analyst': {'status': 'completed'},
            'flow-analyst': {'status': 'pending'},
            'problem-solver': {'status': 'pending'},
            'doc-engineer': {'status': 'pending'}
        }

        # 计算进度
        total_agents = len(agent_outputs)
        completed_agents = sum(1 for output in agent_outputs.values() if output['status'] == 'completed')
        progress_percentage = (completed_agents / total_agents) * 100

        # 验证进度计算
        self.assertEqual(total_agents, 5)
        self.assertEqual(completed_agents, 2)
        self.assertEqual(progress_percentage, 40.0)

    def test_document_content_formatting(self):
        """测试文档内容格式化"""
        # 模拟文档数据
        document_data = {
            'title': 'Config Directory Technical Overview',
            'generated_at': '2024-01-01 12:00:00',
            'agents_used': ['code-analyst', 'architecture-analyst'],
            'sections': {
                'code-analyst': {
                    'agent_name': 'Alex',
                    'agent_role': 'Code Analyst',
                    'content': 'Code analysis completed for config directory',
                    'status': 'completed'
                },
                'architecture-analyst': {
                    'agent_name': 'Architecture Analyst',
                    'agent_role': 'Architecture Specialist',
                    'content': 'Architecture patterns identified in config files',
                    'status': 'completed'
                }
            }
        }

        # 格式化文档内容
        formatted_content = self.bmad_orchestrator._format_document_content(document_data)

        # 验证格式化结果
        self.assertIn('# Config Directory Technical Overview', formatted_content)
        self.assertIn('**Generated at:** 2024-01-01 12:00:00', formatted_content)
        self.assertIn('**Agents used:** code-analyst, architecture-analyst', formatted_content)
        self.assertIn('## Alex (Code Analyst)', formatted_content)
        self.assertIn('## Architecture Analyst (Architecture Specialist)', formatted_content)

    @patch('app.utils.claude_client.Anthropic')
    def test_smart_document_service_integration(self, mock_anthropic):
        """测试智能文档服务集成"""
        # 模拟完整的服务交互
        mock_session = Mock()
        mock_session.id = self.test_session_id

        mock_message = Mock()
        mock_message.id = "test-message-id"

        mock_client = Mock()
        mock_client.beta.workspaces.sessions.create.return_value = mock_session
        mock_client.beta.workspaces.sessions.files.create.return_value = Mock()
        mock_client.beta.workspaces.sessions.messages.create.return_value = mock_message
        mock_client.beta.workspaces.sessions.messages.list.return_value = Mock(
            data=[
                Mock(
                    id="msg-1",
                    content="Documentation generation completed successfully",
                    role="assistant",
                    created_at="2024-01-01T00:03:00Z"
                )
            ]
        )
        mock_anthropic.return_value = mock_client

        # 创建服务实例（需要模拟 Flask 应用上下文）
        with patch('app.services.smart_doc_service.current_app') as mock_app:
            mock_app.config.get.side_effect = lambda key, default=None: {
                'CLAUDE_API_KEY': self.test_api_key,
                'CLAUDE_WORKSPACE_ID': self.test_workspace_id,
                'REPOSITORY_BASE_PATH': self.temp_dir
            }.get(key, default)

            service = SmartDocumentService()

            # 验证服务初始化
            self.assertIsNotNone(service.claude_client)
            self.assertIsNotNone(service.bmad_orchestrator)

    def test_file_upload_filtering(self):
        """测试文件上传过滤"""
        # 测试应该上传的文件
        should_upload = [
            'main.py',
            'config.py',
            'requirements.txt',
            'README.md',
            'package.json',
            'Dockerfile',
            'docker-compose.yml',
            'setup.py',
            'pyproject.toml'
        ]

        # 测试不应该上传的文件
        should_not_upload = [
            '.gitignore',
            '.env',
            '__pycache__/file.py',
            'venv/lib/python.py',
            'node_modules/file.js',
            '.DS_Store',
            'temp.txt',
            'backup.bak'
        ]

        # 创建客户端实例
        client = ClaudeCodeClient(self.test_api_key, self.test_workspace_id)

        # 验证文件过滤
        for filename in should_upload:
            self.assertTrue(client._should_upload_file(filename), f"Should upload: {filename}")

        for filename in should_not_upload:
            self.assertFalse(client._should_upload_file(filename), f"Should not upload: {filename}")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)



