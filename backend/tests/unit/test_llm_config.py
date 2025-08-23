"""
Unit tests for LLM configuration model.
"""

import pytest
import json
from datetime import datetime
from app import create_app, db
from config import TestingConfig
from app.models.llm_config import LLMConfig
from app.models.user import User

class TestLLMConfig:
    """LLM配置模型测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试用户
        self.user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(self.user)
        db.session.commit()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_llm_config(self):
        """测试创建LLM配置"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-api-key'
        )
        
        db.session.add(config)
        db.session.commit()
        
        assert config.id is not None
        assert config.user_id == self.user.id
        assert config.provider == 'openai'
        assert config.model_name == 'gpt-3.5-turbo'
        assert config.is_active is True
        assert config.api_key_encrypted is not None
    
    def test_api_key_encryption(self):
        """测试API密钥加密"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='secret-api-key-123'
        )
        
        db.session.add(config)
        db.session.commit()
        
        # 验证密钥已加密
        assert config.api_key_encrypted != 'secret-api-key-123'
        assert config.api_key_encrypted.startswith('pbkdf2:sha256:')
        
        # 验证可以正确获取密钥
        retrieved_key = config.get_api_key()
        assert retrieved_key == 'secret-api-key-123'
    
    def test_api_key_validation(self):
        """测试API密钥验证"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-api-key'
        )
        
        db.session.add(config)
        db.session.commit()
        
        # 测试正确密钥
        assert config.validate_api_key('test-api-key') is True
        
        # 测试错误密钥
        assert config.validate_api_key('wrong-key') is False
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        
        validation = valid_config.validate_config()
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        
        # 测试无效配置 - 缺少provider
        invalid_config = LLMConfig(
            user_id=self.user.id,
            provider='',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        
        validation = invalid_config.validate_config()
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        
        # 测试无效配置 - 错误的model_name
        invalid_config2 = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='invalid-model',
            api_key='test-key'
        )
        
        validation = invalid_config2.validate_config()
        assert validation['valid'] is False
        assert any('model name should start with' in error for error in validation['errors'])
    
    def test_config_metadata(self):
        """测试配置元数据"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        
        # 设置元数据
        metadata = {
            'custom_setting': 'value',
            'priority': 1
        }
        config.set_config_metadata(metadata)
        
        db.session.add(config)
        db.session.commit()
        
        # 验证元数据
        retrieved_metadata = config.get_config_metadata()
        assert retrieved_metadata['custom_setting'] == 'value'
        assert retrieved_metadata['priority'] == 1
    
    def test_to_dict(self):
        """测试字典转换"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key',
            max_tokens=2000,
            temperature=0.5
        )
        
        db.session.add(config)
        db.session.commit()
        
        config_dict = config.to_dict()
        
        assert config_dict['id'] == config.id
        assert config_dict['user_id'] == self.user.id
        assert config_dict['provider'] == 'openai'
        assert config_dict['model_name'] == 'gpt-3.5-turbo'
        assert config_dict['max_tokens'] == 2000
        assert config_dict['temperature'] == 0.5
        assert config_dict['is_active'] is True
        assert 'api_key' not in config_dict  # 不应包含敏感信息
        assert config_dict['api_key_set'] is True
    
    def test_set_api_key(self):
        """测试设置API密钥"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='original-key'
        )
        
        db.session.add(config)
        db.session.commit()
        
        # 更新API密钥
        config.set_api_key('new-api-key')
        db.session.commit()
        
        # 验证新密钥
        assert config.get_api_key() == 'new-api-key'
        assert config.validate_api_key('new-api-key') is True
        assert config.validate_api_key('original-key') is False
    
    def test_repr(self):
        """测试字符串表示"""
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        
        db.session.add(config)
        db.session.commit()
        
        repr_str = repr(config)
        assert 'LLMConfig' in repr_str
        assert 'openai' in repr_str
        assert 'gpt-3.5-turbo' in repr_str
        assert str(self.user.id) in repr_str