"""
Unit tests for RepositoryService.
"""

import pytest
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.services.repository_service import RepositoryService


class TestRepositoryService:
    """Test cases for RepositoryService."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(self.user)
        db.session.commit()
        
        self.service = RepositoryService()
    
    def teardown_method(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_repository_success(self):
        """Test successful repository creation."""
        with patch.object(self.service, '_start_cloning_process') as mock_clone:
            result = self.service.create_repository(
                user_id=self.user.id,
                url='https://github.com/user/test-repo',
                name='test-repo',
                description='Test repository'
            )
            
            assert result['success'] is True
            assert 'repository_id' in result
            assert result['message'] == 'Repository created and cloning started'
            
            # Verify repository was created in database
            repo = Repository.query.filter_by(url='https://github.com/user/test-repo').first()
            assert repo is not None
            assert repo.name == 'test-repo'
            assert repo.description == 'Test repository'
            assert repo.status == 'cloning'
            assert repo.clone_status == 'pending'
            
            # Verify cloning process was started
            mock_clone.assert_called_once()
    
    def test_create_repository_invalid_url(self):
        """Test repository creation with invalid URL."""
        result = self.service.create_repository(
            user_id=self.user.id,
            url='invalid-url',
            name='test-repo'
        )
        
        assert result['success'] is False
        assert 'Invalid repository URL format' in result['error']
    
    def test_create_repository_duplicate_url(self):
        """Test repository creation with duplicate URL."""
        # Create first repository
        repo1 = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo1)
        db.session.commit()
        
        # Try to create duplicate
        result = self.service.create_repository(
            user_id=self.user.id,
            url='https://github.com/user/test-repo',
            name='test-repo-2'
        )
        
        assert result['success'] is False
        assert 'Repository already exists for this user' in result['error']
    
    def test_create_repository_auto_generate_name(self):
        """Test repository creation with auto-generated name."""
        with patch.object(self.service, '_start_cloning_process'):
            result = self.service.create_repository(
                user_id=self.user.id,
                url='https://github.com/user/my-awesome-repo'
            )
            
            assert result['success'] is True
            
            # Verify name was auto-generated
            repo = Repository.query.filter_by(url='https://github.com/user/my-awesome-repo').first()
            assert repo.name == 'my-awesome-repo'
    
    def test_get_user_repositories(self):
        """Test getting user repositories."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='repo2',
            url='https://github.com/user/repo2'
        )
        
        # Create repository for another user
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password_hash='hashed_password'
        )
        db.session.add(other_user)
        repo3 = Repository(
            user_id=other_user.id,
            name='repo3',
            url='https://github.com/user/repo3'
        )
        
        db.session.add_all([repo1, repo2, repo3])
        db.session.commit()
        
        repositories = self.service.get_user_repositories(self.user.id)
        
        assert len(repositories) == 2
        assert repo1 in repositories
        assert repo2 in repositories
        assert repo3 not in repositories
    
    def test_get_repository_by_id(self):
        """Test getting repository by ID."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        # Test successful retrieval
        found_repo = self.service.get_repository_by_id(repo.id, self.user.id)
        assert found_repo is not None
        assert found_repo.id == repo.id
        
        # Test with wrong user ID
        not_found = self.service.get_repository_by_id(repo.id, 999)
        assert not_found is None
        
        # Test with non-existent ID
        not_found = self.service.get_repository_by_id(999, self.user.id)
        assert not_found is None
    
    def test_update_repository(self):
        """Test repository update."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        original_updated_at = repo.updated_at
        
        result = self.service.update_repository(
            repository_id=repo.id,
            user_id=self.user.id,
            name='updated-repo',
            description='Updated description',
            status='inactive'
        )
        
        assert result['success'] is True
        assert result['message'] == 'Repository updated successfully'
        
        # Verify repository was updated
        updated_repo = Repository.query.get(repo.id)
        assert updated_repo.name == 'updated-repo'
        assert updated_repo.description == 'Updated description'
        assert updated_repo.status == 'inactive'
        assert updated_repo.updated_at > original_updated_at
    
    def test_update_repository_not_found(self):
        """Test updating non-existent repository."""
        result = self.service.update_repository(
            repository_id=999,
            user_id=self.user.id,
            name='updated-repo'
        )
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_delete_repository(self):
        """Test repository deletion."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            local_path='/tmp/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(self.service.git_service, 'delete_repository') as mock_delete:
            mock_delete.return_value = True
            
            result = self.service.delete_repository(repo.id, self.user.id)
            
            assert result['success'] is True
            assert result['message'] == 'Repository deleted successfully'
            
            # Verify repository was deleted from database
            deleted_repo = Repository.query.get(repo.id)
            assert deleted_repo is None
            
            # Verify local files were deleted
            mock_delete.assert_called_once()
    
    def test_delete_repository_not_found(self):
        """Test deleting non-existent repository."""
        result = self.service.delete_repository(999, self.user.id)
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_sync_repository_success(self):
        """Test successful repository sync."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            local_path='/tmp/test-repo',
            clone_status='completed',
            commit_hash='abc123'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(self.service.git_service, 'update_repository') as mock_update:
            mock_update.return_value = {
                'success': True,
                'commit_hash': 'def456',
                'repo_size': 2048,
                'file_count': 20,
                'metadata': {'updated': True}
            }
            
            result = self.service.sync_repository(repo.id, self.user.id)
            
            assert result['success'] is True
            assert result['message'] == 'Repository synced successfully'
            
            # Verify repository was updated
            updated_repo = Repository.query.get(repo.id)
            assert updated_repo.commit_hash == 'def456'
            assert updated_repo.repo_size == 2048
            assert updated_repo.file_count == 20
            assert updated_repo.metadata == {'updated': True}
            assert updated_repo.status == 'active'
            assert updated_repo.last_synced_at is not None
    
    def test_sync_repository_not_ready(self):
        """Test syncing repository that is not ready."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            clone_status='pending'
        )
        db.session.add(repo)
        db.session.commit()
        
        result = self.service.sync_repository(repo.id, self.user.id)
        
        assert result['success'] is False
        assert 'Repository is not ready for sync' in result['error']
    
    def test_get_repository_statistics(self):
        """Test getting repository statistics."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            status='active',
            clone_status='completed',
            repo_size=1024,
            file_count=10
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='repo2',
            url='https://github.com/user/repo2',
            status='error',
            clone_status='failed',
            repo_size=0,
            file_count=0
        )
        
        db.session.add_all([repo1, repo2])
        db.session.commit()
        
        statistics = self.service.get_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 2
        assert statistics['active_repositories'] == 1
        assert statistics['error_repositories'] == 1
        assert statistics['cloned_repositories'] == 1
        assert statistics['total_size_bytes'] == 1024
        assert statistics['total_files'] == 10
        assert statistics['success_rate'] == 50.0
    
    def test_get_repository_statistics_empty(self):
        """Test getting statistics when user has no repositories."""
        statistics = self.service.get_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 0
        assert statistics['active_repositories'] == 0
        assert statistics['error_repositories'] == 0
        assert statistics['cloned_repositories'] == 0
        assert statistics['total_size_bytes'] == 0
        assert statistics['total_files'] == 0
        assert statistics['success_rate'] == 0
    
    @patch('app.services.repository_service.RepositoryService._start_cloning_process')
    def test_start_cloning_process_success(self, mock_clone_process):
        """Test successful cloning process."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(self.service.git_service, 'clone_repository') as mock_clone:
            mock_clone.return_value = {
                'success': True,
                'local_path': '/tmp/test-repo',
                'commit_hash': 'abc123',
                'repo_size': 1024,
                'file_count': 10,
                'branch': 'main',
                'metadata': {'language': 'Python'}
            }
            
            self.service._start_cloning_process(repo)
            
            # Verify repository was updated
            updated_repo = Repository.query.get(repo.id)
            assert updated_repo.clone_status == 'completed'
            assert updated_repo.status == 'active'
            assert updated_repo.local_path == '/tmp/test-repo'
            assert updated_repo.commit_hash == 'abc123'
            assert updated_repo.repo_size == 1024
            assert updated_repo.file_count == 10
    
    @patch('app.services.repository_service.RepositoryService._start_cloning_process')
    def test_start_cloning_process_failure(self, mock_clone_process):
        """Test failed cloning process."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(self.service.git_service, 'clone_repository') as mock_clone:
            mock_clone.return_value = {
                'success': False,
                'error': 'Clone failed: Authentication failed'
            }
            
            self.service._start_cloning_process(repo)
            
            # Verify repository was updated with error
            updated_repo = Repository.query.get(repo.id)
            assert updated_repo.clone_status == 'failed'
            assert updated_repo.status == 'error'
            assert updated_repo.clone_error == 'Clone failed: Authentication failed'
    
    # ==================== 仓库删除功能测试 ====================
    
    def test_delete_repository_success(self):
        """Test successful repository deletion."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            local_path='/tmp/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(self.service, 'git_service') as mock_git:
            mock_git.delete_repository.return_value = {
                'success': True,
                'deleted_files': 5,
                'deleted_dirs': 2
            }
            
            result = self.service.delete_repository(repo.id, self.user.id)
            
            assert result['success'] is True
            assert result['repository_id'] == repo.id
            assert result['repository_name'] == 'test-repo'
            assert 'file_cleanup' in result
            assert result['file_cleanup']['success'] is True
            
            # Verify repository was deleted from database
            deleted_repo = Repository.query.get(repo.id)
            assert deleted_repo is None
    
    def test_delete_repository_not_found(self):
        """Test deletion of non-existent repository."""
        result = self.service.delete_repository(999, self.user.id)
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_delete_repository_wrong_user(self):
        """Test deletion of repository owned by another user."""
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        
        repo = Repository(
            user_id=other_user.id,
            name='other-repo',
            url='https://github.com/other/repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        result = self.service.delete_repository(repo.id, self.user.id)
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_delete_repository_with_file_cleanup_failure(self):
        """Test repository deletion when file cleanup fails."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            local_path='/tmp/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(self.service, 'git_service') as mock_git:
            mock_git.delete_repository.return_value = {
                'success': False,
                'error': 'Permission denied'
            }
            
            result = self.service.delete_repository(repo.id, self.user.id)
            
            # Should still succeed even if file cleanup fails
            assert result['success'] is True
            assert result['repository_id'] == repo.id
            assert 'file_cleanup' in result
            assert result['file_cleanup']['success'] is False
            
            # Verify repository was still deleted from database
            deleted_repo = Repository.query.get(repo.id)
            assert deleted_repo is None
    
    def test_delete_repository_database_error(self):
        """Test repository deletion with database error."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(db.session, 'commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            
            result = self.service.delete_repository(repo.id, self.user.id)
            
            assert result['success'] is False
            assert 'Database error during deletion' in result['error']
            
            # Verify repository was not deleted from database due to rollback
            not_deleted_repo = Repository.query.get(repo.id)
            assert not_deleted_repo is not None
    
    def test_get_delete_confirmation_success(self):
        """Test successful delete confirmation retrieval."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            description='Test repository',
            local_path='/tmp/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        # Add some associated documents and tasks
        from app.models.document import Document
        from app.models.task import Task
        
        doc1 = Document(repository_id=repo.id, title='Doc 1', content='Content 1')
        doc2 = Document(repository_id=repo.id, title='Doc 2', content='Content 2')
        task1 = Task(repository_id=repo.id, name='Task 1', status='pending')
        
        db.session.add_all([doc1, doc2, task1])
        db.session.commit()
        
        with patch.object(FileUtils, 'get_directory_info') as mock_file_info:
            mock_file_info.return_value = {
                'exists': True,
                'file_count': 10,
                'total_size': 2048,
                'size_human': '2.0 KB'
            }
            
            result = self.service.get_delete_confirmation(repo.id, self.user.id)
            
            assert result['success'] is True
            assert result['repository']['id'] == repo.id
            assert result['repository']['name'] == 'test-repo'
            assert result['associated_data']['documents_count'] == 2
            assert result['associated_data']['tasks_count'] == 1
            assert result['file_cleanup']['exists'] is True
            assert result['file_cleanup']['file_count'] == 10
            assert 'warning_message' in result
    
    def test_get_delete_confirmation_not_found(self):
        """Test delete confirmation for non-existent repository."""
        result = self.service.get_delete_confirmation(999, self.user.id)
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_get_delete_confirmation_no_associated_data(self):
        """Test delete confirmation for repository with no associated data."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        with patch.object(FileUtils, 'get_directory_info') as mock_file_info:
            mock_file_info.return_value = {
                'exists': False,
                'file_count': 0,
                'total_size': 0
            }
            
            result = self.service.get_delete_confirmation(repo.id, self.user.id)
            
            assert result['success'] is True
            assert result['associated_data']['documents_count'] == 0
            assert result['associated_data']['tasks_count'] == 0
            assert result['file_cleanup']['exists'] is False
            assert 'warning_message' in result
    
    def test_generate_deletion_warning_comprehensive(self):
        """Test deletion warning generation with all types of data."""
        documents_count = 5
        tasks_count = 3
        file_info = {
            'exists': True,
            'file_count': 100,
            'size_human': '1.5 MB'
        }
        
        warning = self.service._generate_deletion_warning(documents_count, tasks_count, file_info)
        
        assert '5 document(s)' in warning
        assert '3 task(s)' in warning
        assert '100 local file(s) (1.5 MB)' in warning
        assert 'permanently delete' in warning
        assert 'cannot be undone' in warning
    
    def test_generate_deletion_warning_no_data(self):
        """Test deletion warning generation with no associated data."""
        documents_count = 0
        tasks_count = 0
        file_info = None
        
        warning = self.service._generate_deletion_warning(documents_count, tasks_count, file_info)
        
        assert 'permanently delete the repository' in warning
        assert 'cannot be undone' in warning
        # Should not include specific data counts
        assert 'document(s)' not in warning
        assert 'task(s)' not in warning
        assert 'local file(s)' not in warning
    
    def test_generate_deletion_warning_partial_data(self):
        """Test deletion warning generation with only some data types."""
        documents_count = 2
        tasks_count = 0
        file_info = {
            'exists': True,
            'file_count': 50,
            'size_human': '500 KB'
        }
        
        warning = self.service._generate_deletion_warning(documents_count, tasks_count, file_info)
        
        assert '2 document(s)' in warning
        assert 'task(s)' not in warning
        assert '50 local file(s) (500 KB)' in warning
        assert 'permanently delete' in warning