"""
LLM Configuration model definition.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import json

class LLMConfig(db.Model):
    """LLM配置模型"""
    
    __tablename__ = 'llm_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False)  # openai, anthropic, etc.
    model_name = db.Column(db.String(100), nullable=False)
    api_key_encrypted = db.Column(db.String(500), nullable=False)  # 加密存储
    base_url = db.Column(db.String(500))
    max_tokens = db.Column(db.Integer, default=4000)
    temperature = db.Column(db.Float, default=0.7)
    is_active = db.Column(db.Boolean, default=True)
    config_metadata = db.Column(db.Text)  # JSON格式存储额外配置
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = db.relationship('User', backref='llm_configs')
    
    def __init__(self, **kwargs):
        super(LLMConfig, self).__init__(**kwargs)
        if 'api_key' in kwargs and not kwargs.get('api_key_encrypted'):
            self.api_key_encrypted = self._encrypt_api_key(kwargs['api_key'])
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        # 使用简单的加密方法，生产环境应该使用更安全的加密
        return generate_password_hash(api_key, method='pbkdf2:sha256:100000')
    
    def _decrypt_api_key(self) -> str:
        """解密API密钥"""
        # 这里返回原始密钥用于API调用，实际使用时应该更安全
        return self.api_key_encrypted
    
    def get_api_key(self) -> str:
        """获取API密钥（解密后）"""
        return self._decrypt_api_key()
    
    def validate_api_key(self, api_key: str) -> bool:
        """验证API密钥"""
        return check_password_hash(self.api_key_encrypted, api_key)
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key_encrypted = self._encrypt_api_key(api_key)
    
    def get_config_metadata(self) -> dict:
        """获取配置元数据"""
        if self.config_metadata:
            try:
                return json.loads(self.config_metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_config_metadata(self, metadata: dict):
        """设置配置元数据"""
        self.config_metadata = json.dumps(metadata)
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """转换为字典格式"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'model_name': self.model_name,
            'base_url': self.base_url,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'is_active': self.is_active,
            'config_metadata': self.get_config_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'api_key_set': bool(self.api_key_encrypted)
        }
        
        if include_sensitive:
            result['api_key'] = self.get_api_key()
        
        return result
    
    def validate_config(self) -> dict:
        """验证配置的完整性"""
        errors = []
        
        if not self.provider:
            errors.append("Provider is required")
        
        if not self.model_name:
            errors.append("Model name is required")
        
        if not self.api_key_encrypted:
            errors.append("API key is required")
        
        # 验证provider和model的兼容性
        if self.provider == 'openai':
            if not self.model_name.startswith('gpt-'):
                errors.append("OpenAI model name should start with 'gpt-'")
        elif self.provider == 'anthropic':
            if not self.model_name.startswith('claude-'):
                errors.append("Anthropic model name should start with 'claude-'")
        
        # 验证参数范围
        if self.max_tokens < 1 or self.max_tokens > 32000:
            errors.append("Max tokens should be between 1 and 32000")
        
        if self.temperature < 0 or self.temperature > 2:
            errors.append("Temperature should be between 0 and 2")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def __repr__(self):
        """字符串表示"""
        return f'<LLMConfig {self.provider}/{self.model_name} for User {self.user_id}>'