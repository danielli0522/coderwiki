"""
Claude 无头模式文档生成服务

集成 claude_headless_runner.py 实现基于提示词循环的文档自动生成功能。
输出目录格式：coderwiki-output-docs/ai-generate-doc/{repository_name}_{repository_id}/
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from app.models.repository import Repository
from app.models.document import Document
from app.services.directory_service import DirectoryService
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PromptConfig:
    """提示词配置"""
    prompt_file: str
    output_subdir: str
    timeout: int = 600
    tools: List[str] = None
    variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = ["Read", "Grep", "Glob"]
        if self.variables is None:
            self.variables = {}


@dataclass
class GenerationResult:
    """文档生成结果"""
    success: bool
    prompt_file: str
    output_path: str
    content: str
    error: str = ""
    execution_time: float = 0.0


class DocumentGenerationService:
    """优化的Claude 无头模式文档生成服务 - 直接使用prompts + Claude无头模式"""
    
    def __init__(self):
        self.directory_service = DirectoryService()
        self.prompts_dir = "docs/prompts"
        self.config_file = "docs/prompts/sequence.json"
        self.project_root = Path(__file__).parent.parent.parent.parent
        
    def generate_docs_for_repository(self, repository_id: int) -> Dict[str, Any]:
        """
        为指定仓库生成技术文档 - 优化版本
        
        Args:
            repository_id: 仓库ID
            
        Returns:
            生成结果字典
        """
        try:
            # 验证仓库存在
            repository = Repository.query.get(repository_id)
            if not repository:
                return {
                    'success': False,
                    'error': f'仓库 {repository_id} 不存在',
                    'generated_files': []
                }
            
            # 使用DirectoryService获取目录路径
            repo_source_dir = self.directory_service.get_repository_clone_path(repository.name, repository_id)
            output_dir = self.directory_service.get_ai_docs_path(repository.name, repository_id)
            
            # 验证仓库源目录存在
            if not os.path.exists(repo_source_dir):
                return {
                    'success': False,
                    'error': f'仓库源目录不存在: {repo_source_dir}',
                    'generated_files': []
                }
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"🚀 开始为仓库 {repository.name} (ID: {repository_id}) 生成文档")
            logger.info(f"📂 源目录: {repo_source_dir}")
            logger.info(f"📂 输出目录: {output_dir}")
            
            # 加载提示词配置
            prompt_configs = self._load_prompt_sequence()
            if not prompt_configs:
                return {
                    'success': False,
                    'error': '未找到有效的提示词配置',
                    'generated_files': []
                }
            
            # 执行提示词序列
            results = []
            for config in prompt_configs:
                result = self._execute_prompt(config, repository, repo_source_dir, output_dir)
                results.append(result)
                
                if not result.success:
                    logger.error(f"执行提示词 {config.prompt_file} 失败: {result.error}")
            
            # 统计结果
            successful_results = [r for r in results if r.success]
            generated_files = [r.output_path for r in successful_results]
            
            # 记录到数据库
            if successful_results:
                self._save_generation_record(repository_id, output_dir, results)
            
            # 计算总执行时间
            total_execution_time = sum(r.execution_time for r in results)
            
            result = {
                'success': len(successful_results) > 0,
                'repository_id': repository_id,
                'repository_name': repository.name,
                'output_directory': output_dir,
                'generated_files': generated_files,
                'results': [
                    {
                        'prompt_file': r.prompt_file,
                        'success': r.success,
                        'output_path': r.output_path,
                        'error': r.error,
                        'execution_time': r.execution_time
                    }
                    for r in results
                ],
                'statistics': {
                    'total_prompts': len(prompt_configs),
                    'successful_prompts': len(successful_results),
                    'failed_prompts': len(results) - len(successful_results),
                    'total_execution_time': total_execution_time,
                    'success_rate': len(successful_results) / len(results) * 100 if results else 0
                }
            }
            
            if successful_results:
                logger.info(f"✅ 文档生成完成！成功 {len(successful_results)}/{len(results)} 个任务，总耗时 {total_execution_time:.2f}秒")
            else:
                logger.warning(f"⚠️ 文档生成失败！所有 {len(results)} 个任务都失败了")
            
            return result
            
        except Exception as e:
            logger.error(f"文档生成过程发生异常: {str(e)}")
            return {
                'success': False,
                'error': f'文档生成失败: {str(e)}',
                'generated_files': []
            }
    
    
    def _load_prompt_sequence(self) -> List[PromptConfig]:
        """加载提示词序列配置"""
        try:
            config_path = self.project_root / self.config_file
            
            if not config_path.exists():
                # 如果配置文件不存在，返回默认配置
                return self._get_default_prompt_configs()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            prompt_configs = []
            for item in config_data.get('execution_sequence', []):
                config = PromptConfig(
                    prompt_file=item['prompt_file'],
                    output_subdir=item.get('output_subdir', ''),
                    timeout=item.get('timeout', 600),
                    tools=item.get('tools', ["Read", "Grep", "Glob"]),
                    variables=item.get('variables', {})
                )
                prompt_configs.append(config)
            
            logger.info(f"加载了 {len(prompt_configs)} 个提示词配置")
            return prompt_configs
            
        except Exception as e:
            logger.error(f"加载提示词配置失败: {str(e)}")
            return self._get_default_prompt_configs()
    
    def _get_default_prompt_configs(self) -> List[PromptConfig]:
        """获取默认提示词配置"""
        return [
            PromptConfig(
                prompt_file="technical-overview.md",
                output_subdir="",
                timeout=600,
                tools=["Read", "Grep", "Glob"]
            ),
            PromptConfig(
                prompt_file="API逆向分析.md",
                output_subdir="",
                timeout=900,
                tools=["Read", "Grep", "Bash"]
            ),
            PromptConfig(
                prompt_file="模块深度考古与高频提交问题.md",
                output_subdir="",
                timeout=1200,
                tools=["Read", "Grep", "Bash", "WebSearch"]
            )
        ]
    
    def _execute_prompt(self, config: PromptConfig, repository: Repository, repo_source_dir: str, output_dir: str) -> GenerationResult:
        """执行单个提示词"""
        try:
            # 读取提示词内容
            prompt_path = self.project_root / self.prompts_dir / config.prompt_file
            
            if not prompt_path.exists():
                return GenerationResult(
                    success=False,
                    prompt_file=config.prompt_file,
                    output_path="",
                    content="",
                    error=f"提示词文件不存在: {prompt_path}"
                )
            
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                with open(prompt_path, 'r', encoding='utf-8', errors='ignore') as f:
                    prompt_content = f.read()
                    logger.warning(f"使用忽略错误模式读取文件: {prompt_path}")
            
            # 替换变量
            prompt_content = self._replace_variables(
                prompt_content, 
                repository, 
                repo_source_dir,
                config.variables
            )
            
            logger.info(f"📝 执行提示词: {config.prompt_file} (超时: {config.timeout}s, 工具: {config.tools})")
            
            # 使用Claude Headless Runner直接执行
            from claude_headless_runner import ClaudeHeadlessRunner, ClaudeHeadlessOptions
            
            # 构建执行选项 - 设置工作目录为仓库源目录
            # 确保工作目录是绝对路径
            abs_repo_path = Path(repo_source_dir).resolve() if os.path.exists(repo_source_dir) else self.project_root.resolve()
            
            options = ClaudeHeadlessOptions(
                prompt=prompt_content,
                allowed_tools=config.tools,
                timeout=config.timeout,
                cwd=str(abs_repo_path),
                permission_mode='acceptEdits'
            )
            
            logger.info(f"开始执行提示词: {config.prompt_file}")
            runner = ClaudeHeadlessRunner(options)
            result = runner.run()
            
            if result['success']:
                # 生成输出文件名：项目名-提示词名.md
                prompt_basename = os.path.splitext(config.prompt_file)[0]
                output_filename = f"{repository.name}-{prompt_basename}.md"
                output_file = os.path.join(output_dir, output_filename)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['output'])
                
                return GenerationResult(
                    success=True,
                    prompt_file=config.prompt_file,
                    output_path=output_file,
                    content=result['output'],
                    execution_time=result.get('execution_time', 0.0)
                )
            else:
                return GenerationResult(
                    success=False,
                    prompt_file=config.prompt_file,
                    output_path="",
                    content="",
                    error=result.get('error', '未知错误'),
                    execution_time=result.get('execution_time', 0.0)
                )
                
        except Exception as e:
            logger.error(f"执行提示词 {config.prompt_file} 时发生异常: {str(e)}")
            return GenerationResult(
                success=False,
                prompt_file=config.prompt_file,
                output_path="",
                content="",
                error=str(e)
            )
    
    def _replace_variables(self, prompt_content: str, repository: Repository, repo_source_dir, variables: Dict[str, Any]) -> str:
        """替换提示词中的变量"""
        # 基础变量替换
        repo_path_str = str(repo_source_dir)  # 确保是字符串
        replacements = {
            '{project_name}': repository.name,
            '{repository_name}': repository.name,
            '{repository_id}': str(repository.id),
            '{repository_path}': repo_path_str,
            # 兼容旧版本的占位符
            '{YOUR_PROJECT_NAME}': repository.name,
            '{MODULE_NAME}': repository.name,
            '{YOUR_DIRECTORY_PATH}': repo_path_str,
            # 修复API分析报告的文件名问题
            '[YOUR_PROJECT_NAME]-api接口分析报告.md': f'{repository.name}-API逆向分析.md',
            '[YOUR_PROJECT_NAME]': repository.name
        }
        
        # 添加自定义变量
        for key, value in variables.items():
            if not key.startswith('{') or not key.endswith('}'):
                key = f'{{{key}}}'
            replacements[key] = str(value)
        
        # 执行替换
        for placeholder, value in replacements.items():
            prompt_content = prompt_content.replace(placeholder, value)
        
        return prompt_content
    
    def _save_generation_record(self, repository_id: int, output_dir: str, results: List[GenerationResult]) -> None:
        """保存生成记录到数据库"""
        try:
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]
            
            # 创建内容摘要
            content_lines = [f"🚀 AI文档生成完成 - 成功生成 {len(successful_results)} 个文档\n"]
            
            if successful_results:
                content_lines.append("📋 生成的文档:")
                for result in successful_results:
                    filename = os.path.basename(result.output_path)
                    content_lines.append(f"✅ {result.prompt_file} → {filename} ({result.execution_time:.2f}s)")
            
            if failed_results:
                content_lines.append(f"\n⚠️ {len(failed_results)} 个任务执行失败:")
                for result in failed_results:
                    content_lines.append(f"❌ {result.prompt_file}: {result.error}")
            
            content_summary = "\n".join(content_lines)
            
            # 创建文档记录
            document = Document(
                repository_id=repository_id,
                title=f"AI生成技术文档集合",
                content=content_summary,
                document_type='ai_generated',
                status='published',
                file_path=output_dir,
                version='1.0'
            )
            
            from app import db
            db.session.add(document)
            db.session.commit()
            
            logger.info(f"💾 文档记录已保存到数据库: {document.id}")
            
        except Exception as e:
            logger.error(f"💥 保存文档记录失败: {str(e)}")