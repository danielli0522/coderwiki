"""
Task model definition.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Task(db.Model):
    """Task model for managing document generation jobs."""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False, index=True)
    type = db.Column(db.Enum('generate_document', 'sync_repository', 'analyze_code'), nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed', 'cancelled'), default='pending', nullable=False, index=True)
    progress = db.Column(db.Integer, default=0, nullable=False)
    result = db.Column(db.Text)
    error_message = db.Column(db.Text)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(100), default='generate_document')  # For dashboard compatibility
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constants for validation
    VALID_TYPES = ['generate_document', 'sync_repository', 'analyze_code']
    VALID_STATUSES = ['pending', 'running', 'completed', 'failed', 'cancelled']
    STATUS_TRANSITIONS = {
        'pending': ['running', 'failed', 'cancelled'],
        'running': ['completed', 'failed', 'cancelled'],
        'completed': [],
        'failed': ['pending'],  # Allow retry
        'cancelled': ['pending']  # Allow retry
    }
    
    def __init__(self, **kwargs):
        """Initialize task with validation."""
        super().__init__(**kwargs)
        self.validate()
    
    def validate(self):
        """Validate task data."""
        if self.type not in self.VALID_TYPES:
            raise ValueError(f"Invalid task type: {self.type}")
        
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid task status: {self.status}")
        
        if not isinstance(self.progress, int) or self.progress < 0 or self.progress > 100:
            raise ValueError("Progress must be an integer between 0 and 100")
        
        if self.user_id is None:
            raise ValueError("User ID is required")
        
        if self.repository_id is None:
            raise ValueError("Repository ID is required")
    
    def can_transition_to(self, new_status):
        """Check if task can transition to new status."""
        if new_status not in self.VALID_STATUSES:
            return False
        
        if self.status == new_status:
            return True
        
        return new_status in self.STATUS_TRANSITIONS.get(self.status, [])
    
    def update_status(self, new_status):
        """Update task status with validation."""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        
        old_status = self.status
        self.status = new_status
        
        # Update timestamps based on status
        if new_status == 'running' and not self.started_at:
            self.started_at = datetime.utcnow()
        elif new_status in ['completed', 'failed', 'cancelled']:
            self.completed_at = datetime.utcnow()
        
        self.updated_at = datetime.utcnow()
        
        return old_status
    
    def update_progress(self, new_progress):
        """Update task progress with validation."""
        if not isinstance(new_progress, int) or new_progress < 0 or new_progress > 100:
            raise ValueError("Progress must be an integer between 0 and 100")
        
        # Don't allow progress decrease
        if new_progress < self.progress:
            raise ValueError("Progress cannot decrease")
        
        self.progress = new_progress
        self.updated_at = datetime.utcnow()
    
    def get_duration(self):
        """Get task duration in seconds."""
        if not self.started_at:
            return 0
        
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    def is_running(self):
        """Check if task is currently running."""
        return self.status == 'running'
    
    def is_completed(self):
        """Check if task is completed."""
        return self.status == 'completed'
    
    def is_failed(self):
        """Check if task is failed."""
        return self.status == 'failed'
    
    def is_pending(self):
        """Check if task is pending."""
        return self.status == 'pending'
    
    def is_cancelled(self):
        """Check if task is cancelled."""
        return self.status == 'cancelled'
    
    def can_retry(self):
        """Check if task can be retried."""
        return self.status in ['failed', 'cancelled']
    
    def get_status_info(self):
        """Get detailed status information."""
        info = {
            'status': self.status,
            'progress': self.progress,
            'duration': self.get_duration(),
            'can_retry': self.can_retry(),
            'is_running': self.is_running(),
            'is_completed': self.is_completed(),
            'is_failed': self.is_failed(),
            'is_pending': self.is_pending(),
            'is_cancelled': self.is_cancelled()
        }
        
        if self.started_at:
            info['started_at'] = self.started_at.isoformat()
        
        if self.completed_at:
            info['completed_at'] = self.completed_at.isoformat()
        
        return info
    
    def to_dict(self):
        """Convert task to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'repository_id': self.repository_id,
            'type': self.type,
            'status': self.status,
            'progress': self.progress,
            'result': self.result,
            'error_message': self.error_message,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'duration': self.get_duration(),
            'can_retry': self.can_retry(),
            'status_info': self.get_status_info()
        }
    
    def __repr__(self):
        """String representation of task."""
        return f'<Task {self.type} - {self.status}>'