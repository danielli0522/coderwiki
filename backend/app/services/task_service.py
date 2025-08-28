"""
Task service for managing background tasks.
"""

from datetime import datetime
from flask import current_app
from app import db
from app.models.task import Task

class TaskService:
    """Task service for handling background task management."""

    def __init__(self):
        """Initialize the task service."""
        pass

    def create_task(self, user_id, repository_id, task_type, priority=None):
        """Create a new task.

        Args:
            user_id (int): User ID
            repository_id (int): Repository ID
            task_type (str): Task type
            priority (str, optional): Task priority. If not provided, will be set based on task type

        Returns:
            Task: The created task object
        """
        # Set default priority based on task type if not provided
        if priority is None:
            priority_map = {
                'generate_document': 'normal',
                'sync_repository': 'low',
                'analyze_code': 'normal'
            }
            priority = priority_map.get(task_type, 'normal')

        task = Task(
            user_id=user_id,
            repository_id=repository_id,
            type=task_type,
            status='pending',
            progress=0,
            title=f'{task_type} task',
            description=f'Automated {task_type} task',
            priority=priority
        )

        db.session.add(task)
        db.session.commit()

        return task

    def get_user_tasks(self, user_id, repository_id=None, status=None, task_type=None):
        """Get tasks for a user.

        Args:
            user_id (int): User ID
            repository_id (int, optional): Filter by repository
            status (str, optional): Filter by status
            task_type (str, optional): Filter by task type

        Returns:
            list: List of task objects
        """
        query = Task.query.filter_by(user_id=user_id)

        if repository_id:
            query = query.filter_by(repository_id=repository_id)

        if status:
            query = query.filter_by(status=status)

        if task_type:
            query = query.filter_by(type=task_type)

        return query.order_by(Task.created_at.desc()).all()

    def get_task_by_id(self, task_id, user_id=None):
        """Get task by ID.

        Args:
            task_id (int): Task ID
            user_id (int, optional): User ID for permission check

        Returns:
            Task: Task object or None if not found
        """
        query = Task.query.filter_by(id=task_id)

        if user_id:
            query = query.filter_by(user_id=user_id)

        return query.first()

    def update_task_status(self, task_id, status, progress=None, result=None, error_message=None):
        """Update task status.

        Args:
            task_id (int): Task ID
            status (str): New status
            progress (int, optional): Progress percentage
            result (str, optional): Task result
            error_message (str, optional): Error message

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found
        """
        task = Task.query.get(task_id)
        if not task:
            raise ValueError("任务不存在")

        task.status = status

        if progress is not None:
            task.progress = progress

        if result is not None:
            task.result = result

        if error_message is not None:
            task.error_message = error_message

        # Update timestamps based on status
        if status == 'running' and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in ['completed', 'failed']:
            task.completed_at = datetime.utcnow()

        task.updated_at = datetime.utcnow()
        db.session.commit()

        # Broadcast task update via WebSocket
        self._broadcast_task_update(task)

        return task

    def _broadcast_task_update(self, task):
        """Broadcast task update via WebSocket."""
        try:
            if hasattr(current_app, 'broadcast_to_channel'):
                # Broadcast to user-specific channel
                user_channel = f'user:{task.user_id}'
                current_app.broadcast_to_channel(user_channel, {
                    'type': 'task_update',
                    'task_id': task.id,
                    'status': task.status,
                    'progress': task.progress,
                    'title': task.title,
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                    'error_message': task.error_message
                })
                
                # Broadcast to general task updates channel
                current_app.broadcast_to_channel('tasks:updates', {
                    'type': 'task_update',
                    'task_id': task.id,
                    'user_id': task.user_id,
                    'status': task.status,
                    'progress': task.progress,
                    'title': task.title
                })
        except Exception as e:
            # Log error but don't fail the task update
            current_app.logger.warning(f'Failed to broadcast task update: {e}')

    def start_task(self, task_id, user_id=None):
        """Start a task.

        Args:
            task_id (int): Task ID
            user_id (int, optional): User ID for permission check

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or user doesn't have permission
        """
        if user_id:
            task = self.get_task_by_id(task_id, user_id)
        else:
            task = Task.query.get(task_id)

        if not task:
            raise ValueError("任务不存在")

        return self.update_task_status(task_id, 'running', progress=0)

    def complete_task(self, task_id, result=None, user_id=None):
        """Complete a task.

        Args:
            task_id (int): Task ID
            result (str, optional): Task result
            user_id (int, optional): User ID for permission check

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or user doesn't have permission
        """
        if user_id:
            task = self.get_task_by_id(task_id, user_id)
        else:
            task = Task.query.get(task_id)

        if not task:
            raise ValueError("任务不存在")

        return self.update_task_status(task_id, 'completed', progress=100, result=result)

    def fail_task(self, task_id, error_message, user_id=None):
        """Fail a task.

        Args:
            task_id (int): Task ID
            error_message (str): Error message
            user_id (int, optional): User ID for permission check

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or user doesn't have permission
        """
        if user_id:
            task = self.get_task_by_id(task_id, user_id)
        else:
            task = Task.query.get(task_id)

        if not task:
            raise ValueError("任务不存在")

        return self.update_task_status(task_id, 'failed', error_message=error_message)

    def update_task_progress(self, task_id, progress, user_id=None):
        """Update task progress.

        Args:
            task_id (int): Task ID
            progress (int): Progress percentage
            user_id (int, optional): User ID for permission check

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or user doesn't have permission
        """
        if user_id:
            task = self.get_task_by_id(task_id, user_id)
        else:
            task = Task.query.get(task_id)

        if not task:
            raise ValueError("任务不存在")

        return self.update_task_status(task_id, task.status, progress=progress)

    def update_task_priority(self, task_id, priority, user_id=None):
        """Update task priority.

        Args:
            task_id (int): Task ID
            priority (str): New priority
            user_id (int, optional): User ID for permission check

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or invalid priority
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            raise ValueError("任务不存在")

        if priority not in ['low', 'normal', 'high', 'urgent']:
            raise ValueError("无效的优先级")

        task.priority = priority
        db.session.commit()

        return task

    def delete_task(self, task_id, user_id):
        """Delete a task.

        Args:
            task_id (int): Task ID
            user_id (int): User ID for permission check

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If task not found or user doesn't have permission
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            raise ValueError("任务不存在或您没有权限")

        # Delete from database
        db.session.delete(task)
        db.session.commit()

        return True

    def get_pending_tasks(self, limit=10):
        """Get pending tasks for processing.

        Args:
            limit (int): Maximum number of tasks to return

        Returns:
            list: List of pending task objects
        """
        return Task.query.filter_by(status='pending').order_by(Task.created_at.asc()).limit(limit).all()

    def get_running_tasks(self, limit=10):
        """Get running tasks for monitoring.

        Args:
            limit (int): Maximum number of tasks to return

        Returns:
            list: List of running task objects
        """
        return Task.query.filter_by(status='running').order_by(Task.started_at.asc()).limit(limit).all()

    def cleanup_old_tasks(self, days=30):
        """Clean up old completed tasks.

        Args:
            days (int): Age of tasks to clean up in days

        Returns:
            int: Number of tasks cleaned up
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_tasks = Task.query.filter(
            Task.status.in_(['completed', 'failed']),
            Task.completed_at < cutoff_date
        ).all()

        for task in old_tasks:
            db.session.delete(task)

        db.session.commit()

        return len(old_tasks)

    def get_task_statistics(self, user_id=None, repository_id=None, days=30):
        """Get task statistics.

        Args:
            user_id (int, optional): Filter by user ID
            repository_id (int, optional): Filter by repository ID
            days (int): Number of days to include in statistics

        Returns:
            dict: Task statistics
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Base query
        query = Task.query.filter(Task.created_at >= cutoff_date)

        if user_id:
            query = query.filter(Task.user_id == user_id)

        if repository_id:
            query = query.filter(Task.repository_id == repository_id)

        # Get all tasks in time period
        tasks = query.all()

        # Calculate statistics
        stats = {
            'total_tasks': len(tasks),
            'completed_tasks': 0,
            'failed_tasks': 0,
            'running_tasks': 0,
            'pending_tasks': 0,
            'by_type': {},
            'by_status': {},
            'by_day': {},
            'avg_completion_time': 0,
            'total_completion_time': 0,
            'completion_count': 0,
            'success_rate': 0,
            'failure_rate': 0,
            'period_days': days
        }

        completion_times = []

        for task in tasks:
            # Count by type
            if task.type not in stats['by_type']:
                stats['by_type'][task.type] = 0
            stats['by_type'][task.type] += 1

            # Count by status
            if task.status not in stats['by_status']:
                stats['by_status'][task.status] = 0
            stats['by_status'][task.status] += 1

            # Count by day
            day_key = task.created_at.strftime('%Y-%m-%d')
            if day_key not in stats['by_day']:
                stats['by_day'][day_key] = 0
            stats['by_day'][day_key] += 1

            # Count status
            if task.status == 'completed':
                stats['completed_tasks'] += 1
            elif task.status == 'failed':
                stats['failed_tasks'] += 1
            elif task.status == 'running':
                stats['running_tasks'] += 1
            elif task.status == 'pending':
                stats['pending_tasks'] += 1

            # Calculate completion time
            if task.status in ['completed', 'failed'] and task.started_at and task.completed_at:
                completion_time = (task.completed_at - task.started_at).total_seconds()
                completion_times.append(completion_time)
                stats['total_completion_time'] += completion_time
                stats['completion_count'] += 1

        # Calculate averages and rates
        if stats['completion_count'] > 0:
            stats['avg_completion_time'] = stats['total_completion_time'] / stats['completion_count']

        if stats['total_tasks'] > 0:
            stats['success_rate'] = (stats['completed_tasks'] / stats['total_tasks']) * 100
            stats['failure_rate'] = (stats['failed_tasks'] / stats['total_tasks']) * 100

        return stats

    def get_task_performance_metrics(self, user_id=None, repository_id=None, days=30):
        """Get detailed task performance metrics.

        Args:
            user_id (int, optional): Filter by user ID
            repository_id (int, optional): Filter by repository ID
            days (int): Number of days to include

        Returns:
            dict: Performance metrics
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Base query for completed tasks
        query = Task.query.filter(
            Task.status == 'completed',
            Task.completed_at >= cutoff_date
        )

        if user_id:
            query = query.filter(Task.user_id == user_id)

        if repository_id:
            query = query.filter(Task.repository_id == repository_id)

        completed_tasks = query.all()

        # Calculate performance metrics
        metrics = {
            'total_completed': len(completed_tasks),
            'completion_times': [],
            'avg_completion_time': 0,
            'min_completion_time': 0,
            'max_completion_time': 0,
            'completion_time_distribution': {
                'under_1min': 0,
                '1min_5min': 0,
                '5min_30min': 0,
                '30min_1hour': 0,
                'over_1hour': 0
            },
            'by_task_type': {},
            'by_hour': {},
            'by_day_of_week': {}
        }

        completion_times = []

        for task in completed_tasks:
            if task.started_at and task.completed_at:
                completion_time = (task.completed_at - task.started_at).total_seconds()
                completion_times.append(completion_time)

                # Distribution
                if completion_time < 60:
                    metrics['completion_time_distribution']['under_1min'] += 1
                elif completion_time < 300:
                    metrics['completion_time_distribution']['1min_5min'] += 1
                elif completion_time < 1800:
                    metrics['completion_time_distribution']['5min_30min'] += 1
                elif completion_time < 3600:
                    metrics['completion_time_distribution']['30min_1hour'] += 1
                else:
                    metrics['completion_time_distribution']['over_1hour'] += 1

                # By task type
                if task.type not in metrics['by_task_type']:
                    metrics['by_task_type'][task.type] = []
                metrics['by_task_type'][task.type].append(completion_time)

                # By hour
                hour = task.completed_at.hour
                if hour not in metrics['by_hour']:
                    metrics['by_hour'][hour] = 0
                metrics['by_hour'][hour] += 1

                # By day of week
                day_of_week = task.completed_at.strftime('%A')
                if day_of_week not in metrics['by_day_of_week']:
                    metrics['by_day_of_week'][day_of_week] = 0
                metrics['by_day_of_week'][day_of_week] += 1

        if completion_times:
            metrics['completion_times'] = completion_times
            metrics['avg_completion_time'] = sum(completion_times) / len(completion_times)
            metrics['min_completion_time'] = min(completion_times)
            metrics['max_completion_time'] = max(completion_times)

        # Calculate averages by task type
        for task_type, times in metrics['by_task_type'].items():
            if times:
                metrics['by_task_type'][task_type] = {
                    'count': len(times),
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times)
                }

        return metrics

    def get_task_queue_info(self):
        """Get current task queue information.

        Returns:
            dict: Queue information
        """
        pending_count = Task.query.filter_by(status='pending').count()
        running_count = Task.query.filter_by(status='running').count()
        completed_count = Task.query.filter_by(status='completed').count()
        failed_count = Task.query.filter_by(status='failed').count()

        # Get oldest pending task
        oldest_pending = Task.query.filter_by(status='pending').order_by(Task.created_at.asc()).first()
        oldest_pending_time = oldest_pending.created_at if oldest_pending else None

        # Get longest running task
        longest_running = Task.query.filter_by(status='running').order_by(Task.started_at.asc()).first()
        longest_running_time = longest_running.started_at if longest_running else None

        return {
            'pending_count': pending_count,
            'running_count': running_count,
            'completed_count': completed_count,
            'failed_count': failed_count,
            'total_count': pending_count + running_count + completed_count + failed_count,
            'oldest_pending_task': oldest_pending_time.isoformat() if oldest_pending_time else None,
            'longest_running_task': longest_running_time.isoformat() if longest_running_time else None,
            'queue_health': self._calculate_queue_health(pending_count, running_count)
        }

    def _calculate_queue_health(self, pending_count, running_count):
        """Calculate queue health score.

        Args:
            pending_count (int): Number of pending tasks
            running_count (int): Number of running tasks

        Returns:
            str: Health status ('healthy', 'warning', 'critical')
        """
        if pending_count == 0:
            return 'healthy'
        elif pending_count < 10 and running_count < 5:
            return 'healthy'
        elif pending_count < 50 and running_count < 10:
            return 'warning'
        else:
            return 'critical'
