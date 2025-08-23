"""
Task Worker for executing background tasks.
"""

import threading
import time
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Callable, Optional, Any
from app import db
from app.models.task import Task
from app.services.task_service import TaskService
from app.services.task_queue import TaskQueueManager, TaskPriority
from app.utils.git_utils import clone_repository
from app.utils.code_analyzer import analyze_code_structure
from app.services.doc_service import DocService
from app.services.llm_service import LLMService
from app.services.repo_service import RepositoryService


class TaskWorker:
    """Task worker for executing background tasks."""
    
    def __init__(self, max_concurrent_tasks: int = 3, task_timeout: int = 1800):
        """Initialize task worker.
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
            task_timeout: Task timeout in seconds (default: 30 minutes)
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout = task_timeout
        self.queue_manager = TaskQueueManager(max_concurrent_tasks)
        self.task_service = TaskService()
        self.repo_service = RepositoryService()
        self.doc_service = DocService()
        self.llm_service = LLMService()
        self.is_running = False
        self.worker_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Register task handlers
        self._register_task_handlers()
    
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
            running_tasks = self.queue_manager.get_running_tasks()
            
            for task_id in running_tasks:
                task = self.task_service.get_task_by_id(task_id)
                if task and task.started_at:
                    duration = (datetime.utcnow() - task.started_at).total_seconds()
                    
                    if duration > self.task_timeout:
                        # Mark task as failed due to timeout
                        error_msg = f"Task timed out after {duration:.0f} seconds"
                        self.task_service.fail_task(task_id, error_msg)
                        print(f"Task {task_id} timed out: {error_msg}")
                        
        except Exception as e:
            print(f"Error checking timeouts: {e}")
    
    def _process_pending_tasks(self):
        """Process pending tasks from database."""
        try:
            # Get pending tasks that are not already in queue
            pending_tasks = self.task_service.get_pending_tasks(limit=10)
            
            for task in pending_tasks:
                # Check if task is already being processed
                task_info = self.queue_manager.get_task_info(task.id)
                if not task_info:
                    # Add task to queue with appropriate priority
                    priority = self._get_task_priority(task)
                    self.queue_manager.add_task(task.id, priority)
                    
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
        task_age = (datetime.utcnow() - task.created_at).total_seconds()
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
            
            # Clone repository
            self.task_service.update_task_progress(task_id, 20)
            temp_dir = clone_repository(repository.url)
            
            # Analyze code structure
            self.task_service.update_task_progress(task_id, 40)
            code_structure = analyze_code_structure(temp_dir)
            
            # Generate documentation using LLM
            self.task_service.update_task_progress(task_id, 60)
            documentation = self.llm_service.generate_documentation(
                repository.name,
                code_structure
            )
            
            # Save documentation
            self.task_service.update_task_progress(task_id, 80)
            document = self.doc_service.create_document(
                task.user_id,
                task.repository_id,
                f"{repository.name} Documentation",
                documentation,
                task.type
            )
            
            # Complete task
            self.task_service.update_task_progress(task_id, 100)
            
            return {
                'success': True,
                'document_id': document.id,
                'document_title': document.title,
                'message': 'Documentation generated successfully'
            }
            
        except Exception as e:
            error_msg = f"Failed to generate document: {str(e)}"
            raise Exception(error_msg)
    
    def _handle_sync_repository(self, task_id: int) -> Dict[str, Any]:
        """Handle repository synchronization task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict: Task result
        """
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
            temp_dir = clone_repository(repository.url)
            
            # Update repository status
            self.task_service.update_task_progress(task_id, 80)
            self.repo_service.update_repository_status(
                task.repository_id,
                'synced',
                last_synced=datetime.utcnow()
            )
            
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
    
    def _handle_analyze_code(self, task_id: int) -> Dict[str, Any]:
        """Handle code analysis task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict: Task result
        """
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
            temp_dir = clone_repository(repository.url)
            
            # Analyze code structure
            self.task_service.update_task_progress(task_id, 70)
            code_structure = analyze_code_structure(temp_dir)
            
            # Save analysis results
            self.task_service.update_task_progress(task_id, 90)
            analysis_result = {
                'repository_id': repository.id,
                'analysis_date': datetime.utcnow().isoformat(),
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