"""
Analysis service tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app import create_app, db
from app.config import Config
from app.services.analysis_service import AnalysisService
from app.models.analysis import CodeAnalysis
from app.services.cache_service import CacheService
from app.utils.code_analysis_engine import AnalysisConfig


class TestAnalysisService:
    """Analysis service tests."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.analysis_service = AnalysisService()
        
        # Create test repository structure
        (self.temp_dir / 'main.py').write_text('print("Hello World")')
        (self.temp_dir / 'requirements.txt').write_text('flask==2.0.1')
        
        # Mock repository model
        self.mock_repository = Mock()
        self.mock_repository.id = 1
        self.mock_repository.local_path = str(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_init_analysis_service(self):
        """Test analysis service initialization."""
        assert self.analysis_service.analysis_engine is not None
        assert len(self.analysis_service.supported_analysis_types) > 0
        assert 'structure' in self.analysis_service.supported_analysis_types
        assert 'complexity' in self.analysis_service.supported_analysis_types
    
    def test_start_analysis_success(self):
        """Test successful analysis start."""
        with patch('app.services.analysis_service.db.session') as mock_db, \
             patch('app.models.repository.Repository.query.get') as mock_repo_query, \
             patch.object(self.analysis_service, '_run_analysis_async') as mock_run_async:
            
            mock_repo_query.return_value = self.mock_repository
            mock_db.commit.return_value = None
            
            result = self.analysis_service.start_analysis(
                repository_id=1,
                analysis_types=['structure', 'complexity']
            )
            
            assert result['success'] is True
            assert result['message'] == 'Analysis started successfully'
            assert len(result['analysis_ids']) == 2
            assert result['analysis_types'] == ['structure', 'complexity']
            assert result['repository_id'] == 1
            
            # Verify analysis records were created
            assert mock_db.add.call_count == 2
            mock_run_async.assert_called_once()
    
    def test_start_analysis_invalid_types(self):
        """Test analysis start with invalid types."""
        result = self.analysis_service.start_analysis(
            repository_id=1,
            analysis_types=['invalid_type']
        )
        
        assert result['success'] is False
        assert 'Invalid analysis types' in result['message']
        assert result['analysis_ids'] == []
    
    def test_start_analysis_repository_not_found(self):
        """Test analysis start with non-existent repository."""
        with patch('app.models.repository.Repository.query.get') as mock_repo_query:
            mock_repo_query.return_value = None
            
            result = self.analysis_service.start_analysis(
                repository_id=999,
                analysis_types=['structure']
            )
            
            assert result['success'] is False
            assert 'Repository not found' in result['message']
    
    def test_get_analysis_status_success(self):
        """Test successful status retrieval."""
        with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.status = 'completed'
            mock_analysis.analysis_time = 2.5
            mock_analysis.error_message = None
            mock_analysis.created_at = datetime.utcnow()
            mock_analysis.updated_at = datetime.utcnow()
            
            mock_query.return_value = mock_analysis
            
            result = self.analysis_service.get_analysis_status(analysis_id=1)
            
            assert result['success'] is True
            assert result['status'] == 'completed'
            assert result['progress'] == 100
            assert result['analysis_time'] == 2.5
    
    def test_get_analysis_status_not_found(self):
        """Test status retrieval for non-existent analysis."""
        with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
            mock_query.return_value = None
            
            result = self.analysis_service.get_analysis_status(analysis_id=999)
            
            assert result['success'] is False
            assert result['message'] == 'Analysis not found'
            assert result['status'] is None
    
    def test_get_analysis_results_success(self):
        """Test successful results retrieval."""
        with patch('app.models.analysis.CodeAnalysis.query') as mock_query:
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.analysis_type = 'structure'
            mock_analysis.status = 'completed'
            mock_analysis.result_data = {'files': 10}
            mock_analysis.analysis_time = 1.5
            mock_analysis.created_at = datetime.utcnow()
            
            mock_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_analysis]
            
            result = self.analysis_service.get_analysis_results(repository_id=1)
            
            assert result['success'] is True
            assert 'structure' in result['results']
            assert result['results']['structure']['result_data'] == {'files': 10}
    
    def test_get_analysis_results_no_analyses(self):
        """Test results retrieval when no analyses exist."""
        with patch('app.models.analysis.CodeAnalysis.query') as mock_query:
            mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
            
            result = self.analysis_service.get_analysis_results(repository_id=1)
            
            assert result['success'] is False
            assert 'No analyses found' in result['message']
            assert result['results'] == {}
    
    def test_get_combined_analysis_results_from_cache(self):
        """Test combined results retrieval from cache."""
        with patch.object(CacheService, 'get_cache') as mock_get_cache:
            mock_get_cache.return_value = {'combined': 'data'}
            
            result = self.analysis_service.get_combined_analysis_results(repository_id=1)
            
            assert result['success'] is True
            assert result['from_cache'] is True
            assert result['results'] == {'combined': 'data'}
            mock_get_cache.assert_called_once_with(1, 'combined')
    
    def test_get_combined_analysis_results_new_analysis(self):
        """Test combined results retrieval with new analysis."""
        with patch.object(CacheService, 'get_cache') as mock_get_cache, \
             patch.object(self.analysis_service, 'get_analysis_results') as mock_get_results, \
             patch.object(CacheService, 'set_cache') as mock_set_cache:
            
            mock_get_cache.return_value = None
            mock_get_results.return_value = {
                'success': True,
                'results': {
                    'structure': {'result_data': {'files': 10}},
                    'complexity': {'result_data': {'complexity': 5}}
                }
            }
            
            result = self.analysis_service.get_combined_analysis_results(repository_id=1)
            
            assert result['success'] is True
            assert result['from_cache'] is False
            assert 'combined' in result['results']
            mock_set_cache.assert_called_once()
    
    def test_cancel_analysis_success(self):
        """Test successful analysis cancellation."""
        with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query, \
             patch('app.services.analysis_service.db.session') as mock_db:
            
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.status = 'analyzing'
            
            mock_query.return_value = mock_analysis
            mock_db.commit.return_value = None
            
            result = self.analysis_service.cancel_analysis(analysis_id=1)
            
            assert result['success'] is True
            assert result['message'] == 'Analysis cancelled successfully'
            mock_analysis.update_status.assert_called_once_with('cancelled', 'Analysis cancelled by user')
    
    def test_cancel_analysis_not_found(self):
        """Test cancellation of non-existent analysis."""
        with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
            mock_query.return_value = None
            
            result = self.analysis_service.cancel_analysis(analysis_id=999)
            
            assert result['success'] is False
            assert result['message'] == 'Analysis not found'
    
    def test_cancel_analysis_invalid_status(self):
        """Test cancellation of analysis with invalid status."""
        with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.status = 'completed'
            
            mock_query.return_value = mock_analysis
            
            result = self.analysis_service.cancel_analysis(analysis_id=1)
            
            assert result['success'] is False
            assert 'Cannot cancel analysis' in result['message']
    
    def test_clear_analysis_cache_success(self):
        """Test successful cache clearing."""
        with patch.object(CacheService, 'clear_cache') as mock_clear_cache:
            mock_clear_cache.return_value = 3
            
            result = self.analysis_service.clear_analysis_cache(repository_id=1, analysis_type='structure')
            
            assert result['success'] is True
            assert result['cleared_count'] == 3
            assert result['message'] == 'Cleared 3 cache entries'
            mock_clear_cache.assert_called_once_with(1, 'structure')
    
    def test_clear_analysis_cache_error(self):
        """Test cache clearing with error."""
        with patch.object(CacheService, 'clear_cache') as mock_clear_cache:
            mock_clear_cache.side_effect = Exception("Cache error")
            
            result = self.analysis_service.clear_analysis_cache(repository_id=1)
            
            assert result['success'] is False
            assert 'Failed to clear cache' in result['message']
            assert result['cleared_count'] == 0
    
    def test_get_analysis_history_success(self):
        """Test successful history retrieval."""
        with patch('app.models.analysis.CodeAnalysis.query') as mock_query:
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.analysis_type = 'structure'
            mock_analysis.status = 'completed'
            mock_analysis.analysis_time = 1.5
            mock_analysis.created_at = datetime.utcnow()
            mock_analysis.error_message = None
            
            mock_query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_analysis]
            
            result = self.analysis_service.get_analysis_history(repository_id=1, limit=5)
            
            assert result['success'] is True
            assert len(result['history']) == 1
            assert result['history'][0]['id'] == 1
            assert result['history'][0]['analysis_type'] == 'structure'
    
    def test_get_analysis_statistics_success(self):
        """Test successful statistics retrieval."""
        with patch('app.models.analysis.CodeAnalysis.query') as mock_query:
            # Mock basic statistics
            mock_query.count.return_value = 10
            mock_query.filter_by.return_value.count.side_effect = [7, 2, 1]  # completed, failed, pending
            
            # Mock average time
            mock_query.filter_by.return_value.with_entities.return_value.scalar.return_value = 2.5
            
            result = self.analysis_service.get_analysis_statistics(repository_id=1)
            
            assert result['success'] is True
            stats = result['statistics']
            assert stats['total_analyses'] == 10
            assert stats['completed_analyses'] == 7
            assert stats['failed_analyses'] == 2
            assert stats['pending_analyses'] == 1
            assert stats['success_rate'] == 70.0
            assert stats['average_analysis_time'] == 2.5
    
    def test_create_analysis_config_default(self):
        """Test analysis config creation with default values."""
        config = self.analysis_service._create_analysis_config()
        
        assert isinstance(config, AnalysisConfig)
        assert len(config.analysis_types) > 0
        assert '*' in config.include_patterns
        assert 'node_modules/' in config.exclude_patterns
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.timeout == 300
        assert config.enable_cache is True
        assert config.parallel_processing is True
    
    def test_create_analysis_config_custom(self):
        """Test analysis config creation with custom values."""
        custom_config = {
            'analysis_types': ['structure', 'complexity'],
            'include_patterns': ['*.py', '*.js'],
            'exclude_patterns': ['test_*'],
            'max_file_size': 5 * 1024 * 1024,
            'timeout': 600,
            'enable_cache': False,
            'parallel_processing': False
        }
        
        config = self.analysis_service._create_analysis_config(custom_config)
        
        assert config.analysis_types == ['structure', 'complexity']
        assert config.include_patterns == ['*.py', '*.js']
        assert config.exclude_patterns == ['test_*']
        assert config.max_file_size == 5 * 1024 * 1024
        assert config.timeout == 600
        assert config.enable_cache is False
        assert config.parallel_processing is False
    
    def test_calculate_progress(self):
        """Test progress calculation."""
        assert self.analysis_service._calculate_progress('pending') == 0
        assert self.analysis_service._calculate_progress('analyzing') == 50
        assert self.analysis_service._calculate_progress('completed') == 100
        assert self.analysis_service._calculate_progress('failed') == 100
        assert self.analysis_service._calculate_progress('cancelled') == 100
        assert self.analysis_service._calculate_progress('unknown') == 0
    
    def test_combine_analysis_results(self):
        """Test combining individual analysis results."""
        individual_results = {
            'structure': {
                'result_data': {'files': 10, 'directories': 5}
            },
            'complexity': {
                'result_data': {'overall_complexity': 15, 'functions': 20}
            },
            'quality': {
                'result_data': {'overall_quality_score': 85.0}
            },
            'security': {
                'status': 'failed'
            }
        }
        
        combined = self.analysis_service._combine_analysis_results(individual_results)
        
        assert combined['summary']['total_analyses'] == 4
        assert combined['summary']['completed_analyses'] == 3
        assert combined['summary']['failed_analyses'] == 1
        assert combined['summary']['overall_quality_score'] == 85.0
        assert 'structure' in combined
        assert 'complexity' in combined
        assert 'quality' in combined
        assert 'security' in combined
        assert 'recommendations' in combined
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        combined_results = {
            'complexity': {'overall_complexity': 35},
            'quality': {'overall_quality_score': 55.0, 'documentation_coverage': 30.0, 'test_coverage': 40.0},
            'security': {'security_issues': ['issue1', 'issue2']}
        }
        
        recommendations = self.analysis_service._generate_recommendations(combined_results)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for specific recommendations
        recommendation_text = ' '.join(recommendations)
        assert 'refactoring' in recommendation_text.lower()
        assert 'quality' in recommendation_text.lower()
        assert 'security' in recommendation_text.lower()
        assert 'documentation' in recommendation_text.lower()
        assert 'test' in recommendation_text.lower()
    
    def test_generate_recommendations_good_quality(self):
        """Test recommendation generation for good quality code."""
        combined_results = {
            'complexity': {'overall_complexity': 10},
            'quality': {'overall_quality_score': 85.0, 'documentation_coverage': 80.0, 'test_coverage': 75.0},
            'security': {'security_issues': []}
        }
        
        recommendations = self.analysis_service._generate_recommendations(combined_results)
        
        # Should have fewer or no critical recommendations
        recommendation_text = ' '.join(recommendations)
        assert 'refactoring' not in recommendation_text.lower()
        assert 'low' not in recommendation_text.lower()
    
    def test_run_analysis_async_success(self):
        """Test async analysis execution success."""
        with patch('app.services.analysis_service.db.session') as mock_db, \
             patch.object(CacheService, 'get_cache') as mock_get_cache, \
             patch.object(CacheService, 'set_cache') as mock_set_cache, \
             patch.object(self.analysis_service.analysis_engine, 'analyze_repository') as mock_analyze:
            
            # Mock database operations
            mock_db.commit.return_value = None
            
            # Mock cache miss
            mock_get_cache.return_value = None
            
            # Mock successful analysis
            mock_result = Mock()
            mock_result.success = True
            mock_result.to_dict.return_value = {'analysis': 'result'}
            mock_analyze.return_value = mock_result
            
            # Mock analysis records
            mock_analysis = Mock()
            mock_analysis.update_status = Mock()
            mock_analysis.complete_analysis = Mock()
            mock_analysis.fail_analysis = Mock()
            
            with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
                mock_query.return_value = mock_analysis
                
                self.analysis_service._run_analysis_async(
                    repository_id=1,
                    repository_path=str(self.temp_dir),
                    analysis_types=['structure'],
                    config=AnalysisConfig(),
                    analysis_ids=[1]
                )
                
                # Verify status updates
                mock_analysis.update_status.assert_called()
                mock_analysis.complete_analysis.assert_called()
                mock_set_cache.assert_called_once()
    
    def test_run_analysis_async_cache_hit(self):
        """Test async analysis execution with cache hit."""
        with patch('app.services.analysis_service.db.session') as mock_db, \
             patch.object(CacheService, 'get_cache') as mock_get_cache, \
             patch.object(CacheService, 'set_cache') as mock_set_cache:
            
            # Mock database operations
            mock_db.commit.return_value = None
            
            # Mock cache hit
            mock_get_cache.return_value = {'cached': 'result'}
            
            # Mock analysis records
            mock_analysis = Mock()
            mock_analysis.update_status = Mock()
            mock_analysis.complete_analysis = Mock()
            
            with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
                mock_query.return_value = mock_analysis
                
                self.analysis_service._run_analysis_async(
                    repository_id=1,
                    repository_path=str(self.temp_dir),
                    analysis_types=['structure'],
                    config=AnalysisConfig(),
                    analysis_ids=[1]
                )
                
                # Verify cache was used
                mock_get_cache.assert_called_once()
                mock_analysis.complete_analysis.assert_called()
                # Should not call set_cache for cache hit
                mock_set_cache.assert_not_called()
    
    def test_run_analysis_async_error_handling(self):
        """Test async analysis execution error handling."""
        with patch('app.services.analysis_service.db.session') as mock_db, \
             patch.object(CacheService, 'get_cache') as mock_get_cache, \
             patch.object(self.analysis_service.analysis_engine, 'analyze_repository') as mock_analyze:
            
            # Mock database operations
            mock_db.commit.return_value = None
            
            # Mock cache miss
            mock_get_cache.return_value = None
            
            # Mock analysis error
            mock_analyze.side_effect = Exception("Analysis error")
            
            # Mock analysis records
            mock_analysis = Mock()
            mock_analysis.update_status = Mock()
            mock_analysis.fail_analysis = Mock()
            
            with patch('app.models.analysis.CodeAnalysis.query.get') as mock_query:
                mock_query.return_value = mock_analysis
                
                self.analysis_service._run_analysis_async(
                    repository_id=1,
                    repository_path=str(self.temp_dir),
                    analysis_types=['structure'],
                    config=AnalysisConfig(),
                    analysis_ids=[1]
                )
                
                # Verify error handling
                mock_analysis.fail_analysis.assert_called()
                mock_db.commit.assert_called()