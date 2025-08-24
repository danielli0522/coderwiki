"""
Analysis API endpoints for code analysis functionality.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
import logging
from typing import Dict, Any, List, Optional

from app.services.analysis_service import AnalysisService
from app.models.repository import Repository
from app.utils.response_processor import ResponseProcessor

logger = logging.getLogger(__name__)

# Create blueprint
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# Initialize services
analysis_service = AnalysisService()
response_processor = ResponseProcessor()


def validate_repository_access(f):
    """Decorator to validate user access to repository."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract repository_id from different sources based on request method
        repository_id = None

        if request.method == 'GET':
            # For GET requests, get from URL parameters
            repository_id = kwargs.get('repository_id')
        else:
            # For POST/PUT requests, get from JSON body or URL parameters
            repository_id = kwargs.get('repository_id') or request.json.get('repository_id')

        if not repository_id:
            return jsonify({
                'success': False,
                'message': 'Repository ID is required'
            }), 400

        # Check if repository exists and user has access
        repository = Repository.query.get(repository_id)
        if not repository:
            return jsonify({
                'success': False,
                'message': 'Repository not found'
            }), 404

        if repository.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Access denied to this repository'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


@analysis_bp.route('/start', methods=['POST'])
@login_required
@validate_repository_access
def start_analysis():
    """Start a new code analysis task."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['repository_id', 'analysis_types']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        repository_id = data['repository_id']
        analysis_types = data['analysis_types']
        config = data.get('config', {})

        # Validate analysis types
        valid_types = [
            'structure', 'dependencies', 'complexity',
            'tech_stack', 'security', 'patterns', 'quality'
        ]

        invalid_types = set(analysis_types) - set(valid_types)
        if invalid_types:
            return jsonify({
                'success': False,
                'message': f'Invalid analysis types: {list(invalid_types)}',
                'valid_types': valid_types
            }), 400

        # Start analysis
        result = analysis_service.start_analysis(
            repository_id=repository_id,
            analysis_types=analysis_types,
            config=config
        )

        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Analysis started successfully',
                'analysis_ids': result['analysis_ids'],
                'analysis_types': result['analysis_types'],
                'repository_id': result['repository_id']
            }), 202
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/status/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis_status(analysis_id):
    """Get the status of a specific analysis."""
    try:
        result = analysis_service.get_analysis_status(analysis_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 404

    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/results/<int:repository_id>', methods=['GET'])
@login_required
@validate_repository_access
def get_analysis_results(repository_id):
    """Get analysis results for a repository."""
    try:
        # Get optional analysis types filter
        analysis_types = request.args.getlist('analysis_types')
        if analysis_types:
            # Validate analysis types
            valid_types = [
                'structure', 'dependencies', 'complexity',
                'tech_stack', 'security', 'patterns', 'quality'
            ]
            invalid_types = set(analysis_types) - set(valid_types)
            if invalid_types:
                return jsonify({
                    'success': False,
                    'message': f'Invalid analysis types: {list(invalid_types)}',
                    'valid_types': valid_types
                }), 400

        result = analysis_service.get_analysis_results(repository_id, analysis_types or None)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 404

    except Exception as e:
        logger.error(f"Error getting analysis results: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/combined/<int:repository_id>', methods=['GET'])
@login_required
@validate_repository_access
def get_combined_analysis_results(repository_id):
    """Get combined analysis results for a repository."""
    try:
        result = analysis_service.get_combined_analysis_results(repository_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 404

    except Exception as e:
        logger.error(f"Error getting combined analysis results: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/cancel/<int:analysis_id>', methods=['POST'])
@login_required
def cancel_analysis(analysis_id):
    """Cancel a running analysis."""
    try:
        result = analysis_service.cancel_analysis(analysis_id)

        if result['success']:
            return jsonify(result)
        else:
            status_code = 404 if 'not found' in result['message'].lower() else 400
            return jsonify({
                'success': False,
                'message': result['message']
            }), status_code

    except Exception as e:
        logger.error(f"Error cancelling analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/cache/clear/<int:repository_id>', methods=['POST'])
@login_required
@validate_repository_access
def clear_analysis_cache(repository_id):
    """Clear analysis cache for a repository."""
    try:
        analysis_type = request.json.get('analysis_type') if request.json else None

        result = analysis_service.clear_analysis_cache(repository_id, analysis_type)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except Exception as e:
        logger.error(f"Error clearing analysis cache: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/history/<int:repository_id>', methods=['GET'])
@login_required
@validate_repository_access
def get_analysis_history(repository_id):
    """Get analysis history for a repository."""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(max(1, limit), 100)  # Limit between 1 and 100

        result = analysis_service.get_analysis_history(repository_id, limit)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except Exception as e:
        logger.error(f"Error getting analysis history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/statistics', methods=['GET'])
@login_required
def get_analysis_statistics():
    """Get analysis statistics."""
    try:
        repository_id = request.args.get('repository_id', type=int)

        # If repository_id is provided, validate access
        if repository_id:
            repository = Repository.query.get(repository_id)
            if not repository:
                return jsonify({
                    'success': False,
                    'message': 'Repository not found'
                }), 404

            if repository.user_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'Access denied to this repository'
                }), 403

        result = analysis_service.get_analysis_statistics(repository_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except Exception as e:
        logger.error(f"Error getting analysis statistics: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/types', methods=['GET'])
@login_required
def get_supported_analysis_types():
    """Get supported analysis types and their descriptions."""
    try:
        capabilities = analysis_service.analysis_engine.get_analysis_capabilities()

        return jsonify({
            'success': True,
            'message': 'Supported analysis types retrieved successfully',
            'analysis_types': list(capabilities.keys()),
            'capabilities': capabilities
        })

    except Exception as e:
        logger.error(f"Error getting supported analysis types: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/config/validate', methods=['POST'])
@login_required
def validate_analysis_config():
    """Validate analysis configuration."""
    try:
        data = request.get_json()
        config = data.get('config', {})

        # Create analysis config for validation
        from app.utils.code_analysis_engine import AnalysisConfig
        analysis_config = AnalysisConfig(
            analysis_types=config.get('analysis_types', []),
            include_patterns=config.get('include_patterns', ['*']),
            exclude_patterns=config.get('exclude_patterns', [
                '*.log', '*.tmp', 'node_modules/', '.git/', '__pycache__/'
            ]),
            max_file_size=config.get('max_file_size', 10 * 1024 * 1024),
            timeout=config.get('timeout', 300),
            enable_cache=config.get('enable_cache', True),
            parallel_processing=config.get('parallel_processing', True)
        )

        # Validate configuration
        errors = analysis_service.analysis_engine.validate_analysis_config(analysis_config)

        return jsonify({
            'success': True,
            'message': 'Configuration validation completed',
            'valid': len(errors) == 0,
            'errors': errors,
            'config': config
        })

    except Exception as e:
        logger.error(f"Error validating analysis config: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@analysis_bp.route('/health', methods=['GET'])
@login_required
def analysis_health_check():
    """Health check for analysis service."""
    try:
        # Check if analysis engine is working
        supported_types = analysis_service.analysis_engine.get_supported_analysis_types()

        return jsonify({
            'success': True,
            'message': 'Analysis service is healthy',
            'status': 'healthy',
            'supported_analysis_types': supported_types,
            'service_version': '1.0.0'
        })

    except Exception as e:
        logger.error(f"Error in analysis health check: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Analysis service is unhealthy',
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# Error handlers
@analysis_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({
        'success': False,
        'message': 'Bad request'
    }), 400


@analysis_bp.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized errors."""
    return jsonify({
        'success': False,
        'message': 'Unauthorized'
    }), 401


@analysis_bp.errorhandler(403)
def forbidden(error):
    """Handle forbidden errors."""
    return jsonify({
        'success': False,
        'message': 'Forbidden'
    }), 403


@analysis_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404


@analysis_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500
