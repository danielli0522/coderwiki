"""
Task Scheduler for managing and scheduling background tasks.
"""

import threading
import time
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from app import db
from app.models.task import Task
from app.models.repository import Repository
from app.services.task_service import TaskService
from app.services.task_worker import TaskWorker, TaskPriority
from app.services.repo_service import RepositoryService


class ScheduleType(Enum):
    """Schedule types for recurring tasks."""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ScheduledTask:
    """Scheduled task configuration."""
    id: str
    name: str
    task_type: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = None
    repository_ids: List[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.repository_ids is None:
            self.repository_ids = []
        if self.next_run is None:
            self.next_run = self._calculate_next_run()
    
    def _calculate_next_run(self) -> datetime:
        """Calculate next run time based on schedule type."""
        now = datetime.utcnow()
        
        if self.schedule_type == ScheduleType.ONCE:
            config_time = self.schedule_config.get('run_time')
            if config_time:
                if isinstance(config_time, str):
                    return datetime.fromisoformat(config_time)
                return config_time
            return now + timedelta(minutes=1)
        
        elif self.schedule_type == ScheduleType.HOURLY:
            minute = self.schedule_config.get('minute', 0)
            return now.replace(minute=minute, second=0, microsecond=0) + timedelta(hours=1)
        
        elif self.schedule_type == ScheduleType.DAILY:
            hour = self.schedule_config.get('hour', 0)
            minute = self.schedule_config.get('minute', 0)
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time
        
        elif self.schedule_type == ScheduleType.WEEKLY:
            weekday = self.schedule_config.get('weekday', 0)  # 0 = Monday
            hour = self.schedule_config.get('hour', 0)
            minute = self.schedule_config.get('minute', 0)
            
            days_ahead = weekday - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
            if next_time <= now:
                next_time += timedelta(weeks=1)
            return next_time
        
        elif self.schedule_type == ScheduleType.MONTHLY:
            day = self.schedule_config.get('day', 1)
            hour = self.schedule_config.get('hour', 0)
            minute = self.schedule_config.get('minute', 0)
            
            next_time = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                # Move to next month
                if next_time.month == 12:
                    next_time = next_time.replace(year=next_time.year + 1, month=1)
                else:
                    next_time = next_time.replace(month=next_time.month + 1)
            return next_time
        
        return now + timedelta(minutes=1)
    
    def should_run(self) -> bool:
        """Check if task should run now."""
        if not self.is_active:
            return False
        
        if self.next_run is None:
            return False
        
        return datetime.utcnow() >= self.next_run
    
    def update_next_run(self):
        """Update next run time after execution."""
        self.last_run = datetime.utcnow()
        
        if self.schedule_type == ScheduleType.ONCE:
            self.is_active = False
            self.next_run = None
        else:
            self.next_run = self._calculate_next_run()


class TaskScheduler:
    """Task scheduler for managing recurring and scheduled tasks."""
    
    def __init__(self, task_worker: TaskWorker):
        """Initialize task scheduler.
        
        Args:
            task_worker: Task worker instance
        """
        self.task_worker = task_worker
        self.task_service = TaskService()
        self.repo_service = RepositoryService()
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.is_running = False
        self.scheduler_thread = None
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_scheduled': 0,
            'tasks_executed': 0,
            'tasks_failed': 0,
            'last_execution': None,
            'next_execution': None
        }
    
    def start(self):
        """Start the task scheduler."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Set up periodic schedules
        self._setup_schedules()
        
        print("Task scheduler started")
    
    def stop(self):
        """Stop the task scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # Clear schedules
        schedule.clear()
        
        print("Task scheduler stopped")
    
    def _setup_schedules(self):
        """Set up periodic schedules."""
        # Schedule repository sync checks
        schedule.every(5).minutes.do(self._check_repository_syncs)
        
        # Schedule task cleanup
        schedule.every(1).hours.do(self._cleanup_old_tasks)
        
        # Schedule failed task retry
        schedule.every(10).minutes.do(self._retry_failed_tasks)
        
        # Schedule statistics update
        schedule.every(30).minutes.do(self._update_statistics)
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                # Run pending scheduled tasks
                self._run_scheduled_tasks()
                
                # Run schedule library jobs
                schedule.run_pending()
                
                # Update next execution time
                self._update_next_execution()
                
                # Sleep for a while
                time.sleep(10)
                
            except Exception as e:
                print(f"Scheduler loop error: {e}")
                time.sleep(30)
    
    def _run_scheduled_tasks(self):
        """Run scheduled tasks that are due."""
        with self.lock:
            tasks_to_run = []
            for task_id, scheduled_task in self.scheduled_tasks.items():
                if scheduled_task.should_run():
                    tasks_to_run.append(scheduled_task)
        
        for scheduled_task in tasks_to_run:
            try:
                self._execute_scheduled_task(scheduled_task)
            except Exception as e:
                print(f"Error executing scheduled task {scheduled_task.id}: {e}")
                self.stats['tasks_failed'] += 1
    
    def _execute_scheduled_task(self, scheduled_task: ScheduledTask):
        """Execute a scheduled task.
        
        Args:
            scheduled_task: Scheduled task to execute
        """
        try:
            print(f"Executing scheduled task: {scheduled_task.name}")
            
            if scheduled_task.repository_ids:
                # Execute for specific repositories
                for repo_id in scheduled_task.repository_ids:
                    self._create_task_for_repository(
                        scheduled_task.task_type,
                        repo_id,
                        scheduled_task.id
                    )
            else:
                # Execute for all repositories
                repositories = self.repo_service.get_all_repositories()
                for repo in repositories:
                    self._create_task_for_repository(
                        scheduled_task.task_type,
                        repo.id,
                        scheduled_task.id
                    )
            
            # Update scheduled task
            scheduled_task.update_next_run()
            self.stats['tasks_executed'] += 1
            self.stats['last_execution'] = datetime.utcnow()
            
            print(f"Scheduled task {scheduled_task.name} completed")
            
        except Exception as e:
            print(f"Error executing scheduled task {scheduled_task.name}: {e}")
            raise
    
    def _create_task_for_repository(self, task_type: str, repository_id: int, schedule_id: str):
        """Create a task for a specific repository.
        
        Args:
            task_type: Type of task to create
            repository_id: Repository ID
            schedule_id: Schedule ID for tracking
        """
        try:
            # Check if there's already a pending task for this repository
            existing_tasks = self.task_service.get_user_tasks(
                user_id=1,  # System user
                repository_id=repository_id,
                status='pending',
                task_type=task_type
            )
            
            if existing_tasks:
                return  # Skip if there's already a pending task
            
            # Create new task
            task = self.task_service.create_task(
                user_id=1,  # System user
                repository_id=repository_id,
                task_type=task_type
            )
            
            # Add to worker queue
            self.task_worker.add_task(task.id, TaskPriority.NORMAL)
            
        except Exception as e:
            print(f"Error creating task for repository {repository_id}: {e}")
    
    def _check_repository_syncs(self):
        """Check for repositories that need syncing."""
        try:
            repositories = self.repo_service.get_repositories_needing_sync()
            
            for repo in repositories:
                # Check if there's already a sync task
                existing_tasks = self.task_service.get_user_tasks(
                    user_id=1,
                    repository_id=repo.id,
                    status='pending',
                    task_type='sync_repository'
                )
                
                if not existing_tasks:
                    # Create sync task
                    task = self.task_service.create_task(
                        user_id=1,
                        repository_id=repo.id,
                        task_type='sync_repository'
                    )
                    
                    # Add to worker queue
                    self.task_worker.add_task(task.id, TaskPriority.LOW)
                    
        except Exception as e:
            print(f"Error checking repository syncs: {e}")
    
    def _cleanup_old_tasks(self):
        """Clean up old completed tasks."""
        try:
            self.task_worker.cleanup_old_tasks(days=7)
        except Exception as e:
            print(f"Error cleaning up old tasks: {e}")
    
    def _retry_failed_tasks(self):
        """Retry failed tasks."""
        try:
            restarted_count = self.task_worker.restart_failed_tasks()
            if restarted_count > 0:
                print(f"Restarted {restarted_count} failed tasks")
        except Exception as e:
            print(f"Error retrying failed tasks: {e}")
    
    def _update_statistics(self):
        """Update scheduler statistics."""
        try:
            with self.lock:
                self.stats['total_scheduled'] = len(self.scheduled_tasks)
                
                # Find next execution time
                next_executions = []
                for task in self.scheduled_tasks.values():
                    if task.is_active and task.next_run:
                        next_executions.append(task.next_run)
                
                if next_executions:
                    self.stats['next_execution'] = min(next_executions)
                else:
                    self.stats['next_execution'] = None
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def _update_next_execution(self):
        """Update the next execution time."""
        try:
            with self.lock:
                next_executions = []
                for task in self.scheduled_tasks.values():
                    if task.is_active and task.next_run:
                        next_executions.append(task.next_run)
                
                if next_executions:
                    self.stats['next_execution'] = min(next_executions)
                else:
                    self.stats['next_execution'] = None
        except Exception as e:
            print(f"Error updating next execution: {e}")
    
    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> bool:
        """Add a scheduled task.
        
        Args:
            scheduled_task: Scheduled task to add
            
        Returns:
            bool: True if task was added successfully
        """
        try:
            with self.lock:
                self.scheduled_tasks[scheduled_task.id] = scheduled_task
                self.stats['total_scheduled'] += 1
            
            print(f"Added scheduled task: {scheduled_task.name}")
            return True
            
        except Exception as e:
            print(f"Error adding scheduled task: {e}")
            return False
    
    def remove_scheduled_task(self, task_id: str) -> bool:
        """Remove a scheduled task.
        
        Args:
            task_id: Task ID to remove
            
        Returns:
            bool: True if task was removed successfully
        """
        try:
            with self.lock:
                if task_id in self.scheduled_tasks:
                    del self.scheduled_tasks[task_id]
                    self.stats['total_scheduled'] -= 1
                    print(f"Removed scheduled task: {task_id}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error removing scheduled task: {e}")
            return False
    
    def get_scheduled_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a scheduled task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            ScheduledTask or None
        """
        with self.lock:
            return self.scheduled_tasks.get(task_id)
    
    def get_all_scheduled_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks.
        
        Returns:
            List[ScheduledTask]: List of scheduled tasks
        """
        with self.lock:
            return list(self.scheduled_tasks.values())
    
    def update_scheduled_task(self, task_id: str, **kwargs) -> bool:
        """Update a scheduled task.
        
        Args:
            task_id: Task ID to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if task was updated successfully
        """
        try:
            with self.lock:
                if task_id not in self.scheduled_tasks:
                    return False
                
                task = self.scheduled_tasks[task_id]
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                
                # Recalculate next run time if schedule changed
                if 'schedule_type' in kwargs or 'schedule_config' in kwargs:
                    task.next_run = task._calculate_next_run()
                
                print(f"Updated scheduled task: {task_id}")
                return True
            
        except Exception as e:
            print(f"Error updating scheduled task: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status.
        
        Returns:
            Dict: Scheduler status information
        """
        with self.lock:
            return {
                'is_running': self.is_running,
                'scheduled_tasks_count': len(self.scheduled_tasks),
                'stats': self.stats.copy(),
                'scheduled_tasks': [
                    {
                        'id': task.id,
                        'name': task.name,
                        'task_type': task.task_type,
                        'schedule_type': task.schedule_type.value,
                        'is_active': task.is_active,
                        'last_run': task.last_run.isoformat() if task.last_run else None,
                        'next_run': task.next_run.isoformat() if task.next_run else None,
                        'repository_count': len(task.repository_ids)
                    }
                    for task in self.scheduled_tasks.values()
                ]
            }
    
    def create_daily_sync_schedule(self, name: str, hour: int = 2, minute: int = 0, repository_ids: List[int] = None) -> str:
        """Create a daily repository sync schedule.
        
        Args:
            name: Schedule name
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            repository_ids: List of repository IDs to sync (None for all)
            
        Returns:
            str: Schedule ID
        """
        schedule_id = f"daily_sync_{name}_{int(time.time())}"
        
        scheduled_task = ScheduledTask(
            id=schedule_id,
            name=name,
            task_type='sync_repository',
            schedule_type=ScheduleType.DAILY,
            schedule_config={'hour': hour, 'minute': minute},
            repository_ids=repository_ids or []
        )
        
        self.add_scheduled_task(scheduled_task)
        return schedule_id
    
    def create_daily_analysis_schedule(self, name: str, hour: int = 3, minute: int = 0, repository_ids: List[int] = None) -> str:
        """Create a daily code analysis schedule.
        
        Args:
            name: Schedule name
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            repository_ids: List of repository IDs to analyze (None for all)
            
        Returns:
            str: Schedule ID
        """
        schedule_id = f"daily_analysis_{name}_{int(time.time())}"
        
        scheduled_task = ScheduledTask(
            id=schedule_id,
            name=name,
            task_type='analyze_code',
            schedule_type=ScheduleType.DAILY,
            schedule_config={'hour': hour, 'minute': minute},
            repository_ids=repository_ids or []
        )
        
        self.add_scheduled_task(scheduled_task)
        return schedule_id