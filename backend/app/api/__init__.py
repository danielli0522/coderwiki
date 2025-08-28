"""
API blueprints initialization.
"""

from .auth import auth_bp
from .repository import repository_bp
from .document import document_bp
from .task import task_bp
from .analysis import analysis_bp
from .user import user_bp
from .system import system_bp
from .activities import activities_bp
from .llm import llm_bp
from .mkdocs import mkdocs_bp
from .performance import performance_bp
from .smart_document import bp as smart_document_bp

__all__ = [
    'auth_bp',
    'repository_bp',
    'document_bp',
    'task_bp',
    'analysis_bp',
    'user_bp',
    'system_bp',
    'activities_bp',
    'llm_bp',
    'mkdocs_bp',
    'performance_bp',
    'smart_document_bp'
]
