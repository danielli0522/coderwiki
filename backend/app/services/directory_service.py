"""
Directory Service - Centralized directory management for CoderWiki
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DirectoryService:
    """Centralized directory management for consistent path handling across services"""

    def __init__(self):
        """Initialize directory service with unified paths"""
        # Base directory for all CoderWiki output (project root)
        self.base_output_dir = Path("coderwiki-output-docs")

        # Subdirectories as specified in the architecture
        self.repos_dir = self.base_output_dir / "repos"
        self.ai_generate_doc_dir = self.base_output_dir / "ai-generate-doc"
        self.mkdocs_site_dir = self.base_output_dir / "mkdocs-site"

        # Ensure all directories exist
        self._ensure_directories_exist()

        logger.info(f"DirectoryService initialized with base: {self.base_output_dir}")

    def _ensure_directories_exist(self):
        """Ensure all required directories exist"""
        for directory in [self.repos_dir, self.ai_generate_doc_dir, self.mkdocs_site_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def get_repository_clone_path(self, repository_name: str, repository_id: int) -> Path:
        """
        Get the path for cloning a repository

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Path for repository clone
        """
        safe_name = self._sanitize_name(repository_name)
        return self.repos_dir / f"{safe_name}_{repository_id}"

    def get_ai_docs_path(self, repository_name: str, repository_id: int) -> Path:
        """
        Get the path for AI-generated documents

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Path for AI-generated documents
        """
        safe_name = self._sanitize_name(repository_name)
        ai_docs_path = self.ai_generate_doc_dir / f"{safe_name}_{repository_id}"
        ai_docs_path.mkdir(parents=True, exist_ok=True)
        return ai_docs_path

    def get_mkdocs_site_path(self, repository_name: str, repository_id: int) -> Path:
        """
        Get the path for MkDocs site

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Path for MkDocs site
        """
        safe_name = self._sanitize_name(repository_name)
        mkdocs_path = self.mkdocs_site_dir / f"{safe_name}_{repository_id}"
        return mkdocs_path

    def get_mkdocs_docs_path(self, repository_name: str, repository_id: int) -> Path:
        """
        Get the docs subdirectory path for MkDocs site

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Path for MkDocs docs directory
        """
        site_path = self.get_mkdocs_site_path(repository_name, repository_id)
        docs_path = site_path / "docs"
        docs_path.mkdir(parents=True, exist_ok=True)
        return docs_path

    def get_mkdocs_build_path(self, repository_name: str, repository_id: int) -> Path:
        """
        Get the built site path for MkDocs

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Path for built MkDocs site
        """
        site_path = self.get_mkdocs_site_path(repository_name, repository_id)
        return site_path / "site"

    def create_repository_directories(self, repository_name: str, repository_id: int) -> Dict[str, Path]:
        """
        Create all directories for a repository

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Dictionary with all created paths
        """
        paths = {
            'clone_path': self.get_repository_clone_path(repository_name, repository_id),
            'ai_docs_path': self.get_ai_docs_path(repository_name, repository_id),
            'mkdocs_site_path': self.get_mkdocs_site_path(repository_name, repository_id),
            'mkdocs_docs_path': self.get_mkdocs_docs_path(repository_name, repository_id),
            'mkdocs_build_path': self.get_mkdocs_build_path(repository_name, repository_id)
        }

        # Create directories that need to exist upfront
        paths['ai_docs_path'].mkdir(parents=True, exist_ok=True)
        paths['mkdocs_docs_path'].mkdir(parents=True, exist_ok=True)

        logger.info(f"Created directories for repository {repository_name}_{repository_id}")
        return paths

    def cleanup_repository_directories(self, repository_name: str, repository_id: int) -> Dict[str, Any]:
        """
        Clean up all directories for a repository

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Cleanup result dictionary
        """
        import shutil

        paths_to_remove = [
            self.get_repository_clone_path(repository_name, repository_id),
            self.get_ai_docs_path(repository_name, repository_id),
            self.get_mkdocs_site_path(repository_name, repository_id)
        ]

        cleanup_results = []

        for path in paths_to_remove:
            try:
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                        cleanup_results.append(f"Removed directory: {path}")
                    else:
                        path.unlink()
                        cleanup_results.append(f"Removed file: {path}")
                else:
                    cleanup_results.append(f"Path does not exist: {path}")
            except Exception as e:
                cleanup_results.append(f"Failed to remove {path}: {str(e)}")
                logger.error(f"Failed to cleanup {path}: {str(e)}")

        logger.info(f"Cleaned up directories for repository {repository_name}_{repository_id}")

        return {
            'success': True,
            'cleanup_results': cleanup_results
        }

    def get_directory_info(self, repository_name: str, repository_id: int) -> Dict[str, Any]:
        """
        Get information about all repository directories

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Directory information dictionary
        """
        paths = {
            'clone_path': self.get_repository_clone_path(repository_name, repository_id),
            'ai_docs_path': self.get_ai_docs_path(repository_name, repository_id),
            'mkdocs_site_path': self.get_mkdocs_site_path(repository_name, repository_id),
            'mkdocs_build_path': self.get_mkdocs_build_path(repository_name, repository_id)
        }

        info = {}

        for name, path in paths.items():
            if path.exists():
                if path.is_dir():
                    # Count files and calculate size
                    file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                    total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())

                    info[name] = {
                        'path': str(path),
                        'exists': True,
                        'is_directory': True,
                        'file_count': file_count,
                        'total_size': total_size,
                        'size_human': self._format_bytes(total_size)
                    }
                else:
                    info[name] = {
                        'path': str(path),
                        'exists': True,
                        'is_directory': False,
                        'size': path.stat().st_size,
                        'size_human': self._format_bytes(path.stat().st_size)
                    }
            else:
                info[name] = {
                    'path': str(path),
                    'exists': False
                }

        return info

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize repository name for filesystem compatibility

        Args:
            name: Original repository name

        Returns:
            Sanitized name
        """
        import re
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*\s]', '_', name)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')

        # Ensure it's not empty
        if not sanitized:
            sanitized = 'unnamed'

        return sanitized

    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human readable format"""
        if bytes_size == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(bytes_size, 1024)))
        p = math.pow(1024, i)
        s = round(bytes_size / p, 2)

        return f"{s} {size_names[i]}"

    def get_base_output_dir(self) -> Path:
        """Get the base output directory"""
        return self.base_output_dir

    def get_all_repository_paths(self, repository_name: str, repository_id: int) -> Dict[str, str]:
        """
        Get all paths for a repository as strings (for compatibility)

        Args:
            repository_name: Repository name (sanitized)
            repository_id: Repository ID

        Returns:
            Dictionary with all paths as strings
        """
        return {
            'clone_path': str(self.get_repository_clone_path(repository_name, repository_id)),
            'ai_docs_path': str(self.get_ai_docs_path(repository_name, repository_id)),
            'mkdocs_site_path': str(self.get_mkdocs_site_path(repository_name, repository_id)),
            'mkdocs_docs_path': str(self.get_mkdocs_docs_path(repository_name, repository_id)),
            'mkdocs_build_path': str(self.get_mkdocs_build_path(repository_name, repository_id))
        }
