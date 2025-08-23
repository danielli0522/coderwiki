"""
Claude Code Service for document generation using Claude Code SDK.
"""

import os
import json
import logging
import time
import subprocess
import tempfile
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
    
    def __init__(self, claude_code_path: str = None, bmad_docs_path: str = None):
        """
        初始化Claude Code服务
        
        Args:
            claude_code_path: Claude Code SDK路径
            bmad_docs_path: BMAD文档生成器路径
        """
        # Claude Code SDK路径
        self.claude_code_path = claude_code_path or "/usr/local/bin/claude-code"
        
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
        if not os.path.exists(self.claude_code_path):
            logger.warning(f"Claude Code SDK not found at: {self.claude_code_path}")
            logger.info("Please install Claude Code SDK or set correct path")
        
        if not os.path.exists(self.bmad_docs_path):
            logger.warning(f"BMAD docs generator not found at: {self.bmad_docs_path}")
            logger.info("Please check the BMAD docs generator path")
    
    def generate_technical_document(self, 
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
            
            # 准备Claude Code命令参数
            command_args = self._prepare_claude_code_command(
                repository_path=repository_path,
                doc_type=doc_type,
                doc_title=doc_title,
                additional_params=additional_params
            )
            
            logger.info(f"Executing Claude Code command: {' '.join(command_args)}")
            
            # 执行Claude Code命令
            result = self._execute_claude_code_command(command_args)
            
            if result['success']:
                response_time = time.time() - start_time
                
                # 创建指标对象
                metrics = ClaudeCodeMetrics(
                    response_time=response_time,
                    cost_estimate=0.0,  # Claude Code可能不提供成本信息
                    tokens_used=0,      # Claude Code可能不提供token信息
                    model="claude-code",
                    provider="claude-code"
                )
                
                return {
                    'success': True,
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {}),
                    'metrics': metrics.__dict__,
                    'cost_estimate': metrics.cost_estimate,
                    'generation_time': response_time,
                    'output_file': result.get('output_file', '')
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
    
    def _prepare_claude_code_command(self, repository_path: str, doc_type: str, 
                                   doc_title: str, additional_params: Dict[str, Any]) -> List[str]:
        """准备Claude Code命令参数"""
        # 基础命令
        command = [self.claude_code_path]
        
        # 指定sub agent
        command.extend(['--sub-agent', '/bmad//bmadDocs:teams:docs-generation-team'])
        
        # 指定BMAD文档生成器路径
        command.extend(['--bmad-path', self.bmad_docs_path])
        
        # 指定仓库路径
        command.extend(['--repository', repository_path])
        
        # 指定文档类型
        command.extend(['--doc-type', doc_type])
        
        # 指定文档标题
        if doc_title:
            command.extend(['--doc-title', doc_title])
        
        # 添加额外参数
        if additional_params:
            for key, value in additional_params.items():
                if isinstance(value, (str, int, float, bool)):
                    command.extend([f'--{key}', str(value)])
                elif isinstance(value, list):
                    for item in value:
                        command.extend([f'--{key}', str(item)])
        
        # 指定输出格式
        command.extend(['--output-format', 'markdown'])
        
        # 指定语言
        command.extend(['--language', 'zh-CN'])
        
        return command
    
    def _execute_claude_code_command(self, command_args: List[str]) -> Dict[str, Any]:
        """执行Claude Code命令"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries}: Executing Claude Code command")
                
                # 创建临时文件用于输出
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
                    temp_output = temp_file.name
                
                # 添加输出文件参数
                command_with_output = command_args + ['--output', temp_output]
                
                # 执行命令
                process = subprocess.Popen(
                    command_with_output,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    # 读取生成的文档内容
                    try:
                        with open(temp_output, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 清理临时文件
                        os.unlink(temp_output)
                        
                        logger.info(f"Claude Code command successful (attempt {attempt + 1})")
                        
                        return {
                            'success': True,
                            'content': content,
                            'metadata': {
                                'command': ' '.join(command_args),
                                'stdout': stdout,
                                'stderr': stderr,
                                'return_code': process.returncode
                            },
                            'output_file': temp_output
                        }
                        
                    except Exception as e:
                        logger.error(f"Error reading output file: {str(e)}")
                        return {
                            'success': False,
                            'error': f'Error reading output file: {str(e)}',
                            'error_type': 'output_read_error'
                        }
                else:
                    logger.warning(f"Claude Code command failed with return code {process.returncode} (attempt {attempt + 1})")
                    logger.warning(f"STDOUT: {stdout}")
                    logger.warning(f"STDERR: {stderr}")
                    
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': f'Claude Code command failed: {stderr}',
                            'error_type': 'claude_code_command_failed',
                            'stdout': stdout,
                            'stderr': stderr,
                            'return_code': process.returncode
                        }
                    
                    time.sleep(self.retry_delay)
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Claude Code command timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'error': 'Claude Code command timeout',
                        'error_type': 'claude_code_timeout'
                    }
                time.sleep(self.retry_delay)
                
            except subprocess.SubprocessError as e:
                logger.error(f"Claude Code subprocess error (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'error': f'Claude Code subprocess error: {str(e)}',
                        'error_type': 'claude_code_subprocess_error'
                    }
                time.sleep(self.retry_delay)
        
        return {
            'success': False,
            'error': 'Claude Code command failed after all retries',
            'error_type': 'claude_code_max_retries_exceeded'
        }
    
    def check_claude_code_availability(self) -> Dict[str, Any]:
        """检查Claude Code SDK是否可用"""
        try:
            # 检查Claude Code SDK是否安装
            result = subprocess.run(
                [self.claude_code_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'available': True,
                    'version': result.stdout.strip(),
                    'claude_code_path': self.claude_code_path
                }
            else:
                return {
                    'success': False,
                    'available': False,
                    'error': f'Claude Code SDK not available: {result.stderr}',
                    'claude_code_path': self.claude_code_path
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'available': False,
                'error': f'Claude Code SDK not found at: {self.claude_code_path}',
                'claude_code_path': self.claude_code_path
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'available': False,
                'error': 'Claude Code SDK version check timeout',
                'claude_code_path': self.claude_code_path
            }
        except Exception as e:
            return {
                'success': False,
                'available': False,
                'error': f'Error checking Claude Code SDK: {str(e)}',
                'claude_code_path': self.claude_code_path
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
