"""
Analysis models for code analysis functionality.
"""

from datetime import datetime
from app import db


class CodeAnalysis(db.Model):
    """Code analysis result model."""
    
    __tablename__ = 'code_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # 'structure', 'dependencies', 'complexity', 'tech_stack'
    status = db.Column(db.String(50), nullable=False, default='pending')  # 'pending', 'analyzing', 'completed', 'failed'
    result_data = db.Column(db.JSON)  # Analysis result JSON data
    analysis_time = db.Column(db.Float)  # Analysis duration in seconds
    error_message = db.Column(db.Text)  # Error message if analysis failed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = db.relationship('Repository', backref='analyses')
    
    def __init__(self, repository_id, analysis_type, **kwargs):
        self.repository_id = repository_id
        self.analysis_type = analysis_type
        super(CodeAnalysis, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert analysis to dictionary for API responses."""
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'analysis_type': self.analysis_type,
            'status': self.status,
            'result_data': self.result_data,
            'analysis_time': self.analysis_time,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of code analysis."""
        return f'<CodeAnalysis {self.analysis_type} for Repository {self.repository_id}>'
    
    def update_status(self, status, error_message=None):
        """Update analysis status and optionally error message."""
        self.status = status
        if error_message:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def complete_analysis(self, result_data, analysis_time):
        """Mark analysis as completed with results."""
        self.status = 'completed'
        self.result_data = result_data
        self.analysis_time = analysis_time
        self.updated_at = datetime.utcnow()
    
    def fail_analysis(self, error_message):
        """Mark analysis as failed with error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.updated_at = datetime.utcnow()


class AnalysisCache(db.Model):
    """Analysis cache model for storing analysis results."""
    
    __tablename__ = 'analysis_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    cache_key = db.Column(db.String(255), nullable=False, unique=True, index=True)
    cache_data = db.Column(db.JSON, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    repository = db.relationship('Repository', backref='cache_entries')
    
    def __init__(self, repository_id, cache_key, cache_data, expires_at, **kwargs):
        self.repository_id = repository_id
        self.cache_key = cache_key
        self.cache_data = cache_data
        self.expires_at = expires_at
        super(AnalysisCache, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert cache entry to dictionary for API responses."""
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'cache_key': self.cache_key,
            'cache_data': self.cache_data,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of analysis cache."""
        return f'<AnalysisCache {self.cache_key} for Repository {self.repository_id}>'
    
    def is_expired(self):
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at
    
    def update_cache(self, cache_data, expires_at):
        """Update cache data and expiration."""
        self.cache_data = cache_data
        self.expires_at = expires_at
        self.created_at = datetime.utcnow()