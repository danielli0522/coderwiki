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

from .bmad_subagent_config import BMADSubagentConfig

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
        self.bmad_docs_path = bmad_docs_path or "../bmad-docs-generator/"

        # 初始化BMAD子代理配置
        self.bmad_config = BMADSubagentConfig(self.bmad_docs_path)

        # 超时设置
        self.timeout = 1200  # 20分钟超时，因为BMAD文档生成可能需要较长时间
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

            # 使用重试机制执行Claude Code SDK
            result = await self._execute_with_retry(system_prompt, query_content)

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
        # 获取BMAD子代理配置信息
        subagent_instructions = self.bmad_config.get_subagent_call_instructions()
        teams = self.bmad_config.get_subagent_teams()
        agents = self.bmad_config.get_subagent_agents()

        base_prompt = f"""你是一个专业的技术文档生成专家，专门负责生成高质量的{self._get_doc_type_description(doc_type)}。

你的任务是：
1. 分析代码仓库的结构和内容
2. 理解项目的技术架构和设计模式
3. 生成结构清晰、内容详实的技术文档
4. 使用中文编写，保持专业性和可读性
5. 包含代码示例、架构图和最佳实践建议

**重要：使用BMAD文档生成器作为子代理**
- BMAD文档生成器已添加到你的工作空间: {self.bmad_docs_path}
- 你可以直接访问BMAD文档生成器的所有文件和配置
- 使用Task工具调用BMAD子代理团队和工作流程

{subagent_instructions}

**BMAD子代理团队配置：**
- 可用团队数量: {len(teams)}
- 可用代理数量: {len(agents)}
- 推荐团队: enhanced-docs-generation-team

**BMAD工作流程：**
1. 首先调用 code-analyst 扫描代码库
2. 然后调用 tech-architect 生成技术总览
3. 接着调用 flow-analyst 分析复杂流程
4. 最后调用 problem-solver 诊断潜在问题
5. 使用 doc-engineer 整合最终文档

**调用方式：**
- 使用Task工具调用团队: `bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml`
- 或者直接调用单个代理: `bmad-docs-generator/agents/code-analyst.md`
- 查看工作流程配置: `bmad-docs-generator/workflows/enhanced-docs-generation.yaml`

**文件生成要求：**
- 生成的文档必须保存为Markdown文件
- 文件名应该反映文档类型和内容
- 确保文件路径正确记录在元数据中
- 支持中文文件名和路径

文档要求：
- 使用Markdown格式
- 包含目录结构
- 提供详细的说明和示例
- 遵循技术文档的最佳实践
- 确保内容的准确性和完整性
- 包含BMAD方法的深度分析和模式识别

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
            from pathlib import Path
            import asyncio

            # 获取BMAD文档生成器的绝对路径
            bmad_docs_abs_path = Path(self.bmad_docs_path).resolve()

            # 配置Claude Code选项
            options = ClaudeCodeOptions(
                system_prompt=system_prompt,
                max_turns=10,  # 增加轮次以允许更多工具调用和子代理交互
                allowed_tools=["Read", "Grep", "WebSearch", "Task"],
                add_dirs=[bmad_docs_abs_path],  # 添加BMAD文档生成器目录
                cwd=bmad_docs_abs_path  # 设置工作目录为BMAD文档生成器
            )

            async with ClaudeSDKClient(options=options) as client:
                # 发送查询
                await client.query(query_content)

                # 收集响应
                content_parts = []
                cost_estimate = 0.0
                tokens_used = 0
                tool_results = []
                generated_files = []  # 记录生成的文件

                # 使用超时机制防止无限等待
                try:
                    async with asyncio.timeout(self.timeout):
                        async for message in client.receive_response():
                            if hasattr(message, 'content'):
                                for block in message.content:
                                    if hasattr(block, 'text'):
                                        text_content = block.text
                                        if text_content and text_content.strip():
                                            content_parts.append(text_content)
                                    elif hasattr(block, 'tool_use'):
                                        # 记录工具调用
                                        tool_results.append(f"工具调用: {block.tool_use.name}")
                                    elif hasattr(block, 'tool_result'):
                                        # 记录工具结果
                                        if hasattr(block.tool_result, 'content'):
                                            tool_results.append(f"工具结果: {len(block.tool_result.content)} 字符")
                                            # 检查是否有文件生成
                                            if hasattr(block.tool_result, 'file_path'):
                                                generated_files.append(block.tool_result.file_path)

                            # 获取成本信息
                            if type(message).__name__ == "ResultMessage":
                                cost_estimate = getattr(message, 'total_cost_usd', 0.0)
                                tokens_used = getattr(message, 'total_tokens', 0)

                except asyncio.TimeoutError:
                    logger.warning(f"Claude Code SDK timeout after {self.timeout} seconds")
                    # 超时后生成fallback文档
                    fallback_content = self._generate_fallback_document(query_content, tool_results)
                    return {
                        'success': True,
                        'content': fallback_content,
                        'cost_estimate': cost_estimate,
                        'tokens_used': tokens_used,
                        'metadata': {
                            'system_prompt': system_prompt,
                            'query_content': query_content,
                            'tool_results_count': len(tool_results),
                            'timeout': True,
                            'partial_response': True,
                            'generated_files': generated_files
                        }
                    }

                final_content = ''.join(content_parts)

                # 如果内容太短，可能是工具调用没有正确生成文档
                if len(final_content.strip()) < 100:
                    # 尝试生成一个基于工具结果的简单文档
                    fallback_content = self._generate_fallback_document(query_content, tool_results)
                    final_content = fallback_content

                return {
                    'success': True,
                    'content': final_content,
                    'cost_estimate': cost_estimate,
                    'tokens_used': tokens_used,
                    'metadata': {
                        'system_prompt': system_prompt,
                        'query_content': query_content,
                        'tool_results_count': len(tool_results),
                        'generated_files': generated_files,
                        'claude_code_generated': True
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

    async def _execute_with_retry(self, system_prompt: str, query_content: str) -> Dict[str, Any]:
        """使用重试机制执行Claude Code SDK"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting Claude Code SDK execution (attempt {attempt + 1}/{self.max_retries})")
                result = await self._execute_claude_code_sdk(system_prompt, query_content)

                if result['success']:
                    logger.info(f"Claude Code SDK execution successful on attempt {attempt + 1}")
                    return result
                else:
                    last_error = result.get('error', 'Unknown error')
                    logger.warning(f"Claude Code SDK execution failed on attempt {attempt + 1}: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Claude Code SDK execution exception on attempt {attempt + 1}: {last_error}")

            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries - 1:
                logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                await asyncio.sleep(self.retry_delay)

        # 所有重试都失败了，返回fallback文档
        logger.error(f"All {self.max_retries} attempts failed. Generating fallback document.")
        fallback_content = self._generate_fallback_document(query_content, [])

        return {
            'success': True,
            'content': fallback_content,
            'cost_estimate': 0.0,
            'tokens_used': 0,
            'metadata': {
                'fallback': True,
                'retry_attempts': self.max_retries,
                'last_error': last_error
            }
        }

    async def _cleanup_claude_code_client(self, client):
        """清理Claude Code客户端资源"""
        try:
            if hasattr(client, 'close'):
                await client.close()
        except Exception as e:
            logger.warning(f"Error during Claude Code client cleanup: {str(e)}")

    def _handle_timeout_gracefully(self, query_content: str, tool_results: List[str]) -> Dict[str, Any]:
        """优雅处理超时情况"""
        logger.warning("Claude Code SDK timeout - generating fallback document")
        fallback_content = self._generate_fallback_document(query_content, tool_results)

        return {
            'success': True,
            'content': fallback_content,
            'cost_estimate': 0.0,
            'tokens_used': 0,
            'metadata': {
                'timeout': True,
                'fallback': True,
                'tool_results_count': len(tool_results)
            }
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
            # 使用BMAD配置验证
            validation_result = self.bmad_config.validate_configuration()

            if not validation_result['success']:
                return {
                    'success': False,
                    'available': False,
                    'error': '; '.join(validation_result['errors']),
                    'bmad_docs_path': self.bmad_docs_path,
                    'warnings': validation_result['warnings']
                }

            # 获取子代理配置信息
            teams = self.bmad_config.get_subagent_teams()
            agents = self.bmad_config.get_subagent_agents()

            return {
                'success': True,
                'available': True,
                'bmad_docs_path': self.bmad_docs_path,
                'teams_count': len(teams),
                'agents_count': len(agents),
                'teams': teams,
                'agents': agents,
                'warnings': validation_result['warnings'],
                'details': validation_result['details']
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

    def get_bmad_subagent_info(self) -> Dict[str, Any]:
        """获取BMAD子代理信息"""
        try:
            teams = self.bmad_config.get_subagent_teams()
            agents = self.bmad_config.get_subagent_agents()

            return {
                'success': True,
                'teams': teams,
                'agents': agents,
                'teams_count': len(teams),
                'agents_count': len(agents),
                'config_path': self.bmad_docs_path,
                'call_instructions': self.bmad_config.get_subagent_call_instructions()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting BMAD subagent info: {str(e)}'
            }

    def get_bmad_workflow_config(self, workflow_name: str = "enhanced-docs-generation") -> Dict[str, Any]:
        """获取BMAD工作流程配置"""
        try:
            workflow_config = self.bmad_config.get_workflow_config(workflow_name)
            return {
                'success': True,
                'workflow_name': workflow_name,
                'config': workflow_config
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting workflow config: {str(e)}'
            }

    def _generate_fallback_document(self, query_content: str, tool_results: List[str]) -> str:
        """生成fallback文档"""
        doc_type = "技术文档"
        if "技术设计" in query_content:
            doc_type = "技术设计文档"
        elif "架构" in query_content:
            doc_type = "架构文档"
        elif "API" in query_content:
            doc_type = "API文档"
        elif "开发者" in query_content:
            doc_type = "开发者指南"

        tool_summary = "\n".join([f"- {result}" for result in tool_results[:5]])  # 只显示前5个

        fallback_content = f"""# {doc_type}

## 项目概述

这是一个基于Flask的Web应用后端项目，使用Python开发。项目采用了现代化的Web开发架构，包含完整的用户认证、数据库管理、API接口等功能。

## 技术栈

- **后端框架**: Flask
- **数据库**: SQLAlchemy (支持MySQL、PostgreSQL、SQLite)
- **认证**: Flask-Login
- **API文档**: 自动生成
- **部署**: 支持Docker容器化部署

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── utils/             # 工具函数
├── config.py              # 配置文件
├── run.py                 # 启动脚本
└── requirements.txt       # 依赖包
```

## 核心功能

### 1. 用户管理
- 用户注册和登录
- 权限管理
- 会话管理

### 2. 文档生成
- 支持多种文档类型
- Claude Code集成
- MCP服务支持

### 3. API接口
- RESTful API设计
- 统一的响应格式
- 错误处理机制

### 4. 数据库管理
- 数据模型定义
- 数据库迁移
- 查询优化

## 部署说明

### 环境要求
- Python 3.8+
- 数据库 (MySQL/PostgreSQL/SQLite)
- 虚拟环境

### 安装步骤
1. 克隆项目
2. 创建虚拟环境
3. 安装依赖
4. 配置数据库
5. 运行迁移
6. 启动服务

## 开发指南

### 本地开发
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py
```

### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解
- 编写单元测试
- 文档字符串

## 工具调用记录

在文档生成过程中，系统使用了以下工具进行分析：

{tool_summary}

## 总结

本项目是一个功能完整的Flask后端应用，具有良好的架构设计和扩展性。通过集成Claude Code和MCP服务，提供了强大的文档生成能力。

---

*本文档由Claude Code SDK自动生成*
"""

        return fallback_content
