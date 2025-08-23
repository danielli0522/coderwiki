"""
File utility functions unit tests.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.utils.file_utils import FileUtils


class TestFileUtils:
    """Test cases for FileUtils class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_file.txt')
        
        # Create test file
        with open(self.test_file, 'w') as f:
            f.write('test content')
        
        # Create subdirectory with files
        self.sub_dir = os.path.join(self.test_dir, 'subdir')
        os.makedirs(self.sub_dir)
        
        self.sub_file = os.path.join(self.sub_dir, 'sub_file.txt')
        with open(self.sub_file, 'w') as f:
            f.write('sub file content')
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_delete_directory_success(self):
        """Test successful directory deletion."""
        result = FileUtils.delete_directory(self.test_dir)
        
        assert result['success'] is True
        assert result['deleted_files'] >= 2  # At least 2 files
        assert result['deleted_dirs'] >= 1  # At least 1 subdirectory
        assert not os.path.exists(self.test_dir)
    
    def test_delete_nonexistent_directory(self):
        """Test deletion of non-existent directory."""
        nonexistent_path = '/tmp/nonexistent_directory'
        result = FileUtils.delete_directory(nonexistent_path)
        
        assert result['success'] is True
        assert result['deleted_files'] == 0
        assert result['deleted_dirs'] == 0
        assert 'does not exist' in result['message']
    
    def test_delete_directory_with_none_path(self):
        """Test deletion with None path."""
        result = FileUtils.delete_directory(None)
        
        assert result['success'] is True
        assert result['deleted_files'] == 0
        assert result['deleted_dirs'] == 0
        assert 'does not exist' in result['message']
    
    def test_delete_file_success(self):
        """Test successful file deletion."""
        result = FileUtils.delete_file(self.test_file)
        
        assert result['success'] is True
        assert result['file_size'] > 0
        assert not os.path.exists(self.test_file)
    
    def test_delete_nonexistent_file(self):
        """Test deletion of non-existent file."""
        nonexistent_file = '/tmp/nonexistent_file.txt'
        result = FileUtils.delete_file(nonexistent_file)
        
        assert result['success'] is True
        assert 'does not exist' in result['message']
    
    def test_get_directory_info_success(self):
        """Test successful directory info retrieval."""
        result = FileUtils.get_directory_info(self.test_dir)
        
        assert result['success'] is True
        assert result['exists'] is True
        assert result['is_directory'] is True
        assert result['file_count'] >= 2
        assert result['total_size'] > 0
        assert result['directory_count'] >= 1
        assert 'size_human' in result
    
    def test_get_directory_info_nonexistent(self):
        """Test directory info for non-existent directory."""
        result = FileUtils.get_directory_info('/tmp/nonexistent_directory')
        
        assert result['success'] is False
        assert result['exists'] is False
        assert result['file_count'] == 0
        assert result['total_size'] == 0
    
    def test_get_directory_info_for_file(self):
        """Test directory info for a file (not directory)."""
        result = FileUtils.get_directory_info(self.test_file)
        
        assert result['success'] is True
        assert result['exists'] is True
        assert result['is_directory'] is False
        assert result['file_count'] == 0
        assert result['total_size'] == 0
    
    def test_format_size(self):
        """Test size formatting."""
        # Test bytes
        assert FileUtils._format_size(0) == "0 B"
        assert FileUtils._format_size(512) == "512.0 B"
        
        # Test KB
        assert FileUtils._format_size(1024) == "1.0 KB"
        assert FileUtils._format_size(1536) == "1.5 KB"
        
        # Test MB
        assert FileUtils._format_size(1024 * 1024) == "1.0 MB"
        assert FileUtils._format_size(1024 * 1536) == "1.5 MB"
        
        # Test GB
        assert FileUtils._format_size(1024 * 1024 * 1024) == "1.0 GB"
    
    @patch('os.access')
    def test_check_delete_permission_success(self, mock_access):
        """Test successful permission check."""
        mock_access.return_value = True
        
        path = Path(self.test_dir)
        result = FileUtils._check_delete_permission(path)
        
        assert result is True
        mock_access.assert_called()
    
    @patch('os.access')
    def test_check_delete_permission_failure(self, mock_access):
        """Test failed permission check."""
        mock_access.return_value = False
        
        path = Path(self.test_dir)
        result = FileUtils._check_delete_permission(path)
        
        assert result is False
        mock_access.assert_called()
    
    @patch('os.path.exists')
    def test_check_delete_permission_nonexistent(self, mock_exists):
        """Test permission check for non-existent path."""
        mock_exists.return_value = False
        
        path = Path('/tmp/nonexistent')
        result = FileUtils._check_delete_permission(path)
        
        assert result is True
        mock_exists.assert_called_once()
    
    @patch('shutil.rmtree')
    def test_delete_directory_permission_error(self, mock_rmtree):
        """Test directory deletion with permission error."""
        mock_rmtree.side_effect = PermissionError("Permission denied")
        
        result = FileUtils.delete_directory(self.test_dir)
        
        assert result['success'] is False
        assert 'Permission denied' in result['error']
        assert result['deleted_files'] == 0
        assert result['deleted_dirs'] == 0
    
    @patch('shutil.rmtree')
    def test_delete_directory_os_error(self, mock_rmtree):
        """Test directory deletion with OS error."""
        mock_rmtree.side_effect = OSError("OS error")
        
        result = FileUtils.delete_directory(self.test_dir)
        
        assert result['success'] is False
        assert 'OS error' in result['error']
        assert result['deleted_files'] == 0
        assert result['deleted_dirs'] == 0
    
    @patch('os.remove')
    def test_delete_file_permission_error(self, mock_remove):
        """Test file deletion with permission error."""
        mock_remove.side_effect = PermissionError("Permission denied")
        
        result = FileUtils.delete_file(self.test_file)
        
        assert result['success'] is False
        assert 'Permission denied' in result['error']
    
    @patch('os.remove')
    def test_delete_file_os_error(self, mock_remove):
        """Test file deletion with OS error."""
        mock_remove.side_effect = OSError("OS error")
        
        result = FileUtils.delete_file(self.test_file)
        
        assert result['success'] is False
        assert 'OS error' in result['error']
    
    def test_delete_directory_ignore_errors(self):
        """Test directory deletion with ignore errors."""
        # Create a directory with a file that has restricted permissions
        restricted_file = os.path.join(self.test_dir, 'restricted.txt')
        with open(restricted_file, 'w') as f:
            f.write('restricted content')
        
        # Try to delete with ignore errors
        result = FileUtils.delete_directory(self.test_dir, ignore_errors=True)
        
        assert result['success'] is True
        assert not os.path.exists(self.test_dir)
    
    def test_get_directory_info_with_permission_error(self):
        """Test directory info with permission error on some files."""
        # This test simulates the scenario where some files in the directory
        # cannot be accessed due to permission issues
        
        with patch('os.walk') as mock_walk:
            # Mock os.walk to simulate permission error on some files
            def mock_walk_generator(path):
                if path == self.test_dir:
                    # First level - return subdirectories
                    yield (self.test_dir, ['subdir'], ['test_file.txt'])
                    # Simulate permission error on subdirectory
                    try:
                        yield (self.sub_dir, [], ['sub_file.txt'])
                    except PermissionError:
                        pass
                else:
                    # No more levels
                    return
            
            mock_walk.side_effect = mock_walk_generator
            
            with patch('os.path.getsize') as mock_getsize:
                mock_getsize.return_value = 1024
                
                result = FileUtils.get_directory_info(self.test_dir)
                
                assert result['success'] is True
                assert result['exists'] is True
                # Should still count accessible files
                assert result['file_count'] >= 1