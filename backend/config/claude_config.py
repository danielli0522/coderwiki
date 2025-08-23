"""
Claude Code 配置文件
"""

import os
from typing import Dict, Any
from pathlib import Path


class ClaudeConfig:
    """Claude Code 配置类"""

    # Claude Code API 配置
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    CLAUDE_WORKSPACE_ID = os.getenv('CLAUDE_WORKSPACE_ID', '')

    # BMAD 代理配置
    BMAD_AGENTS_PATH = os.getenv('BMAD_AGENTS_PATH', 'bmad-docs-generator')
    BMAD_WORKFLOW_TIMEOUT = int(os.getenv('BMAD_WORKFLOW_TIMEOUT', '300'))  # 5分钟

    # 文档生成配置
    REPOSITORY_BASE_PATH = os.getenv('REPOSITORY_BASE_PATH', str(Path(__file__).parent.parent / 'repos'))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
    MAX_FILES_PER_REPO = int(os.getenv('MAX_FILES_PER_REPO', '1000'))

    # 默认生成配置
    DEFAULT_GENERATION_CONFIG = {
        'analysis_depth': 'detailed',
        'include_diagrams': True,
        'include_troubleshooting': True,
        'include_code_examples': True,
        'doc_type': 'complete'
    }

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取完整配置"""
        return {
            'claude_api_key': cls.CLAUDE_API_KEY,
            'claude_workspace_id': cls.CLAUDE_WORKSPACE_ID,
            'bmad_agents_path': cls.BMAD_AGENTS_PATH,
            'bmad_workflow_timeout': cls.BMAD_WORKFLOW_TIMEOUT,
            'repository_base_path': cls.REPOSITORY_BASE_PATH,
            'max_file_size': cls.MAX_FILE_SIZE,
            'max_files_per_repo': cls.MAX_FILES_PER_REPO,
            'default_generation_config': cls.DEFAULT_GENERATION_CONFIG
        }

    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否完整"""
        required_fields = [
            'CLAUDE_API_KEY',
            'CLAUDE_WORKSPACE_ID'
        ]

        for field in required_fields:
            if not getattr(cls, field):
                return False

        return True

    @classmethod
    def get_missing_fields(cls) -> list:
        """获取缺失的配置字段"""
        missing = []

        if not cls.CLAUDE_API_KEY:
            missing.append('CLAUDE_API_KEY')

        if not cls.CLAUDE_WORKSPACE_ID:
            missing.append('CLAUDE_WORKSPACE_ID')

        return missing

