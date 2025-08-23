"""
Document model definition.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db
import json

class Document(db.Model):
    """Document model for storing generated documentation."""

    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'error', 'draft', 'published', 'archived'), default='pending', nullable=False, index=True)
    file_path = db.Column(db.String(500))
    language = db.Column(db.String(100))
    document_type = db.Column(db.String(100), default='readme')
    format = db.Column(db.String(50), default='markdown')
    generated_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    llm_config_id = db.Column(db.Integer, db.ForeignKey('llm_configs.id'))
    prompt_tokens = db.Column(db.Integer)
    completion_tokens = db.Column(db.Integer)
    total_tokens = db.Column(db.Integer)
    cost_estimate = db.Column(db.Float)
    generation_time = db.Column(db.Float)
    generation_metadata = db.Column(db.Text)

    # 关系
    llm_config = db.relationship('LLMConfig', backref='documents')

    def to_dict(self):
        """Convert document to dictionary for API responses."""
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'version': self.version,
            'status': self.status,
            'file_path': self.file_path,
            'language': self.language,
            'document_type': self.document_type,
            'format': self.format,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'llm_config_id': self.llm_config_id,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'cost_estimate': self.cost_estimate,
            'generation_time': self.generation_time,
            'generation_metadata': self.get_generation_metadata()
        }

    def get_generation_metadata(self) -> dict:
        """获取生成元数据"""
        if self.generation_metadata:
            try:
                return json.loads(self.generation_metadata)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_generation_metadata(self, metadata: dict):
        """设置生成元数据"""
        self.generation_metadata = json.dumps(metadata)

    def __repr__(self):
        """String representation of document."""
        return f'<Document {self.title} v{self.version}>'
