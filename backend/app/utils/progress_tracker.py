"""
Progress tracking tools for monitoring task execution.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from app import db
from app.models.task import Task
from app.services.task_service import TaskService


class ProgressStage(Enum):
    """Progress stages for task execution."""
    INITIALIZATION = "initialization"
    CLONING_REPOSITORY = "cloning_repository"
    ANALYZING_CODE = "analyzing_code"
    GENERATING_DOCUMENTATION = "generating_documentation"
    SAVING_RESULTS = "saving_results"
    CLEANUP = "cleanup"
    COMPLETED = "completed"


@dataclass
class ProgressStep:
    """Individual progress step."""
    name: str
    stage: ProgressStage
    weight: float = 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressTracker:
    """Progress tracker for individual tasks."""
    task_id: int
    task_type: str
    total_weight: float = 100.0
    steps: List[ProgressStep] = field(default_factory=list)
    current_step: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_update: Optional[datetime] = None
    lock: threading.Lock = field(default_factory=threading.Lock)
    
    def __post_init__(self):
        self.steps = self._create_default_steps()
    
    def _create_default_steps(self) -> List[ProgressStep]:
        """Create default progress steps based on task type."""
        steps_map = {
            'generate_document': [
                ProgressStep("Initialize", ProgressStage.INITIALIZATION, 5),
                ProgressStep("Clone Repository", ProgressStage.CLONING_REPOSITORY, 15),
                ProgressStep("Analyze Code Structure", ProgressStage.ANALYZING_CODE, 25),
                ProgressStep("Generate Documentation", ProgressStage.GENERATING_DOCUMENTATION, 40),
                ProgressStep("Save Results", ProgressStage.SAVING_RESULTS, 10),
                ProgressStep("Cleanup", ProgressStage.CLEANUP, 5)
            ],
            'sync_repository': [
                ProgressStep("Initialize", ProgressStage.INITIALIZATION, 10),
                ProgressStep("Clone Repository", ProgressStage.CLONING_REPOSITORY, 70),
                ProgressStep("Update Status", ProgressStage.SAVING_RESULTS, 15),
                ProgressStep("Cleanup", ProgressStage.CLEANUP, 5)
            ],
            'analyze_code': [
                ProgressStep("Initialize", ProgressStage.INITIALIZATION, 10),
                ProgressStep("Clone Repository", ProgressStage.CLONING_REPOSITORY, 20),
                ProgressStep("Analyze Code Structure", ProgressStage.ANALYZING_CODE, 60),
                ProgressStep("Save Results", ProgressStage.SAVING_RESULTS, 5),
                ProgressStep("Cleanup", ProgressStage.CLEANUP, 5)
            ]
        }
        
        return steps_map.get(self.task_type, [
            ProgressStep("Initialize", ProgressStage.INITIALIZATION, 10),
            ProgressStep("Execute Task", ProgressStage.ANALYZING_CODE, 80),
            ProgressStep("Save Results", ProgressStage.SAVING_RESULTS, 5),
            ProgressStep("Cleanup", ProgressStage.CLEANUP, 5)
        ])
    
    def start(self):
        """Start progress tracking."""
        with self.lock:
            self.start_time = datetime.utcnow()
            self.last_update = self.start_time
            self._update_step_progress(0, 0)
    
    def start_step(self, step_index: int, details: Dict[str, Any] = None):
        """Start a specific step.
        
        Args:
            step_index: Index of step to start
            details: Additional details for the step
        """
        with self.lock:
            if 0 <= step_index < len(self.steps):
                step = self.steps[step_index]
                step.start_time = datetime.utcnow()
                step.status = "running"
                step.details = details or {}
                self.current_step = step_index
                self.last_update = datetime.utcnow()
    
    def update_step_progress(self, step_index: int, progress: float, details: Dict[str, Any] = None):
        """Update progress for a specific step.
        
        Args:
            step_index: Index of step to update
            progress: Progress percentage (0-100)
            details: Additional details for the step
        """
        with self.lock:
            if 0 <= step_index < len(self.steps):
                step = self.steps[step_index]
                step.progress = max(0, min(100, progress))
                if details:
                    step.details.update(details)
                self.last_update = datetime.utcnow()
                
                # Update overall progress
                self._update_step_progress(step_index, step.progress)
    
    def complete_step(self, step_index: int, result: Dict[str, Any] = None):
        """Complete a specific step.
        
        Args:
            step_index: Index of step to complete
            result: Step result details
        """
        with self.lock:
            if 0 <= step_index < len(self.steps):
                step = self.steps[step_index]
                step.end_time = datetime.utcnow()
                step.status = "completed"
                step.progress = 100.0
                if result:
                    step.details.update(result)
                self.last_update = datetime.utcnow()
                
                # Update overall progress
                self._update_step_progress(step_index, 100.0)
    
    def fail_step(self, step_index: int, error_message: str, details: Dict[str, Any] = None):
        """Fail a specific step.
        
        Args:
            step_index: Index of step to fail
            error_message: Error message
            details: Additional details
        """
        with self.lock:
            if 0 <= step_index < len(self.steps):
                step = self.steps[step_index]
                step.end_time = datetime.utcnow()
                step.status = "failed"
                step.error_message = error_message
                if details:
                    step.details.update(details)
                self.last_update = datetime.utcnow()
    
    def _update_step_progress(self, step_index: int, progress: float):
        """Update overall progress based on step progress."""
        total_progress = 0.0
        
        for i, step in enumerate(self.steps):
            if i < step_index:
                # Completed steps
                total_progress += step.weight
            elif i == step_index:
                # Current step
                total_progress += step.weight * (progress / 100.0)
            # Future steps don't contribute to progress
        
        # Update task progress in database
        try:
            task_service = TaskService()
            task_service.update_task_progress(self.task_id, int(total_progress))
        except Exception as e:
            print(f"Error updating task progress: {e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information.
        
        Returns:
            Dict: Progress information
        """
        with self.lock:
            total_progress = 0.0
            completed_steps = 0
            running_steps = 0
            failed_steps = 0
            
            for step in self.steps:
                if step.status == "completed":
                    total_progress += step.weight
                    completed_steps += 1
                elif step.status == "running":
                    total_progress += step.weight * (step.progress / 100.0)
                    running_steps += 1
                elif step.status == "failed":
                    failed_steps += 1
            
            current_step_info = None
            if self.current_step < len(self.steps):
                current_step = self.steps[self.current_step]
                current_step_info = {
                    'name': current_step.name,
                    'stage': current_step.stage.value,
                    'progress': current_step.progress,
                    'status': current_step.status,
                    'start_time': current_step.start_time.isoformat() if current_step.start_time else None,
                    'details': current_step.details
                }
            
            return {
                'task_id': self.task_id,
                'task_type': self.task_type,
                'total_progress': total_progress,
                'completed_steps': completed_steps,
                'running_steps': running_steps,
                'failed_steps': failed_steps,
                'total_steps': len(self.steps),
                'current_step': current_step_info,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'steps': [
                    {
                        'name': step.name,
                        'stage': step.stage.value,
                        'weight': step.weight,
                        'progress': step.progress,
                        'status': step.status,
                        'start_time': step.start_time.isoformat() if step.start_time else None,
                        'end_time': step.end_time.isoformat() if step.end_time else None,
                        'error_message': step.error_message,
                        'details': step.details
                    }
                    for step in self.steps
                ]
            }
    
    def complete(self, result: Dict[str, Any] = None):
        """Complete the entire task."""
        with self.lock:
            self.end_time = datetime.utcnow()
            self.last_update = self.end_time
            
            # Mark all remaining steps as completed
            for i in range(self.current_step, len(self.steps)):
                if self.steps[i].status != "completed":
                    self.steps[i].status = "completed"
                    self.steps[i].progress = 100.0
                    self.steps[i].end_time = self.end_time
            
            # Update final progress
            self._update_step_progress(len(self.steps) - 1, 100.0)
    
    def fail(self, error_message: str, details: Dict[str, Any] = None):
        """Fail the entire task."""
        with self.lock:
            self.end_time = datetime.utcnow()
            self.last_update = self.end_time
            
            # Mark current step as failed
            if self.current_step < len(self.steps):
                self.steps[self.current_step].status = "failed"
                self.steps[self.current_step].error_message = error_message
                if details:
                    self.steps[self.current_step].details.update(details)


class ProgressTrackerManager:
    """Manager for multiple progress trackers."""
    
    def __init__(self):
        """Initialize progress tracker manager."""
        self.trackers: Dict[int, ProgressTracker] = {}
        self.lock = threading.Lock()
    
    def create_tracker(self, task_id: int, task_type: str) -> ProgressTracker:
        """Create a new progress tracker.
        
        Args:
            task_id: Task ID
            task_type: Task type
            
        Returns:
            ProgressTracker: Created tracker
        """
        with self.lock:
            tracker = ProgressTracker(task_id, task_type)
            self.trackers[task_id] = tracker
            return tracker
    
    def get_tracker(self, task_id: int) -> Optional[ProgressTracker]:
        """Get a progress tracker by task ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            ProgressTracker or None
        """
        with self.lock:
            return self.trackers.get(task_id)
    
    def remove_tracker(self, task_id: int) -> bool:
        """Remove a progress tracker.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if tracker was removed
        """
        with self.lock:
            if task_id in self.trackers:
                del self.trackers[task_id]
                return True
            return False
    
    def get_all_trackers(self) -> Dict[int, ProgressTracker]:
        """Get all progress trackers.
        
        Returns:
            Dict: All trackers
        """
        with self.lock:
            return self.trackers.copy()
    
    def cleanup_old_trackers(self, max_age_hours: int = 24):
        """Clean up old trackers.
        
        Args:
            max_age_hours: Maximum age of trackers to keep
        """
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            trackers_to_remove = []
            for task_id, tracker in self.trackers.items():
                if tracker.end_time and tracker.end_time < cutoff_time:
                    trackers_to_remove.append(task_id)
                elif tracker.start_time and tracker.start_time < cutoff_time:
                    # Remove very old incomplete trackers
                    trackers_to_remove.append(task_id)
            
            for task_id in trackers_to_remove:
                del self.trackers[task_id]
    
    def get_active_trackers(self) -> Dict[int, ProgressTracker]:
        """Get active (running) trackers.
        
        Returns:
            Dict: Active trackers
        """
        with self.lock:
            active = {}
            for task_id, tracker in self.trackers.items():
                if tracker.start_time and not tracker.end_time:
                    active[task_id] = tracker
            return active
    
    def get_tracker_statistics(self) -> Dict[str, Any]:
        """Get tracker statistics.
        
        Returns:
            Dict: Statistics
        """
        with self.lock:
            total_trackers = len(self.trackers)
            active_trackers = len(self.get_active_trackers())
            completed_trackers = sum(1 for t in self.trackers.values() if t.end_time)
            
            return {
                'total_trackers': total_trackers,
                'active_trackers': active_trackers,
                'completed_trackers': completed_trackers,
                'average_completion_time': self._calculate_average_completion_time()
            }
    
    def _calculate_average_completion_time(self) -> float:
        """Calculate average completion time.
        
        Returns:
            float: Average completion time in seconds
        """
        completed_times = []
        
        for tracker in self.trackers.values():
            if tracker.start_time and tracker.end_time:
                completion_time = (tracker.end_time - tracker.start_time).total_seconds()
                completed_times.append(completion_time)
        
        if completed_times:
            return sum(completed_times) / len(completed_times)
        return 0.0


# Global instance
progress_manager = ProgressTrackerManager()


def get_progress_tracker(task_id: int, task_type: str = None) -> ProgressTracker:
    """Get or create a progress tracker for a task.
    
    Args:
        task_id: Task ID
        task_type: Task type (required for new trackers)
        
    Returns:
        ProgressTracker: Progress tracker
    """
    tracker = progress_manager.get_tracker(task_id)
    
    if tracker is None:
        if not task_type:
            raise ValueError("Task type is required for new trackers")
        tracker = progress_manager.create_tracker(task_id, task_type)
    
    return tracker


def update_task_progress_detailed(task_id: int, step_name: str, progress: float, details: Dict[str, Any] = None):
    """Update task progress with detailed step information.
    
    Args:
        task_id: Task ID
        step_name: Name of the current step
        progress: Progress percentage (0-100)
        details: Additional details
    """
    tracker = progress_manager.get_tracker(task_id)
    
    if tracker:
        # Find step by name
        step_index = None
        for i, step in enumerate(tracker.steps):
            if step.name == step_name:
                step_index = i
                break
        
        if step_index is not None:
            tracker.update_step_progress(step_index, progress, details)
        else:
            # Update current step if step name not found
            tracker.update_step_progress(tracker.current_step, progress, details)


def get_task_progress_details(task_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed progress information for a task.
    
    Args:
        task_id: Task ID
        
    Returns:
        Dict or None: Progress details
    """
    tracker = progress_manager.get_tracker(task_id)
    
    if tracker:
        return tracker.get_progress()
    
    return None