"""
Unit tests for enhanced repository service functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.document import Document
from app.models.task import Task
from app.services.repository_service import RepositoryService
from config import TestingConfig


class TestEnhancedRepositoryService:
    """Test cases for enhanced repository service functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app(TestingConfig)
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
    
    def test_get_enhanced_repository_statistics_basic(self):
        """Test getting enhanced repository statistics with basic data."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            status='active',
            clone_status='completed',
            repo_size=1024,
            file_count=10,
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='repo2',
            url='https://github.com/user/repo2',
            status='error',
            clone_status='failed',
            repo_size=0,
            file_count=0,
            created_at=datetime.utcnow() - timedelta(days=15)
        )
        
        db.session.add_all([repo1, repo2])
        db.session.commit()
        
        statistics = self.service.get_enhanced_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 2
        assert statistics['active_repositories'] == 1
        assert statistics['error_repositories'] == 1
        assert statistics['total_documents'] == 0
        assert statistics['active_tasks'] == 0
        assert statistics['monthly_generated'] == 0
        assert statistics['total_size_bytes'] == 1024
        assert statistics['total_files'] == 10
        assert statistics['success_rate'] == 50.0
    
    def test_get_enhanced_repository_statistics_with_documents(self):
        """Test getting enhanced repository statistics with documents."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo1)
        db.session.commit()
        
        # Create test documents
        doc1 = Document(
            repository_id=repo1.id,
            title='Document 1',
            content='Content 1',
            status='completed'
        )
        doc2 = Document(
            repository_id=repo1.id,
            title='Document 2',
            content='Content 2',
            status='processing'
        )
        
        db.session.add_all([doc1, doc2])
        db.session.commit()
        
        statistics = self.service.get_enhanced_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 1
        assert statistics['total_documents'] == 2
        assert statistics['active_tasks'] == 1  # One processing document
    
    def test_get_enhanced_repository_statistics_with_tasks(self):
        """Test getting enhanced repository statistics with tasks."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo1)
        db.session.commit()
        
        # Create test tasks
        task1 = Task(
            repository_id=repo1.id,
            task_type='analysis',
            status='running',
            progress=50
        )
        task2 = Task(
            repository_id=repo1.id,
            task_type='documentation',
            status='pending',
            progress=0
        )
        task3 = Task(
            repository_id=repo1.id,
            task_type='sync',
            status='completed',
            progress=100
        )
        
        db.session.add_all([task1, task2, task3])
        db.session.commit()
        
        statistics = self.service.get_enhanced_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 1
        assert statistics['active_tasks'] == 2  # Running and pending tasks
    
    def test_get_enhanced_repository_statistics_monthly_generated(self):
        """Test getting enhanced repository statistics with monthly generated documents."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo1)
        db.session.commit()
        
        # Create documents from current month
        current_month_doc = Document(
            repository_id=repo1.id,
            title='Current Month Doc',
            content='Content',
            status='completed',
            created_at=datetime.utcnow()
        )
        
        # Create documents from previous month
        previous_month_doc = Document(
            repository_id=repo1.id,
            title='Previous Month Doc',
            content='Content',
            status='completed',
            created_at=datetime.utcnow() - timedelta(days=35)
        )
        
        db.session.add_all([current_month_doc, previous_month_doc])
        db.session.commit()
        
        statistics = self.service.get_enhanced_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 1
        assert statistics['total_documents'] == 2
        assert statistics['monthly_generated'] == 1  # Only current month document
    
    def test_get_enhanced_repository_statistics_empty(self):
        """Test getting enhanced repository statistics when user has no data."""
        statistics = self.service.get_enhanced_repository_statistics(self.user.id)
        
        assert statistics['total_repositories'] == 0
        assert statistics['active_repositories'] == 0
        assert statistics['error_repositories'] == 0
        assert statistics['total_documents'] == 0
        assert statistics['active_tasks'] == 0
        assert statistics['monthly_generated'] == 0
        assert statistics['total_size_bytes'] == 0
        assert statistics['total_files'] == 0
        assert statistics['success_rate'] == 0
    
    def test_get_repositories_paginated_basic(self):
        """Test basic repository pagination."""
        # Create test repositories
        for i in range(15):
            repo = Repository(
                user_id=self.user.id,
                name=f'repo{i}',
                url=f'https://github.com/user/repo{i}',
                status='active',
                clone_status='completed'
            )
            db.session.add(repo)
        
        db.session.commit()
        
        # Test first page
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=1,
            per_page=10
        )
        
        assert result['success'] is True
        assert len(result['repositories']) == 10
        assert result['current_page'] == 1
        assert result['total_pages'] == 2
        assert result['total_items'] == 15
        assert result['has_next'] is True
        assert result['has_prev'] is False
    
    def test_get_repositories_paginated_second_page(self):
        """Test second page of repository pagination."""
        # Create test repositories
        for i in range(15):
            repo = Repository(
                user_id=self.user.id,
                name=f'repo{i}',
                url=f'https://github.com/user/repo{i}',
                status='active',
                clone_status='completed'
            )
            db.session.add(repo)
        
        db.session.commit()
        
        # Test second page
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=2,
            per_page=10
        )
        
        assert result['success'] is True
        assert len(result['repositories']) == 5
        assert result['current_page'] == 2
        assert result['total_pages'] == 2
        assert result['total_items'] == 15
        assert result['has_next'] is False
        assert result['has_prev'] is True
    
    def test_get_repositories_paginated_with_search(self):
        """Test repository pagination with search."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='python-project',
            url='https://github.com/user/python-project',
            status='active',
            clone_status='completed'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='javascript-app',
            url='https://github.com/user/javascript-app',
            status='active',
            clone_status='completed'
        )
        repo3 = Repository(
            user_id=self.user.id,
            name='python-script',
            url='https://github.com/user/python-script',
            status='active',
            clone_status='completed'
        )
        
        db.session.add_all([repo1, repo2, repo3])
        db.session.commit()
        
        # Test search for 'python'
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=1,
            per_page=10,
            search_query='python'
        )
        
        assert result['success'] is True
        assert len(result['repositories']) == 2
        repo_names = [repo['name'] for repo in result['repositories']]
        assert 'python-project' in repo_names
        assert 'python-script' in repo_names
        assert 'javascript-app' not in repo_names
    
    def test_get_repositories_paginated_with_status_filter(self):
        """Test repository pagination with status filter."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='active-repo',
            url='https://github.com/user/active-repo',
            status='active',
            clone_status='completed'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='error-repo',
            url='https://github.com/user/error-repo',
            status='error',
            clone_status='failed'
        )
        repo3 = Repository(
            user_id=self.user.id,
            name='inactive-repo',
            url='https://github.com/user/inactive-repo',
            status='inactive',
            clone_status='completed'
        )
        
        db.session.add_all([repo1, repo2, repo3])
        db.session.commit()
        
        # Test filter for 'active' status
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=1,
            per_page=10,
            status_filter='active'
        )
        
        assert result['success'] is True
        assert len(result['repositories']) == 1
        assert result['repositories'][0]['name'] == 'active-repo'
    
    def test_get_repositories_paginated_with_sorting(self):
        """Test repository pagination with sorting."""
        # Create test repositories with different creation times
        repo1 = Repository(
            user_id=self.user.id,
            name='first-repo',
            url='https://github.com/user/first-repo',
            status='active',
            clone_status='completed',
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='second-repo',
            url='https://github.com/user/second-repo',
            status='active',
            clone_status='completed',
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        repo3 = Repository(
            user_id=self.user.id,
            name='third-repo',
            url='https://github.com/user/third-repo',
            status='active',
            clone_status='completed',
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        db.session.add_all([repo1, repo2, repo3])
        db.session.commit()
        
        # Test sort by created_at descending
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=1,
            per_page=10,
            sort_field='created_at',
            sort_order='desc'
        )
        
        assert result['success'] is True
        assert len(result['repositories']) == 3
        assert result['repositories'][0]['name'] == 'third-repo'
        assert result['repositories'][1]['name'] == 'second-repo'
        assert result['repositories'][2]['name'] == 'first-repo'
    
    def test_get_repositories_paginated_invalid_parameters(self):
        """Test repository pagination with invalid parameters."""
        # Create test repositories
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed'
        )
        db.session.add(repo)
        db.session.commit()
        
        # Test with invalid per_page (should be clamped to valid range)
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=1,
            per_page=100  # Should be clamped to 50
        )
        
        assert result['success'] is True
        assert result['per_page'] == 50
        
        # Test with invalid page (should be set to 1)
        result = self.service.get_repositories_paginated(
            user_id=self.user.id,
            page=0,  # Should be set to 1
            per_page=10
        )
        
        assert result['success'] is True
        assert result['current_page'] == 1
    
    def test_get_repository_status(self):
        """Test getting detailed repository status."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed',
            analysis_progress=75,
            last_analysis=datetime.utcnow() - timedelta(hours=1),
            last_synced_at=datetime.utcnow() - timedelta(days=1)
        )
        
        db.session.add(repo)
        db.session.commit()
        
        result = self.service.get_repository_status(repo.id, self.user.id)
        
        assert result['success'] is True
        assert result['status'] == 'active'
        assert result['clone_status'] == 'completed'
        assert result['analysis_progress'] == 75
        assert result['last_analysis'] is not None
        assert result['last_synced_at'] is not None
    
    def test_get_repository_status_not_found(self):
        """Test getting status for non-existent repository."""
        result = self.service.get_repository_status(999, self.user.id)
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_update_repository_analysis_progress(self):
        """Test updating repository analysis progress."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed',
            analysis_progress=25
        )
        
        db.session.add(repo)
        db.session.commit()
        
        result = self.service.update_repository_analysis_progress(repo.id, self.user.id, 75)
        
        assert result['success'] is True
        assert result['message'] == 'Analysis progress updated'
        
        # Verify progress was updated
        updated_repo = Repository.query.get(repo.id)
        assert updated_repo.analysis_progress == 75
        assert updated_repo.last_analysis is not None
    
    def test_update_repository_analysis_progress_invalid_value(self):
        """Test updating repository analysis progress with invalid value."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        # Test with invalid progress (should be clamped to 0-100)
        result = self.service.update_repository_analysis_progress(repo.id, self.user.id, 150)
        
        assert result['success'] is True
        
        # Verify progress was clamped to 100
        updated_repo = Repository.query.get(repo.id)
        assert updated_repo.analysis_progress == 100