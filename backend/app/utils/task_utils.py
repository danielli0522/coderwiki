"""
Task utility functions for common task operations.
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from app.models.task import Task
from app.models.user import User
from app.models.repository import Repository
from app.services.task_service import TaskService


def generate_task_id() -> str:
    """Generate a unique task ID.
    
    Returns:
        str: Unique task ID
    """
    return str(uuid.uuid4())


def validate_task_type(task_type: str) -> bool:
    """Validate task type.
    
    Args:
        task_type: Task type to validate
        
    Returns:
        bool: True if valid
    """
    return task_type in Task.VALID_TYPES


def validate_task_status(status: str) -> bool:
    """Validate task status.
    
    Args:
        status: Task status to validate
        
    Returns:
        bool: True if valid
    """
    return status in Task.VALID_STATUSES


def validate_task_progress(progress: Union[int, float]) -> bool:
    """Validate task progress.
    
    Args:
        progress: Progress value to validate
        
    Returns:
        bool: True if valid
    """
    return isinstance(progress, (int, float)) and 0 <= progress <= 100


def format_task_duration(duration_seconds: float) -> str:
    """Format task duration in human-readable format.
    
    Args:
        duration_seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if duration_seconds < 60:
        return f"{duration_seconds:.1f}s"
    elif duration_seconds < 3600:
        minutes = duration_seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = duration_seconds / 3600
        return f"{hours:.1f}h"


def get_task_status_color(status: str) -> str:
    """Get CSS color class for task status.
    
    Args:
        status: Task status
        
    Returns:
        str: CSS color class
    """
    color_map = {
        'pending': 'warning',
        'running': 'info',
        'completed': 'success',
        'failed': 'danger'
    }
    return color_map.get(status, 'secondary')


def get_task_status_icon(status: str) -> str:
    """Get icon for task status.
    
    Args:
        status: Task status
        
    Returns:
        str: Icon name
    """
    icon_map = {
        'pending': 'clock',
        'running': 'play-circle',
        'completed': 'check-circle',
        'failed': 'x-circle'
    }
    return icon_map.get(status, 'question-circle')


def get_task_type_display_name(task_type: str) -> str:
    """Get display name for task type.
    
    Args:
        task_type: Task type
        
    Returns:
        str: Display name
    """
    display_names = {
        'generate_document': 'Generate Document',
        'sync_repository': 'Sync Repository',
        'analyze_code': 'Analyze Code'
    }
    return display_names.get(task_type, task_type.replace('_', ' ').title())


def calculate_task_eta(task: Task, avg_completion_time: float = None) -> Optional[datetime]:
    """Calculate estimated time of completion for a task.
    
    Args:
        task: Task object
        avg_completion_time: Average completion time in seconds
        
    Returns:
        datetime or None: Estimated completion time
    """
    if task.status != 'running' or not task.started_at:
        return None
    
    if avg_completion_time is None:
        # Use default completion time based on task type
        default_times = {
            'generate_document': 600,  # 10 minutes
            'sync_repository': 120,    # 2 minutes
            'analyze_code': 300        # 5 minutes
        }
        avg_completion_time = default_times.get(task.type, 300)
    
    # Calculate progress-based ETA
    if task.progress > 0:
        elapsed_time = (datetime.utcnow() - task.started_at).total_seconds()
        remaining_time = (avg_completion_time * (100 - task.progress)) / task.progress
        total_time = elapsed_time + remaining_time
    else:
        total_time = avg_completion_time
    
    return task.started_at + timedelta(seconds=total_time)


def create_batch_tasks(user_id: int, repository_ids: List[int], task_type: str) -> List[Task]:
    """Create multiple tasks for batch processing.
    
    Args:
        user_id: User ID
        repository_ids: List of repository IDs
        task_type: Task type
        
    Returns:
        List[Task]: Created tasks
    """
    if not validate_task_type(task_type):
        raise ValueError(f"Invalid task type: {task_type}")
    
    task_service = TaskService()
    created_tasks = []
    
    for repo_id in repository_ids:
        try:
            task = task_service.create_task(user_id, repo_id, task_type)
            created_tasks.append(task)
        except Exception as e:
            print(f"Failed to create task for repository {repo_id}: {e}")
    
    return created_tasks


def get_task_summary(task: Task) -> Dict[str, Any]:
    """Get a summary of task information.
    
    Args:
        task: Task object
        
    Returns:
        Dict: Task summary
    """
    return {
        'id': task.id,
        'type': get_task_type_display_name(task.type),
        'status': task.status,
        'progress': task.progress,
        'duration': format_task_duration(task.get_duration()),
        'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'started_at': task.started_at.strftime('%Y-%m-%d %H:%M:%S') if task.started_at else None,
        'completed_at': task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else None,
        'status_color': get_task_status_color(task.status),
        'status_icon': get_task_status_icon(task.status),
        'can_retry': task.can_retry(),
        'is_running': task.is_running(),
        'is_completed': task.is_completed(),
        'is_failed': task.is_failed()
    }


def export_task_data(tasks: List[Task], format: str = 'json') -> str:
    """Export task data in various formats.
    
    Args:
        tasks: List of tasks to export
        format: Export format ('json', 'csv', 'txt')
        
    Returns:
        str: Exported data
    """
    if format == 'json':
        return json.dumps([task.to_dict() for task in tasks], indent=2, default=str)
    
    elif format == 'csv':
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Type', 'Status', 'Progress', 'Duration', 'Created At', 
            'Started At', 'Completed At', 'Error Message'
        ])
        
        # Write data
        for task in tasks:
            writer.writerow([
                task.id,
                task.type,
                task.status,
                task.progress,
                task.get_duration(),
                task.created_at,
                task.started_at,
                task.completed_at,
                task.error_message or ''
            ])
        
        return output.getvalue()
    
    elif format == 'txt':
        lines = []
        for task in tasks:
            lines.append(f"Task {task.id}:")
            lines.append(f"  Type: {get_task_type_display_name(task.type)}")
            lines.append(f"  Status: {task.status}")
            lines.append(f"  Progress: {task.progress}%")
            lines.append(f"  Duration: {format_task_duration(task.get_duration())}")
            lines.append(f"  Created: {task.created_at}")
            if task.started_at:
                lines.append(f"  Started: {task.started_at}")
            if task.completed_at:
                lines.append(f"  Completed: {task.completed_at}")
            if task.error_message:
                lines.append(f"  Error: {task.error_message}")
            lines.append("")
        
        return "\n".join(lines)
    
    else:
        raise ValueError(f"Unsupported export format: {format}")


def get_task_filters() -> Dict[str, List[str]]:
    """Get available task filters.
    
    Returns:
        Dict: Available filters
    """
    return {
        'status': Task.VALID_STATUSES,
        'type': Task.VALID_TYPES,
        'progress_ranges': ['0-25', '26-50', '51-75', '76-100'],
        'time_ranges': ['today', 'yesterday', 'last_7_days', 'last_30_days', 'all_time']
    }


def apply_task_filters(query, filters: Dict[str, Any]):
    """Apply filters to task query.
    
    Args:
        query: SQLAlchemy query
        filters: Filter dictionary
        
    Returns:
        Query: Filtered query
    """
    from datetime import datetime, timedelta
    
    # Status filter
    if 'status' in filters and filters['status']:
        if isinstance(filters['status'], list):
            query = query.filter(Task.status.in_(filters['status']))
        else:
            query = query.filter(Task.status == filters['status'])
    
    # Type filter
    if 'type' in filters and filters['type']:
        if isinstance(filters['type'], list):
            query = query.filter(Task.type.in_(filters['type']))
        else:
            query = query.filter(Task.type == filters['type'])
    
    # Progress filter
    if 'progress_range' in filters and filters['progress_range']:
        progress_range = filters['progress_range']
        if progress_range == '0-25':
            query = query.filter(Task.progress.between(0, 25))
        elif progress_range == '26-50':
            query = query.filter(Task.progress.between(26, 50))
        elif progress_range == '51-75':
            query = query.filter(Task.progress.between(51, 75))
        elif progress_range == '76-100':
            query = query.filter(Task.progress.between(76, 100))
    
    # Time range filter
    if 'time_range' in filters and filters['time_range']:
        time_range = filters['time_range']
        now = datetime.utcnow()
        
        if time_range == 'today':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Task.created_at >= start_time)
        elif time_range == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Task.created_at.between(start_time, end_time))
        elif time_range == 'last_7_days':
            start_time = now - timedelta(days=7)
            query = query.filter(Task.created_at >= start_time)
        elif time_range == 'last_30_days':
            start_time = now - timedelta(days=30)
            query = query.filter(Task.created_at >= start_time)
    
    # User filter
    if 'user_id' in filters and filters['user_id']:
        query = query.filter(Task.user_id == filters['user_id'])
    
    # Repository filter
    if 'repository_id' in filters and filters['repository_id']:
        query = query.filter(Task.repository_id == filters['repository_id'])
    
    return query


def validate_task_permissions(user: User, task: Task) -> bool:
    """Validate if user has permissions to access a task.
    
    Args:
        user: User object
        task: Task object
        
    Returns:
        bool: True if user has permissions
    """
    # Admin users can access all tasks
    if hasattr(user, 'is_admin') and user.is_admin:
        return True
    
    # Users can only access their own tasks
    return task.user_id == user.id


def get_task_dependencies(task: Task) -> List[Task]:
    """Get tasks that depend on this task.
    
    Args:
        task: Task object
        
    Returns:
        List[Task]: List of dependent tasks
    """
    # This is a placeholder for future dependency management
    # For now, return empty list as dependencies are not implemented
    return []


def can_execute_task(task: Task) -> bool:
    """Check if a task can be executed.
    
    Args:
        task: Task object
        
    Returns:
        bool: True if task can be executed
    """
    # Check if task is in a valid state for execution
    if task.status != 'pending':
        return False
    
    # Check if task has required dependencies
    dependencies = get_task_dependencies(task)
    for dep in dependencies:
        if dep.status != 'completed':
            return False
    
    return True


def get_task_resource_requirements(task_type: str) -> Dict[str, Any]:
    """Get resource requirements for a task type.
    
    Args:
        task_type: Task type
        
    Returns:
        Dict: Resource requirements
    """
    requirements = {
        'generate_document': {
            'memory_mb': 512,
            'cpu_cores': 1,
            'timeout_seconds': 1800,
            'max_retries': 3
        },
        'sync_repository': {
            'memory_mb': 256,
            'cpu_cores': 1,
            'timeout_seconds': 600,
            'max_retries': 2
        },
        'analyze_code': {
            'memory_mb': 1024,
            'cpu_cores': 2,
            'timeout_seconds': 1200,
            'max_retries': 3
        }
    }
    
    return requirements.get(task_type, {
        'memory_mb': 512,
        'cpu_cores': 1,
        'timeout_seconds': 900,
        'max_retries': 2
    })