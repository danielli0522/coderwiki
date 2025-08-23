"""
Integration tests for Repository API.
"""

import pytest
import json
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from config import TestingConfig


class TestRepositoryAPI:
    """Test cases for Repository API endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('testpassword123')
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
    
    def test_get_repositories_empty(self):
        """Test getting repositories when user has none."""
        response = self.client.get('/api/repositories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['repositories'] == []
    
    def test_get_repositories_with_data(self):
        """Test getting repositories when user has some."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/user/repo1',
            status='active',
            clone_status='completed'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='repo2',
            url='https://github.com/user/repo2',
            status='inactive',
            clone_status='pending'
        )
        
        db.session.add_all([repo1, repo2])
        db.session.commit()
        
        response = self.client.get('/api/repositories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 2
        
        # Verify repositories are returned
        repo_names = [repo['name'] for repo in data['repositories']]
        assert 'repo1' in repo_names
        assert 'repo2' in repo_names
    
    def test_add_repository_success(self):
        """Test successful repository addition."""
        with pytest.mock.patch('app.services.repository_service.RepositoryService._start_cloning_process'):
            data = {
                'url': 'https://github.com/user/test-repo',
                'name': 'test-repo',
                'description': 'Test repository'
            }
            
            response = self.client.post(
                '/api/repositories',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert 'repository' in response_data
            assert response_data['repository']['name'] == 'test-repo'
            
            # Verify repository was created in database
            repo = Repository.query.filter_by(url='https://github.com/user/test-repo').first()
            assert repo is not None
    
    def test_add_repository_missing_url(self):
        """Test repository addition with missing URL."""
        data = {
            'name': 'test-repo',
            'description': 'Test repository'
        }
        
        response = self.client.post(
            '/api/repositories',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == '仓库URL不能为空'
    
    def test_add_repository_invalid_url(self):
        """Test repository addition with invalid URL."""
        data = {
            'url': 'invalid-url',
            'name': 'test-repo'
        }
        
        response = self.client.post(
            '/api/repositories',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_get_repository_by_id(self):
        """Test getting repository by ID."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        response = self.client.get(f'/api/repositories/{repo.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['repository']['id'] == repo.id
        assert data['repository']['name'] == 'test-repo'
    
    def test_get_repository_not_found(self):
        """Test getting non-existent repository."""
        response = self.client.get('/api/repositories/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_repository(self):
        """Test repository update."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        data = {
            'name': 'updated-repo',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            f'/api/repositories/{repo.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['repository']['name'] == 'updated-repo'
        
        # Verify repository was updated in database
        updated_repo = Repository.query.get(repo.id)
        assert updated_repo.name == 'updated-repo'
        assert updated_repo.description == 'Updated description'
    
    def test_update_repository_not_found(self):
        """Test updating non-existent repository."""
        data = {'name': 'updated-repo'}
        
        response = self.client.put(
            '/api/repositories/999',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
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
        
        with pytest.mock.patch('app.services.repository_service.GitService.delete_repository') as mock_delete:
            mock_delete.return_value = True
            
            response = self.client.delete(f'/api/repositories/{repo.id}')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            
            # Verify repository was deleted from database
            deleted_repo = Repository.query.get(repo.id)
            assert deleted_repo is None
    
    def test_delete_repository_not_found(self):
        """Test deleting non-existent repository."""
        response = self.client.delete('/api/repositories/999')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_sync_repository(self):
        """Test repository sync."""
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
        
        with pytest.mock.patch('app.services.repository_service.GitService.update_repository') as mock_update:
            mock_update.return_value = {
                'success': True,
                'commit_hash': 'def456',
                'repo_size': 2048,
                'file_count': 20,
                'metadata': {'updated': True}
            }
            
            response = self.client.post(f'/api/repositories/{repo.id}/sync')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
    
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
        
        response = self.client.post(f'/api/repositories/{repo.id}/sync')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_analyze_repository(self):
        """Test repository analysis."""
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
        
        with pytest.mock.patch('app.utils.repository_analyzer.RepositoryAnalyzer.analyze_repository') as mock_analyze:
            mock_analyze.return_value = {
                'structure': {'total_files': 10},
                'languages': [{'name': 'Python', 'file_count': 5}],
                'dependencies': {'package_managers': ['pip']},
                'configuration': {'frameworks': ['Flask']},
                'documentation': {'readme': {'path': 'README.md'}},
                'metadata': {'estimated_complexity': 'low'}
            }
            
            response = self.client.post(f'/api/repositories/{repo.id}/analyze')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert 'analysis' in response_data
            assert response_data['analysis']['structure']['total_files'] == 10
    
    def test_analyze_repository_not_ready(self):
        """Test analyzing repository that is not ready."""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            clone_status='pending'
        )
        db.session.add(repo)
        db.session.commit()
        
        response = self.client.post(f'/api/repositories/{repo.id}/analyze')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
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
        
        response = self.client.get('/api/repositories/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['statistics']['total_repositories'] == 2
        assert data['statistics']['active_repositories'] == 1
        assert data['statistics']['cloned_repositories'] == 1
        assert data['statistics']['total_files'] == 10
    
    def test_validate_url_success(self):
        """Test successful URL validation."""
        with pytest.mock.patch('app.services.repository_service.GitService.validate_repository_url') as mock_validate:
            mock_validate.return_value = True
            
            data = {'url': 'https://github.com/user/test-repo'}
            
            response = self.client.post(
                '/api/repositories/validate-url',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert response_data['valid'] is True
    
    def test_validate_url_invalid_format(self):
        """Test URL validation with invalid format."""
        data = {'url': 'invalid-url'}
        
        response = self.client.post(
            '/api/repositories/validate-url',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['valid'] is False
        assert 'invalid' in response_data['message']
    
    def test_validate_url_missing_url(self):
        """Test URL validation with missing URL."""
        data = {}
        
        response = self.client.post(
            '/api/repositories/validate-url',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data