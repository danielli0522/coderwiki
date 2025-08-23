"""
Integration tests for enhanced repository API endpoints.
"""

import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.document import Document
from app.models.task import Task
from config import TestingConfig


class TestEnhancedRepositoryAPI:
    """Test cases for enhanced repository API endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
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
        
        self.client = self.app.test_client()
        
        # Mock login
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True
    
    def teardown_method(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_enhanced_repository_statistics_basic(self):
        """Test getting enhanced repository statistics."""
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
        
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_repositories'] == 2
        assert data['active_repositories'] == 1
        assert data['error_repositories'] == 1
        assert data['total_documents'] == 0
        assert data['active_tasks'] == 0
        assert data['monthly_generated'] == 0
        assert data['total_size_bytes'] == 1024
        assert data['total_files'] == 10
        assert data['success_rate'] == 50.0
    
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
        
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_repositories'] == 1
        assert data['total_documents'] == 2
        assert data['active_tasks'] == 1
    
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
        
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_repositories'] == 1
        assert data['total_documents'] == 2
        assert data['monthly_generated'] == 1
    
    def test_get_enhanced_repository_statistics_empty(self):
        """Test getting enhanced repository statistics when user has no data."""
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_repositories'] == 0
        assert data['active_repositories'] == 0
        assert data['error_repositories'] == 0
        assert data['total_documents'] == 0
        assert data['active_tasks'] == 0
        assert data['monthly_generated'] == 0
        assert data['total_size_bytes'] == 0
        assert data['total_files'] == 0
        assert data['success_rate'] == 0
    
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
        
        response = self.client.get('/api/repositories?page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 10
        assert data['current_page'] == 1
        assert data['total_pages'] == 2
        assert data['total_items'] == 15
        assert data['has_next'] is True
        assert data['has_prev'] is False
    
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
        
        response = self.client.get('/api/repositories?page=2&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 5
        assert data['current_page'] == 2
        assert data['total_pages'] == 2
        assert data['total_items'] == 15
        assert data['has_next'] is False
        assert data['has_prev'] is True
    
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
        
        response = self.client.get('/api/repositories?search=python')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 2
        repo_names = [repo['name'] for repo in data['repositories']]
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
        
        response = self.client.get('/api/repositories?status=active')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 1
        assert data['repositories'][0]['name'] == 'active-repo'
    
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
        
        response = self.client.get('/api/repositories?sort_field=created_at&sort_order=desc')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 3
        assert data['repositories'][0]['name'] == 'third-repo'
        assert data['repositories'][1]['name'] == 'second-repo'
        assert data['repositories'][2]['name'] == 'first-repo'
    
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
        response = self.client.get('/api/repositories?per_page=100')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['per_page'] == 10  # Should be clamped to default
        
        # Test with invalid page (should be set to 1)
        response = self.client.get('/api/repositories?page=0')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['current_page'] == 1
    
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
        
        response = self.client.get(f'/api/repositories/{repo.id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['status'] == 'active'
        assert data['clone_status'] == 'completed'
        assert data['analysis_progress'] == 75
        assert data['last_analysis'] is not None
        assert data['last_synced_at'] is not None
    
    def test_get_repository_status_not_found(self):
        """Test getting status for non-existent repository."""
        response = self.client.get('/api/repositories/999/status')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
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
        
        data = {'progress': 75}
        response = self.client.put(
            f'/api/repositories/{repo.id}/progress',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['message'] == 'Analysis progress updated'
        
        # Verify progress was updated
        updated_repo = Repository.query.get(repo.id)
        assert updated_repo.analysis_progress == 75
    
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
        
        # Test with invalid progress value
        data = {'progress': 150}
        response = self.client.put(
            f'/api/repositories/{repo.id}/progress',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_update_repository_analysis_progress_missing_progress(self):
        """Test updating repository analysis progress with missing progress parameter."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        # Test with missing progress parameter
        data = {}
        response = self.client.put(
            f'/api/repositories/{repo.id}/progress',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_reanalyze_repository(self):
        """Test reanalyzing repository."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed',
            local_path='/tmp/test-repo'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        with pytest.mock.patch('app.services.repository_service.RepositoryService.reanalyze_repository') as mock_reanalyze:
            mock_reanalyze.return_value = {
                'success': True,
                'message': 'Repository analysis restarted'
            }
            
            response = self.client.post(f'/api/repositories/{repo.id}/reanalyze')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert response_data['message'] == 'Repository analysis restarted'
    
    def test_update_github_stats(self):
        """Test updating GitHub statistics."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        with pytest.mock.patch('app.services.repository_service.RepositoryService.update_repository_github_stats') as mock_update:
            mock_update.return_value = {
                'success': True,
                'message': 'GitHub statistics updated'
            }
            
            response = self.client.post(f'/api/repositories/{repo.id}/github-stats')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert response_data['message'] == 'GitHub statistics updated'
    
    def test_bulk_delete_repositories(self):
        """Test bulk deleting repositories."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            local_path='/tmp/repo1'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='repo2',
            url='https://github.com/user/repo2',
            local_path='/tmp/repo2'
        )
        
        db.session.add_all([repo1, repo2])
        db.session.commit()
        
        data = {'repository_ids': [repo1.id, repo2.id]}
        
        with pytest.mock.patch('app.services.repository_service.RepositoryService.bulk_delete_repositories') as mock_bulk_delete:
            mock_bulk_delete.return_value = {
                'success': True,
                'message': 'Repositories deleted successfully'
            }
            
            response = self.client.post(
                '/api/repositories/bulk-delete',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert response_data['message'] == 'Repositories deleted successfully'
    
    def test_bulk_delete_repositories_missing_ids(self):
        """Test bulk deleting repositories with missing IDs."""
        data = {}
        
        response = self.client.post(
            '/api/repositories/bulk-delete',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_bulk_delete_repositories_invalid_ids(self):
        """Test bulk deleting repositories with invalid IDs."""
        data = {'repository_ids': 'invalid'}
        
        response = self.client.post(
            '/api/repositories/bulk-delete',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data