"""
Repository service layer for business logic.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import or_, and_, desc, asc, func
from app import db
from app.models.repository import Repository
from app.models.user import User
from app.models.document import Document
from app.models.task import Task
from app.utils.git_service import GitService
from app.utils.repo_analyzer import RepositoryAnalyzer
from app.utils.file_utils import FileUtils
from app.services.directory_service import DirectoryService
from app.utils.db_context import db_transaction, safe_db_commit
import logging

logger = logging.getLogger(__name__)


class RepositoryService:
    """Service for repository management business logic."""

    def __init__(self):
        """Initialize repository service."""
        # Use the centralized directory service
        self.directory_service = DirectoryService()
        
        # Initialize Git service with the unified repos directory
        git_repos_path = str(self.directory_service.repos_dir)
        self.git_service = GitService(base_repo_path=git_repos_path)
        self.repo_analyzer = RepositoryAnalyzer()

    def create_repository(self, user_id: int, url: str, name: str = None, description: str = None) -> Dict[str, Any]:
        """Create a new repository."""
        try:
            # Validate URL
            if not url:
                return {
                    'success': False,
                    'error': 'Repository URL is required'
                }

            # Extract name from URL if not provided
            if not name:
                name = Repository.get_repository_name_from_url_static(url)

            # Check if repository already exists for this user
            existing_repo = Repository.query.filter_by(
                user_id=user_id,
                url=url
            ).first()

            if existing_repo:
                return {
                    'success': False,
                    'error': 'Repository already exists for this user'
                }

            # Create new repository with database transaction
            with db_transaction():
                repository = Repository(
                    user_id=user_id,
                    name=name,
                    url=url,
                    description=description,
                    status='active',
                    clone_status='pending'
                )

                db.session.add(repository)
                db.session.flush()  # Get the ID without committing
                repo_id = repository.id  # Store ID while in session

            # Create all required directories using the unified directory service
            try:
                directory_paths = self.directory_service.create_repository_directories(name, repo_id)
                logger.info(f"Created unified directories for repository {repo_id}: {directory_paths}")
            except Exception as dir_error:
                logger.error(f"Failed to create directories for repository {repo_id}: {str(dir_error)}")
                # Don't fail the repository creation, but log the error

            logger.info(f"Created repository {repo_id} for user {user_id}")

            # Re-fetch repository for further operations
            repository = Repository.query.get(repo_id)
            
            # Start the cloning process
            try:
                self._start_cloning_process(repository)
                logger.info(f"Cloning process started for repository {repo_id}")
            except Exception as clone_error:
                logger.error(f"Failed to start cloning process for repository {repo_id}: {str(clone_error)}")
                try:
                    with db_transaction():
                        repo = Repository.query.get(repo_id)
                        repo.update_clone_status('failed', str(clone_error))
                        repo.status = 'error'
                except Exception as update_error:
                    logger.error(f"Failed to update repository status after clone error: {update_error}")

            return {
                'success': True,
                'repository_id': repo_id,
                'message': 'Repository created successfully'
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating repository: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create repository: {str(e)}'
            }

    def _start_cloning_process(self, repository: Repository) -> None:
        """Start the repository cloning process using unified directory structure."""
        try:
            # Update status to cloning
            repository.update_clone_status('cloning')
            db.session.commit()

            # Get the unified clone path
            clone_path = self.directory_service.get_repository_clone_path(repository.name, repository.id)

            # Start cloning process with specific path
            clone_result = self.git_service.clone_repository(repository.url, str(clone_path))

            if clone_result['success']:
                # Update repository with clone information using unified path
                repository.local_path = str(clone_path)
                repository.branch = clone_result.get('branch', 'main')
                repository.update_repository_info(
                    clone_result['commit_hash'],
                    clone_result['repo_size'],
                    clone_result['file_count'],
                    clone_result.get('metadata', {})
                )
                repository.update_clone_status('completed')
                repository.status = 'active'

                logger.info(f"Repository {repository.id} cloned successfully to {clone_path}")
            else:
                # Update with error information
                repository.update_clone_status('failed', clone_result['error'])
                repository.status = 'error'

                logger.error(f"Failed to clone repository {repository.id}: {clone_result['error']}")

            db.session.commit()

        except Exception as e:
            logger.error(f"Error in cloning process: {str(e)}")
            repository.update_clone_status('failed', str(e))
            repository.status = 'error'
            db.session.commit()

    def get_user_repositories(self, user_id: int) -> List[Repository]:
        """Get all repositories for a user."""
        try:
            # Check database connection health
            from app import db
            try:
                db.session.execute(db.text('SELECT 1'))
                logger.debug("Database connection health check passed")
            except Exception as health_check_error:
                logger.warning(f"Database connection health check failed: {health_check_error}")
                # Try to refresh the connection
                db.session.rollback()

            return Repository.query.filter_by(user_id=user_id).order_by(Repository.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error in get_user_repositories for user {user_id}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {e}")

            # Check if this is a column not found error
            if "Unknown column 'repositories.url'" in str(e):
                logger.warning("Detected missing 'url' column, attempting fallback query")
                try:
                    # Fallback: Use raw SQL to get repositories without the url column
                    from sqlalchemy import text
                    from app import db

                    # Get all columns except url
                    result = db.session.execute(text("""
                        SELECT id, user_id, name, description, language, status,
                               last_synced_at, created_at, updated_at, local_path,
                               branch, commit_hash, repo_size, file_count, is_private,
                               clone_status, clone_error, star_count, fork_count,
                               commit_count, last_commit, analysis_progress,
                               last_analysis, metadata
                        FROM repositories
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC
                    """), {'user_id': user_id})

                    # Convert raw results to Repository objects
                    repositories = []
                    for row in result.fetchall():
                        repo = Repository()
                        repo.id = row[0]
                        repo.user_id = row[1]
                        repo.name = row[2]
                        repo.description = row[3]
                        repo.language = row[4]
                        repo.status = row[5]
                        repo.last_synced_at = row[6]
                        repo.created_at = row[7]
                        repo.updated_at = row[8]
                        repo.local_path = row[9]
                        repo.branch = row[10]
                        repo.commit_hash = row[11]
                        repo.repo_size = row[12]
                        repo.file_count = row[13]
                        repo.is_private = row[14]
                        repo.clone_status = row[15]
                        repo.clone_error = row[16]
                        repo.star_count = row[17]
                        repo.fork_count = row[18]
                        repo.commit_count = row[19]
                        repo.last_commit = row[20]
                        repo.analysis_progress = row[21]
                        repo.last_analysis = row[22]
                        repo.repo_metadata = row[23]
                        # Set a default URL since it's missing
                        repo.url = f"https://github.com/user/{repo.name}"
                        repositories.append(repo)

                    logger.info(f"Fallback query successful, retrieved {len(repositories)} repositories")
                    return repositories

                except Exception as fallback_error:
                    logger.error(f"Fallback query also failed: {fallback_error}")
                    raise e  # Re-raise the original error

            # Try to get more information about the database connection
            try:
                from app import db
                logger.error(f"Database URI: {db.engine.url}")
                logger.error(f"Database engine: {db.engine}")
            except Exception as db_error:
                logger.error(f"Could not get database info: {db_error}")
            raise

    def get_repository_by_id(self, repository_id: int, user_id: int) -> Optional[Repository]:
        """Get repository by ID and user ID."""
        return Repository.query.filter_by(id=repository_id, user_id=user_id).first()

    def update_repository(self, repository_id: int, user_id: int,
                         **kwargs) -> Dict[str, Any]:
        """Update repository information."""
        try:
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            # Update allowed fields
            allowed_fields = ['name', 'description', 'status']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(repository, field):
                    setattr(repository, field, value)

            repository.updated_at = datetime.utcnow()
            db.session.commit()

            return {
                'success': True,
                'message': 'Repository updated successfully'
            }

        except Exception as e:
            logger.error(f"Error updating repository: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_repository(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete repository with cascading deletes and file cleanup.

        Args:
            repository_id: Repository ID to delete
            user_id: User ID for permission validation

        Returns:
            Dictionary with deletion result
        """
        try:
            # Get repository with permission validation
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            logger.info(f"Starting deletion process for repository {repository_id}: {repository.name}")

            # Start transaction for data consistency
            try:
                # Store repository info for cleanup logging
                repo_info = {
                    'id': repository.id,
                    'name': repository.name,
                    'url': repository.url,
                    'local_path': repository.local_path
                }

                # Step 1: Delete all repository directories using unified cleanup
                logger.info(f"Cleaning up unified directories for repository {repository_id}: {repository.name}")
                file_cleanup_result = self.directory_service.cleanup_repository_directories(
                    repository.name, repository.id
                )
                
                if not file_cleanup_result['success']:
                    logger.warning(f"Unified directory cleanup had issues for repository {repository_id}")
                    # Continue with database deletion even if file cleanup fails

                # Step 2: Delete database record (cascade delete will handle documents and tasks)
                logger.info(f"Deleting database record for repository {repository_id}")
                db.session.delete(repository)
                db.session.commit()

                # Prepare success response
                result = {
                    'success': True,
                    'message': 'Repository deleted successfully',
                    'repository_id': repository_id,
                    'repository_name': repo_info['name']
                }

                # Add file cleanup details if available
                if file_cleanup_result:
                    result['file_cleanup'] = file_cleanup_result

                logger.info(f"Repository {repository_id} deleted successfully")
                return result

            except Exception as e:
                # Rollback transaction on error
                db.session.rollback()
                logger.error(f"Database error during repository deletion: {str(e)}")
                return {
                    'success': False,
                    'error': f'Database error during deletion: {str(e)}'
                }

        except Exception as e:
            logger.error(f"Unexpected error during repository deletion: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error during deletion: {str(e)}'
            }

    def get_delete_confirmation(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get deletion confirmation information including associated data counts.

        Args:
            repository_id: Repository ID to check
            user_id: User ID for permission validation

        Returns:
            Dictionary with deletion confirmation information
        """
        try:
            # Get repository with permission validation
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            # Count associated documents
            documents_count = Document.query.filter_by(repository_id=repository_id).count()

            # Count associated tasks
            tasks_count = Task.query.filter_by(repository_id=repository_id).count()

            # Get local file information
            file_info = None
            if repository.local_path:
                file_info = FileUtils.get_directory_info(repository.local_path)

            # Prepare confirmation response
            confirmation_info = {
                'success': True,
                'repository': {
                    'id': repository.id,
                    'name': repository.name,
                    'url': repository.url,
                    'description': repository.description,
                    'status': repository.status,
                    'created_at': repository.created_at.isoformat() if repository.created_at else None,
                    'local_path': repository.local_path
                },
                'associated_data': {
                    'documents_count': documents_count,
                    'tasks_count': tasks_count
                },
                'file_cleanup': file_info,
                'warning_message': self._generate_deletion_warning(documents_count, tasks_count, file_info)
            }

            return confirmation_info

        except Exception as e:
            logger.error(f"Error getting delete confirmation for repository {repository_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Error getting deletion confirmation: {str(e)}'
            }

    def _generate_deletion_warning(self, documents_count: int, tasks_count: int, file_info: Optional[Dict[str, Any]]) -> str:
        """
        Generate appropriate warning message based on what will be deleted.

        Args:
            documents_count: Number of associated documents
            tasks_count: Number of associated tasks
            file_info: File system information

        Returns:
            Warning message string
        """
        warnings = []

        if documents_count > 0:
            warnings.append(f"{documents_count} document(s)")

        if tasks_count > 0:
            warnings.append(f"{tasks_count} task(s)")

        if file_info and file_info.get('exists') and file_info.get('file_count', 0) > 0:
            file_count = file_info.get('file_count', 0)
            size_human = file_info.get('size_human', 'Unknown size')
            warnings.append(f"{file_count} local file(s) ({size_human})")

        if warnings:
            return f"This action will permanently delete: {', '.join(warnings)}. This operation cannot be undone."
        else:
            return "This action will permanently delete the repository. This operation cannot be undone."

    def sync_repository(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """Sync repository with remote."""
        try:
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            if not repository.is_ready_for_analysis():
                return {
                    'success': False,
                    'error': 'Repository is not ready for sync'
                }

            # Update status to syncing
            repository.status = 'analyzing'
            db.session.commit()

            # Update repository
            if repository.local_path:
                update_result = self.git_service.update_repository(repository.local_path)

                if update_result['success']:
                    repository.update_repository_info(
                        update_result['commit_hash'],
                        update_result['repo_size'],
                        update_result['file_count'],
                        update_result.get('metadata', {})
                    )
                    repository.status = 'active'
                    repository.last_synced_at = datetime.utcnow()

                    logger.info(f"Repository {repository_id} synced successfully")
                else:
                    repository.status = 'error'
                    logger.error(f"Failed to sync repository {repository_id}: {update_result['error']}")
            else:
                repository.status = 'error'
                logger.error(f"Repository {repository_id} has no local path")

            db.session.commit()

            return {
                'success': True,
                'message': 'Repository synced successfully'
            }

        except Exception as e:
            logger.error(f"Error syncing repository: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_repository_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get repository statistics for a user."""
        try:
            logger.info(f"Getting repository statistics for user {user_id}")
            repositories = self.get_user_repositories(user_id)
            logger.info(f"Successfully retrieved {len(repositories)} repositories for user {user_id}")

            total_repos = len(repositories)
            active_repos = len([r for r in repositories if r.status == 'active'])
            error_repos = len([r for r in repositories if r.status == 'error'])
            cloned_repos = len([r for r in repositories if r.clone_status == 'completed'])

            total_size = sum(r.repo_size or 0 for r in repositories)
            total_files = sum(r.file_count or 0 for r in repositories)

            return {
                'total_repositories': total_repos,
                'active_repositories': active_repos,
                'error_repositories': error_repos,
                'cloned_repositories': cloned_repos,
                'total_size_bytes': total_size,
                'total_files': total_files,
                'success_rate': (cloned_repos / total_repos * 100) if total_repos > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting repository statistics for user {user_id}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Try a direct database query as a last resort
            try:
                logger.info("Attempting direct database query as fallback")
                from sqlalchemy import text
                from app import db

                # Get basic statistics directly from database
                result = db.session.execute(text("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error,
                        SUM(CASE WHEN clone_status = 'completed' THEN 1 ELSE 0 END) as cloned,
                        SUM(COALESCE(repo_size, 0)) as total_size,
                        SUM(COALESCE(file_count, 0)) as total_files
                    FROM repositories
                    WHERE user_id = :user_id
                """), {'user_id': user_id})

                row = result.fetchone()
                if row:
                    total_repos = row[0] or 0
                    active_repos = row[1] or 0
                    error_repos = row[2] or 0
                    cloned_repos = row[3] or 0
                    total_size = row[4] or 0
                    total_files = row[5] or 0
                    success_rate = (cloned_repos / total_repos * 100) if total_repos > 0 else 0

                    logger.info("Direct database query successful")
                    return {
                        'total_repositories': total_repos,
                        'active_repositories': active_repos,
                        'error_repositories': error_repos,
                        'cloned_repositories': cloned_repos,
                        'total_size_bytes': total_size,
                        'total_files': total_files,
                        'success_rate': success_rate
                    }
            except Exception as direct_query_error:
                logger.error(f"Direct database query also failed: {direct_query_error}")

            # Return default values if all else fails
            return {
                'total_repositories': 0,
                'active_repositories': 0,
                'error_repositories': 0,
                'cloned_repositories': 0,
                'total_size_bytes': 0,
                'total_files': 0,
                'success_rate': 0
            }

    def get_repositories_paginated(self, user_id: int, page: int = 1,
                                   per_page: int = 10, sort_field: str = 'created_at',
                                   sort_order: str = 'desc', status_filter: str = None,
                                   search_query: str = None) -> Dict[str, Any]:
        """Get paginated repositories with sorting and filtering.

        Args:
            user_id: User ID
            page: Page number (1-based)
            per_page: Items per page
            sort_field: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            status_filter: Filter by status
            search_query: Search in name and description

        Returns:
            Dictionary with paginated results
        """
        try:
            # Build base query
            query = Repository.query.filter_by(user_id=user_id)

            # Apply status filter
            if status_filter:
                query = query.filter(Repository.status == status_filter)

            # Add search functionality
            if search_query:
                search_term = f'%{search_query}%'
                query = query.filter(
                    db.or_(
                        Repository.name.ilike(search_term),
                        Repository.description.ilike(search_term),
                        Repository.url.ilike(search_term)
                    )
                )

            # Apply sorting
            sort_column = getattr(Repository, sort_field, Repository.created_at)
            if sort_order == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Execute pagination
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            # Convert to dictionaries
            repositories = [repo.to_dict() for repo in pagination.items]

            return {
                'repositories': repositories,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error getting paginated repositories: {str(e)}")
            return {
                'repositories': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0,
                'has_next': False,
                'has_prev': False,
                'success': False,
                'error': str(e)
            }

    def get_repository_status(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """Get detailed repository status including progress.

        Args:
            repository_id: Repository ID
            user_id: User ID

        Returns:
            Dictionary with repository status information
        """
        try:
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            # Get analysis progress
            analysis_progress = repository.analysis_progress or 0

            # Determine status text
            status_text = {
                'active': 'Ready',
                'cloning': 'Cloning...',
                'analyzing': 'Analyzing...',
                'error': 'Error',
                'inactive': 'Inactive'
            }.get(repository.status, 'Unknown')

            # Get clone status
            clone_status_text = {
                'pending': 'Pending',
                'cloning': 'Cloning...',
                'completed': 'Completed',
                'failed': 'Failed'
            }.get(repository.clone_status, 'Unknown')

            return {
                'success': True,
                'id': repository.id,
                'name': repository.name,
                'status': repository.status,
                'status_text': status_text,
                'clone_status': repository.clone_status,
                'clone_status_text': clone_status_text,
                'analysis_progress': analysis_progress,
                'last_analysis': repository.last_analysis.isoformat() if repository.last_analysis else None,
                'last_updated': repository.updated_at.isoformat() if repository.updated_at else None,
                'is_ready': repository.is_ready_for_analysis()
            }

        except Exception as e:
            logger.error(f"Error getting repository status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_repository_analysis_progress(self, repository_id: int, user_id: int,
                                          progress: int) -> Dict[str, Any]:
        """Update repository analysis progress.

        Args:
            repository_id: Repository ID
            user_id: User ID
            progress: Progress percentage (0-100)

        Returns:
            Dictionary with operation result
        """
        try:
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            # Update progress
            repository.update_analysis_progress(progress)

            # Update status based on progress
            if progress == 100:
                repository.status = 'active'
                repository.last_analysis = datetime.utcnow()
            elif progress > 0:
                repository.status = 'analyzing'

            db.session.commit()

            return {
                'success': True,
                'progress': progress,
                'message': 'Analysis progress updated'
            }

        except Exception as e:
            logger.error(f"Error updating analysis progress: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def reanalyze_repository(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """Start reanalysis of a repository.

        Args:
            repository_id: Repository ID
            user_id: User ID

        Returns:
            Dictionary with operation result
        """
        try:
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            if not repository.is_ready_for_analysis():
                return {
                    'success': False,
                    'error': 'Repository is not ready for analysis'
                }

            # Reset analysis progress and update status
            repository.analysis_progress = 0
            repository.status = 'analyzing'
            repository.last_analysis = None
            db.session.commit()

            # Here you would typically start a background task for analysis
            # For now, we'll simulate it by updating the progress
            logger.info(f"Started reanalysis of repository {repository_id}")

            return {
                'success': True,
                'message': 'Reanalysis started',
                'repository_id': repository_id
            }

        except Exception as e:
            logger.error(f"Error starting reanalysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_enhanced_repository_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get enhanced repository statistics for dashboard.

        Args:
            user_id: User ID

        Returns:
            Dictionary with detailed statistics
        """
        try:
            # Get all repositories for user
            repositories = Repository.query.filter_by(user_id=user_id).all()

            # Basic counts
            total_repos = len(repositories)

            # Status counts
            status_counts = {}
            for repo in repositories:
                status = repo.status
                status_counts[status] = status_counts.get(status, 0) + 1

            # Clone status counts
            clone_counts = {}
            for repo in repositories:
                status = repo.clone_status
                clone_counts[status] = clone_counts.get(status, 0) + 1

            # Analysis progress summary
            analyzing_repos = [r for r in repositories if r.status == 'analyzing']
            avg_analysis_progress = 0
            if analyzing_repos:
                avg_analysis_progress = sum(r.analysis_progress or 0 for r in analyzing_repos) / len(analyzing_repos)

            # GitHub statistics
            total_stars = sum(r.star_count or 0 for r in repositories)
            total_forks = sum(r.fork_count or 0 for r in repositories)
            total_commits = sum(r.commit_count or 0 for r in repositories)

            # Size statistics
            total_size = sum(r.repo_size or 0 for r in repositories)
            avg_size = total_size / total_repos if total_repos > 0 else 0

            # Language distribution
            languages = {}
            for repo in repositories:
                if repo.language:
                    languages[repo.language] = languages.get(repo.language, 0) + 1

            # Recent activity (repositories updated in last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = len([r for r in repositories if r.updated_at > week_ago])

            return {
                'summary': {
                    'total_repositories': total_repos,
                    'recent_activity': recent_activity,
                    'average_analysis_progress': round(avg_analysis_progress, 1)
                },
                'status_distribution': status_counts,
                'clone_status_distribution': clone_counts,
                'github_statistics': {
                    'total_stars': total_stars,
                    'total_forks': total_forks,
                    'total_commits': total_commits
                },
                'size_statistics': {
                    'total_size_bytes': total_size,
                    'average_size_bytes': round(avg_size, 2)
                },
                'language_distribution': languages,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error getting enhanced repository statistics: {str(e)}")
            return {
                'summary': {
                    'total_repositories': 0,
                    'recent_activity': 0,
                    'average_analysis_progress': 0
                },
                'status_distribution': {},
                'clone_status_distribution': {},
                'github_statistics': {
                    'total_stars': 0,
                    'total_forks': 0,
                    'total_commits': 0
                },
                'size_statistics': {
                    'total_size_bytes': 0,
                    'average_size_bytes': 0
                },
                'language_distribution': {},
                'success': False,
                'error': str(e)
            }

    def update_repository_github_stats(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """Update repository GitHub statistics.

        Args:
            repository_id: Repository ID
            user_id: User ID

        Returns:
            Dictionary with operation result
        """
        try:
            repository = self.get_repository_by_id(repository_id, user_id)

            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found'
                }

            # Update GitHub statistics if it's a GitHub repository
            if 'github.com' not in repository.url:
                return {
                    'success': True,
                    'message': 'Repository is not a GitHub repository'
                }

            try:
                github_stats = self.repo_analyzer._get_github_stats(repository.url)

                if github_stats:
                    # Update repository with GitHub stats
                    repository.update_github_stats(
                        star_count=github_stats.get('stars', 0),
                        fork_count=github_stats.get('forks', 0),
                        commit_count=github_stats.get('commit_count', 0),
                        last_commit=github_stats.get('last_commit')
                    )

                    # Update language if available
                    if github_stats.get('language'):
                        repository.language = github_stats['language']

                    db.session.commit()

                    return {
                        'success': True,
                        'message': 'GitHub statistics updated',
                        'stats': github_stats
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to fetch GitHub statistics'
                    }
            except Exception as e:
                logger.error(f"Error updating GitHub stats: {str(e)}")
                return {
                    'success': False,
                    'error': str(e)
                }

        except Exception as e:
            logger.error(f"Error updating GitHub stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def bulk_delete_repositories(self, user_id: int, repository_ids: List[int]) -> Dict[str, Any]:
        """Delete multiple repositories.

        Args:
            user_id: User ID
            repository_ids: List of repository IDs to delete

        Returns:
            Dictionary with operation result
        """
        try:
            # Get repositories that belong to the user
            repositories = Repository.query.filter(
                Repository.id.in_(repository_ids),
                Repository.user_id == user_id
            ).all()

            if not repositories:
                return {
                    'success': False,
                    'error': 'No repositories found for deletion'
                }

            deleted_count = 0
            failed_count = 0

            for repository in repositories:
                try:
                    # Delete local repository files
                    if repository.local_path:
                        self.git_service.delete_repository(repository.local_path)

                    # Delete database record
                    db.session.delete(repository)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Error deleting repository {repository.id}: {str(e)}")
                    failed_count += 1

            db.session.commit()

            return {
                'success': True,
                'deleted_count': deleted_count,
                'failed_count': failed_count,
                'message': f'Successfully deleted {deleted_count} repositories'
            }

        except Exception as e:
            logger.error(f"Error in bulk deletion: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
