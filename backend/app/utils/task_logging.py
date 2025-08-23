"""
Task logging tools for comprehensive task execution logging.
"""

import logging
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import os

from app import db
from app.models.task import Task


class LogLevel(Enum):
    """Log levels for task logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TaskLogEntry:
    """Individual task log entry."""
    task_id: int
    timestamp: datetime
    level: LogLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    step_name: Optional[str] = None
    progress: Optional[float] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary.
        
        Returns:
            Dict: Log entry as dictionary
        """
        return {
            'task_id': self.task_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'details': self.details,
            'step_name': self.step_name,
            'progress': self.progress,
            'duration': self.duration
        }


class TaskLogger:
    """Logger for individual tasks."""
    
    def __init__(self, task_id: int, log_to_file: bool = True, log_to_db: bool = True):
        """Initialize task logger.
        
        Args:
            task_id: Task ID
            log_to_file: Whether to log to file
            log_to_db: Whether to log to database
        """
        self.task_id = task_id
        self.log_to_file = log_to_file
        self.log_to_db = log_to_db
        self.entries: List[TaskLogEntry] = []
        self.lock = threading.Lock()
        self.start_time = datetime.utcnow()
        
        # Setup file logging
        if self.log_to_file:
            self._setup_file_logging()
        
        # Log initialization
        self.info(f"Task logger initialized for task {task_id}")
    
    def _setup_file_logging(self):
        """Setup file logging for the task."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"task_{self.task_id}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        
        # Setup Python logging
        self.python_logger = logging.getLogger(f"task_{self.task_id}")
        self.python_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.python_logger.handlers[:]:
            self.python_logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.python_logger.addHandler(file_handler)
        self.python_logger.addHandler(console_handler)
        
        self.log_file = log_file
    
    def debug(self, message: str, details: Dict[str, Any] = None, step_name: str = None):
        """Log debug message.
        
        Args:
            message: Log message
            details: Additional details
            step_name: Current step name
        """
        self._log(LogLevel.DEBUG, message, details, step_name)
    
    def info(self, message: str, details: Dict[str, Any] = None, step_name: str = None):
        """Log info message.
        
        Args:
            message: Log message
            details: Additional details
            step_name: Current step name
        """
        self._log(LogLevel.INFO, message, details, step_name)
    
    def warning(self, message: str, details: Dict[str, Any] = None, step_name: str = None):
        """Log warning message.
        
        Args:
            message: Log message
            details: Additional details
            step_name: Current step name
        """
        self._log(LogLevel.WARNING, message, details, step_name)
    
    def error(self, message: str, details: Dict[str, Any] = None, step_name: str = None):
        """Log error message.
        
        Args:
            message: Log message
            details: Additional details
            step_name: Current step name
        """
        self._log(LogLevel.ERROR, message, details, step_name)
    
    def critical(self, message: str, details: Dict[str, Any] = None, step_name: str = None):
        """Log critical message.
        
        Args:
            message: Log message
            details: Additional details
            step_name: Current step name
        """
        self._log(LogLevel.CRITICAL, message, details, step_name)
    
    def _log(self, level: LogLevel, message: str, details: Dict[str, Any] = None, step_name: str = None):
        """Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            details: Additional details
            step_name: Current step name
        """
        timestamp = datetime.utcnow()
        
        # Create log entry
        entry = TaskLogEntry(
            task_id=self.task_id,
            timestamp=timestamp,
            level=level,
            message=message,
            details=details or {},
            step_name=step_name
        )
        
        with self.lock:
            self.entries.append(entry)
        
        # Log to Python logger
        if self.log_to_file and hasattr(self, 'python_logger'):
            log_message = f"[{step_name or 'GENERAL'}] {message}"
            if details:
                log_message += f" - {json.dumps(details, default=str)}"
            
            if level == LogLevel.DEBUG:
                self.python_logger.debug(log_message)
            elif level == LogLevel.INFO:
                self.python_logger.info(log_message)
            elif level == LogLevel.WARNING:
                self.python_logger.warning(log_message)
            elif level == LogLevel.ERROR:
                self.python_logger.error(log_message)
            elif level == LogLevel.CRITICAL:
                self.python_logger.critical(log_message)
        
        # Log to database (if implemented)
        if self.log_to_db:
            self._log_to_database(entry)
    
    def _log_to_database(self, entry: TaskLogEntry):
        """Log entry to database (placeholder for future implementation).
        
        Args:
            entry: Log entry to save
        """
        # This would be implemented when we create a task_log table
        pass
    
    def start_step(self, step_name: str, details: Dict[str, Any] = None):
        """Log step start.
        
        Args:
            step_name: Step name
            details: Additional details
        """
        self.info(f"Starting step: {step_name}", details, step_name)
    
    def complete_step(self, step_name: str, result: Dict[str, Any] = None):
        """Log step completion.
        
        Args:
            step_name: Step name
            result: Step result
        """
        self.info(f"Completed step: {step_name}", result, step_name)
    
    def fail_step(self, step_name: str, error_message: str, details: Dict[str, Any] = None):
        """Log step failure.
        
        Args:
            step_name: Step name
            error_message: Error message
            details: Additional details
        """
        self.error(f"Failed step: {step_name} - {error_message}", details, step_name)
    
    def update_progress(self, progress: float, step_name: str = None, details: Dict[str, Any] = None):
        """Log progress update.
        
        Args:
            progress: Progress percentage
            step_name: Current step name
            details: Additional details
        """
        details = details or {}
        details['progress'] = progress
        self.info(f"Progress updated: {progress}%", details, step_name)
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            details: Additional details
        """
        perf_details = {
            'operation': operation,
            'duration_seconds': duration,
            'duration_formatted': self._format_duration(duration)
        }
        if details:
            perf_details.update(details)
        
        self.info(f"Performance: {operation} took {self._format_duration(duration)}", perf_details)
    
    def _format_duration(self, duration: float) -> str:
        """Format duration in human-readable format.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            str: Formatted duration
        """
        if duration < 1:
            return f"{duration*1000:.1f}ms"
        elif duration < 60:
            return f"{duration:.2f}s"
        elif duration < 3600:
            return f"{duration/60:.2f}m"
        else:
            return f"{duration/3600:.2f}h"
    
    def get_logs(self, level: LogLevel = None, step_name: str = None, limit: int = None) -> List[TaskLogEntry]:
        """Get log entries with optional filtering.
        
        Args:
            level: Filter by log level
            step_name: Filter by step name
            limit: Maximum number of entries to return
            
        Returns:
            List[TaskLogEntry]: Filtered log entries
        """
        with self.lock:
            filtered_logs = self.entries
            
            if level:
                filtered_logs = [log for log in filtered_logs if log.level == level]
            
            if step_name:
                filtered_logs = [log for log in filtered_logs if log.step_name == step_name]
            
            if limit:
                filtered_logs = filtered_logs[-limit:]
            
            return filtered_logs
    
    def get_error_logs(self) -> List[TaskLogEntry]:
        """Get error and critical log entries.
        
        Returns:
            List[TaskLogEntry]: Error logs
        """
        return self.get_logs(level=LogLevel.ERROR) + self.get_logs(level=LogLevel.CRITICAL)
    
    def get_step_logs(self, step_name: str) -> List[TaskLogEntry]:
        """Get logs for a specific step.
        
        Args:
            step_name: Step name
            
        Returns:
            List[TaskLogEntry]: Step logs
        """
        return self.get_logs(step_name=step_name)
    
    def export_logs(self, format: str = 'json') -> str:
        """Export logs in various formats.
        
        Args:
            format: Export format ('json', 'txt', 'csv')
            
        Returns:
            str: Exported logs
        """
        logs = [log.to_dict() for log in self.entries]
        
        if format == 'json':
            return json.dumps(logs, indent=2, default=str)
        
        elif format == 'txt':
            lines = []
            for log in logs:
                lines.append(f"{log['timestamp']} [{log['level'].upper()}] {log['message']}")
                if log['step_name']:
                    lines.append(f"  Step: {log['step_name']}")
                if log['details']:
                    lines.append(f"  Details: {json.dumps(log['details'], default=str)}")
                lines.append("")
            return "\n".join(lines)
        
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Timestamp', 'Level', 'Message', 'Step Name', 'Progress', 'Details'])
            
            # Write data
            for log in logs:
                writer.writerow([
                    log['timestamp'],
                    log['level'],
                    log['message'],
                    log['step_name'] or '',
                    log['progress'] or '',
                    json.dumps(log['details'], default=str)
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get log summary statistics.
        
        Returns:
            Dict: Log summary
        """
        with self.lock:
            total_logs = len(self.entries)
            level_counts = {}
            step_counts = {}
            
            for log in self.entries:
                # Count by level
                level = log.level.value
                level_counts[level] = level_counts.get(level, 0) + 1
                
                # Count by step
                if log.step_name:
                    step_counts[log.step_name] = step_counts.get(log.step_name, 0) + 1
            
            return {
                'task_id': self.task_id,
                'total_logs': total_logs,
                'level_counts': level_counts,
                'step_counts': step_counts,
                'error_count': level_counts.get('error', 0) + level_counts.get('critical', 0),
                'start_time': self.start_time.isoformat(),
                'log_file': str(self.log_file) if hasattr(self, 'log_file') else None
            }
    
    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'python_logger'):
            for handler in self.python_logger.handlers[:]:
                handler.close()
                self.python_logger.removeHandler(handler)


class TaskLoggerManager:
    """Manager for multiple task loggers."""
    
    def __init__(self):
        """Initialize task logger manager."""
        self.loggers: Dict[int, TaskLogger] = {}
        self.lock = threading.Lock()
    
    def get_logger(self, task_id: int, create_if_missing: bool = True) -> Optional[TaskLogger]:
        """Get or create a task logger.
        
        Args:
            task_id: Task ID
            create_if_missing: Whether to create logger if missing
            
        Returns:
            TaskLogger or None
        """
        with self.lock:
            if task_id not in self.loggers:
                if create_if_missing:
                    self.loggers[task_id] = TaskLogger(task_id)
                else:
                    return None
            
            return self.loggers[task_id]
    
    def remove_logger(self, task_id: int) -> bool:
        """Remove a task logger.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if logger was removed
        """
        with self.lock:
            if task_id in self.loggers:
                logger = self.loggers[task_id]
                logger.cleanup()
                del self.loggers[task_id]
                return True
            return False
    
    def get_all_loggers(self) -> Dict[int, TaskLogger]:
        """Get all task loggers.
        
        Returns:
            Dict: All loggers
        """
        with self.lock:
            return self.loggers.copy()
    
    def cleanup_old_loggers(self, max_age_hours: int = 48):
        """Clean up old loggers.
        
        Args:
            max_age_hours: Maximum age of loggers to keep
        """
        with self.lock:
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            loggers_to_remove = []
            for task_id, logger in self.loggers.items():
                if logger.start_time < cutoff_time:
                    loggers_to_remove.append(task_id)
            
            for task_id in loggers_to_remove:
                self.remove_logger(task_id)
    
    def get_logger_statistics(self) -> Dict[str, Any]:
        """Get logger statistics.
        
        Returns:
            Dict: Statistics
        """
        with self.lock:
            total_loggers = len(self.loggers)
            total_logs = sum(len(logger.entries) for logger in self.loggers.values())
            
            level_counts = {}
            for logger in self.loggers.values():
                for entry in logger.entries:
                    level = entry.level.value
                    level_counts[level] = level_counts.get(level, 0) + 1
            
            return {
                'total_loggers': total_loggers,
                'total_logs': total_logs,
                'level_counts': level_counts,
                'average_logs_per_logger': total_logs / total_loggers if total_loggers > 0 else 0
            }


# Global instance
task_logger_manager = TaskLoggerManager()


def get_task_logger(task_id: int) -> TaskLogger:
    """Get or create a task logger.
    
    Args:
        task_id: Task ID
        
    Returns:
        TaskLogger: Task logger
    """
    return task_logger_manager.get_logger(task_id)


def log_task_event(task_id: int, level: str, message: str, details: Dict[str, Any] = None, step_name: str = None):
    """Log a task event.
    
    Args:
        task_id: Task ID
        level: Log level
        message: Log message
        details: Additional details
        step_name: Current step name
    """
    logger = get_task_logger(task_id)
    
    level_map = {
        'debug': LogLevel.DEBUG,
        'info': LogLevel.INFO,
        'warning': LogLevel.WARNING,
        'error': LogLevel.ERROR,
        'critical': LogLevel.CRITICAL
    }
    
    log_level = level_map.get(level.lower(), LogLevel.INFO)
    
    if log_level == LogLevel.DEBUG:
        logger.debug(message, details, step_name)
    elif log_level == LogLevel.INFO:
        logger.info(message, details, step_name)
    elif log_level == LogLevel.WARNING:
        logger.warning(message, details, step_name)
    elif log_level == LogLevel.ERROR:
        logger.error(message, details, step_name)
    elif log_level == LogLevel.CRITICAL:
        logger.critical(message, details, step_name)


def get_task_logs(task_id: int, level: str = None, step_name: str = None, limit: int = None) -> List[Dict[str, Any]]:
    """Get logs for a task.
    
    Args:
        task_id: Task ID
        level: Filter by log level
        step_name: Filter by step name
        limit: Maximum number of entries
        
    Returns:
        List[Dict]: Log entries
    """
    logger = task_logger_manager.get_logger(task_id, create_if_missing=False)
    
    if not logger:
        return []
    
    log_level = None
    if level:
        level_map = {
            'debug': LogLevel.DEBUG,
            'info': LogLevel.INFO,
            'warning': LogLevel.WARNING,
            'error': LogLevel.ERROR,
            'critical': LogLevel.CRITICAL
        }
        log_level = level_map.get(level.lower())
    
    logs = logger.get_logs(level=log_level, step_name=step_name, limit=limit)
    return [log.to_dict() for log in logs]