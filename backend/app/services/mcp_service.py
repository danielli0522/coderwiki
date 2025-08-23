"""
MCP (Model Context Protocol) Service for document generation.
"""

import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app import db
from app.models.llm_config import LLMConfig

logger = logging.getLogger(__name__)

@dataclass
class MCPMetrics:
    """MCP调用指标数据类"""
    response_time: float = 0.0
    cost_estimate: float = 0.0
    tokens_used: int = 0
    model: str = ""
    provider: str = "mcp"

class MCPService:
    """MCP服务类，用于与doc-generator-tool的MCP服务通信"""

    def __init__(self, mcp_server_url: str = None, mcp_server_port: int = None):
        """
        初始化MCP服务

        Args:
            mcp_server_url: MCP服务器URL，默认为localhost
            mcp_server_port: MCP服务器端口，默认为3000
        """
        self.mcp_server_url = mcp_server_url or "http://localhost"
        self.mcp_server_port = mcp_server_port or 3000
        self.base_url = f"{self.mcp_server_url}:{self.mcp_server_port}"
        self.timeout = 300  # 5分钟超时，因为文档生成可能需要较长时间
        self.max_retries = 3
        self.retry_delay = 2

    def generate_document(self,
                         repository_path: str,
                         doc_type: str = 'overview',
                         doc_title: str = None,
                         llm_config: LLMConfig = None,
                         additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        通过MCP服务生成文档

        Args:
            repository_path: 代码仓库路径
            doc_type: 文档类型 (overview, api, database, architecture, etc.)
            doc_title: 文档标题
            llm_config: LLM配置对象
            additional_params: 额外参数

        Returns:
            包含生成结果的字典
        """
        try:
            start_time = time.time()

            # 构建MCP请求参数
            request_data = {
                "method": "generate_document",
                "params": {
                    "repository_path": repository_path,
                    "doc_type": doc_type,
                    "doc_title": doc_title or f"{doc_type}_documentation",
                    "llm_config": self._format_llm_config(llm_config) if llm_config else None,
                    "additional_params": additional_params or {}
                }
            }

            logger.info(f"Sending MCP request to {self.base_url}/api/mcp")
            logger.debug(f"MCP request data: {json.dumps(request_data, indent=2)}")

            # 发送请求到MCP服务
            response = self._send_mcp_request(request_data)

            if response['success']:
                response_time = time.time() - start_time

                # 创建指标对象
                metrics = MCPMetrics(
                    response_time=response_time,
                    cost_estimate=response.get('cost_estimate', 0.0),
                    tokens_used=response.get('tokens_used', 0),
                    model=response.get('model', 'unknown'),
                    provider='mcp'
                )

                return {
                    'success': True,
                    'content': response.get('content', ''),
                    'metadata': response.get('metadata', {}),
                    'metrics': metrics.__dict__,
                    'cost_estimate': metrics.cost_estimate,
                    'generation_time': response_time
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Unknown MCP error'),
                    'error_type': response.get('error_type', 'mcp_error')
                }

        except Exception as e:
            logger.error(f"Error in MCP document generation: {str(e)}")
            return {
                'success': False,
                'error': f'MCP service error: {str(e)}',
                'error_type': 'mcp_service_error'
            }

    def _send_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送MCP请求"""
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

                response = requests.post(
                    f"{self.base_url}/api/mcp",
                    headers=headers,
                    json=request_data,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"MCP request successful (attempt {attempt + 1})")
                    return result
                else:
                    logger.warning(f"MCP request failed with status {response.status_code} (attempt {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': f'MCP service returned status {response.status_code}',
                            'error_type': 'mcp_http_error'
                        }
                    time.sleep(self.retry_delay)

            except requests.exceptions.Timeout:
                logger.warning(f"MCP request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'error': 'MCP service request timeout',
                        'error_type': 'mcp_timeout'
                    }
                time.sleep(self.retry_delay)

            except requests.exceptions.RequestException as e:
                logger.error(f"MCP request exception (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'error': f'MCP service request failed: {str(e)}',
                        'error_type': 'mcp_request_error'
                    }
                time.sleep(self.retry_delay)

        return {
            'success': False,
            'error': 'MCP service request failed after all retries',
            'error_type': 'mcp_max_retries_exceeded'
        }

    def _format_llm_config(self, llm_config: LLMConfig) -> Dict[str, Any]:
        """格式化LLM配置为MCP服务可接受的格式"""
        if not llm_config:
            return None

        return {
            'provider': llm_config.provider,
            'model_name': llm_config.model_name,
            'api_key': llm_config.get_api_key(),
            'base_url': llm_config.base_url,
            'max_tokens': llm_config.max_tokens,
            'temperature': llm_config.temperature,
            'timeout': llm_config.timeout
        }

    def check_mcp_service_health(self) -> Dict[str, Any]:
        """检查MCP服务健康状态"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=10
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'status': 'healthy',
                    'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
            else:
                return {
                    'success': False,
                    'status': 'unhealthy',
                    'error': f'Health check returned status {response.status_code}'
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status': 'unreachable',
                'error': f'Health check failed: {str(e)}'
            }

    def get_mcp_service_info(self) -> Dict[str, Any]:
        """获取MCP服务信息"""
        try:
            response = requests.get(
                f"{self.base_url}/info",
                timeout=10
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'info': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
            else:
                return {
                    'success': False,
                    'error': f'Info request returned status {response.status_code}'
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Info request failed: {str(e)}'
            }

    def list_available_doc_types(self) -> Dict[str, Any]:
        """获取可用的文档类型列表"""
        try:
            response = requests.get(
                f"{self.base_url}/api/doc-types",
                timeout=10
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'doc_types': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
            else:
                return {
                    'success': False,
                    'error': f'Doc types request returned status {response.status_code}'
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Doc types request failed: {str(e)}'
            }
