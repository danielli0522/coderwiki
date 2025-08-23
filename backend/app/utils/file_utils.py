"""
File utility functions for repository cleanup operations.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import stat

logger = logging.getLogger(__name__)


class FileUtils:
    """Utility class for file system operations."""
    
    @staticmethod
    def delete_directory(directory_path: str, ignore_errors: bool = False) -> Dict[str, Any]:
        """
        Recursively delete a directory and all its contents.
        
        Args:
            directory_path: Path to the directory to delete
            ignore_errors: Whether to ignore errors during deletion
            
        Returns:
            Dictionary with deletion result
        """
        try:
            if not directory_path or not os.path.exists(directory_path):
                return {
                    'success': True,
                    'message': 'Directory does not exist',
                    'deleted_files': 0,
                    'deleted_dirs': 0
                }
            
            path = Path(directory_path)
            
            # Check if we have permission to delete
            if not FileUtils._check_delete_permission(path):
                return {
                    'success': False,
                    'error': 'Permission denied for directory deletion',
                    'deleted_files': 0,
                    'deleted_dirs': 0
                }
            
            # Count files and directories before deletion
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(directory_path):
                file_count += len(files)
                dir_count += len(dirs)
            
            # Perform the deletion
            if ignore_errors:
                shutil.rmtree(directory_path, ignore_errors=True)
            else:
                shutil.rmtree(directory_path)
            
            logger.info(f"Successfully deleted directory {directory_path}: {file_count} files, {dir_count} directories")
            
            return {
                'success': True,
                'message': f'Directory deleted successfully: {file_count} files, {dir_count} directories',
                'deleted_files': file_count,
                'deleted_dirs': dir_count
            }
            
        except PermissionError as e:
            error_msg = f"Permission denied while deleting directory {directory_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'deleted_files': 0,
                'deleted_dirs': 0
            }
        except OSError as e:
            error_msg = f"OS error while deleting directory {directory_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'deleted_files': 0,
                'deleted_dirs': 0
            }
        except Exception as e:
            error_msg = f"Unexpected error while deleting directory {directory_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'deleted_files': 0,
                'deleted_dirs': 0
            }
    
    @staticmethod
    def delete_file(file_path: str) -> Dict[str, Any]:
        """
        Delete a single file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            if not file_path or not os.path.exists(file_path):
                return {
                    'success': True,
                    'message': 'File does not exist'
                }
            
            path = Path(file_path)
            
            # Check if we have permission to delete
            if not FileUtils._check_delete_permission(path):
                return {
                    'success': False,
                    'error': 'Permission denied for file deletion'
                }
            
            # Get file size before deletion for logging
            file_size = path.stat().st_size
            
            # Perform the deletion
            os.remove(file_path)
            
            logger.info(f"Successfully deleted file {file_path} ({file_size} bytes)")
            
            return {
                'success': True,
                'message': f'File deleted successfully: {file_size} bytes',
                'file_size': file_size
            }
            
        except PermissionError as e:
            error_msg = f"Permission denied while deleting file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except OSError as e:
            error_msg = f"OS error while deleting file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error while deleting file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    @staticmethod
    def get_directory_info(directory_path: str) -> Dict[str, Any]:
        """
        Get information about a directory including file count and total size.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Dictionary with directory information
        """
        try:
            if not directory_path or not os.path.exists(directory_path):
                return {
                    'exists': False,
                    'file_count': 0,
                    'total_size': 0,
                    'directory_count': 0
                }
            
            if not os.path.isdir(directory_path):
                return {
                    'exists': True,
                    'is_directory': False,
                    'file_count': 0,
                    'total_size': 0,
                    'directory_count': 0
                }
            
            total_size = 0
            file_count = 0
            directory_count = 0
            
            for root, dirs, files in os.walk(directory_path):
                directory_count += len(dirs)
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
            
            return {
                'exists': True,
                'is_directory': True,
                'file_count': file_count,
                'total_size': total_size,
                'directory_count': directory_count,
                'size_human': FileUtils._format_size(total_size)
            }
            
        except Exception as e:
            logger.error(f"Error getting directory info for {directory_path}: {str(e)}")
            return {
                'exists': False,
                'error': str(e),
                'file_count': 0,
                'total_size': 0,
                'directory_count': 0
            }
    
    @staticmethod
    def _check_delete_permission(path: Path) -> bool:
        """
        Check if we have permission to delete the given path.
        
        Args:
            path: Path object to check
            
        Returns:
            True if we have permission, False otherwise
        """
        try:
            # Check if path exists
            if not path.exists():
                return True
            
            # Check write permission on the path itself
            if os.access(path, os.W_OK):
                return True
            
            # Check write permission on parent directory
            parent = path.parent
            if parent.exists() and os.access(parent, os.W_OK):
                return True
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        Format size in bytes to human readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human readable size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"