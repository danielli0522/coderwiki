"""
API配额管理工具

用于监控和管理LLM API的配额使用情况，提供配额检查和优化建议。
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class QuotaInfo:
    """配额信息数据类"""
    provider: str
    model: str
    used_tokens: int = 0
    total_tokens: int = 0
    used_requests: int = 0
    total_requests: int = 0
    reset_time: Optional[datetime] = None
    cost_estimate: float = 0.0
    status: str = "unknown"

@dataclass
class QuotaRecommendation:
    """配额优化建议数据类"""
    priority: str  # high, medium, low
    title: str
    description: str
    action: str
    estimated_savings: Optional[float] = None

class APIQuotaManager:
    """API配额管理器"""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.llm_api_key = os.getenv('LLM_API_KEY')

        # 成本估算 (每1000 tokens的美元价格)
        self.cost_estimates = {
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
            'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125}
        }

    def check_openai_usage(self) -> Optional[QuotaInfo]:
        """检查OpenAI API使用情况"""
        if not self.openai_api_key:
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }

            # 获取使用情况
            response = requests.get(
                'https://api.openai.com/v1/usage',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                usage_data = data.get('data', [{}])[0]

                return QuotaInfo(
                    provider='OpenAI',
                    model='gpt-3.5-turbo',  # 默认模型
                    used_tokens=usage_data.get('n_requests', 0),
                    total_tokens=usage_data.get('n_requests', 0),
                    used_requests=usage_data.get('n_requests', 0),
                    status='active'
                )
            else:
                logger.warning(f"无法获取OpenAI使用情况: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"检查OpenAI使用情况时出错: {str(e)}")
            return None

    def check_anthropic_usage(self) -> Optional[QuotaInfo]:
        """检查Anthropic API使用情况"""
        if not self.anthropic_api_key:
            return None

        try:
            headers = {
                'x-api-key': self.anthropic_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            # Anthropic目前没有公开的使用情况API，返回基本信息
            return QuotaInfo(
                provider='Anthropic',
                model='claude-3-sonnet-20240229',
                status='active',
                used_requests=0,  # 无法获取具体数据
                total_requests=0
            )

        except Exception as e:
            logger.error(f"检查Anthropic使用情况时出错: {str(e)}")
            return None

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算API调用成本"""
        if model not in self.cost_estimates:
            return 0.0

        costs = self.cost_estimates[model]
        input_cost = (input_tokens / 1000) * costs['input']
        output_cost = (output_tokens / 1000) * costs['output']

        return input_cost + output_cost

    def get_quota_recommendations(self) -> List[QuotaRecommendation]:
        """获取配额优化建议"""
        recommendations = []

        # 检查API密钥配置
        if not any([self.openai_api_key, self.anthropic_api_key, self.llm_api_key]):
            recommendations.append(QuotaRecommendation(
                priority='high',
                title='配置API密钥',
                description='未检测到任何LLM API密钥配置',
                action='请设置OPENAI_API_KEY、ANTHROPIC_API_KEY或LLM_API_KEY环境变量'
            ))

        # 成本优化建议
        recommendations.append(QuotaRecommendation(
            priority='medium',
            title='使用更经济的模型',
            description='考虑使用gpt-3.5-turbo或claude-3-haiku来降低成本',
            action='在配置中设置LLM_MODEL=gpt-3.5-turbo',
            estimated_savings=0.02  # 每1000 tokens节省约$0.02
        ))

        # 缓存建议
        recommendations.append(QuotaRecommendation(
            priority='medium',
            title='实现响应缓存',
            description='对相同请求的响应进行缓存，避免重复API调用',
            action='在LLMService中实现缓存机制',
            estimated_savings=0.05  # 可节省20-30%的API调用
        ))

        # 批处理建议
        recommendations.append(QuotaRecommendation(
            priority='low',
            title='批量处理请求',
            description='将多个小请求合并为批量请求',
            action='实现请求批处理逻辑',
            estimated_savings=0.01
        ))

        return recommendations

    def get_quota_status_summary(self) -> Dict[str, Any]:
        """获取配额状态摘要"""
        openai_info = self.check_openai_usage()
        anthropic_info = self.check_anthropic_usage()

        recommendations = self.get_quota_recommendations()

        return {
            'timestamp': datetime.now().isoformat(),
            'providers': {
                'openai': asdict(openai_info) if openai_info else None,
                'anthropic': asdict(anthropic_info) if anthropic_info else None
            },
            'recommendations': [asdict(rec) for rec in recommendations],
            'total_recommendations': len(recommendations),
            'high_priority_count': len([r for r in recommendations if r.priority == 'high']),
            'estimated_monthly_savings': sum([r.estimated_savings or 0 for r in recommendations])
        }

    def create_quota_alert(self, threshold_percentage: float = 80.0) -> Optional[Dict[str, Any]]:
        """创建配额告警"""
        openai_info = self.check_openai_usage()

        if openai_info and openai_info.total_tokens > 0:
            usage_percentage = (openai_info.used_tokens / openai_info.total_tokens) * 100

            if usage_percentage >= threshold_percentage:
                return {
                    'alert_type': 'quota_warning',
                    'provider': 'OpenAI',
                    'usage_percentage': usage_percentage,
                    'threshold': threshold_percentage,
                    'message': f'OpenAI API使用量已达到{usage_percentage:.1f}%，建议检查配额设置',
                    'timestamp': datetime.now().isoformat(),
                    'recommendations': [
                        '考虑升级API套餐',
                        '优化请求频率',
                        '实现缓存机制'
                    ]
                }

        return None

def check_api_health() -> Dict[str, Any]:
    """检查API健康状态"""
    manager = APIQuotaManager()

    # 测试API连接
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'openai_status': 'unknown',
        'anthropic_status': 'unknown',
        'recommendations': []
    }

    # 测试OpenAI
    if manager.openai_api_key:
        try:
            headers = {'Authorization': f'Bearer {manager.openai_api_key}'}
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=5
            )
            health_status['openai_status'] = 'healthy' if response.status_code == 200 else 'error'
        except Exception as e:
            health_status['openai_status'] = 'error'
            health_status['recommendations'].append(f'OpenAI连接失败: {str(e)}')

    # 测试Anthropic
    if manager.anthropic_api_key:
        try:
            headers = {
                'x-api-key': manager.anthropic_api_key,
                'anthropic-version': '2023-06-01'
            }
            response = requests.get(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                timeout=5
            )
            # Anthropic在GET请求时返回405是正常的，说明API可用
            health_status['anthropic_status'] = 'healthy' if response.status_code in [200, 405] else 'error'
        except Exception as e:
            health_status['anthropic_status'] = 'error'
            health_status['recommendations'].append(f'Anthropic连接失败: {str(e)}')

    return health_status

def get_quota_optimization_tips() -> List[str]:
    """获取配额优化提示"""
    return [
        "1. 使用更经济的模型（如gpt-3.5-turbo）",
        "2. 实现响应缓存机制",
        "3. 批量处理多个请求",
        "4. 设置合理的max_tokens限制",
        "5. 使用流式响应减少延迟",
        "6. 监控API使用情况",
        "7. 设置使用量告警",
        "8. 考虑使用本地模型作为备选"
    ]

