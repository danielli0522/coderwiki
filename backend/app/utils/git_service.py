"""
Git repository management utilities.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GitService:
    """Service for Git repository operations."""

    def __init__(self, base_repo_path: str = None):
        """Initialize Git service with base repository path."""
        if base_repo_path is None:
            # 从配置中获取路径，如果没有配置则使用默认路径
            try:
                from flask import current_app
                base_repo_path = current_app.config.get('GIT_REPOS_PATH', '/tmp/coderwiki_repos')
            except:
                # 如果无法获取Flask配置，使用默认路径
                base_repo_path = '/tmp/coderwiki_repos'

        self.base_repo_path = Path(base_repo_path)
        self.base_repo_path.mkdir(parents=True, exist_ok=True)

    def clone_repository(self, url: str, local_path: Optional[str] = None,
                       branch: str = "main") -> Dict[str, Any]:
        """
        Clone a Git repository.

        Args:
            url: Repository URL
            local_path: Local path to clone to (optional)
            branch: Branch to clone

        Returns:
            Dictionary with clone result information
        """
        try:
            # Generate local path if not provided
            if not local_path:
                repo_name = self._extract_repo_name(url)
                local_path = self.base_repo_path / f"{repo_name}_{hash(url) % 10000}"
            else:
                local_path = Path(local_path)

            # Remove existing directory if it exists
            if local_path.exists():
                shutil.rmtree(local_path)

            # Create parent directory
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone the repository
            logger.info(f"Cloning repository {url} to {local_path}")

            # Try shallow clone first for better performance
            try:
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', '--branch', branch, url, str(local_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
            except subprocess.TimeoutExpired:
                logger.error(f"Clone timeout for repository {url}")
                return {
                    'success': False,
                    'error': 'Clone timeout',
                    'local_path': None,
                    'commit_hash': None
                }

            if result.returncode != 0:
                # Try full clone if shallow clone fails
                result = subprocess.run(
                    ['git', 'clone', '--branch', branch, url, str(local_path)],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes timeout
                )

            if result.returncode != 0:
                logger.error(f"Failed to clone repository {url}: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'local_path': None,
                    'commit_hash': None
                }

            # Get repository information
            repo_info = self._get_repository_info(local_path)

            return {
                'success': True,
                'local_path': str(local_path),
                'commit_hash': repo_info['commit_hash'],
                'repo_size': repo_info['repo_size'],
                'file_count': repo_info['file_count'],
                'branch': repo_info['branch'],
                'metadata': repo_info['metadata']
            }

        except Exception as e:
            logger.error(f"Error cloning repository {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'local_path': None,
                'commit_hash': None
            }

    def _extract_repo_name(self, url: str) -> str:
        """Extract repository name from URL."""
        if url.endswith('.git'):
            url = url[:-4]
        return url.split('/')[-1]

    def _get_repository_info(self, local_path: Path) -> Dict[str, Any]:
        """Get repository information from local path."""
        try:
            # Get current commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip() if result.returncode == 0 else None

            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            branch = result.stdout.strip() if result.returncode == 0 else 'main'

            # Get repository size and file count
            file_count = 0
            repo_size = 0
            for f in local_path.rglob('*'):
                if f.is_file():
                    file_count += 1
                    repo_size += f.stat().st_size

            # Get repository metadata
            metadata = self._get_repository_metadata(local_path)

            return {
                'commit_hash': commit_hash,
                'repo_size': repo_size,
                'file_count': file_count,
                'branch': branch,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return {
                'commit_hash': None,
                'repo_size': 0,
                'file_count': 0,
                'branch': 'main',
                'metadata': {}
            }

    def _get_repository_metadata(self, local_path: Path) -> Dict[str, Any]:
        """Get repository metadata."""
        metadata = {}

        try:
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                metadata['remote_url'] = result.stdout.strip()

            # Get repository description (from README or git config)
            readme_path = local_path / 'README.md'
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        metadata['description'] = first_line[2:]

            # Get default branch
            result = subprocess.run(
                ['git', 'config', 'init.defaultBranch'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                metadata['default_branch'] = result.stdout.strip()

        except Exception as e:
            logger.warning(f"Error getting repository metadata: {str(e)}")

        return metadata

    def update_repository(self, local_path: Path) -> Dict[str, Any]:
        """Update repository by pulling latest changes."""
        try:
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull', 'origin', 'HEAD'],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr
                }

            # Get updated repository information
            repo_info = self._get_repository_info(local_path)

            return {
                'success': True,
                'commit_hash': repo_info['commit_hash'],
                'repo_size': repo_info['repo_size'],
                'file_count': repo_info['file_count'],
                'metadata': repo_info['metadata']
            }

        except Exception as e:
            logger.error(f"Error updating repository: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_repository(self, local_path: Path) -> bool:
        """Delete local repository."""
        try:
            if local_path.exists():
                shutil.rmtree(local_path)
                logger.info(f"Deleted repository at {local_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting repository: {str(e)}")
            return False

    def validate_repository_url(self, url: str) -> bool:
        """Validate if repository URL is accessible."""
        try:
            # Try to get repository information without cloning
            result = subprocess.run(
                ['git', 'ls-remote', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False
