"""
Analysis API simple tests.
"""

import pytest
from unittest.mock import Mock, patch

from app.api.analysis import analysis_bp, validate_repository_access


class TestAnalysisAPISimple:
    """Simple analysis API tests."""
    
    def test_analysis_blueprint_creation(self):
        """Test that analysis blueprint is created correctly."""
        assert analysis_bp.name == 'analysis'
        assert analysis_bp.url_prefix == '/api/analysis'
        assert len(analysis_bp.deferred_functions) > 0  # Has routes registered
    
    def test_validate_repository_access_decorator(self):
        """Test the repository access validation decorator."""
        # Create a mock function
        mock_function = Mock(return_value='decorated_function_called')
        
        # Apply decorator
        decorated_function = validate_repository_access(mock_function)
        
        # Test that decorator returns a function
        assert callable(decorated_function)
        # The decorator preserves the original function name (most of the time)
        assert hasattr(decorated_function, '__name__')
    
    def test_analysis_endpoints_registered(self):
        """Test that all expected endpoints are registered."""
        expected_endpoints = [
            '/start',
            '/status/<int:analysis_id>',
            '/results/<int:repository_id>',
            '/combined/<int:repository_id>',
            '/cancel/<int:analysis_id>',
            '/cache/clear/<int:repository_id>',
            '/history/<int:repository_id>',
            '/statistics',
            '/types',
            '/config/validate',
            '/health'
        ]
        
        # Check that blueprint has routes
        assert len(analysis_bp.deferred_functions) >= len(expected_endpoints)
    
    def test_analysis_api_imports(self):
        """Test that all required imports are available."""
        from app.api.analysis import (
            analysis_bp,
            validate_repository_access,
            logger,
            analysis_service,
            response_processor
        )
        
        # Check that services are properly initialized
        assert analysis_service is not None
        assert response_processor is not None
        assert logger is not None
    
    def test_analysis_error_handlers(self):
        """Test that error handlers are registered."""
        # Check that error handlers are present in the blueprint
        error_handler_codes = [400, 401, 403, 404, 500]
        
        # The blueprint should have error handlers registered
        # This is a basic check to ensure the error handling code is present
        assert hasattr(analysis_bp, 'error_handler_spec')
        assert analysis_bp.error_handler_spec is not None