"""
Analysis API tests.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from app.api.analysis import analysis_bp
from app.services.analysis_service import AnalysisService
from app.models.repository import Repository


class TestAnalysisAPI:
    """Analysis API test class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.register_blueprint(analysis_bp)
        
        self.client = self.app.test_client()
        self.analysis_service = AnalysisService()
        
        # Mock user
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.is_authenticated = True
        
        # Mock repository
        self.mock_repository = Mock()
        self.mock_repository.id = 1
        self.mock_repository.user_id = 1
    
    def test_start_analysis_success(self):
        """Test successful analysis start."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.start_analysis.return_value = {
                'success': True,
                'analysis_ids': [1, 2],
                'analysis_types': ['structure', 'complexity'],
                'repository_id': 1
            }
            mock_service_class.return_value = mock_service
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            # Mock login required
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.post('/api/analysis/start', 
                    json={
                        'repository_id': 1,
                        'analysis_types': ['structure', 'complexity'],
                        'config': {'timeout': 300}
                    },
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 202
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['analysis_ids'] == [1, 2]
                assert data['analysis_types'] == ['structure', 'complexity']
    
    def test_start_analysis_missing_fields(self):
        """Test analysis start with missing required fields."""
        with self.app.test_request_context():
            from flask_login import login_user
            login_user(self.mock_user)
            
            response = self.client.post('/api/analysis/start', 
                json={'repository_id': 1},  # Missing analysis_types
                headers={'Authorization': 'Bearer test-token'}
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Missing required field' in data['message']
    
    def test_start_analysis_invalid_types(self):
        """Test analysis start with invalid analysis types."""
        with self.app.test_request_context():
            from flask_login import login_user
            login_user(self.mock_user)
            
            response = self.client.post('/api/analysis/start', 
                json={
                    'repository_id': 1,
                    'analysis_types': ['invalid_type']
                },
                headers={'Authorization': 'Bearer test-token'}
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Invalid analysis types' in data['message']
    
    def test_get_analysis_status_success(self):
        """Test successful analysis status retrieval."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_analysis_status.return_value = {
                'success': True,
                'status': 'completed',
                'progress': 100,
                'analysis_time': 2.5
            }
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/status/1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['status'] == 'completed'
                assert data['progress'] == 100
    
    def test_get_analysis_status_not_found(self):
        """Test analysis status retrieval for non-existent analysis."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_analysis_status.return_value = {
                'success': False,
                'message': 'Analysis not found'
            }
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/status/999',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 404
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'Analysis not found' in data['message']
    
    def test_get_analysis_results_success(self):
        """Test successful analysis results retrieval."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_analysis_results.return_value = {
                'success': True,
                'results': {
                    'structure': {'files': 10},
                    'complexity': {'complexity': 5}
                },
                'repository_id': 1
            }
            mock_service_class.return_value = mock_service
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/results/1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'structure' in data['results']
                assert 'complexity' in data['results']
    
    def test_get_analysis_results_invalid_types(self):
        """Test analysis results retrieval with invalid analysis types."""
        with patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/results/1?analysis_types=invalid_type',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 400
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'Invalid analysis types' in data['message']
    
    def test_get_combined_analysis_results_success(self):
        """Test successful combined analysis results retrieval."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_combined_analysis_results.return_value = {
                'success': True,
                'results': {
                    'summary': {'overall_quality_score': 85.0},
                    'structure': {'files': 10},
                    'recommendations': ['Refactor complex code']
                },
                'from_cache': False,
                'repository_id': 1
            }
            mock_service_class.return_value = mock_service
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/combined/1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'summary' in data['results']
                assert 'recommendations' in data['results']
                assert data['from_cache'] is False
    
    def test_cancel_analysis_success(self):
        """Test successful analysis cancellation."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.cancel_analysis.return_value = {
                'success': True,
                'message': 'Analysis cancelled successfully',
                'analysis_id': 1
            }
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.post('/api/analysis/cancel/1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'cancelled successfully' in data['message']
    
    def test_cancel_analysis_not_found(self):
        """Test cancellation of non-existent analysis."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.cancel_analysis.return_value = {
                'success': False,
                'message': 'Analysis not found'
            }
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.post('/api/analysis/cancel/999',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 404
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'Analysis not found' in data['message']
    
    def test_clear_analysis_cache_success(self):
        """Test successful analysis cache clearing."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.clear_analysis_cache.return_value = {
                'success': True,
                'message': 'Cleared 3 cache entries',
                'cleared_count': 3
            }
            mock_service_class.return_value = mock_service
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.post('/api/analysis/cache/clear/1',
                    json={'analysis_type': 'structure'},
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['cleared_count'] == 3
    
    def test_get_analysis_history_success(self):
        """Test successful analysis history retrieval."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_analysis_history.return_value = {
                'success': True,
                'history': [
                    {
                        'id': 1,
                        'analysis_type': 'structure',
                        'status': 'completed',
                        'analysis_time': 2.5
                    }
                ],
                'repository_id': 1
            }
            mock_service_class.return_value = mock_service
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/history/1?limit=5',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert len(data['history']) == 1
                assert data['history'][0]['analysis_type'] == 'structure'
    
    def test_get_analysis_statistics_success(self):
        """Test successful analysis statistics retrieval."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_analysis_statistics.return_value = {
                'success': True,
                'statistics': {
                    'total_analyses': 10,
                    'completed_analyses': 8,
                    'success_rate': 80.0,
                    'average_analysis_time': 2.5
                }
            }
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/statistics',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['statistics']['total_analyses'] == 10
                assert data['statistics']['success_rate'] == 80.0
    
    def test_get_analysis_statistics_with_repository(self):
        """Test analysis statistics retrieval for specific repository."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.get_analysis_statistics.return_value = {
                'success': True,
                'statistics': {
                    'total_analyses': 5,
                    'completed_analyses': 4,
                    'success_rate': 80.0
                },
                'repository_id': 1
            }
            mock_service_class.return_value = mock_service
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/statistics?repository_id=1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['statistics']['total_analyses'] == 5
    
    def test_get_supported_analysis_types_success(self):
        """Test successful supported analysis types retrieval."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.analysis_engine.get_analysis_capabilities.return_value = {
                'structure': {
                    'description': 'File structure analysis',
                    'capabilities': ['Directory tree generation', 'File type statistics']
                },
                'complexity': {
                    'description': 'Code complexity analysis',
                    'capabilities': ['Cyclomatic complexity', 'Code quality metrics']
                }
            }
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/types',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'structure' in data['capabilities']
                assert 'complexity' in data['capabilities']
    
    def test_validate_analysis_config_success(self):
        """Test successful analysis configuration validation."""
        with patch('flask_login.current_user', self.mock_user):
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.post('/api/analysis/config/validate',
                    json={
                        'config': {
                            'analysis_types': ['structure', 'complexity'],
                            'timeout': 300,
                            'max_file_size': 10485760
                        }
                    },
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'valid' in data
                assert 'errors' in data
    
    def test_analysis_health_check_success(self):
        """Test successful analysis health check."""
        with patch('app.services.analysis_service.AnalysisService') as mock_service_class, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock service
            mock_service = Mock()
            mock_service.analysis_engine.get_supported_analysis_types.return_value = [
                'structure', 'complexity', 'tech_stack'
            ]
            mock_service_class.return_value = mock_service
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/health',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['status'] == 'healthy'
                assert 'supported_analysis_types' in data
    
    def test_validate_repository_access_success(self):
        """Test successful repository access validation."""
        with patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock repository
            mock_repo_query.return_value = self.mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                # Test through actual endpoint that uses the decorator
                response = self.client.get('/api/analysis/results/1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                # The actual response will be handled by the service mock
                # This test just ensures the decorator doesn't block access
                assert response.status_code != 403
    
    def test_validate_repository_access_denied(self):
        """Test repository access validation with wrong user."""
        with patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock repository with different user
            mock_repository = Mock()
            mock_repository.id = 1
            mock_repository.user_id = 2  # Different user
            mock_repo_query.return_value = mock_repository
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/results/1',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 403
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'Access denied' in data['message']
    
    def test_validate_repository_not_found(self):
        """Test repository access validation with non-existent repository."""
        with patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch('flask_login.current_user', self.mock_user):
            
            # Mock repository not found
            mock_repo_query.return_value = None
            
            with self.app.test_request_context():
                from flask_login import login_user
                login_user(self.mock_user)
                
                response = self.client.get('/api/analysis/results/999',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 404
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'Repository not found' in data['message']