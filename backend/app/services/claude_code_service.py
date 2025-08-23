"""
Claude Code Service for document generation using Claude Code SDK.
"""

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ClaudeCodeMetrics:
    """Claude Code调用指标数据类"""
    response_time: float = 0.0
    cost_estimate: float = 0.0
    tokens_used: int = 0
    model: str = "claude-code"
    provider: str = "claude-code"

class ClaudeCodeService:
    """Claude Code服务类，用于调用Claude Code SDK和指定的sub agent"""
    
    def __init__(self, bmad_docs_path: str = None):
        """
        初始化Claude Code服务
        
        Args:
            bmad_docs_path: BMAD文档生成器路径
        """
        # BMAD文档生成器路径
        self.bmad_docs_path = bmad_docs_path or "/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/"
        
        # 超时设置
        self.timeout = 600  # 10分钟超时，因为文档生成可能需要较长时间
        self.max_retries = 3
        self.retry_delay = 5
        
        # 验证路径
        self._validate_paths()
    
    def _validate_paths(self):
        """验证必要的路径是否存在"""
        if not os.path.exists(self.bmad_docs_path):
            logger.warning(f"BMAD docs generator not found at: {self.bmad_docs_path}")
            logger.info("Please check the BMAD docs generator path")
    
    async def generate_technical_document(self, 
                                        repository_path: str,
                                        doc_type: str = 'technical_design',
                                        doc_title: str = None,
                                        additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        通过Claude Code SDK生成技术设计文档
        
        Args:
            repository_path: 代码仓库路径
            doc_type: 文档类型 (technical_design, api_docs, architecture, etc.)
            doc_title: 文档标题
            additional_params: 额外参数
            
        Returns:
            包含生成结果的字典
        """
        try:
            start_time = time.time()
            
            # 验证路径
            if not os.path.exists(repository_path):
                return {
                    'success': False,
                    'error': f'Repository path not found: {repository_path}',
                    'error_type': 'path_not_found'
                }
            
            # 准备系统提示词
            system_prompt = self._prepare_system_prompt(doc_type, doc_title, additional_params)
            
            # 准备查询内容
            query_content = self._prepare_query_content(repository_path, doc_type, doc_title)
            
            logger.info(f"Generating document for repository: {repository_path}, type: {doc_type}")
            
            # 使用Claude Code SDK生成文档
            result = await self._execute_claude_code_sdk(system_prompt, query_content)
            
            if result['success']:
                response_time = time.time() - start_time
                
                # 创建指标对象
                metrics = ClaudeCodeMetrics(
                    response_time=response_time,
                    cost_estimate=result.get('cost_estimate', 0.0),
                    tokens_used=result.get('tokens_used', 0),
                    model="claude-code",
                    provider="claude-code"
                )
                
                return {
                    'success': True,
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {}),
                    'metrics': metrics.__dict__,
                    'cost_estimate': metrics.cost_estimate,
                    'generation_time': response_time
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown Claude Code error'),
                    'error_type': result.get('error_type', 'claude_code_error')
                }
                
        except Exception as e:
            logger.error(f"Error in Claude Code document generation: {str(e)}")
            return {
                'success': False,
                'error': f'Claude Code service error: {str(e)}',
                'error_type': 'claude_code_service_error'
            }
    
    def _prepare_system_prompt(self, doc_type: str, doc_title: str, additional_params: Dict[str, Any]) -> str:
        """准备系统提示词"""
        base_prompt = f"""你是一个专业的技术文档生成专家，专门负责生成高质量的{self._get_doc_type_description(doc_type)}。

你的任务是：
1. 分析代码仓库的结构和内容
2. 理解项目的技术架构和设计模式
3. 生成结构清晰、内容详实的技术文档
4. 使用中文编写，保持专业性和可读性
5. 包含代码示例、架构图和最佳实践建议

文档要求：
- 使用Markdown格式
- 包含目录结构
- 提供详细的说明和示例
- 遵循技术文档的最佳实践
- 确保内容的准确性和完整性

BMAD文档生成器路径: {self.bmad_docs_path}
文档类型: {doc_type}
文档标题: {doc_title or f'{doc_type}_documentation'}"""

        # 添加额外参数到系统提示词
        if additional_params:
            if additional_params.get('detailed', False):
                base_prompt += "\n\n要求：生成详细的文档，包含深入的技术分析。"
            if additional_params.get('include_examples', False):
                base_prompt += "\n\n要求：包含丰富的代码示例和用例。"
            if additional_params.get('comprehensive', False):
                base_prompt += "\n\n要求：生成全面的文档，涵盖所有重要方面。"
            if additional_params.get('summary', False):
                base_prompt += "\n\n要求：生成简洁的概览文档，突出重点。"
        
        return base_prompt
    
    def _prepare_query_content(self, repository_path: str, doc_type: str, doc_title: str) -> str:
        """准备查询内容"""
        return f"""请为以下代码仓库生成{self._get_doc_type_description(doc_type)}：

仓库路径: {repository_path}
文档类型: {doc_type}
文档标题: {doc_title or f'{doc_type}_documentation'}

请分析仓库中的代码文件，理解项目结构，并生成相应的技术文档。"""
    
    def _get_doc_type_description(self, doc_type: str) -> str:
        """获取文档类型的中文描述"""
        doc_type_map = {
            'technical_design': '技术设计文档',
            'api_docs': 'API文档',
            'architecture': '架构文档',
            'database_design': '数据库设计文档',
            'deployment_guide': '部署指南',
            'user_manual': '用户手册',
            'developer_guide': '开发者指南',
            'system_overview': '系统概览文档'
        }
        return doc_type_map.get(doc_type, '技术文档')

    async def _execute_claude_code_sdk(self, system_prompt: str, query_content: str) -> Dict[str, Any]:
        """使用Claude Code SDK执行文档生成"""
        try:
            # 导入Claude Code SDK
            from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
            
            async with ClaudeSDKClient(
                options=ClaudeCodeOptions(
                    system_prompt=system_prompt,
                    max_turns=3,
                    allowed_tools=["Read", "Grep", "WebSearch"]
                )
            ) as client:
                # 发送查询
                await client.query(query_content)
                
                # 收集响应
                content_parts = []
                cost_estimate = 0.0
                tokens_used = 0
                
                async for message in client.receive_response():
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                content_parts.append(block.text)
                    
                    # 获取成本信息
                    if type(message).__name__ == "ResultMessage":
                        cost_estimate = getattr(message, 'total_cost_usd', 0.0)
                        tokens_used = getattr(message, 'total_tokens', 0)
                
                return {
                    'success': True,
                    'content': ''.join(content_parts),
                    'cost_estimate': cost_estimate,
                    'tokens_used': tokens_used,
                    'metadata': {
                        'system_prompt': system_prompt,
                        'query_content': query_content
                    }
                }
                
        except ImportError:
            logger.error("Claude Code SDK not installed. Please install: pip install claude-code-sdk")
            return {
                'success': False,
                'error': 'Claude Code SDK not installed',
                'error_type': 'sdk_not_installed'
            }
        except Exception as e:
            logger.error(f"Error executing Claude Code SDK: {str(e)}")
            return {
                'success': False,
                'error': f'SDK execution error: {str(e)}',
                'error_type': 'sdk_execution_error'
            }
    
    def check_claude_code_availability(self) -> Dict[str, Any]:
        """检查Claude Code SDK是否可用"""
        try:
            # 尝试导入Claude Code SDK
            from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
            
            return {
                'success': True,
                'available': True,
                'version': 'claude-code-sdk',
                'message': 'Claude Code SDK is available'
            }
                
        except ImportError:
            return {
                'success': False,
                'available': False,
                'error': 'Claude Code SDK not installed. Please install: pip install claude-code-sdk',
                'message': 'Please install Claude Code SDK'
            }
        except Exception as e:
            return {
                'success': False,
                'available': False,
                'error': f'Error checking Claude Code SDK: {str(e)}',
                'message': 'Error checking SDK availability'
            }
    
    def check_bmad_docs_generator(self) -> Dict[str, Any]:
        """检查BMAD文档生成器是否可用"""
        try:
            if not os.path.exists(self.bmad_docs_path):
                return {
                    'success': False,
                    'available': False,
                    'error': f'BMAD docs generator not found at: {self.bmad_docs_path}',
                    'bmad_docs_path': self.bmad_docs_path
                }
            
            # 检查关键文件是否存在
            key_files = ['package.json', 'README.md', 'src/']
            missing_files = []
            
            for file_name in key_files:
                file_path = os.path.join(self.bmad_docs_path, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)
            
            if missing_files:
                return {
                    'success': False,
                    'available': False,
                    'error': f'Missing key files in BMAD docs generator: {missing_files}',
                    'bmad_docs_path': self.bmad_docs_path,
                    'missing_files': missing_files
                }
            
            return {
                'success': True,
                'available': True,
                'bmad_docs_path': self.bmad_docs_path,
                'key_files': key_files
            }
            
        except Exception as e:
            return {
                'success': False,
                'available': False,
                'error': f'Error checking BMAD docs generator: {str(e)}',
                'bmad_docs_path': self.bmad_docs_path
            }
    
    def get_supported_doc_types(self) -> Dict[str, Any]:
        """获取支持的文档类型"""
        # 这里可以根据BMAD文档生成器的实际支持情况返回
        return {
            'success': True,
            'doc_types': [
                'technical_design',
                'api_docs',
                'architecture',
                'database_design',
                'deployment_guide',
                'user_manual',
                'developer_guide',
                'system_overview'
            ],
            'source': 'claude_code_bmad'
        }
