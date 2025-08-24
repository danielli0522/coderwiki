"""
Task Queue Manager for managing background task queues.
"""

import threading
import time
import queue
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from flask import current_app
from app import db
from app.models.task import Task
from app.services.task_service import TaskService


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class QueueTask:
    """Task wrapper for queue management."""
    task_id: int
    priority: TaskPriority
    created_at: datetime
    retry_count: int = 0
    max_retries: int = 3

    def __lt__(self, other):
        """Priority queue comparison."""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        return self.created_at < other.created_at


class TaskQueueManager:
    """Manages task queues with priority and concurrency control."""

    def __init__(self, max_concurrent_tasks: int = 5, app=None):
        """Initialize task queue manager.

        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
            app: Flask application instance
        """
        self.app = app
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[int, QueueTask] = {}
        self.completed_tasks: List[int] = []
        self.failed_tasks: List[int] = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.worker_threads: List[threading.Thread] = []
        self.task_handlers: Dict[str, Callable] = {}
        self.is_running = False

        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'running_tasks': 0,
            'queued_tasks': 0,
            'avg_completion_time': 0,
            'total_completion_time': 0,
            'start_time': datetime.utcnow()
        }

    def _ensure_app_context(self, func):
        """Decorator to ensure Flask app context for database operations."""
        def wrapper(*args, **kwargs):
            if self.app:
                with self.app.app_context():
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper

    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler for a specific task type.

        Args:
            task_type: Type of task to handle
            handler: Function to handle the task
        """
        self.task_handlers[task_type] = handler

    def add_task(self, task_id: int, priority: TaskPriority = TaskPriority.NORMAL) -> bool:
        """Add a task to the queue.

        Args:
            task_id: Database task ID
            priority: Task priority level

        Returns:
            bool: True if task was added successfully
        """
        try:
            # Get task from database
            task_service = TaskService()
            task = task_service.get_task_by_id(task_id)

            if not task:
                return False

            if task.status != 'pending':
                return False

            # Create queue task
            queue_task = QueueTask(
                task_id=task_id,
                priority=priority,
                created_at=datetime.utcnow()
            )

            # Add to queue
            self.task_queue.put(queue_task)

            with self.lock:
                self.stats['total_tasks'] += 1
                self.stats['queued_tasks'] += 1

            return True

        except Exception as e:
            print(f"Error adding task to queue: {e}")
            return False

    def get_next_task(self) -> Optional[QueueTask]:
        """Get the next task from the queue.

        Returns:
            QueueTask or None if no tasks available
        """
        try:
            if self.task_queue.empty():
                return None

            return self.task_queue.get_nowait()

        except queue.Empty:
            return None

    def start_worker(self):
        """Start worker threads."""
        if self.is_running:
            return

        self.is_running = True
        self.stop_event.clear()

        # Start worker threads
        for i in range(self.max_concurrent_tasks):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)

    def stop_worker(self):
        """Stop worker threads."""
        self.is_running = False
        self.stop_event.set()

        # Wait for workers to finish
        for worker in self.worker_threads:
            if worker.is_alive():
                worker.join(timeout=5)

        self.worker_threads.clear()

    def _worker_loop(self):
        """Worker thread main loop."""
        while not self.stop_event.is_set():
            try:
                # Check if we can start a new task
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    time.sleep(0.1)
                    continue

                # Get next task
                queue_task = self.get_next_task()
                if not queue_task:
                    time.sleep(0.1)
                    continue

                # Start task
                self._execute_task(queue_task)

            except Exception as e:
                print(f"Worker loop error: {e}")
                time.sleep(1)

    def _execute_task(self, queue_task: QueueTask):
        """Execute a task.

        Args:
            queue_task: Task to execute
        """
        def _do_execute_task():
            task_id = queue_task.task_id

            try:
                # Mark task as running
                with self.lock:
                    self.running_tasks[task_id] = queue_task
                    self.stats['running_tasks'] += 1
                    self.stats['queued_tasks'] -= 1

                # Update task status in database
                task_service = TaskService()
                task_service.start_task(task_id)

                # Get task handler
                task = task_service.get_task_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")

                handler = self.task_handlers.get(task.type)
                if not handler:
                    raise ValueError(f"No handler for task type: {task.type}")

                # Execute task
                result = handler(task_id)

                # Mark task as completed
                task_service.complete_task(task_id, result=str(result))

                with self.lock:
                    self.running_tasks.pop(task_id, None)
                    self.completed_tasks.append(task_id)
                    self.stats['completed_tasks'] += 1
                    self.stats['running_tasks'] -= 1

                    # Update completion time stats (simplified)
                    if self.stats['completed_tasks'] > 0:
                        self.stats['avg_completion_time'] = (
                            self.stats['total_completion_time'] / self.stats['completed_tasks']
                        )

            except Exception as e:
                error_msg = str(e)

                # Handle retry logic
                if queue_task.retry_count < queue_task.max_retries:
                    queue_task.retry_count += 1

                    # Re-queue with lower priority
                    new_priority = TaskPriority.LOW if queue_task.retry_count > 1 else TaskPriority.NORMAL
                    queue_task.priority = new_priority

                    self.task_queue.put(queue_task)

                    with self.lock:
                        self.running_tasks.pop(task_id, None)
                        self.stats['running_tasks'] -= 1
                        self.stats['queued_tasks'] += 1
                else:
                    # Mark task as failed
                    try:
                        task_service = TaskService()
                        task_service.fail_task(task_id, error_msg)
                    except Exception as db_error:
                        print(f"Failed to mark task as failed: {db_error}")

                    with self.lock:
                        self.running_tasks.pop(task_id, None)
                        self.failed_tasks.append(task_id)
                        self.stats['failed_tasks'] += 1
                        self.stats['running_tasks'] -= 1

                print(f"Task {task_id} failed: {error_msg}")

        # Execute with app context
        self._ensure_app_context(_do_execute_task)()

    def get_queue_status(self) -> Dict:
        """Get current queue status.

        Returns:
            Dict: Queue status information
        """
        with self.lock:
            return {
                'is_running': self.is_running,
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'running_tasks': len(self.running_tasks),
                'queued_tasks': self.task_queue.qsize(),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'stats': self.stats.copy()
            }

    def cancel_task(self, task_id: int) -> bool:
        """Cancel a task.

        Args:
            task_id: Task ID to cancel

        Returns:
            bool: True if task was cancelled
        """
        with self.lock:
            # Check if task is running
            if task_id in self.running_tasks:
                # Cannot cancel running tasks in this implementation
                return False

            # Check if task is in queue (hard to remove from priority queue)
            # For now, we'll mark it as failed in the database
            try:
                task_service = TaskService()
                task_service.fail_task(task_id, "Task cancelled by user")
                return True
            except Exception:
                return False

    def get_running_tasks(self) -> List[int]:
        """Get list of currently running task IDs.

        Returns:
            List[int]: List of running task IDs
        """
        with self.lock:
            return list(self.running_tasks.keys())

    def get_task_info(self, task_id: int) -> Optional[Dict]:
        """Get information about a specific task.

        Args:
            task_id: Task ID

        Returns:
            Dict or None: Task information
        """
        with self.lock:
            if task_id in self.running_tasks:
                queue_task = self.running_tasks[task_id]
                return {
                    'task_id': task_id,
                    'status': 'running',
                    'priority': queue_task.priority.name,
                    'retry_count': queue_task.retry_count,
                    'max_retries': queue_task.max_retries,
                    'created_at': queue_task.created_at.isoformat()
                }
            elif task_id in self.completed_tasks:
                return {'task_id': task_id, 'status': 'completed'}
            elif task_id in self.failed_tasks:
                return {'task_id': task_id, 'status': 'failed'}
            else:
                return None

    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks from memory.

        Args:
            max_age_hours: Maximum age of tasks to keep
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        with self.lock:
            # Clean up completed tasks
            self.completed_tasks = [
                task_id for task_id in self.completed_tasks
                if self._get_task_completion_time(task_id) > cutoff_time
            ]

            # Clean up failed tasks
            self.failed_tasks = [
                task_id for task_id in self.failed_tasks
                if self._get_task_completion_time(task_id) > cutoff_time
            ]

    def _get_task_completion_time(self, task_id: int) -> datetime:
        """Get task completion time from database.

        Args:
            task_id: Task ID

        Returns:
            datetime: Completion time
        """
        try:
            task_service = TaskService()
            task = task_service.get_task_by_id(task_id)
            return task.completed_at or datetime.utcnow()
        except Exception:
            return datetime.utcnow()

    def restart_failed_tasks(self) -> int:
        """Restart all failed tasks.

        Returns:
            int: Number of tasks restarted
        """
        restarted_count = 0

        with self.lock:
            failed_task_ids = self.failed_tasks.copy()
            self.failed_tasks.clear()

        for task_id in failed_task_ids:
            try:
                # Reset task status to pending
                task_service = TaskService()
                task_service.update_task_status(task_id, 'pending')

                # Add back to queue
                self.add_task(task_id, TaskPriority.NORMAL)
                restarted_count += 1

            except Exception as e:
                print(f"Failed to restart task {task_id}: {e}")

        return restarted_count
