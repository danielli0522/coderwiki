"""
Unit tests for analysis models.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.analysis import CodeAnalysis, AnalysisCache
from app.models.user import User
from app.models.repository import Repository
from config import TestingConfig


class TestCodeAnalysis:
    """Test cases for CodeAnalysis model."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create test repository
        self.repository = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo'
        )
        db.session.add(self.repository)
        db.session.commit()
        
        # Create test analysis
        self.analysis = CodeAnalysis(
            repository_id=self.repository.id,
            analysis_type='structure'
        )
        db.session.add(self.analysis)
        db.session.commit()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_code_analysis_creation(self):
        """Test CodeAnalysis model creation."""
        assert self.analysis.repository_id == self.repository.id
        assert self.analysis.analysis_type == 'structure'
        assert self.analysis.status == 'pending'
        assert self.analysis.result_data is None
        assert self.analysis.analysis_time is None
        assert self.analysis.error_message is None
        assert isinstance(self.analysis.created_at, datetime)
        assert isinstance(self.analysis.updated_at, datetime)
    
    def test_code_analysis_to_dict(self):
        """Test CodeAnalysis to_dict method."""
        analysis_dict = self.analysis.to_dict()
        
        assert analysis_dict['repository_id'] == 1
        assert analysis_dict['analysis_type'] == 'structure'
        assert analysis_dict['status'] == 'pending'
        assert analysis_dict['result_data'] is None
        assert analysis_dict['analysis_time'] is None
        assert analysis_dict['error_message'] is None
        assert 'created_at' in analysis_dict
        assert 'updated_at' in analysis_dict
    
    def test_code_analysis_repr(self):
        """Test CodeAnalysis __repr__ method."""
        repr_str = repr(self.analysis)
        assert 'CodeAnalysis' in repr_str
        assert 'structure' in repr_str
        assert '1' in repr_str
    
    def test_update_status(self):
        """Test update_status method."""
        original_updated_at = self.analysis.updated_at
        
        self.analysis.update_status('analyzing')
        assert self.analysis.status == 'analyzing'
        assert self.analysis.updated_at > original_updated_at
        
        self.analysis.update_status('failed', 'Test error message')
        assert self.analysis.status == 'failed'
        assert self.analysis.error_message == 'Test error message'
    
    def test_complete_analysis(self):
        """Test complete_analysis method."""
        test_data = {'files': 10, 'directories': 5}
        test_time = 2.5
        
        self.analysis.complete_analysis(test_data, test_time)
        
        assert self.analysis.status == 'completed'
        assert self.analysis.result_data == test_data
        assert self.analysis.analysis_time == test_time
    
    def test_fail_analysis(self):
        """Test fail_analysis method."""
        error_msg = 'Analysis failed due to timeout'
        
        self.analysis.fail_analysis(error_msg)
        
        assert self.analysis.status == 'failed'
        assert self.analysis.error_message == error_msg


class TestAnalysisCache:
    """Test cases for AnalysisCache model."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create test repository
        self.repository = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo'
        )
        db.session.add(self.repository)
        db.session.commit()
        
        # Create test cache
        self.cache = AnalysisCache(
            repository_id=self.repository.id,
            cache_key='test_cache_key',
            cache_data={'test': 'data'},
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(self.cache)
        db.session.commit()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_analysis_cache_creation(self):
        """Test AnalysisCache model creation."""
        assert self.cache.repository_id == self.repository.id
        assert self.cache.cache_key == 'test_cache_key'
        assert self.cache.cache_data == {'test': 'data'}
        assert isinstance(self.cache.expires_at, datetime)
        assert isinstance(self.cache.created_at, datetime)
    
    def test_analysis_cache_to_dict(self):
        """Test AnalysisCache to_dict method."""
        cache_dict = self.cache.to_dict()
        
        assert cache_dict['repository_id'] == 1
        assert cache_dict['cache_key'] == 'test_cache_key'
        assert cache_dict['cache_data'] == {'test': 'data'}
        assert 'expires_at' in cache_dict
        assert 'created_at' in cache_dict
    
    def test_analysis_cache_repr(self):
        """Test AnalysisCache __repr__ method."""
        repr_str = repr(self.cache)
        assert 'AnalysisCache' in repr_str
        assert 'test_cache_key' in repr_str
        assert '1' in repr_str
    
    def test_is_expired(self):
        """Test is_expired method."""
        # Test non-expired cache
        assert not self.cache.is_expired()
        
        # Test expired cache
        self.cache.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert self.cache.is_expired()
    
    def test_update_cache(self):
        """Test update_cache method."""
        new_data = {'updated': 'data'}
        new_expires_at = datetime.utcnow() + timedelta(hours=2)
        original_created_at = self.cache.created_at
        
        self.cache.update_cache(new_data, new_expires_at)
        
        assert self.cache.cache_data == new_data
        assert self.cache.expires_at == new_expires_at
        assert self.cache.created_at > original_created_at


class TestAnalysisModelIntegration:
    """Integration tests for analysis models."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        
        self.repository = Repository(
            user_id=1,
            name='test-repo',
            url='https://github.com/test/test-repo'
        )
    
    @patch('app.db.session')
    def test_code_analysis_repository_relationship(self, mock_session):
        """Test CodeAnalysis relationship with Repository."""
        # Mock repository relationship
        mock_repository = Mock()
        mock_repository.id = 1
        mock_repository.name = 'test-repo'
        
        analysis = CodeAnalysis(
            repository_id=1,
            analysis_type='structure'
        )
        analysis.repository = mock_repository
        
        assert analysis.repository.id == 1
        assert analysis.repository.name == 'test-repo'
    
    @patch('app.db.session')
    def test_analysis_cache_repository_relationship(self, mock_session):
        """Test AnalysisCache relationship with Repository."""
        # Mock repository relationship
        mock_repository = Mock()
        mock_repository.id = 1
        mock_repository.name = 'test-repo'
        
        cache = AnalysisCache(
            repository_id=1,
            cache_key='test_key',
            cache_data={'test': 'data'},
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        cache.repository = mock_repository
        
        assert cache.repository.id == 1
        assert cache.repository.name == 'test-repo'
    
    def test_multiple_analyses_per_repository(self):
        """Test that a repository can have multiple analyses."""
        analyses = [
            CodeAnalysis(repository_id=1, analysis_type='structure'),
            CodeAnalysis(repository_id=1, analysis_type='dependencies'),
            CodeAnalysis(repository_id=1, analysis_type='complexity')
        ]
        
        assert len(analyses) == 3
        assert all(analysis.repository_id == 1 for analysis in analyses)
        assert analyses[0].analysis_type == 'structure'
        assert analyses[1].analysis_type == 'dependencies'
        assert analyses[2].analysis_type == 'complexity'
    
    def test_multiple_cache_entries_per_repository(self):
        """Test that a repository can have multiple cache entries."""
        cache_entries = [
            AnalysisCache(
                repository_id=1,
                cache_key='1_structure',
                cache_data={'structure': 'data'},
                expires_at=datetime.utcnow() + timedelta(hours=1)
            ),
            AnalysisCache(
                repository_id=1,
                cache_key='1_dependencies',
                cache_data={'dependencies': 'data'},
                expires_at=datetime.utcnow() + timedelta(hours=12)
            )
        ]
        
        assert len(cache_entries) == 2
        assert all(entry.repository_id == 1 for entry in cache_entries)
        assert cache_entries[0].cache_key == '1_structure'
        assert cache_entries[1].cache_key == '1_dependencies'