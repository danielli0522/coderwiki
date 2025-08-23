"""
Repository service for managing Git repositories.
"""

import os
import subprocess
from datetime import datetime
from app import db
from app.models.repository import Repository
from app.models.task import Task

class RepositoryService:
    """Repository service for handling Git repository operations."""

    def __init__(self):
        """Initialize the repository service."""
        self.repo_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repos')

        # Create repositories directory if it doesn't exist
        if not os.path.exists(self.repo_base_path):
            os.makedirs(self.repo_base_path)

    def add_repository(self, user_id, name, url, description=None):
        """Add a new repository.

        Args:
            user_id (int): User ID
            name (str): Repository name
            url (str): Repository URL
            description (str, optional): Repository description

        Returns:
            Repository: The created repository object

        Raises:
            ValueError: If repository URL is invalid or already exists
        """
        # Check if repository already exists for this user
        existing_repo = Repository.query.filter_by(user_id=user_id, url=url).first()
        if existing_repo:
            raise ValueError("该仓库已存在")

        # Validate repository URL
        if not self._validate_repository_url(url):
            raise ValueError("无效的仓库URL")

        # Create new repository
        repository = Repository(
            user_id=user_id,
            name=name,
            url=url,
            description=description
        )

        # Save to database
        db.session.add(repository)
        db.session.commit()

        return repository

    def get_user_repositories(self, user_id, status=None):
        """Get repositories for a user.

        Args:
            user_id (int): User ID
            status (str, optional): Filter by status

        Returns:
            list: List of repository objects
        """
        query = Repository.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        return query.order_by(Repository.created_at.desc()).all()

    def get_repository_by_id(self, repository_id, user_id=None):
        """Get repository by ID.

        Args:
            repository_id (int): Repository ID
            user_id (int, optional): User ID for permission check

        Returns:
            Repository: Repository object or None if not found
        """
        query = Repository.query.filter_by(id=repository_id)

        if user_id:
            query = query.filter_by(user_id=user_id)

        return query.first()

    def update_repository(self, repository_id, user_id, **kwargs):
        """Update repository information.

        Args:
            repository_id (int): Repository ID
            user_id (int): User ID for permission check
            **kwargs: Fields to update

        Returns:
            Repository: Updated repository object

        Raises:
            ValueError: If repository not found or user doesn't have permission
        """
        repository = self.get_repository_by_id(repository_id, user_id)
        if not repository:
            raise ValueError("仓库不存在或您没有权限")

        # Update fields
        for field, value in kwargs.items():
            if hasattr(repository, field):
                setattr(repository, field, value)

        repository.updated_at = datetime.utcnow()
        db.session.commit()

        return repository

    def delete_repository(self, repository_id, user_id):
        """Delete a repository.

        Args:
            repository_id (int): Repository ID
            user_id (int): User ID for permission check

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If repository not found or user doesn't have permission
        """
        repository = self.get_repository_by_id(repository_id, user_id)
        if not repository:
            raise ValueError("仓库不存在或您没有权限")

        # Delete repository files
        repo_path = self._get_repository_path(repository_id)
        if os.path.exists(repo_path):
            subprocess.run(['rm', '-rf', repo_path], check=True)

        # Delete from database
        db.session.delete(repository)
        db.session.commit()

        return True

    def sync_repository(self, repository_id, user_id):
        """Sync a repository by pulling latest changes.

        Args:
            repository_id (int): Repository ID
            user_id (int): User ID for permission check

        Returns:
            Task: Task object for tracking the sync operation

        Raises:
            ValueError: If repository not found or user doesn't have permission
        """
        repository = self.get_repository_by_id(repository_id, user_id)
        if not repository:
            raise ValueError("仓库不存在或您没有权限")

        # Create task for sync operation
        task = Task(
            user_id=user_id,
            repository_id=repository_id,
            type='sync_repository',
            status='pending'
        )

        db.session.add(task)
        db.session.commit()

        return task

    def _validate_repository_url(self, url):
        """Validate repository URL.

        Args:
            url (str): Repository URL

        Returns:
            bool: True if URL is valid
        """
        # Basic validation for Git repository URLs
        return (url.startswith('https://github.com/') or
                url.startswith('https://gitlab.com/') or
                url.startswith('git@github.com:') or
                url.startswith('git@gitlab.com:'))

    def _get_repository_path(self, repository_id):
        """Get local path for repository.

        Args:
            repository_id (int): Repository ID

        Returns:
            str: Local path for the repository
        """
        return os.path.join(self.repo_base_path, str(repository_id))

    def clone_repository(self, repository_id, user_id):
        """Clone a repository to local storage.

        Args:
            repository_id (int): Repository ID
            user_id (int): User ID for permission check

        Returns:
            str: Path to the cloned repository

        Raises:
            ValueError: If repository not found or user doesn't have permission
        """
        repository = self.get_repository_by_id(repository_id, user_id)
        if not repository:
            raise ValueError("仓库不存在或您没有权限")

        repo_path = self._get_repository_path(repository_id)

        # Clone the repository
        try:
            subprocess.run([
                'git', 'clone', repository.url, repo_path
            ], check=True, capture_output=True)

            # Update repository status
            repository.status = 'active'
            repository.last_synced_at = datetime.utcnow()
            db.session.commit()

            return repo_path

        except subprocess.CalledProcessError as e:
            # Update repository status to error
            repository.status = 'error'
            db.session.commit()
            raise ValueError(f"克隆仓库失败: {e.stderr.decode().strip()}")

    def analyze_repository(self, repository_id, user_id):
        """Analyze repository structure and content.

        Args:
            repository_id (int): Repository ID
            user_id (int): User ID for permission check

        Returns:
            Task: Task object for tracking the analysis operation

        Raises:
            ValueError: If repository not found or user doesn't have permission
        """
        repository = self.get_repository_by_id(repository_id, user_id)
        if not repository:
            raise ValueError("仓库不存在或您没有权限")

        # Create task for analysis operation
        task = Task(
            user_id=user_id,
            repository_id=repository_id,
            type='analyze_code',
            status='pending'
        )

        db.session.add(task)
        db.session.commit()

        return task
