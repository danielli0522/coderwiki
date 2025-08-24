"""
Document generation service for creating technical documentation using LLM.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from app import db
from app.models.document import Document
from app.models.repository import Repository
from app.models.llm_config import LLMConfig
from app.models.task import Task
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.services.task_service import TaskService
from app.services.mcp_service import MCPService
from app.services.claude_code_service import ClaudeCodeService
from app.utils.llm_client import LLMClientFactory, LLMMetrics

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """文档生成器"""

    def __init__(self, use_mcp: bool = None, use_claude_code: bool = None):
        """
        初始化文档生成器

        Args:
            use_mcp: 是否使用MCP服务，如果为None则根据配置自动决定
            use_claude_code: 是否使用Claude Code服务，如果为None则根据配置自动决定
        """

        self.llm_service = LLMService()
        self.prompt_service = PromptService()
        self.task_service = TaskService()

        # 根据配置决定是否使用MCP服务
        if use_mcp is None:
            # 从环境变量或默认值获取MCP配置
            import os
            self.use_mcp = os.environ.get('MCP_ENABLED', 'true').lower() == 'true'
        else:
            self.use_mcp = use_mcp

        if self.use_mcp:
            import os
            self.mcp_service = MCPService(
                mcp_server_url=os.environ.get('MCP_SERVER_URL', 'http://localhost'),
                mcp_server_port=int(os.environ.get('MCP_SERVER_PORT', '3000'))
            )
        else:
            self.mcp_service = None

        # 根据配置决定是否使用Claude Code服务
        if use_claude_code is None:
            # 从环境变量或默认值获取Claude Code配置
            import os
            self.use_claude_code = os.environ.get('CLAUDE_CODE_ENABLED', 'false').lower() == 'true'
        else:
            self.use_claude_code = use_claude_code

        if self.use_claude_code:
            import os
            self.claude_code_service = ClaudeCodeService(
                bmad_docs_path=os.environ.get('BMAD_DOCS_PATH', '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/')
            )
        else:
            self.claude_code_service = None

    def generate_document(self, repository_id: int, user_id: int, llm_config_id: int,
                         doc_type: str = 'overview', doc_title: str = None) -> Dict[str, Any]:
        """生成文档"""
        try:
            # 获取仓库信息
            repository = Repository.query.filter_by(id=repository_id, user_id=user_id).first()
            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found',
                    'error_type': 'not_found'
                }

            # 获取LLM配置
            llm_config = LLMConfig.query.filter_by(id=llm_config_id, user_id=user_id).first()
            if not llm_config:
                return {
                    'success': False,
                    'error': 'LLM configuration not found',
                    'error_type': 'not_found'
                }

            # 创建任务记录
            task = self.task_service.create_task(
                user_id=user_id,
                task_type='document_generation',
                repository_id=repository_id,
                status='pending',
                metadata={
                    'doc_type': doc_type,
                    'llm_config_id': llm_config_id,
                    'doc_title': doc_title or f"{repository.name}_{doc_type}_doc"
                }
            )

            # 异步生成文档
            generation_result = self._generate_document_async(
                repository=repository,
                llm_config=llm_config,
                task=task,
                doc_type=doc_type,
                doc_title=doc_title
            )

            return generation_result

        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            return {
                'success': False,
                'error': f'Generation error: {str(e)}'
            }

    def _generate_document_async(self, repository: Repository, llm_config: LLMConfig,
                               task: Task, doc_type: str, doc_title: str) -> Dict[str, Any]:
        """异步生成文档"""
        try:
            # 更新任务状态
            self.task_service.update_task_status(task.id, 'processing', 'Starting document generation')

            # 步骤1: 分析代码仓库
            self.task_service.update_task_status(task.id, 'processing', 'Analyzing repository structure')
            analysis_results = self._analyze_repository(repository)

            # 步骤2: 生成提示词
            self.task_service.update_task_status(task.id, 'processing', 'Generating prompt template')
            prompt_result = self.prompt_service.create_technical_documentation_prompt(
                analysis_results=analysis_results,
                doc_type=doc_type
            )

            if not prompt_result['success']:
                raise Exception(f"Prompt generation failed: {prompt_result['error']}")

            # 步骤3: 调用文档生成服务
            if self.use_claude_code and self.claude_code_service:
                self.task_service.update_task_status(task.id, 'processing', 'Calling Claude Code service for document generation')
                # 使用asyncio运行异步函数
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                llm_result = loop.run_until_complete(
                    self._call_claude_code_for_documentation(
                        repository=repository,
                        doc_type=doc_type,
                        doc_title=doc_title
                    )
                )
            elif self.use_mcp and self.mcp_service:
                self.task_service.update_task_status(task.id, 'processing', 'Calling MCP service for document generation')
                llm_result = self._call_mcp_for_documentation(
                    repository=repository,
                    llm_config=llm_config,
                    doc_type=doc_type,
                    doc_title=doc_title
                )
            else:
                self.task_service.update_task_status(task.id, 'processing', 'Calling LLM API')
                llm_result = self._call_llm_for_documentation(
                    llm_config=llm_config,
                    prompt=prompt_result['prompt'],
                    doc_type=doc_type
                )

            if not llm_result['success']:
                raise Exception(f"LLM call failed: {llm_result['error']}")

            # 步骤4: 处理和格式化文档
            self.task_service.update_task_status(task.id, 'processing', 'Processing and formatting document')
            processed_document = self._process_generated_document(
                content=llm_result['content'],
                repository=repository,
                doc_type=doc_type,
                metrics=llm_result.get('metrics')
            )

            # 步骤5: 保存文档
            self.task_service.update_task_status(task.id, 'processing', 'Saving document')
            document = self._save_document(
                repository=repository,
                llm_config=llm_config,
                content=processed_document['content'],
                doc_type=doc_type,
                doc_title=doc_title,
                metrics=llm_result.get('metrics'),
                generation_metadata=processed_document.get('metadata', {})
            )

            # 更新任务状态为完成
            self.task_service.update_task_status(
                task.id,
                'completed',
                'Document generation completed successfully',
                result_data={
                    'document_id': document.id,
                    'title': document.title,
                    'doc_type': doc_type,
                    'generation_time': llm_result.get('metrics', {}).get('response_time', 0),
                    'cost_estimate': llm_result.get('cost_estimate', 0)
                }
            )

            return {
                'success': True,
                'document_id': document.id,
                'task_id': task.id,
                'document': document.to_dict(),
                'generation_stats': {
                    'generation_time': llm_result.get('metrics', {}).get('response_time', 0),
                    'cost_estimate': llm_result.get('cost_estimate', 0),
                    'tokens_used': llm_result.get('metrics', {}).get('total_tokens', 0)
                }
            }

        except Exception as e:
            # 更新任务状态为失败
            self.task_service.update_task_status(
                task.id,
                'failed',
                f'Document generation failed: {str(e)}'
            )

            logger.error(f"Document generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.id
            }

    def _analyze_repository(self, repository: Repository) -> Dict[str, Any]:
        """分析代码仓库"""
        try:
            from app.utils.repository_analyzer import RepositoryAnalyzer

            analyzer = RepositoryAnalyzer()
            analysis_result = analyzer.analyze_repository(repository.local_path)

            # 添加仓库基本信息
            analysis_result.update({
                'project_name': repository.name,
                'repository_url': repository.url,
                'analysis_time': datetime.utcnow().isoformat()
            })

            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            # 返回基本分析结果
            return {
                'project_name': repository.name,
                'repository_url': repository.url,
                'tech_stack': 'Unknown',
                'project_type': 'General',
                'language': 'Unknown',
                'file_count': 0,
                'line_count': 0,
                'analysis_time': datetime.utcnow().isoformat(),
                'analysis_error': str(e)
            }

    async def _call_claude_code_for_documentation(self, repository: Repository,
                                                doc_type: str, doc_title: str) -> Dict[str, Any]:
        """通过Claude Code服务生成文档"""
        try:
            # 准备额外参数
            additional_params = {
                'language': 'zh-CN',  # 使用中文
                'format': 'markdown',
                'detailed': True,     # 生成详细文档
                'include_examples': True  # 包含示例
            }

            # 根据文档类型调整参数
            if doc_type in ['api', 'database', 'architecture']:
                additional_params['comprehensive'] = True
            elif doc_type == 'overview':
                additional_params['summary'] = True

            # 调用Claude Code服务
            claude_result = await self.claude_code_service.generate_technical_document(
                repository_path=repository.local_path,
                doc_type=doc_type,
                doc_title=doc_title,
                additional_params=additional_params
            )

            if claude_result['success']:
                return {
                    'success': True,
                    'content': claude_result['content'],
                    'metrics': claude_result.get('metrics'),
                    'cost_estimate': claude_result.get('cost_estimate', 0)
                }
            else:
                return {
                    'success': False,
                    'error': claude_result.get('error', 'Unknown Claude Code error')
                }

        except Exception as e:
            logger.error(f"Error calling Claude Code service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _call_mcp_for_documentation(self, repository: Repository, llm_config: LLMConfig,
                                   doc_type: str, doc_title: str) -> Dict[str, Any]:
        """通过MCP服务生成文档"""
        try:
            # 准备额外参数
            additional_params = {
                'max_tokens': llm_config.max_tokens,
                'temperature': llm_config.temperature,
                'language': 'zh-CN',  # 使用中文
                'format': 'markdown'
            }

            # 根据文档类型调整参数
            if doc_type in ['api', 'database', 'architecture']:
                additional_params['max_tokens'] = min(additional_params['max_tokens'], 6000)
            elif doc_type == 'overview':
                additional_params['temperature'] = 0.5  # 降低随机性，提高一致性

            # 调用MCP服务
            mcp_result = self.mcp_service.generate_document(
                repository_path=repository.local_path,
                doc_type=doc_type,
                doc_title=doc_title,
                llm_config=llm_config,
                additional_params=additional_params
            )

            if mcp_result['success']:
                return {
                    'success': True,
                    'content': mcp_result['content'],
                    'metrics': mcp_result.get('metrics'),
                    'cost_estimate': mcp_result.get('cost_estimate', 0)
                }
            else:
                return {
                    'success': False,
                    'error': mcp_result.get('error', 'Unknown MCP error')
                }

        except Exception as e:
            logger.error(f"Error calling MCP service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _call_llm_for_documentation(self, llm_config: LLMConfig, prompt: str,
                                   doc_type: str) -> Dict[str, Any]:
        """调用LLM生成文档"""
        try:
            # 创建LLM客户端
            client_factory = LLMClientFactory()
            client = client_factory.create_client(
                provider=llm_config.provider,
                api_key=llm_config.get_api_key(),
                model=llm_config.model_name,
                base_url=llm_config.base_url
            )

            # 设置生成参数
            generation_params = {
                'max_tokens': llm_config.max_tokens,
                'temperature': llm_config.temperature
            }

            # 根据文档类型调整参数
            if doc_type in ['api', 'database', 'architecture']:
                generation_params['max_tokens'] = min(generation_params['max_tokens'], 6000)
            elif doc_type == 'overview':
                generation_params['temperature'] = 0.5  # 降低随机性，提高一致性

            # 发送请求
            system_prompt = "你是一个专业的技术文档撰写专家，请生成准确、详细、结构化的技术文档。使用中文回答，保持专业性和可读性。"

            response = client.send_message(
                messages=[
                    client.LLMMessage(role="system", content=system_prompt),
                    client.LLMMessage(role="user", content=prompt)
                ],
                **generation_params
            )

            if response['success']:
                return {
                    'success': True,
                    'content': response['content'],
                    'metrics': response.get('metrics'),
                    'cost_estimate': response.get('cost_estimate', 0)
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Unknown error')
                }

        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _process_generated_document(self, content: str, repository: Repository,
                                  doc_type: str, metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理生成的文档"""
        try:
            processed_content = content

            # 文档后处理
            processed_content = self._post_process_content(processed_content, doc_type)

            # 生成文档元数据
            metadata = {
                'generated_at': datetime.utcnow().isoformat(),
                'doc_type': doc_type,
                'repository_name': repository.name,
                'processing_applied': True,
                'quality_score': self._calculate_quality_score(processed_content)
            }

            if metrics:
                metadata.update({
                    'prompt_tokens': metrics.get('prompt_tokens', 0),
                    'completion_tokens': metrics.get('completion_tokens', 0),
                    'total_tokens': metrics.get('total_tokens', 0),
                    'generation_time': metrics.get('response_time', 0),
                    'llm_model': metrics.get('model', 'unknown'),
                    'llm_provider': metrics.get('provider', 'unknown')
                })

            return {
                'content': processed_content,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                'content': content,
                'metadata': {'processing_error': str(e)}
            }

    def _post_process_content(self, content: str, doc_type: str) -> str:
        """后处理文档内容"""
        try:
            processed = content

            # 清理多余的空行
            processed = '\n'.join(line for line in processed.split('\n') if line.strip())

            # 确保标题格式正确
            if doc_type == 'overview':
                if not processed.startswith('# '):
                    processed = f"# {doc_type.title()} Documentation\n\n{processed}"

            # 添加文档头部信息
            header = f"<!-- Generated by CoderWiki LLM Integration -->\n"
            header += f"<!-- Document Type: {doc_type} -->\n"
            header += f"<!-- Generated at: {datetime.utcnow().isoformat()} -->\n\n"

            processed = header + processed

            return processed

        except Exception as e:
            logger.error(f"Error in post-processing: {str(e)}")
            return content

    def _calculate_quality_score(self, content: str) -> float:
        """计算文档质量分数"""
        try:
            score = 0.0

            # 基础分数
            if len(content) > 100:
                score += 2.0

            # 结构化内容
            if '#' in content:  # 有标题
                score += 1.0

            if '```' in content:  # 有代码块
                score += 1.0

            if '|' in content and '-' in content:  # 可能有表格
                score += 1.0

            # 内容长度
            if len(content) > 1000:
                score += 1.0
            elif len(content) > 500:
                score += 0.5

            # 中文内容
            chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
            if chinese_chars > 50:
                score += 1.0

            return min(score, 5.0)  # 最高5分

        except Exception as e:
            logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0

    def _save_document(self, repository: Repository, llm_config: LLMConfig,
                      content: str, doc_type: str, doc_title: str,
                      metrics: Dict[str, Any] = None, generation_metadata: Dict[str, Any] = None) -> Document:
        """保存文档"""
        try:
            # 生成文档标题
            if not doc_title:
                doc_title = f"{repository.name}_{doc_type}_documentation"

            # 检查是否有Claude Code生成的文件
            claude_generated_files = []
            if generation_metadata and isinstance(generation_metadata, dict):
                claude_generated_files = generation_metadata.get('generated_files', [])
                is_claude_code_generated = generation_metadata.get('claude_code_generated', False)
            else:
                is_claude_code_generated = False

            # 创建文档存储目录
            import os
            from pathlib import Path

            # 创建文档存储目录
            docs_dir = Path(__file__).parent.parent.parent / 'docs' / 'generated'
            docs_dir.mkdir(parents=True, exist_ok=True)

            # 确定文件路径
            file_path = None

            # 如果有Claude Code生成的文件，使用第一个作为主要文件
            if claude_generated_files and is_claude_code_generated:
                # 使用Claude Code生成的文件路径
                claude_file_path = claude_generated_files[0]
                if os.path.exists(claude_file_path):
                    # 复制Claude Code生成的文件到我们的文档目录
                    claude_path = Path(claude_file_path)
                    # 使用仓库名称作为文件名前缀
                    safe_repo_name = "".join(c for c in repository.name if c.isalnum() or c in ('-', '_')).rstrip()
                    filename = f"{safe_repo_name}_{doc_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
                    file_path = docs_dir / filename

                    # 复制文件内容
                    with open(claude_path, 'r', encoding='utf-8') as src:
                        claude_content = src.read()

                    # 写入到我们的文档目录
                    with open(file_path, 'w', encoding='utf-8') as dst:
                        dst.write(claude_content)

                    logger.info(f"Using Claude Code generated file: {claude_file_path} -> {file_path}")
                else:
                    logger.warning(f"Claude Code generated file not found: {claude_file_path}")
                    file_path = None

            # 如果没有Claude Code生成的文件或文件不存在，创建新文件
            if file_path is None:
                # 使用仓库名称作为文件名前缀
                safe_repo_name = "".join(c for c in repository.name if c.isalnum() or c in ('-', '_')).rstrip()
                filename = f"{safe_repo_name}_{doc_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
                file_path = docs_dir / filename

                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # 创建文档对象
            document = Document(
                repository_id=repository.id,
                user_id=repository.user_id,
                title=doc_title,
                content=content,
                version="1.0",
                status="published",
                language="markdown",
                document_type=doc_type,
                format="markdown",
                file_path=str(file_path),
                generated_at=datetime.utcnow(),
                llm_config_id=llm_config.id
            )

            # 设置LLM相关字段
            if metrics:
                document.prompt_tokens = metrics.get('prompt_tokens', 0)
                document.completion_tokens = metrics.get('completion_tokens', 0)
                document.total_tokens = metrics.get('total_tokens', 0)
                document.cost_estimate = metrics.get('cost_estimate', 0.0)
                document.generation_time = metrics.get('response_time', 0.0)

            # 设置生成元数据
            if generation_metadata:
                # 添加Claude Code文件信息到元数据
                if claude_generated_files:
                    generation_metadata['claude_generated_files'] = claude_generated_files
                    generation_metadata['primary_file'] = str(file_path)
                document.set_generation_metadata(generation_metadata)

            # 保存到数据库
            db.session.add(document)
            db.session.commit()

            logger.info(f"Document saved: {document.title} (ID: {document.id}, File: {file_path})")
            if claude_generated_files:
                logger.info(f"Claude Code generated files: {claude_generated_files}")

            return document

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving document: {str(e)}")
            raise

    def get_generation_status(self, task_id: int, user_id: int) -> Dict[str, Any]:
        """获取文档生成状态"""
        try:
            task = self.task_service.get_task_by_id(task_id, user_id)
            if not task:
                return {
                    'success': False,
                    'error': 'Task not found',
                    'error_type': 'not_found'
                }

            return {
                'success': True,
                'task': task.to_dict(),
                'status': task.status,
                'progress': self._calculate_progress(task),
                'message': task.status_message or 'Processing...'
            }

        except Exception as e:
            logger.error(f"Error getting generation status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_progress(self, task: Task) -> float:
        """计算任务进度"""
        if task.status == 'completed':
            return 100.0
        elif task.status == 'failed':
            return 0.0
        elif task.status == 'processing':
            # 基于状态消息估算进度
            message = task.status_message or ''
            if 'Starting' in message:
                return 10.0
            elif 'Analyzing' in message:
                return 25.0
            elif 'Generating' in message:
                return 40.0
            elif 'Calling' in message:
                return 60.0
            elif 'Processing' in message:
                return 80.0
            elif 'Saving' in message:
                return 95.0
            else:
                return 50.0
        else:
            return 0.0

    def get_user_documents(self, user_id: int, repository_id: int = None,
                          doc_type: str = None, limit: int = 50) -> List[Document]:
        """获取用户文档列表"""
        try:
            query = Document.query.filter_by(user_id=user_id)

            if repository_id:
                query = query.filter_by(repository_id=repository_id)

            if doc_type:
                # 根据文档类型过滤（可以扩展Document模型添加doc_type字段）
                pass

            return query.order_by(Document.created_at.desc()).limit(limit).all()

        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            return []

    def get_document_by_id(self, document_id: int, user_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        try:
            return Document.query.filter_by(id=document_id, user_id=user_id).first()
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None

    def check_claude_code_service_status(self) -> Dict[str, Any]:
        """检查Claude Code服务状态"""
        if not self.use_claude_code or not self.claude_code_service:
            return {
                'success': False,
                'error': 'Claude Code service is not enabled',
                'enabled': False
            }

        try:
            claude_availability = self.claude_code_service.check_claude_code_availability()
            bmad_availability = self.claude_code_service.check_bmad_docs_generator()

            return {
                'success': True,
                'enabled': True,
                'claude_code': claude_availability,
                'bmad_docs_generator': bmad_availability,
                'bmad_docs_path': self.claude_code_service.bmad_docs_path
            }
        except Exception as e:
            logger.error(f"Error checking Claude Code service status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'enabled': True
            }

    def check_mcp_service_status(self) -> Dict[str, Any]:
        """检查MCP服务状态"""
        if not self.use_mcp or not self.mcp_service:
            return {
                'success': False,
                'error': 'MCP service is not enabled',
                'enabled': False
            }

        try:
            health_result = self.mcp_service.check_mcp_service_health()
            info_result = self.mcp_service.get_mcp_service_info()

            return {
                'success': True,
                'enabled': True,
                'health': health_result,
                'info': info_result,
                'service_url': self.mcp_service.base_url
            }
        except Exception as e:
            logger.error(f"Error checking MCP service status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'enabled': True
            }

    def get_available_doc_types(self) -> Dict[str, Any]:
        """获取可用的文档类型"""
        if self.use_claude_code and self.claude_code_service:
            try:
                result = self.claude_code_service.get_supported_doc_types()
                if result['success']:
                    result['source'] = 'claude_code_bmad'
                return result
            except Exception as e:
                logger.error(f"Error getting Claude Code doc types: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'source': 'claude_code_bmad'
                }
        elif self.use_mcp and self.mcp_service:
            try:
                result = self.mcp_service.list_available_doc_types()
                if result['success']:
                    result['source'] = 'mcp_service'
                return result
            except Exception as e:
                logger.error(f"Error getting MCP doc types: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'source': 'mcp_service'
                }
        else:
            # 返回默认的文档类型
            return {
                'success': True,
                'doc_types': [
                    'overview',
                    'api',
                    'database',
                    'architecture',
                    'deployment',
                    'user_guide',
                    'developer_guide',
                    'technical_design',
                    'api_docs',
                    'database_design',
                    'deployment_guide',
                    'user_manual',
                    'developer_guide',
                    'system_overview'
                ],
                'source': 'default'
            }
