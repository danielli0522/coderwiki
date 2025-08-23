"""
Unit tests for LLM service.
"""

import pytest
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.llm_config import LLMConfig
from app.models.user import User
from app.services.llm_service import LLMService

class TestLLMService:
    """LLM服务测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app('testing')
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
        
        self.llm_service = LLMService()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_config_success(self):
        """测试成功创建配置"""
        result = self.llm_service.create_config(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-api-key',
            max_tokens=2000,
            temperature=0.5
        )
        
        assert result['success'] is True
        assert 'config_id' in result
        assert 'config' in result
        assert result['config']['provider'] == 'openai'
        assert result['config']['model_name'] == 'gpt-3.5-turbo'
        
        # 验证数据库中存在记录
        config = LLMConfig.query.filter_by(user_id=self.user.id).first()
        assert config is not None
        assert config.provider == 'openai'
    
    def test_create_config_unsupported_provider(self):
        """测试创建不支持的提供商配置"""
        result = self.llm_service.create_config(
            user_id=self.user.id,
            provider='unsupported_provider',
            model_name='test-model',
            api_key='test-key'
        )
        
        assert result['success'] is False
        assert 'unsupported provider' in result['error']
    
    def test_create_config_validation_error(self):
        """测试创建配置验证错误"""
        result = self.llm_service.create_config(
            user_id=self.user.id,
            provider='openai',
            model_name='invalid-model-name',  # 不符合OpenAI模型命名规范
            api_key='test-key'
        )
        
        assert result['success'] is False
        assert 'validation_errors' in result
        assert len(result['validation_errors']) > 0
    
    def test_get_user_configs(self):
        """测试获取用户配置"""
        # 创建测试配置
        config1 = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='key1'
        )
        config2 = LLMConfig(
            user_id=self.user.id,
            provider='anthropic',
            model_name='claude-3-sonnet-20240229',
            api_key='key2',
            is_active=False
        )
        
        db.session.add(config1)
        db.session.add(config2)
        db.session.commit()
        
        # 测试获取活跃配置
        active_configs = self.llm_service.get_user_configs(self.user.id)
        assert len(active_configs) == 1
        assert active_configs[0].provider == 'openai'
        
        # 测试获取所有配置
        all_configs = self.llm_service.get_user_configs(self.user.id, include_inactive=True)
        assert len(all_configs) == 2
    
    def test_get_config_by_id(self):
        """测试根据ID获取配置"""
        # 创建测试配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        db.session.add(config)
        db.session.commit()
        
        # 测试获取存在的配置
        retrieved_config = self.llm_service.get_config_by_id(config.id, self.user.id)
        assert retrieved_config is not None
        assert retrieved_config.id == config.id
        
        # 测试获取不存在的配置
        non_existent = self.llm_service.get_config_by_id(999, self.user.id)
        assert non_existent is None
        
        # 测试获取其他用户的配置
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password_hash='hashed_password'
        )
        db.session.add(other_user)
        db.session.commit()
        
        other_config = self.llm_service.get_config_by_id(config.id, other_user.id)
        assert other_config is None
    
    def test_update_config(self):
        """测试更新配置"""
        # 创建测试配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='original-key'
        )
        db.session.add(config)
        db.session.commit()
        
        # 更新配置
        result = self.llm_service.update_config(
            config_id=config.id,
            user_id=self.user.id,
            model_name='gpt-4',
            max_tokens=4000,
            temperature=0.8
        )
        
        assert result['success'] is True
        assert result['config']['model_name'] == 'gpt-4'
        assert result['config']['max_tokens'] == 4000
        assert result['config']['temperature'] == 0.8
        
        # 验证数据库已更新
        updated_config = LLMConfig.query.get(config.id)
        assert updated_config.model_name == 'gpt-4'
        assert updated_config.max_tokens == 4000
    
    def test_update_config_not_found(self):
        """测试更新不存在的配置"""
        result = self.llm_service.update_config(
            config_id=999,
            user_id=self.user.id,
            model_name='gpt-4'
        )
        
        assert result['success'] is False
        assert 'not_found' in result['error_type']
    
    def test_delete_config(self):
        """测试删除配置"""
        # 创建测试配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        db.session.add(config)
        db.session.commit()
        
        # 删除配置
        result = self.llm_service.delete_config(config.id, self.user.id)
        
        assert result['success'] is True
        assert 'Configuration deleted successfully' in result['message']
        
        # 验证配置已删除
        deleted_config = LLMConfig.query.get(config.id)
        assert deleted_config is None
    
    def test_delete_config_not_found(self):
        """测试删除不存在的配置"""
        result = self.llm_service.delete_config(999, self.user.id)
        
        assert result['success'] is False
        assert 'not_found' in result['error_type']
    
    def test_set_active_config(self):
        """测试设置活跃配置"""
        # 创建多个配置
        config1 = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='key1',
            is_active=True
        )
        config2 = LLMConfig(
            user_id=self.user.id,
            provider='anthropic',
            model_name='claude-3-sonnet-20240229',
            api_key='key2',
            is_active=False
        )
        
        db.session.add(config1)
        db.session.add(config2)
        db.session.commit()
        
        # 设置config2为活跃配置
        result = self.llm_service.set_active_config(config2.id, self.user.id)
        
        assert result['success'] is True
        assert result['config']['id'] == config2.id
        
        # 验证配置状态已更新
        updated_config1 = LLMConfig.query.get(config1.id)
        updated_config2 = LLMConfig.query.get(config2.id)
        
        assert updated_config1.is_active is False
        assert updated_config2.is_active is True
    
    def test_get_active_config(self):
        """测试获取活跃配置"""
        # 创建活跃配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key',
            is_active=True
        )
        db.session.add(config)
        db.session.commit()
        
        # 获取活跃配置
        active_config = self.llm_service.get_active_config(self.user.id)
        assert active_config is not None
        assert active_config.id == config.id
        assert active_config.is_active is True
        
        # 测试无活跃配置的情况
        active_config.is_active = False
        db.session.commit()
        
        no_active = self.llm_service.get_active_config(self.user.id)
        assert no_active is None
    
    @patch('app.services.llm_service.LLMClientFactory')
    def test_test_config_success(self, mock_factory):
        """测试配置测试成功"""
        # 创建测试配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        db.session.add(config)
        db.session.commit()
        
        # Mock LLM客户端
        mock_client = Mock()
        mock_client.chat.return_value = 'Test response from LLM'
        mock_factory.create_client.return_value = mock_client
        
        # 测试配置
        result = self.llm_service.test_config(config.id, self.user.id)
        
        assert result['success'] is True
        assert 'Test response from LLM' in result['response']
        
        # 验证客户端创建参数
        mock_factory.create_client.assert_called_once_with(
            provider='openai',
            api_key='test-key',
            model='gpt-3.5-turbo',
            base_url=None
        )
    
    @patch('app.services.llm_service.LLMClientFactory')
    def test_test_config_failure(self, mock_factory):
        """测试配置测试失败"""
        # 创建测试配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key'
        )
        db.session.add(config)
        db.session.commit()
        
        # Mock LLM客户端返回空响应
        mock_client = Mock()
        mock_client.chat.return_value = ''
        mock_factory.create_client.return_value = mock_client
        
        # 测试配置
        result = self.llm_service.test_config(config.id, self.user.id)
        
        assert result['success'] is False
        assert 'test_failed' in result['error_type']
    
    def test_get_config_stats(self):
        """测试获取配置统计"""
        # 创建多个配置
        config1 = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='key1',
            is_active=True
        )
        config2 = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-4',
            api_key='key2',
            is_active=False
        )
        config3 = LLMConfig(
            user_id=self.user.id,
            provider='anthropic',
            model_name='claude-3-sonnet-20240229',
            api_key='key3',
            is_active=True
        )
        
        db.session.add(config1)
        db.session.add(config2)
        db.session.add(config3)
        db.session.commit()
        
        # 获取统计信息
        result = self.llm_service.get_config_stats(self.user.id)
        
        assert result['success'] is True
        stats = result['stats']
        
        assert stats['total_configs'] == 3
        assert stats['active_configs'] == 2
        assert stats['providers']['openai'] == 2
        assert stats['providers']['anthropic'] == 1
        assert stats['models']['gpt-3.5-turbo'] == 1
        assert stats['models']['gpt-4'] == 1
        assert stats['models']['claude-3-sonnet-20240229'] == 1
    
    @patch('app.services.llm_service.LLMClientFactory')
    def test_get_llm_client_for_user(self, mock_factory):
        """测试为用户获取LLM客户端"""
        # 创建活跃配置
        config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key',
            is_active=True,
            base_url='https://api.example.com'
        )
        db.session.add(config)
        db.session.commit()
        
        # Mock LLM客户端
        mock_client = Mock()
        mock_factory.create_client.return_value = mock_client
        
        # 获取客户端
        client = self.llm_service.get_llm_client_for_user(self.user.id)
        
        assert client is not None
        mock_factory.create_client.assert_called_once_with(
            provider='openai',
            api_key='test-key',
            model='gpt-3.5-turbo',
            base_url='https://api.example.com'
        )
        
        # 测试无活跃配置的情况
        config.is_active = False
        db.session.commit()
        
        no_client = self.llm_service.get_llm_client_for_user(self.user.id)
        assert no_client is None