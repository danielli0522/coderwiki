"""
Task Worker for executing background tasks.
"""

import threading
import time
import signal
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Callable, Optional, Any
from flask import current_app
from app import db
from app.models.task import Task
from app.services.task_service import TaskService
from app.services.task_queue import TaskQueueManager, TaskPriority
from app.utils.git_service import GitService
# from app.utils.code_analyzer import analyze_code_structure  # Function not found
from app.services.doc_service import DocumentService
from app.services.llm_service import LLMService
from app.services.repo_service import RepositoryService


class TaskWorker:
    """Task worker for executing background tasks."""

    def __init__(self, app=None, max_concurrent_tasks: int = 3, task_timeout: int = 1800):
        """Initialize task worker.

        Args:
            app: Flask application instance
            max_concurrent_tasks: Maximum number of concurrent tasks
            task_timeout: Task timeout in seconds (default: 30 minutes)
        """
        self.app = app
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout = task_timeout
        self.queue_manager = TaskQueueManager(max_concurrent_tasks, app=self.app)
        self.task_service = TaskService()
        self.repo_service = RepositoryService()
        self.doc_service = DocumentService()
        self.llm_service = LLMService()
        self.git_service = GitService()
        self.is_running = False
        self.worker_thread = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Register task handlers
        self._register_task_handlers()

    def _ensure_app_context(self, func):
        """Decorator to ensure Flask app context for database operations."""
        def wrapper(*args, **kwargs):
            if self.app:
                with self.app.app_context():
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper

    def _register_task_handlers(self):
        """Register task handlers for different task types."""
        self.queue_manager.register_task_handler('generate_document', self._handle_generate_document)
        self.queue_manager.register_task_handler('sync_repository', self._handle_sync_repository)
        self.queue_manager.register_task_handler('analyze_code', self._handle_analyze_code)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the task worker."""
        if self.is_running:
            return

        self.is_running = True
        self.queue_manager.start_worker()

        # Start monitoring thread
        self.worker_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.worker_thread.start()

        print("Task worker started")

    def stop(self):
        """Stop the task worker."""
        if not self.is_running:
            return

        self.is_running = False
        self.queue_manager.stop_worker()

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)

        print("Task worker stopped")

    def _monitor_loop(self):
        """Monitor task execution and handle timeouts."""
        while self.is_running:
            try:
                # Check for timed out tasks
                self._check_timeouts()

                # Process pending tasks from database
                self._process_pending_tasks()

                # Update task statistics
                self._update_statistics()

                # Sleep for a while
                time.sleep(5)

            except Exception as e:
                print(f"Monitor loop error: {e}")
                time.sleep(10)

    def _check_timeouts(self):
        """Check for tasks that have timed out."""
        try:
            def _do_check_timeouts():
                running_tasks = self.queue_manager.get_running_tasks()

                for task_id in running_tasks:
                    task = self.task_service.get_task_by_id(task_id)
                    if task and task.started_at:
                        # Handle timezone-aware and timezone-naive datetime comparison
                        if task.started_at.tzinfo is None:
                            # If started_at is timezone-naive, assume it's UTC
                            started_at_utc = task.started_at.replace(tzinfo=timezone.utc)
                        else:
                            started_at_utc = task.started_at
                        duration = (datetime.now(timezone.utc) - started_at_utc).total_seconds()

                        if duration > self.task_timeout:
                            # Mark task as failed due to timeout
                            error_msg = f"Task timed out after {duration:.0f} seconds"
                            self.task_service.fail_task(task_id, error_msg)
                            print(f"Task {task_id} timed out: {error_msg}")

            # Execute with app context
            self._ensure_app_context(_do_check_timeouts)()

        except Exception as e:
            print(f"Error checking timeouts: {e}")

    def _process_pending_tasks(self):
        """Process pending tasks from database."""
        try:
            def _do_process_pending_tasks():
                # Get pending tasks that are not already in queue
                pending_tasks = self.task_service.get_pending_tasks(limit=10)

                for task in pending_tasks:
                    # Check if task is already being processed
                    task_info = self.queue_manager.get_task_info(task.id)
                    if not task_info:
                        # Add task to queue with appropriate priority
                        priority = self._get_task_priority(task)
                        self.queue_manager.add_task(task.id, priority)

            # Execute with app context
            self._ensure_app_context(_do_process_pending_tasks)()

        except Exception as e:
            print(f"Error processing pending tasks: {e}")

    def _get_task_priority(self, task: Task) -> TaskPriority:
        """Get priority for a task based on its type and age."""
        # Base priority by task type
        type_priority = {
            'generate_document': TaskPriority.NORMAL,
            'sync_repository': TaskPriority.LOW,
            'analyze_code': TaskPriority.NORMAL
        }

        priority = type_priority.get(task.type, TaskPriority.NORMAL)

        # Increase priority for old tasks
        # Handle timezone-aware and timezone-naive datetime comparison
        if task.created_at.tzinfo is None:
            # If created_at is timezone-naive, assume it's UTC
            created_at_utc = task.created_at.replace(tzinfo=timezone.utc)
        else:
            created_at_utc = task.created_at
        task_age = (datetime.now(timezone.utc) - created_at_utc).total_seconds()
        if task_age > 300:  # 5 minutes
            priority = TaskPriority.HIGH
        elif task_age > 600:  # 10 minutes
            priority = TaskPriority.URGENT

        return priority

    def _update_statistics(self):
        """Update task statistics."""
        try:
            # This could be expanded to update database statistics
            pass
        except Exception as e:
            print(f"Error updating statistics: {e}")

    def _handle_generate_document(self, task_id: int) -> Dict[str, Any]:
        """Handle document generation task.

        Args:
            task_id: Task ID

        Returns:
            Dict: Task result
        """
        def _do_generate_document():
            try:
                task = self.task_service.get_task_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")

                # Update progress
                self.task_service.update_task_progress(task_id, 10)

                # Get repository
                repository = self.repo_service.get_repository_by_id(task.repository_id)
                if not repository:
                    raise ValueError(f"Repository {task.repository_id} not found")

                # Get or clone repository
                self.task_service.update_task_progress(task_id, 20)

                local_path = None
                if repository.local_path and os.path.exists(repository.local_path):
                    # Use existing local repository
                    local_path = repository.local_path
                    print(f"Using existing repository at: {local_path}")
                else:
                    # Clone repository
                    clone_result = self.git_service.clone_repository(repository.url)
                    if not clone_result['success']:
                        raise ValueError(f"Failed to clone repository: {clone_result['error']}")
                    local_path = clone_result['local_path']

                    # Update repository with local path
                    repository.local_path = local_path
                    db.session.commit()

                # Analyze code structure (simplified for now)
                self.task_service.update_task_progress(task_id, 40)
                code_structure = {
                    'repository_name': repository.name,
                    'url': repository.url,
                    'local_path': local_path
                }

                # Generate documentation using LLM
                self.task_service.update_task_progress(task_id, 60)
                documentation = self.llm_service.generate_documentation(
                    repository.name,
                    code_structure
                )

                # Save documentation
                self.task_service.update_task_progress(task_id, 80)
                document_result = self.doc_service.create_document(
                    task.user_id,
                    f"{repository.name} Documentation",
                    task.repository_id,
                    task.type,
                    description=f"Generated documentation for {repository.name}",
                    content=documentation,  # 传递生成的文档内容
                    skip_permission_check=True  # 系统级操作，跳过权限检查
                )

                # Complete task
                self.task_service.update_task_progress(task_id, 100)

                return {
                    'success': True,
                    'document_id': document_result['id'],
                    'document_title': document_result['title'],
                    'message': 'Documentation generated successfully'
                }

            except Exception as e:
                error_msg = f"Failed to generate document: {str(e)}"
                raise Exception(error_msg)

        # Execute with app context
        return self._ensure_app_context(_do_generate_document)()

    def _handle_sync_repository(self, task_id: int) -> Dict[str, Any]:
        """Handle repository synchronization task.

        Args:
            task_id: Task ID

        Returns:
            Dict: Task result
        """
        def _do_sync_repository():
            try:
                task = self.task_service.get_task_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")

                # Update progress
                self.task_service.update_task_progress(task_id, 20)

                # Get repository
                repository = self.repo_service.get_repository_by_id(task.repository_id)
                if not repository:
                    raise ValueError(f"Repository {task.repository_id} not found")

                # Sync repository (pull latest changes)
                self.task_service.update_task_progress(task_id, 50)

                if repository.local_path:
                    # Update existing repository
                    update_result = self.git_service.update_repository(repository.local_path)

                    if update_result['success']:
                        # Update repository information
                        repository.status = 'active'
                        repository.last_synced_at = datetime.now(timezone.utc)
                        db.session.commit()
                    else:
                        repository.status = 'error'
                        db.session.commit()
                        raise Exception(f"Failed to update repository: {update_result['error']}")
                else:
                    # Clone new repository
                    clone_result = self.git_service.clone_repository(repository.url)

                    if clone_result['success']:
                        # Update repository information
                        repository.local_path = clone_result['local_path']
                        repository.branch = clone_result.get('branch', 'main')
                        repository.status = 'active'
                        repository.last_synced_at = datetime.now(timezone.utc)
                        db.session.commit()
                    else:
                        repository.status = 'error'
                        db.session.commit()
                        raise Exception(f"Failed to clone repository: {clone_result['error']}")

                # Complete task
                self.task_service.update_task_progress(task_id, 100)

                return {
                    'success': True,
                    'repository_id': repository.id,
                    'repository_name': repository.name,
                    'message': 'Repository synchronized successfully'
                }

            except Exception as e:
                error_msg = f"Failed to sync repository: {str(e)}"
                raise Exception(error_msg)

        # Execute with app context
        return self._ensure_app_context(_do_sync_repository)()

    def _handle_analyze_code(self, task_id: int) -> Dict[str, Any]:
        """Handle code analysis task.

        Args:
            task_id: Task ID

        Returns:
            Dict: Task result
        """
        def _do_analyze_code():
            try:
                task = self.task_service.get_task_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")

                # Update progress
                self.task_service.update_task_progress(task_id, 20)

                # Get repository
                repository = self.repo_service.get_repository_by_id(task.repository_id)
                if not repository:
                    raise ValueError(f"Repository {task.repository_id} not found")

                # Clone repository
                self.task_service.update_task_progress(task_id, 40)
                clone_result = self.git_service.clone_repository(repository.url)

                if not clone_result['success']:
                    raise ValueError(f"Failed to clone repository: {clone_result['error']}")

                # Analyze code structure (simplified for now)
                self.task_service.update_task_progress(task_id, 70)
                code_structure = {
                    'repository_name': repository.name,
                    'url': repository.url,
                    'local_path': clone_result['local_path'],
                    'files': [],
                    'languages': {},
                    'complexity': {}
                }

                # Save analysis results
                self.task_service.update_task_progress(task_id, 90)
                analysis_result = {
                    'repository_id': repository.id,
                    'analysis_date': datetime.now(timezone.utc).isoformat(),
                    'code_structure': code_structure,
                    'summary': {
                        'total_files': len(code_structure.get('files', [])),
                        'languages': code_structure.get('languages', {}),
                        'complexity': code_structure.get('complexity', {})
                    }
                }

                # Complete task
                self.task_service.update_task_progress(task_id, 100)

                return {
                    'success': True,
                    'analysis_result': analysis_result,
                    'message': 'Code analysis completed successfully'
                }

            except Exception as e:
                error_msg = f"Failed to analyze code: {str(e)}"
                raise Exception(error_msg)

        # Execute with app context
        return self._ensure_app_context(_do_analyze_code)()

    def get_status(self) -> Dict[str, Any]:
        """Get worker status.

        Returns:
            Dict: Worker status information
        """
        queue_status = self.queue_manager.get_queue_status()

        return {
            'is_running': self.is_running,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'task_timeout': self.task_timeout,
            'queue_status': queue_status
        }

    def add_task(self, task_id: int, priority: TaskPriority = TaskPriority.NORMAL) -> bool:
        """Add a task to the worker queue.

        Args:
            task_id: Task ID
            priority: Task priority

        Returns:
            bool: True if task was added successfully
        """
        return self.queue_manager.add_task(task_id, priority)

    def cancel_task(self, task_id: int) -> bool:
        """Cancel a task.

        Args:
            task_id: Task ID

        Returns:
            bool: True if task was cancelled
        """
        return self.queue_manager.cancel_task(task_id)

    def get_task_info(self, task_id: int) -> Optional[Dict]:
        """Get information about a specific task.

        Args:
            task_id: Task ID

        Returns:
            Dict or None: Task information
        """
        return self.queue_manager.get_task_info(task_id)

    def restart_failed_tasks(self) -> int:
        """Restart all failed tasks.

        Returns:
            int: Number of tasks restarted
        """
        return self.queue_manager.restart_failed_tasks()

    def cleanup_old_tasks(self, days: int = 7):
        """Clean up old completed tasks.

        Args:
            days: Age of tasks to clean up
        """
        self.task_service.cleanup_old_tasks(days)
        self.queue_manager.cleanup_completed_tasks(days * 24)  # Convert to hours
