"""
Analysis service for managing code analysis operations.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from app import db
from app.models.analysis import CodeAnalysis
from app.services.cache_service import CacheService
from app.utils.code_analysis_engine import CodeAnalysisEngine, AnalysisConfig, AnalysisResult

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing code analysis operations."""
    
    def __init__(self):
        self.analysis_engine = CodeAnalysisEngine()
        self.supported_analysis_types = [
            'structure', 'dependencies', 'complexity', 
            'tech_stack', 'security', 'patterns', 'quality'
        ]
    
    def start_analysis(self, repository_id: int, analysis_types: List[str], 
                      config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a new code analysis task."""
        try:
            # Validate analysis types
            invalid_types = set(analysis_types) - set(self.supported_analysis_types)
            if invalid_types:
                raise ValueError(f"Invalid analysis types: {invalid_types}")
            
            # Create analysis configuration
            analysis_config = self._create_analysis_config(config)
            
            # Create analysis records for each type
            analysis_records = []
            for analysis_type in analysis_types:
                analysis = CodeAnalysis(
                    repository_id=repository_id,
                    analysis_type=analysis_type,
                    status='pending'
                )
                db.session.add(analysis)
                analysis_records.append(analysis)
            
            db.session.commit()
            
            # Get repository path
            from app.models.repository import Repository
            repository = Repository.query.get(repository_id)
            if not repository:
                raise ValueError(f"Repository not found: {repository_id}")
            
            repository_path = repository.local_path
            
            # Validate repository path exists
            import os
            if not repository_path or not os.path.exists(repository_path):
                raise ValueError(f"Repository path does not exist: {repository_path}")
            
            # Start analysis in background
            analysis_ids = [record.id for record in analysis_records]
            self._run_analysis_async(
                repository_id, 
                repository_path, 
                analysis_types, 
                analysis_config,
                analysis_ids
            )
            
            return {
                'success': True,
                'message': 'Analysis started successfully',
                'analysis_ids': analysis_ids,
                'analysis_types': analysis_types,
                'repository_id': repository_id
            }
            
        except Exception as e:
            logger.error(f"Error starting analysis: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to start analysis: {str(e)}',
                'analysis_ids': [],
                'analysis_types': [],
                'repository_id': repository_id
            }
    
    def get_analysis_status(self, analysis_id: int) -> Dict[str, Any]:
        """Get the status of a specific analysis."""
        try:
            analysis = CodeAnalysis.query.get(analysis_id)
            if not analysis:
                return {
                    'success': False,
                    'message': 'Analysis not found',
                    'status': None,
                    'progress': 0
                }
            
            # Calculate progress based on status
            progress = self._calculate_progress(analysis.status)
            
            return {
                'success': True,
                'message': 'Status retrieved successfully',
                'status': analysis.status,
                'progress': progress,
                'analysis_time': analysis.analysis_time,
                'error_message': analysis.error_message,
                'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                'updated_at': analysis.updated_at.isoformat() if analysis.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis status: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to get status: {str(e)}',
                'status': None,
                'progress': 0
            }
    
    def get_analysis_results(self, repository_id: int, analysis_types: List[str] = None) -> Dict[str, Any]:
        """Get analysis results for a repository."""
        try:
            # Build query
            query = CodeAnalysis.query.filter_by(repository_id=repository_id)
            
            if analysis_types:
                query = query.filter(CodeAnalysis.analysis_type.in_(analysis_types))
            
            # Get most recent analyses
            analyses = query.order_by(CodeAnalysis.created_at.desc()).all()
            
            if not analyses:
                return {
                    'success': False,
                    'message': 'No analyses found for this repository',
                    'results': {}
                }
            
            # Group results by analysis type
            results = {}
            for analysis in analyses:
                if analysis.status == 'completed':
                    results[analysis.analysis_type] = {
                        'analysis_id': analysis.id,
                        'result_data': analysis.result_data,
                        'analysis_time': analysis.analysis_time,
                        'created_at': analysis.created_at.isoformat() if analysis.created_at else None
                    }
                else:
                    results[analysis.analysis_type] = {
                        'analysis_id': analysis.id,
                        'status': analysis.status,
                        'error_message': analysis.error_message,
                        'created_at': analysis.created_at.isoformat() if analysis.created_at else None
                    }
            
            return {
                'success': True,
                'message': 'Results retrieved successfully',
                'results': results,
                'repository_id': repository_id
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis results: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to get results: {str(e)}',
                'results': {},
                'repository_id': repository_id
            }
    
    def get_combined_analysis_results(self, repository_id: int) -> Dict[str, Any]:
        """Get combined analysis results from cache or run new analysis."""
        try:
            # Check cache first
            cached_results = CacheService.get_cache(repository_id, 'combined')
            if cached_results:
                return {
                    'success': True,
                    'message': 'Results retrieved from cache',
                    'results': cached_results,
                    'from_cache': True,
                    'repository_id': repository_id
                }
            
            # Get all analysis types
            all_types = self.supported_analysis_types
            
            # Get individual results
            individual_results = self.get_analysis_results(repository_id, all_types)
            
            if not individual_results['success']:
                return individual_results
            
            # Combine results
            combined_results = self._combine_analysis_results(individual_results['results'])
            
            # Cache the combined results
            CacheService.set_cache(repository_id, 'combined', combined_results)
            
            return {
                'success': True,
                'message': 'Combined analysis completed successfully',
                'results': combined_results,
                'from_cache': False,
                'repository_id': repository_id
            }
            
        except Exception as e:
            logger.error(f"Error getting combined analysis results: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to get combined results: {str(e)}',
                'results': {},
                'repository_id': repository_id
            }
    
    def cancel_analysis(self, analysis_id: int) -> Dict[str, Any]:
        """Cancel a running analysis."""
        try:
            analysis = CodeAnalysis.query.get(analysis_id)
            if not analysis:
                return {
                    'success': False,
                    'message': 'Analysis not found'
                }
            
            if analysis.status not in ['pending', 'analyzing']:
                return {
                    'success': False,
                    'message': f'Cannot cancel analysis in {analysis.status} status'
                }
            
            analysis.update_status('cancelled', 'Analysis cancelled by user')
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Analysis cancelled successfully',
                'analysis_id': analysis_id
            }
            
        except Exception as e:
            logger.error(f"Error cancelling analysis: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to cancel analysis: {str(e)}',
                'analysis_id': analysis_id
            }
    
    def clear_analysis_cache(self, repository_id: int, analysis_type: str = None) -> Dict[str, Any]:
        """Clear analysis cache for a repository."""
        try:
            count = CacheService.clear_cache(repository_id, analysis_type)
            
            return {
                'success': True,
                'message': f'Cleared {count} cache entries',
                'cleared_count': count,
                'repository_id': repository_id,
                'analysis_type': analysis_type
            }
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to clear cache: {str(e)}',
                'cleared_count': 0,
                'repository_id': repository_id,
                'analysis_type': analysis_type
            }
    
    def get_analysis_history(self, repository_id: int, limit: int = 10) -> Dict[str, Any]:
        """Get analysis history for a repository."""
        try:
            analyses = CodeAnalysis.query.filter_by(repository_id=repository_id)\
                .order_by(CodeAnalysis.created_at.desc())\
                .limit(limit)\
                .all()
            
            history = []
            for analysis in analyses:
                history.append({
                    'id': analysis.id,
                    'analysis_type': analysis.analysis_type,
                    'status': analysis.status,
                    'analysis_time': analysis.analysis_time,
                    'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                    'error_message': analysis.error_message
                })
            
            return {
                'success': True,
                'message': 'History retrieved successfully',
                'history': history,
                'repository_id': repository_id
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis history: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to get history: {str(e)}',
                'history': [],
                'repository_id': repository_id
            }
    
    def get_analysis_statistics(self, repository_id: int = None) -> Dict[str, Any]:
        """Get analysis statistics."""
        try:
            query = CodeAnalysis.query
            
            if repository_id:
                query = query.filter_by(repository_id=repository_id)
            
            # Basic statistics
            total_analyses = query.count()
            completed_analyses = query.filter_by(status='completed').count()
            failed_analyses = query.filter_by(status='failed').count()
            pending_analyses = query.filter_by(status='pending').count()
            
            # Average analysis time
            completed_query = query.filter_by(status='completed')
            avg_time = completed_query.with_entities(
                db.func.avg(CodeAnalysis.analysis_time)
            ).scalar() or 0
            
            # Group by analysis type
            type_stats = {}
            if repository_id:
                analyses = query.all()
                for analysis in analyses:
                    analysis_type = analysis.analysis_type
                    if analysis_type not in type_stats:
                        type_stats[analysis_type] = {
                            'total': 0,
                            'completed': 0,
                            'failed': 0,
                            'avg_time': 0
                        }
                    
                    type_stats[analysis_type]['total'] += 1
                    if analysis.status == 'completed':
                        type_stats[analysis_type]['completed'] += 1
                    elif analysis.status == 'failed':
                        type_stats[analysis_type]['failed'] += 1
            
            # Calculate average times by type
            for analysis_type in type_stats:
                completed_count = type_stats[analysis_type]['completed']
                if completed_count > 0:
                    type_query = query.filter_by(
                        repository_id=repository_id,
                        analysis_type=analysis_type,
                        status='completed'
                    )
                    avg_time = type_query.with_entities(
                        db.func.avg(CodeAnalysis.analysis_time)
                    ).scalar() or 0
                    type_stats[analysis_type]['avg_time'] = avg_time
            
            return {
                'success': True,
                'message': 'Statistics retrieved successfully',
                'statistics': {
                    'total_analyses': total_analyses,
                    'completed_analyses': completed_analyses,
                    'failed_analyses': failed_analyses,
                    'pending_analyses': pending_analyses,
                    'success_rate': (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
                    'average_analysis_time': avg_time,
                    'type_statistics': type_stats
                },
                'repository_id': repository_id
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis statistics: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to get statistics: {str(e)}',
                'statistics': {},
                'repository_id': repository_id
            }
    
    def _create_analysis_config(self, config: Optional[Dict[str, Any]] = None) -> AnalysisConfig:
        """Create analysis configuration from user input."""
        if config is None:
            config = {}
        
        return AnalysisConfig(
            analysis_types=config.get('analysis_types', self.supported_analysis_types),
            include_patterns=config.get('include_patterns', ['*']),
            exclude_patterns=config.get('exclude_patterns', [
                '*.log', '*.tmp', 'node_modules/', '.git/', '__pycache__/'
            ]),
            max_file_size=config.get('max_file_size', 10 * 1024 * 1024),  # 10MB
            timeout=config.get('timeout', 300),  # 5 minutes
            enable_cache=config.get('enable_cache', True),
            parallel_processing=config.get('parallel_processing', True)
        )
    
    def _run_analysis_async(self, repository_id: int, repository_path: str, 
                           analysis_types: List[str], config: AnalysisConfig,
                           analysis_ids: List[int]):
        """Run analysis asynchronously (simplified version)."""
        try:
            # Update status to analyzing
            for analysis_id in analysis_ids:
                analysis = CodeAnalysis.query.get(analysis_id)
                if analysis:
                    analysis.update_status('analyzing')
            
            db.session.commit()
            
            # Run analysis for each type
            for i, analysis_type in enumerate(analysis_types):
                analysis_id = analysis_ids[i]
                analysis = CodeAnalysis.query.get(analysis_id)
                
                if not analysis:
                    continue
                
                try:
                    # Check cache first
                    cached_result = CacheService.get_cache(repository_id, analysis_type)
                    if cached_result:
                        analysis.complete_analysis(cached_result, 0.1)  # Cache hit is very fast
                        db.session.commit()
                        continue
                    
                    # Run analysis
                    start_time = time.time()
                    result = self.analysis_engine.analyze_repository(
                        repository_path, 
                        [analysis_type], 
                        config
                    )
                    analysis_time = time.time() - start_time
                    
                    if result.success:
                        analysis.complete_analysis(result.to_dict(), analysis_time)
                        # Cache the result
                        CacheService.set_cache(repository_id, analysis_type, result.to_dict())
                    else:
                        analysis.fail_analysis(result.error_message)
                    
                    db.session.commit()
                    
                except Exception as e:
                    logger.error(f"Error in {analysis_type} analysis: {str(e)}")
                    analysis.fail_analysis(str(e))
                    db.session.commit()
            
        except Exception as e:
            logger.error(f"Error in async analysis: {str(e)}")
            # Mark all analyses as failed
            for analysis_id in analysis_ids:
                analysis = CodeAnalysis.query.get(analysis_id)
                if analysis:
                    analysis.fail_analysis(str(e))
            
            db.session.commit()
    
    def _calculate_progress(self, status: str) -> int:
        """Calculate progress percentage based on status."""
        progress_map = {
            'pending': 0,
            'analyzing': 50,
            'completed': 100,
            'failed': 100,
            'cancelled': 100
        }
        return progress_map.get(status, 0)
    
    def _combine_analysis_results(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine individual analysis results into a comprehensive report."""
        combined = {
            'summary': {
                'total_analyses': len(individual_results),
                'completed_analyses': 0,
                'failed_analyses': 0,
                'overall_quality_score': 0
            },
            'structure': {},
            'dependencies': {},
            'complexity': {},
            'tech_stack': {},
            'security': {},
            'patterns': {},
            'quality': {},
            'recommendations': []
        }
        
        completed_count = 0
        failed_count = 0
        quality_scores = []
        
        for analysis_type, result in individual_results.items():
            if analysis_type in combined:
                if 'result_data' in result:
                    combined[analysis_type] = result['result_data']
                    completed_count += 1
                    
                    # Extract quality scores
                    if analysis_type == 'quality' and 'overall_quality_score' in result['result_data']:
                        quality_scores.append(result['result_data']['overall_quality_score'])
                else:
                    combined[analysis_type] = {'status': result.get('status', 'unknown')}
                    failed_count += 1
        
        # Update summary
        combined['summary']['completed_analyses'] = completed_count
        combined['summary']['failed_analyses'] = failed_count
        
        # Calculate overall quality score
        if quality_scores:
            combined['summary']['overall_quality_score'] = sum(quality_scores) / len(quality_scores)
        
        # Generate recommendations
        combined['recommendations'] = self._generate_recommendations(combined)
        
        return combined
    
    def _generate_recommendations(self, combined_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Complexity recommendations
        if 'complexity' in combined_results and 'overall_complexity' in combined_results['complexity']:
            complexity = combined_results['complexity']['overall_complexity']
            if complexity > 30:
                recommendations.append("Consider refactoring high-complexity code to improve maintainability")
            elif complexity > 20:
                recommendations.append("Code complexity is moderate, consider reviewing complex functions")
        
        # Quality recommendations
        if 'quality' in combined_results and 'overall_quality_score' in combined_results['quality']:
            quality_score = combined_results['quality']['overall_quality_score']
            if quality_score < 60:
                recommendations.append("Overall code quality is low, consider implementing code quality improvements")
            elif quality_score < 80:
                recommendations.append("Code quality is good but has room for improvement")
        
        # Security recommendations
        if 'security' in combined_results and 'security_issues' in combined_results['security']:
            security_issues = combined_results['security']['security_issues']
            if len(security_issues) > 0:
                recommendations.append(f"Found {len(security_issues)} security issues that should be addressed")
        
        # Documentation recommendations
        if 'quality' in combined_results and 'documentation_coverage' in combined_results['quality']:
            doc_coverage = combined_results['quality']['documentation_coverage']
            if doc_coverage < 50:
                recommendations.append("Consider improving code documentation coverage")
        
        # Test coverage recommendations
        if 'quality' in combined_results and 'test_coverage' in combined_results['quality']:
            test_coverage = combined_results['quality']['test_coverage']
            if test_coverage < 50:
                recommendations.append("Consider increasing test coverage for better code reliability")
        
        return recommendations