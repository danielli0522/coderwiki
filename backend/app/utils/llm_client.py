import os
import json
import requests
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMMessage:
    """LLM消息数据类"""
    role: str
    content: str

@dataclass
class LLMMetrics:
    """LLM调用指标数据类"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_estimate: float = 0.0
    response_time: float = 0.0
    model: str = ""
    provider: str = ""

class LLMClient:
    """LLM客户端抽象类"""

    # 模型定价配置 (每1000 tokens的价格，单位：美元)
    PRICING = {
        'openai': {
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'gpt-3.5-turbo-16k': {'input': 0.003, 'output': 0.004},
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-32k': {'input': 0.06, 'output': 0.12},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-4-turbo-2024-04-09': {'input': 0.01, 'output': 0.03},
        },
        'anthropic': {
            'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
            'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
            'claude-2.1': {'input': 0.008, 'output': 0.024},
            'claude-2.0': {'input': 0.008, 'output': 0.024},
        }
    }

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv('LLM_API_KEY')
        self.base_url = base_url or os.getenv('LLM_BASE_URL')
        self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # 成本监控
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.call_count = 0

    def send_message(self, messages: List[LLMMessage], **kwargs) -> Dict[str, Any]:
        """发送消息到LLM"""
        raise NotImplementedError("子类必须实现此方法")

    def _handle_api_error(self, response: requests.Response) -> Dict[str, Any]:
        """处理API错误响应"""
        try:
            error_data = response.json()
        except json.JSONDecodeError:
            error_data = {"error": {"message": response.text}}

        error_message = "未知错误"
        error_type = "unknown"

        # 提取错误信息
        if isinstance(error_data, dict):
            if "error" in error_data:
                error_info = error_data["error"]
                if isinstance(error_info, dict):
                    error_message = error_info.get("message", "未知错误")
                    error_type = error_info.get("type", "unknown")
                else:
                    error_message = str(error_info)
            else:
                error_message = str(error_data)

        # 根据状态码和错误类型进行分类
        if response.status_code == 429:
            if "insufficient balance" in error_message.lower() or "1113" in str(error_type):
                return {
                    'success': False,
                    'error': f"API配额不足: {error_message}",
                    'error_type': 'quota_exceeded',
                    'status_code': 429,
                    'suggestion': '请检查API账户余额或升级套餐'
                }
            else:
                return {
                    'success': False,
                    'error': f"请求频率过高: {error_message}",
                    'error_type': 'rate_limited',
                    'status_code': 429,
                    'suggestion': '请稍后重试或减少请求频率'
                }
        elif response.status_code == 401:
            return {
                'success': False,
                'error': f"API密钥无效: {error_message}",
                'error_type': 'authentication_error',
                'status_code': 401,
                'suggestion': '请检查API密钥配置'
            }
        elif response.status_code == 403:
            return {
                'success': False,
                'error': f"访问被拒绝: {error_message}",
                'error_type': 'permission_denied',
                'status_code': 403,
                'suggestion': '请检查API权限设置'
            }
        else:
            return {
                'success': False,
                'error': f"API请求失败 ({response.status_code}): {error_message}",
                'error_type': 'api_error',
                'status_code': response.status_code,
                'suggestion': '请检查网络连接和API服务状态'
            }

    def _retry_request(self, request_func, *args, **kwargs) -> Dict[str, Any]:
        """重试请求机制"""
        for attempt in range(self.max_retries):
            try:
                response = request_func(*args, **kwargs)

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # 对于429错误，等待更长时间
                    wait_time = (attempt + 1) * self.retry_delay * 2
                    logger.warning(f"遇到频率限制，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    # 其他错误不重试
                    return response

            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(self.retry_delay)

        return None

    def chat(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """简单的聊天接口"""
        messages = []

        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))

        messages.append(LLMMessage(role="user", content=prompt))

        response = self.send_message(messages, **kwargs)
        return response.get('content', '')

    def calculate_cost(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算API调用成本"""
        try:
            if provider not in self.PRICING:
                logger.warning(f"Unknown provider: {provider}")
                return 0.0
            
            if model not in self.PRICING[provider]:
                logger.warning(f"Unknown model for {provider}: {model}")
                return 0.0
            
            pricing = self.PRICING[provider][model]
            input_cost = (prompt_tokens / 1000) * pricing['input']
            output_cost = (completion_tokens / 1000) * pricing['output']
            
            return round(input_cost + output_cost, 6)
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return 0.0
    
    def update_metrics(self, metrics: LLMMetrics):
        """更新调用指标"""
        self.total_tokens_used += metrics.total_tokens
        self.total_cost += metrics.cost_estimate
        self.call_count += 1
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        avg_cost_per_call = self.total_cost / self.call_count if self.call_count > 0 else 0
        avg_tokens_per_call = self.total_tokens_used / self.call_count if self.call_count > 0 else 0
        
        return {
            'total_tokens_used': self.total_tokens_used,
            'total_cost': self.total_cost,
            'call_count': self.call_count,
            'avg_cost_per_call': avg_cost_per_call,
            'avg_tokens_per_call': avg_tokens_per_call,
            'model': self.model
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'model': self.model,
            'base_url': self.base_url,
            'api_key_set': bool(self.api_key),
            'usage_stats': self.get_usage_stats()
        }

class OpenAIClient(LLMClient):
    """OpenAI API客户端"""

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(api_key)
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.base_url = self.base_url or "https://api.openai.com/v1"

    def send_message(self, messages: List[LLMMessage], **kwargs) -> Dict[str, Any]:
        """发送消息到OpenAI API"""
        import time
        
        if not self.api_key:
            return {
                'success': False,
                'error': 'OpenAI API密钥未配置',
                'error_type': 'configuration_error',
                'suggestion': '请设置OPENAI_API_KEY环境变量'
            }

        try:
            start_time = time.time()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': kwargs.get('model', self.model),
                'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 1000)
            }

            def make_request():
                return requests.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=30
                )

            response = self._retry_request(make_request)

            if response is None:
                return {
                    'success': False,
                    'error': '请求失败，已达到最大重试次数',
                    'error_type': 'max_retries_exceeded'
                }

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                
                # 提取使用信息
                usage = result.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)
                
                # 计算成本
                cost_estimate = self.calculate_cost('openai', self.model, prompt_tokens, completion_tokens)
                
                # 创建指标对象
                metrics = LLMMetrics(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_estimate=cost_estimate,
                    response_time=response_time,
                    model=self.model,
                    provider='openai'
                )
                
                # 更新使用统计
                self.update_metrics(metrics)
                
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'usage': usage,
                    'model': result.get('model', self.model),
                    'metrics': metrics.__dict__,
                    'cost_estimate': cost_estimate
                }
            else:
                return self._handle_api_error(response)

        except Exception as e:
            logger.error(f"OpenAI API请求异常: {str(e)}")
            return {
                'success': False,
                'error': f"请求异常: {str(e)}",
                'error_type': 'request_exception'
            }

class AnthropicClient(LLMClient):
    """Anthropic Claude客户端"""

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(api_key)
        self.model = model or os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        self.base_url = self.base_url or "https://api.anthropic.com"

    def send_message(self, messages: List[LLMMessage], **kwargs) -> Dict[str, Any]:
        """发送消息到Anthropic API"""
        import time
        
        if not self.api_key:
            return {
                'success': False,
                'error': 'Anthropic API密钥未配置',
                'error_type': 'configuration_error',
                'suggestion': '请设置ANTHROPIC_API_KEY环境变量'
            }

        try:
            start_time = time.time()
            
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            # 构建消息格式
            system_prompt = ""
            user_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    user_messages.append({
                        'role': msg.role,
                        'content': msg.content
                    })

            data = {
                'model': kwargs.get('model', self.model),
                'max_tokens': kwargs.get('max_tokens', 1000),
                'temperature': kwargs.get('temperature', 0.7),
                'messages': user_messages
            }

            if system_prompt:
                data['system'] = system_prompt

            def make_request():
                return requests.post(
                    f'{self.base_url}/v1/messages',
                    headers=headers,
                    json=data,
                    timeout=30
                )

            response = self._retry_request(make_request)

            if response is None:
                return {
                    'success': False,
                    'error': '请求失败，已达到最大重试次数',
                    'error_type': 'max_retries_exceeded'
                }

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                
                # 提取使用信息
                usage = result.get('usage', {})
                prompt_tokens = usage.get('input_tokens', 0)
                completion_tokens = usage.get('output_tokens', 0)
                total_tokens = prompt_tokens + completion_tokens
                
                # 计算成本
                cost_estimate = self.calculate_cost('anthropic', self.model, prompt_tokens, completion_tokens)
                
                # 创建指标对象
                metrics = LLMMetrics(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_estimate=cost_estimate,
                    response_time=response_time,
                    model=self.model,
                    provider='anthropic'
                )
                
                # 更新使用统计
                self.update_metrics(metrics)
                
                return {
                    'success': True,
                    'content': result['content'][0]['text'],
                    'usage': usage,
                    'model': result.get('model', self.model),
                    'metrics': metrics.__dict__,
                    'cost_estimate': cost_estimate
                }
            else:
                return self._handle_api_error(response)

        except Exception as e:
            logger.error(f"Anthropic API请求异常: {str(e)}")
            return {
                'success': False,
                'error': f"请求异常: {str(e)}",
                'error_type': 'request_exception'
            }

class LLMClientFactory:
    """LLM客户端工厂类"""

    @staticmethod
    def create_client(provider: str = 'openai', **kwargs) -> LLMClient:
        """创建LLM客户端"""
        provider = provider.lower()

        if provider == 'openai':
            return OpenAIClient(**kwargs)
        elif provider == 'anthropic':
            return AnthropicClient(**kwargs)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

    @staticmethod
    def get_available_providers() -> List[str]:
        """获取可用的提供商列表"""
        return ['openai', 'anthropic']

class LLMService:
    """LLM服务类"""

    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClientFactory.create_client()

    def generate_code_documentation(self, code: str, language: str = 'python') -> str:
        """生成代码文档"""
        prompt = f"""
        请为以下{language}代码生成详细的文档说明：

        ```{language}
        {code}
        ```

        请包含：
        1. 函数/类的功能说明
        2. 参数说明
        3. 返回值说明
        4. 使用示例
        5. 注意事项
        """

        return self.client.chat(prompt)

    def analyze_code_quality(self, code: str, language: str = 'python') -> str:
        """分析代码质量"""
        prompt = f"""
        请分析以下{language}代码的质量：

        ```{language}
        {code}
        ```

        请从以下方面分析：
        1. 代码结构和组织
        2. 命名规范
        3. 注释和文档
        4. 错误处理
        5. 性能优化建议
        6. 安全性考虑
        """

        return self.client.chat(prompt)

    def generate_test_cases(self, code: str, language: str = 'python') -> str:
        """生成测试用例"""
        prompt = f"""
        请为以下{language}代码生成完整的测试用例：

        ```{language}
        {code}
        ```

        请包含：
        1. 单元测试
        2. 边界条件测试
        3. 异常情况测试
        4. 集成测试建议
        """

        return self.client.chat(prompt)

    def refactor_code(self, code: str, requirements: str = '', language: str = 'python') -> str:
        """重构代码"""
        prompt = f"""
        请重构以下{language}代码：

        ```{language}
        {code}
        ```

        重构要求：{requirements}

        请提供重构后的代码，并说明重构的改进点。
        """

        return self.client.chat(prompt)
