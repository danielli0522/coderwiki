"""
Database context manager for safe session management.
"""

import logging
from contextlib import contextmanager
from typing import Generator
from app import db

logger = logging.getLogger(__name__)


@contextmanager
def db_transaction() -> Generator[None, None, None]:
    """
    Context manager for database transactions with automatic commit/rollback.
    
    Usage:
        with db_transaction():
            # Database operations here
            db.session.add(obj)
            # Automatically commits on success, rolls back on exception
    """
    try:
        yield
        db.session.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        # Ensure session is cleaned up
        try:
            db.session.remove()
        except Exception as e:
            logger.warning(f"Error during session cleanup: {e}")


@contextmanager
def db_session_scope() -> Generator[None, None, None]:
    """
    Context manager for database session scope with automatic cleanup.
    
    Usage:
        with db_session_scope():
            # Database queries here
            users = User.query.all()
            # Session automatically cleaned up
    """
    try:
        yield
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        # Always clean up session
        try:
            db.session.close()
        except Exception as e:
            logger.warning(f"Error during session close: {e}")


def safe_db_commit():
    """
    Safely commit database changes with proper error handling.
    
    Returns:
        bool: True if commit succeeded, False otherwise
    """
    try:
        db.session.commit()
        logger.debug("Database commit successful")
        return True
    except Exception as e:
        logger.error(f"Database commit failed: {e}")
        try:
            db.session.rollback()
            logger.debug("Database rollback successful")
        except Exception as rollback_error:
            logger.error(f"Database rollback also failed: {rollback_error}")
        return False


def safe_db_rollback():
    """
    Safely rollback database changes with proper error handling.
    
    Returns:
        bool: True if rollback succeeded, False otherwise
    """
    try:
        db.session.rollback()
        logger.debug("Database rollback successful")
        return True
    except Exception as e:
        logger.error(f"Database rollback failed: {e}")
        return False


class DatabaseConnectionPool:
    """
    Simple connection pool monitor to track connections.
    """
    
    @staticmethod
    def get_connection_info():
        """Get database connection pool information."""
        try:
            engine = db.engine
            pool = engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as e:
            logger.error(f"Error getting connection info: {e}")
            return {
                'error': str(e),
                'pool_size': 'unknown',
                'checked_in': 'unknown',
                'checked_out': 'unknown',
                'overflow': 'unknown',
                'invalid': 'unknown'
            }
    
    @staticmethod
    def health_check():
        """Perform a basic database health check."""
        try:
            from sqlalchemy import text
            # Simple query to test connection
            result = db.session.execute(text('SELECT 1')).fetchone()
            return {
                'status': 'healthy',
                'connection': 'active',
                'query_result': result[0] if result else None
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'connection': 'failed',
                'error': str(e)
            }
        finally:
            # Always clean up test connection
            try:
                db.session.close()
            except:
                pass