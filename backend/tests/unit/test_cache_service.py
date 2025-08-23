"""
Unit tests for cache service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.cache_service import CacheService
from app.models.analysis import AnalysisCache


class TestCacheService:
    """Test cases for CacheService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository_id = 1
        self.analysis_type = 'structure'
        self.test_data = {'files': 10, 'directories': 5}
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        # Basic cache key
        key = CacheService.generate_cache_key(1, 'structure')
        assert key == '1_structure'
        
        # Cache key with additional params
        key_with_params = CacheService.generate_cache_key(1, 'structure', 'v1')
        assert key_with_params == '1_structure_v1'
        
        # Cache key with complex params
        key_complex = CacheService.generate_cache_key(2, 'dependencies', 'full_scan')
        assert key_complex == '2_dependencies_full_scan'
    
    @patch('app.services.cache_service.AnalysisCache.query')
    def test_get_cache_hit(self, mock_query):
        """Test getting cache entry that exists and is not expired."""
        # Mock cache entry
        mock_cache = Mock()
        mock_cache.is_expired.return_value = False
        mock_cache.cache_data = self.test_data
        
        mock_query.filter_by.return_value.first.return_value = mock_cache
        
        result = CacheService.get_cache(self.repository_id, self.analysis_type)
        
        assert result == self.test_data
        mock_query.filter_by.assert_called_once_with(
            repository_id=self.repository_id,
            cache_key='1_structure'
        )
    
    @patch('app.services.cache_service.AnalysisCache.query')
    def test_get_cache_miss_expired(self, mock_query):
        """Test getting cache entry that exists but is expired."""
        # Mock expired cache entry
        mock_cache = Mock()
        mock_cache.is_expired.return_value = True
        
        mock_query.filter_by.return_value.first.return_value = mock_cache
        
        with patch('app.services.cache_service.db.session') as mock_db:
            result = CacheService.get_cache(self.repository_id, self.analysis_type)
            
            assert result is None
            mock_db.session.delete.assert_called_once_with(mock_cache)
            mock_db.session.commit.assert_called_once()
    
    @patch('app.services.cache_service.AnalysisCache.query')
    def test_get_cache_miss_no_entry(self, mock_query):
        """Test getting cache entry that doesn't exist."""
        mock_query.filter_by.return_value.first.return_value = None
        
        result = CacheService.get_cache(self.repository_id, self.analysis_type)
        
        assert result is None
    
    @patch('app.services.cache_service.AnalysisCache.query')
    @patch('app.services.cache_service.db.session')
    def test_set_cache_new_entry(self, mock_db, mock_query):
        """Test setting cache entry when none exists."""
        mock_query.filter_by.return_value.first.return_value = None
        
        with patch('app.services.cache_service.datetime') as mock_datetime:
            mock_now = datetime.utcnow()
            mock_datetime.utcnow.return_value = mock_now
            
            result = CacheService.set_cache(
                self.repository_id,
                self.analysis_type,
                self.test_data
            )
            
            assert isinstance(result, AnalysisCache)
            assert result.repository_id == self.repository_id
            assert result.cache_key == '1_structure'
            assert result.cache_data == self.test_data
            
            # Check expiration time (24 hours for structure analysis)
            expected_expires = mock_now + timedelta(hours=24)
            assert result.expires_at == expected_expires
            
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.services.cache_service.AnalysisCache.query')
    @patch('app.services.cache_service.db.session')
    def test_set_cache_update_existing(self, mock_db, mock_query):
        """Test setting cache entry when one already exists."""
        # Mock existing cache entry
        existing_cache = Mock()
        existing_cache.update_cache = Mock()
        
        mock_query.filter_by.return_value.first.return_value = existing_cache
        
        with patch('app.services.cache_service.datetime') as mock_datetime:
            mock_now = datetime.utcnow()
            mock_datetime.utcnow.return_value = mock_now
            
            result = CacheService.set_cache(
                self.repository_id,
                self.analysis_type,
                self.test_data
            )
            
            assert result == existing_cache
            existing_cache.update_cache.assert_called_once_with(
                self.test_data,
                mock_now + timedelta(hours=24)
            )
            mock_db.session.commit.assert_called_once()
    
    @patch('app.services.cache_service.AnalysisCache.query')
    @patch('app.services.cache_service.db.session')
    def test_clear_cache_all_types(self, mock_db, mock_query):
        """Test clearing all cache entries for a repository."""
        # Mock cache entries
        mock_entries = [Mock(), Mock(), Mock()]
        mock_query.filter_by.return_value.all.return_value = mock_entries
        
        result = CacheService.clear_cache(self.repository_id)
        
        assert result == 3
        mock_query.filter_by.assert_called_once_with(repository_id=self.repository_id)
        
        # Check that all entries were deleted
        assert mock_db.session.delete.call_count == 3
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.cache_service.AnalysisCache.query')
    @patch('app.services.cache_service.db.session')
    def test_clear_cache_specific_type(self, mock_db, mock_query):
        """Test clearing cache entries for a specific analysis type."""
        # Mock cache entries
        mock_entries = [Mock(), Mock()]
        mock_query.filter.return_value.all.return_value = mock_entries
        
        result = CacheService.clear_cache(self.repository_id, 'structure')
        
        assert result == 2
        mock_query.filter_by.assert_called_once_with(repository_id=self.repository_id)
        mock_query.filter.assert_called_once()
        
        # Check that all entries were deleted
        assert mock_db.session.delete.call_count == 2
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.cache_service.AnalysisCache.query')
    @patch('app.services.cache_service.db.session')
    def test_clear_expired_cache(self, mock_db, mock_query):
        """Test clearing all expired cache entries."""
        # Mock expired cache entries
        mock_entries = [Mock(), Mock(), Mock(), Mock()]
        mock_query.filter.return_value.all.return_value = mock_entries
        
        result = CacheService.clear_expired_cache()
        
        assert result == 4
        mock_query.filter.assert_called_once()
        
        # Check that all entries were deleted
        assert mock_db.session.delete.call_count == 4
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.cache_service.AnalysisCache.query')
    def test_get_cache_stats_with_repository_id(self, mock_query):
        """Test getting cache statistics for a specific repository."""
        # Mock cache entries
        mock_entries = [
            Mock(cache_key='1_structure_data'),
            Mock(cache_key='1_dependencies_data'),
            Mock(cache_key='1_structure_v2')
        ]
        mock_query.filter_by.return_value.all.return_value = mock_entries
        mock_query.filter_by.return_value.count.return_value = 3
        mock_query.filter.return_value.count.return_value = 0
        
        result = CacheService.get_cache_stats(self.repository_id)
        
        assert result['total_entries'] == 3
        assert result['expired_entries'] == 0
        assert result['active_entries'] == 3
        assert result['type_stats'] == {'structure': 2, 'dependencies': 1}
    
    @patch('app.services.cache_service.AnalysisCache.query')
    def test_get_cache_stats_global(self, mock_query):
        """Test getting global cache statistics."""
        mock_query.count.return_value = 100
        mock_query.filter.return_value.count.return_value = 20
        
        result = CacheService.get_cache_stats()
        
        assert result['total_entries'] == 100
        assert result['expired_entries'] == 20
        assert result['active_entries'] == 80
        assert result['type_stats'] == {}
    
    def test_cache_expiration_times(self):
        """Test that different analysis types have correct expiration times."""
        assert CacheService.CACHE_EXPIRATION['structure'] == 24
        assert CacheService.CACHE_EXPIRATION['dependencies'] == 12
        assert CacheService.CACHE_EXPIRATION['complexity'] == 6
        assert CacheService.CACHE_EXPIRATION['tech_stack'] == 24
        assert CacheService.CACHE_EXPIRATION['combined'] == 4
    
    def test_set_cache_different_expiration_times(self):
        """Test that different analysis types get different expiration times."""
        with patch('app.services.cache_service.AnalysisCache.query') as mock_query:
            with patch('app.services.cache_service.db.session') as mock_db:
                with patch('app.services.cache_service.datetime') as mock_datetime:
                    mock_now = datetime.utcnow()
                    mock_datetime.utcnow.return_value = mock_now
                    
                    mock_query.filter_by.return_value.first.return_value = None
                    
                    # Test structure analysis (24 hours)
                    CacheService.set_cache(1, 'structure', {})
                    call_args = mock_db.session.add.call_args[0][0]
                    assert call_args.expires_at == mock_now + timedelta(hours=24)
                    
                    # Test complexity analysis (6 hours)
                    CacheService.set_cache(1, 'complexity', {})
                    call_args = mock_db.session.add.call_args[0][0]
                    assert call_args.expires_at == mock_now + timedelta(hours=6)