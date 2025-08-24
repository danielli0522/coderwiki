"""
LLM Service for managing LLM configurations and operations.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app import db
from app.models.llm_config import LLMConfig
from app.models.user import User
from app.utils.llm_client import LLMClientFactory, LLMClient

logger = logging.getLogger(__name__)

class LLMService:
    """LLM服务类，管理LLM配置和操作"""

    def __init__(self):
        self.client_factory = LLMClientFactory()

    def create_config(self, user_id: int, provider: str, model_name: str, api_key: str,
                     base_url: str = None, max_tokens: int = 4000, temperature: float = 0.7,
                     config_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建LLM配置"""
        try:
            # 验证provider支持
            if provider not in self.client_factory.get_available_providers():
                return {
                    'success': False,
                    'error': f'Unsupported provider: {provider}',
                    'error_type': 'unsupported_provider'
                }

            # 创建配置对象
            config = LLMConfig(
                user_id=user_id,
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                base_url=base_url,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # 设置额外的配置元数据
            if config_metadata:
                config.set_config_metadata(config_metadata)

            # 验证配置
            validation = config.validate_config()
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Configuration validation failed',
                    'validation_errors': validation['errors']
                }

            # 保存配置
            db.session.add(config)
            db.session.commit()

            logger.info(f"Created LLM config {config.id} for user {user_id}")

            return {
                'success': True,
                'config_id': config.id,
                'config': config.to_dict()
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating LLM config: {str(e)}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }

    def get_user_configs(self, user_id: int, include_inactive: bool = False) -> List[LLMConfig]:
        """获取用户的LLM配置列表"""
        query = LLMConfig.query.filter_by(user_id=user_id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.order_by(LLMConfig.created_at.desc()).all()

    def get_config_by_id(self, config_id: int, user_id: int) -> Optional[LLMConfig]:
        """根据ID获取配置"""
        return LLMConfig.query.filter_by(id=config_id, user_id=user_id).first()

    def update_config(self, config_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """更新LLM配置"""
        try:
            config = self.get_config_by_id(config_id, user_id)
            if not config:
                return {
                    'success': False,
                    'error': 'Configuration not found',
                    'error_type': 'not_found'
                }

            # 更新字段
            update_fields = ['model_name', 'base_url', 'max_tokens', 'temperature', 'is_active']

            for field in update_fields:
                if field in kwargs:
                    setattr(config, field, kwargs[field])

            # 特殊处理API密钥
            if 'api_key' in kwargs and kwargs['api_key']:
                config.set_api_key(kwargs['api_key'])

            # 更新配置元数据
            if 'config_metadata' in kwargs:
                config.set_config_metadata(kwargs['config_metadata'])

            # 验证配置
            validation = config.validate_config()
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Configuration validation failed',
                    'validation_errors': validation['errors']
                }

            # 保存更新
            config.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"Updated LLM config {config_id} for user {user_id}")

            return {
                'success': True,
                'config': config.to_dict()
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating LLM config: {str(e)}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }

    def delete_config(self, config_id: int, user_id: int) -> Dict[str, Any]:
        """删除LLM配置"""
        try:
            config = self.get_config_by_id(config_id, user_id)
            if not config:
                return {
                    'success': False,
                    'error': 'Configuration not found',
                    'error_type': 'not_found'
                }

            # 检查是否有关联的文档
            if config.documents:
                return {
                    'success': False,
                    'error': 'Cannot delete configuration with associated documents',
                    'error_type': 'has_dependencies'
                }

            # 删除配置
            db.session.delete(config)
            db.session.commit()

            logger.info(f"Deleted LLM config {config_id} for user {user_id}")

            return {
                'success': True,
                'message': 'Configuration deleted successfully'
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting LLM config: {str(e)}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }

    def set_active_config(self, config_id: int, user_id: int) -> Dict[str, Any]:
        """设置活跃配置"""
        try:
            config = self.get_config_by_id(config_id, user_id)
            if not config:
                return {
                    'success': False,
                    'error': 'Configuration not found',
                    'error_type': 'not_found'
                }

            # 停用用户的其他配置
            LLMConfig.query.filter_by(user_id=user_id).update({'is_active': False})

            # 激活指定配置
            config.is_active = True
            config.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"Set LLM config {config_id} as active for user {user_id}")

            return {
                'success': True,
                'config': config.to_dict()
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error setting active config: {str(e)}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }

    def get_active_config(self, user_id: int) -> Optional[LLMConfig]:
        """获取用户的活跃配置"""
        return LLMConfig.query.filter_by(user_id=user_id, is_active=True).first()

    def test_config(self, config_id: int, user_id: int) -> Dict[str, Any]:
        """测试LLM配置"""
        try:
            config = self.get_config_by_id(config_id, user_id)
            if not config:
                return {
                    'success': False,
                    'error': 'Configuration not found',
                    'error_type': 'not_found'
                }

            # 创建LLM客户端
            client = self.client_factory.create_client(
                provider=config.provider,
                api_key=config.get_api_key(),
                model=config.model_name,
                base_url=config.base_url
            )

            # 发送测试消息
            test_prompt = "Hello, this is a test message."
            response = client.chat(test_prompt, max_tokens=10)

            if response:
                return {
                    'success': True,
                    'message': 'Configuration test successful',
                    'response': response[:100] + '...' if len(response) > 100 else response
                }
            else:
                return {
                    'success': False,
                    'error': 'Test failed - no response from LLM',
                    'error_type': 'test_failed'
                }

        except Exception as e:
            logger.error(f"Error testing LLM config: {str(e)}")
            return {
                'success': False,
                'error': f'Test error: {str(e)}'
            }

    def get_config_stats(self, user_id: int) -> Dict[str, Any]:
        """获取配置统计信息"""
        try:
            configs = self.get_user_configs(user_id, include_inactive=True)

            stats = {
                'total_configs': len(configs),
                'active_configs': len([c for c in configs if c.is_active]),
                'providers': {},
                'models': {}
            }

            for config in configs:
                # 统计提供商
                provider = config.provider
                stats['providers'][provider] = stats['providers'].get(provider, 0) + 1

                # 统计模型
                model = config.model_name
                stats['models'][model] = stats['models'].get(model, 0) + 1

            return {
                'success': True,
                'stats': stats
            }

        except Exception as e:
            logger.error(f"Error getting config stats: {str(e)}")
            return {
                'success': False,
                'error': f'Stats error: {str(e)}'
            }

    def get_llm_client_for_user(self, user_id: int) -> Optional[LLMClient]:
        """为用户获取LLM客户端"""
        config = self.get_active_config(user_id)
        if not config:
            return None

        return self.client_factory.create_client(
            provider=config.provider,
            api_key=config.get_api_key(),
            model=config.model_name,
            base_url=config.base_url
        )

    def generate_documentation(self, repository_name: str, code_structure: Dict[str, Any]) -> str:
        """生成代码文档

        Args:
            repository_name: 仓库名称
            code_structure: 代码结构信息

        Returns:
            str: 生成的文档内容
        """
        try:
            # 构建文档生成提示
            prompt = f"""
请为代码仓库 '{repository_name}' 生成详细的技术文档。

代码结构信息：
- 仓库名称: {code_structure.get('repository_name', 'Unknown')}
- 仓库URL: {code_structure.get('url', 'Unknown')}
- 本地路径: {code_structure.get('local_path', 'Unknown')}

请生成包含以下内容的文档：
1. 项目概述
2. 技术架构
3. 核心功能
4. 部署说明
5. API文档（如果有）
6. 开发指南

请使用Markdown格式，确保文档结构清晰、内容详实。
"""

            # 获取默认用户（user_id=1）的LLM客户端
            client = self.get_llm_client_for_user(1)

            if not client:
                # 如果没有配置LLM，返回默认文档
                return self._generate_default_documentation(repository_name, code_structure)

            # 使用LLM生成文档
            response = client.chat(prompt, max_tokens=2000)

            if response:
                return response
            else:
                return self._generate_default_documentation(repository_name, code_structure)

        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            return self._generate_default_documentation(repository_name, code_structure)

    def _generate_default_documentation(self, repository_name: str, code_structure: Dict[str, Any]) -> str:
        """生成默认文档（当LLM不可用时）"""
        return f"""# {repository_name} 技术文档

## 项目概述

这是 {repository_name} 项目的技术文档。

## 技术架构

- 项目类型: 代码仓库
- 仓库地址: {code_structure.get('url', 'Unknown')}
- 本地路径: {code_structure.get('local_path', 'Unknown')}

## 核心功能

待补充...

## 部署说明

待补充...

## API文档

待补充...

## 开发指南

待补充...

---
*此文档由 CoderWiki 自动生成*
"""
