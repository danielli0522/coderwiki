"""
Cache management service for analysis results.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app import db
from app.models.analysis import AnalysisCache


class CacheService:
    """Service for managing analysis cache."""
    
    # Cache expiration times (in hours)
    CACHE_EXPIRATION = {
        'structure': 24,      # 24 hours
        'dependencies': 12,   # 12 hours
        'complexity': 6,      # 6 hours
        'tech_stack': 24,     # 24 hours
        'combined': 4         # 4 hours
    }
    
    @staticmethod
    def generate_cache_key(repository_id: int, analysis_type: str, additional_params: str = '') -> str:
        """Generate a unique cache key for analysis results."""
        key_parts = [str(repository_id), analysis_type]
        if additional_params:
            key_parts.append(additional_params)
        return '_'.join(key_parts)
    
    @staticmethod
    def get_cache(repository_id: int, analysis_type: str, additional_params: str = '') -> Optional[Dict[str, Any]]:
        """Get cached analysis result if it exists and is not expired."""
        cache_key = CacheService.generate_cache_key(repository_id, analysis_type, additional_params)
        
        cache_entry = AnalysisCache.query.filter_by(
            repository_id=repository_id,
            cache_key=cache_key
        ).first()
        
        if cache_entry and not cache_entry.is_expired():
            return cache_entry.cache_data
        
        # Clean up expired cache entries
        if cache_entry and cache_entry.is_expired():
            db.session.delete(cache_entry)
            db.session.commit()
        
        return None
    
    @staticmethod
    def set_cache(repository_id: int, analysis_type: str, cache_data: Dict[str, Any], 
                  additional_params: str = '') -> AnalysisCache:
        """Set cache entry for analysis results."""
        cache_key = CacheService.generate_cache_key(repository_id, analysis_type, additional_params)
        
        # Calculate expiration time
        expiration_hours = CacheService.CACHE_EXPIRATION.get(analysis_type, 4)
        expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        # Check if cache entry already exists
        existing_cache = AnalysisCache.query.filter_by(
            repository_id=repository_id,
            cache_key=cache_key
        ).first()
        
        if existing_cache:
            existing_cache.update_cache(cache_data, expires_at)
            db.session.commit()
            return existing_cache
        
        # Create new cache entry
        cache_entry = AnalysisCache(
            repository_id=repository_id,
            cache_key=cache_key,
            cache_data=cache_data,
            expires_at=expires_at
        )
        
        db.session.add(cache_entry)
        db.session.commit()
        
        return cache_entry
    
    @staticmethod
    def clear_cache(repository_id: int, analysis_type: str = None) -> int:
        """Clear cache entries for a repository."""
        query = AnalysisCache.query.filter_by(repository_id=repository_id)
        
        if analysis_type:
            # Clear cache for specific analysis type
            cache_key_pattern = f"{repository_id}_{analysis_type}"
            query = query.filter(AnalysisCache.cache_key.like(f"{cache_key_pattern}%"))
        
        cache_entries = query.all()
        count = len(cache_entries)
        
        for entry in cache_entries:
            db.session.delete(entry)
        
        db.session.commit()
        return count
    
    @staticmethod
    def clear_expired_cache() -> int:
        """Clear all expired cache entries."""
        expired_entries = AnalysisCache.query.filter(
            AnalysisCache.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_entries)
        
        for entry in expired_entries:
            db.session.delete(entry)
        
        db.session.commit()
        return count
    
    @staticmethod
    def get_cache_stats(repository_id: int = None) -> Dict[str, Any]:
        """Get cache statistics."""
        query = AnalysisCache.query
        
        if repository_id:
            query = query.filter_by(repository_id=repository_id)
        
        total_entries = query.count()
        expired_entries = query.filter(AnalysisCache.expires_at < datetime.utcnow()).count()
        active_entries = total_entries - expired_entries
        
        # Group by analysis type
        type_stats = {}
        if repository_id:
            entries = query.all()
            for entry in entries:
                analysis_type = entry.cache_key.split('_')[1]
                if analysis_type not in type_stats:
                    type_stats[analysis_type] = 0
                type_stats[analysis_type] += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': active_entries,
            'type_stats': type_stats
        }