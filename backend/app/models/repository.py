"""
Repository model definition.
"""

import re
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Repository(db.Model):
    """Repository model for storing Git repository information."""

    __tablename__ = 'repositories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    language = db.Column(db.String(100))
    status = db.Column(db.Enum('active', 'inactive', 'error', 'cloning', 'analyzing'), default='active', nullable=False, index=True)
    last_synced_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    local_path = db.Column(db.String(1000))
    branch = db.Column(db.String(255))
    commit_hash = db.Column(db.String(40))
    repo_size = db.Column(db.Integer)
    file_count = db.Column(db.Integer)
    is_private = db.Column(db.Boolean)
    clone_status = db.Column(db.Enum('pending', 'cloning', 'completed', 'failed'))
    clone_error = db.Column(db.Text)
    star_count = db.Column(db.Integer)
    fork_count = db.Column(db.Integer)
    commit_count = db.Column(db.Integer)
    last_commit = db.Column(db.String(50))
    analysis_progress = db.Column(db.Integer)
    last_analysis = db.Column(db.DateTime)
    repo_metadata = db.Column('repo_metadata', db.JSON)

    # Relationships
    documents = db.relationship('Document', backref='repository', lazy='dynamic',
                               cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='repository', lazy='dynamic',
                           cascade='all, delete-orphan')

    def to_dict(self):
        """Convert repository to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'language': self.language,
            'status': self.status,
            'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'local_path': self.local_path,
            'branch': self.branch,
            'commit_hash': self.commit_hash,
            'repo_size': self.repo_size,
            'file_count': self.file_count,
            'is_private': self.is_private,
            'clone_status': self.clone_status,
            'clone_error': self.clone_error,
            'star_count': self.star_count,
            'fork_count': self.fork_count,
            'commit_count': self.commit_count,
            'last_commit': self.last_commit,
            'analysis_progress': self.analysis_progress,
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'metadata': self.repo_metadata
        }

    def __repr__(self):
        """String representation of repository."""
        return f'<Repository {self.name}>'

    @staticmethod
    def validate_github_url(url):
        """Validate GitHub repository URL format."""
        github_pattern = r'^https?://github\.com/[^/]+/[^/]+/?$'
        return re.match(github_pattern, url) is not None

    @staticmethod
    def validate_git_url(url):
        """Validate Git repository URL format."""
        git_pattern = r'^https?://.*\.git$|^git@.*:.*\.git$'
        return re.match(git_pattern, url) is not None

    @staticmethod
    def get_repository_name_from_url_static(url):
        """Extract repository name from URL (static method)."""
        if 'github.com' in url:
            return url.split('/')[-1].replace('.git', '')
        return url.split('/')[-1].replace('.git', '')

    def update_repository_info(self, commit_hash: str, repo_size: int, file_count: int, metadata: dict = None):
        """Update repository information after cloning or syncing."""
        self.commit_hash = commit_hash
        self.repo_size = repo_size
        self.file_count = file_count
        if metadata:
            self.repo_metadata = metadata
        self.updated_at = datetime.utcnow()

    def update_clone_status(self, status: str, error: str = None):
        """Update clone status."""
        self.clone_status = status
        if error:
            self.clone_error = error
        self.updated_at = datetime.utcnow()

    def is_ready_for_analysis(self) -> bool:
        """Check if repository is ready for analysis."""
        return (
            self.local_path is not None and
            self.clone_status == 'completed' and
            self.commit_hash is not None
        )
