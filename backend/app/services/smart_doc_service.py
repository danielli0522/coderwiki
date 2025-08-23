"""
智能文档生成服务
集成 Claude Code SDK 和 BMAD 代理系统
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import current_app
from ..models.task import Task
from ..models.document import Document
from ..models.bmad_agent_execution import BMADAgentExecution
from ..utils.claude_client import ClaudeCodeClient
from ..utils.bmad_orchestrator import BMADOrchestrator
from pathlib import Path

logger = logging.getLogger(__name__)


class SmartDocumentService:
    """智能文档生成服务"""

    def __init__(self):
        """初始化服务"""
        self.claude_client = None
        self.bmad_orchestrator = None
        self._initialize_clients()

    def _initialize_clients(self):
        """初始化 Claude Code 客户端和 BMAD 编排器"""
        try:
            api_key = current_app.config.get('CLAUDE_API_KEY')
            workspace_id = current_app.config.get('CLAUDE_WORKSPACE_ID')

            if not api_key or not workspace_id:
                logger.warning("Claude Code credentials not configured")
                return

            self.claude_client = ClaudeCodeClient(api_key, workspace_id)
            self.bmad_orchestrator = BMADOrchestrator(self.claude_client)
            logger.info("Smart document service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize smart document service: {e}")

    def generate_smart_document(self, repository_id: int, user_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成智能文档

        Args:
            repository_id: 仓库 ID
            user_id: 用户 ID
            config: 生成配置

        Returns:
            生成结果
        """
        try:
            # 1. 创建任务记录
            task = self._create_task(repository_id, user_id, config)

            # 2. 获取仓库路径
            repo_path = self._get_repository_path(repository_id)
            if not repo_path:
                raise Exception("Repository path not found")

            # 3. 执行 BMAD 工作流
            if not self.bmad_orchestrator:
                raise Exception("BMAD orchestrator not initialized")

            workflow_result = self.bmad_orchestrator.execute_workflow(repo_path, config)

            # 4. 更新任务状态
            self._update_task_status(task, workflow_result)

            # 5. 保存生成的文档
            if workflow_result['status'] == 'completed':
                document = self._save_document(repository_id, workflow_result, task)

                # 6. 记录代理执行状态
                self._save_agent_executions(task.id, workflow_result.get('agent_outputs', {}))

                return {
                    'success': True,
                    'task_id': task.id,
                    'document_id': document.id,
                    'session_id': workflow_result.get('session_id'),
                    'execution_time': workflow_result.get('execution_time')
                }
            else:
                return {
                    'success': False,
                    'task_id': task.id,
                    'error': workflow_result.get('error', 'Unknown error')
                }

        except Exception as e:
            logger.error(f"Smart document generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            task_id: 任务 ID

        Returns:
            任务状态
        """
        try:
            task = Task.query.get(task_id)
            if not task:
                return {'error': 'Task not found'}

            # 如果有 Claude Code 会话 ID，获取实时状态
            if task.claude_session_id and self.bmad_orchestrator:
                progress = self.bmad_orchestrator.get_workflow_progress(task.claude_session_id)
                agent_status = self.bmad_orchestrator.get_agent_status(task.claude_session_id)

                return {
                    'task_id': task.id,
                    'status': task.status,
                    'progress': task.progress,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat(),
                    'claude_session_id': task.claude_session_id,
                    'bmad_workflow_id': task.bmad_workflow_id,
                    'real_time_progress': progress,
                    'agent_status': agent_status
                }
            else:
                return {
                    'task_id': task.id,
                    'status': task.status,
                    'progress': task.progress,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat(),
                    'claude_session_id': task.claude_session_id,
                    'bmad_workflow_id': task.bmad_workflow_id
                }

        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {'error': str(e)}

    def get_bmad_agents_status(self, task_id: int) -> Dict[str, Any]:
        """
        获取 BMAD 代理状态

        Args:
            task_id: 任务 ID

        Returns:
            代理状态
        """
        try:
            task = Task.query.get(task_id)
            if not task:
                return {'error': 'Task not found'}

            if not task.claude_session_id or not self.bmad_orchestrator:
                return {'error': 'No active Claude Code session'}

            agent_status = self.bmad_orchestrator.get_agent_status(task.claude_session_id)
            progress = self.bmad_orchestrator.get_workflow_progress(task.claude_session_id)

            return {
                'task_id': task_id,
                'session_id': task.claude_session_id,
                'agent_status': agent_status,
                'progress': progress
            }

        except Exception as e:
            logger.error(f"Failed to get BMAD agents status: {e}")
            return {'error': str(e)}

    def _create_task(self, repository_id: int, user_id: int, config: Dict[str, Any]) -> Task:
        """
        创建任务记录

        Args:
            repository_id: 仓库 ID
            user_id: 用户 ID
            config: 配置

        Returns:
            任务实例
        """
        task = Task(
            repository_id=repository_id,
            type='generation',
            status='pending',
            progress=0,
            config=config
        )

        from .. import db
        db.session.add(task)
        db.session.commit()

        logger.info(f"Created task {task.id} for repository {repository_id}")
        return task

    def _get_repository_path(self, repository_id: int) -> Optional[str]:
        """
        获取仓库路径

        Args:
            repository_id: 仓库 ID

        Returns:
            仓库路径
        """
        from ..models.repository import Repository

        repo = Repository.query.get(repository_id)
        if not repo:
            return None

        # 优先使用repository的local_path字段
        if repo.local_path and os.path.exists(repo.local_path):
            return repo.local_path

        # 如果local_path不存在，则构建路径（兼容性处理）
        repo_name = repo.name
        base_path = current_app.config.get('REPOSITORY_BASE_PATH', str(Path(__file__).parent.parent.parent / 'repos'))
        # 确保使用正确的路径分隔符
        if isinstance(base_path, str):
            repo_path = os.path.join(base_path, repo_name)
        else:
            repo_path = str(base_path / repo_name)

        if not os.path.exists(repo_path):
            logger.warning(f"Repository path does not exist: {repo_path}")
            return None

        return repo_path

    def _update_task_status(self, task: Task, workflow_result: Dict[str, Any]):
        """
        更新任务状态

        Args:
            task: 任务实例
            workflow_result: 工作流结果
        """
        try:
            if workflow_result['status'] == 'completed':
                task.status = 'completed'
                task.progress = 100
                task.claude_session_id = workflow_result.get('session_id')
                task.bmad_workflow_id = workflow_result.get('workflow_id')
            else:
                task.status = 'failed'
                task.error_message = workflow_result.get('error', 'Unknown error')

            from .. import db
            db.session.commit()

            logger.info(f"Updated task {task.id} status to {task.status}")

        except Exception as e:
            logger.error(f"Failed to update task status: {e}")

    def _save_document(self, repository_id: int, workflow_result: Dict[str, Any], task: Task) -> Document:
        """
        保存生成的文档

        Args:
            repository_id: 仓库 ID
            workflow_result: 工作流结果
            task: 任务实例

        Returns:
            文档实例
        """
        try:
            document_data = workflow_result['document']

            # 构建文档内容
            content = self._format_document_content(document_data)

            # 获取最新版本号
            latest_version = Document.query.filter_by(repository_id=repository_id).count() + 1

            # 创建文档存储目录
            import os
            from pathlib import Path
            from datetime import datetime

            # 创建文档存储目录
            docs_dir = Path(__file__).parent.parent.parent / 'docs' / 'generated'
            docs_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            title = document_data.get('title', 'Technical Documentation')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
            file_path = docs_dir / filename

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            document = Document(
                repository_id=repository_id,
                version=latest_version,
                title=document_data.get('title', 'Technical Documentation'),
                content=content,
                doc_type='complete_documentation',
                format='markdown',
                file_path=str(file_path),
                generated_at=datetime.utcnow(),
                status='published'
            )

            from .. import db
            db.session.add(document)
            db.session.commit()

            logger.info(f"Saved document {document.id} for repository {repository_id} (File: {file_path})")
            return document

        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise

    def _save_agent_executions(self, task_id: int, agent_outputs: Dict[str, Dict[str, Any]]):
        """
        保存代理执行记录

        Args:
            task_id: 任务 ID
            agent_outputs: 代理输出
        """
        try:
            for agent_id, output in agent_outputs.items():
                execution = BMADAgentExecution(
                    task_id=task_id,
                    agent_name=output.get('name', ''),
                    agent_role=output.get('role', ''),
                    execution_status=output.get('status', 'pending'),
                    output_content=output.get('content'),
                    start_time=datetime.now(),
                    end_time=datetime.now() if output.get('status') == 'completed' else None
                )

                from .. import db
                db.session.add(execution)

            from .. import db
            db.session.commit()

            logger.info(f"Saved agent executions for task {task_id}")

        except Exception as e:
            logger.error(f"Failed to save agent executions: {e}")

    def _format_document_content(self, document_data: Dict[str, Any]) -> str:
        """
        格式化文档内容

        Args:
            document_data: 文档数据

        Returns:
            格式化的文档内容
        """
        content_parts = []

        # 添加标题
        content_parts.append(f"# {document_data.get('title', 'Technical Documentation')}")
        content_parts.append(f"\n**Generated at:** {document_data.get('generated_at', '')}")
        content_parts.append(f"**Agents used:** {', '.join(document_data.get('agents_used', []))}")
        content_parts.append("\n---\n")

        # 添加各个代理的输出
        sections = document_data.get('sections', {})
        for agent_id, section in sections.items():
            agent_name = section.get('agent_name', '')
            agent_role = section.get('agent_role', '')
            section_content = section.get('content', '')

            content_parts.append(f"## {agent_name} ({agent_role})")
            content_parts.append(f"\n{section_content}\n")
            content_parts.append("---\n")

        return "\n".join(content_parts)

