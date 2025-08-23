"""
Response processor for handling LLM responses and document formatting.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """处理结果数据类"""
    success: bool
    content: str
    metadata: Dict[str, Any]
    warnings: List[str]
    errors: List[str]

class ResponseProcessor:
    """响应处理器"""
    
    def __init__(self):
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'avg_processing_time': 0.0
        }
    
    def process_llm_response(self, response: Dict[str, Any], doc_type: str = 'general') -> ProcessingResult:
        """处理LLM响应"""
        start_time = datetime.utcnow()
        
        try:
            if not response.get('success'):
                return ProcessingResult(
                    success=False,
                    content='',
                    metadata={},
                    warnings=[],
                    errors=[response.get('error', 'Unknown error')]
                )
            
            content = response.get('content', '')
            metrics = response.get('metrics', {})
            
            # 基础处理
            processed_content = self._basic_cleanup(content)
            
            # 根据文档类型进行专门处理
            if doc_type == 'api':
                processed_content = self._process_api_documentation(processed_content)
            elif doc_type == 'database':
                processed_content = self._process_database_documentation(processed_content)
            elif doc_type == 'architecture':
                processed_content = self._process_architecture_documentation(processed_content)
            elif doc_type == 'overview':
                processed_content = self._process_overview_documentation(processed_content)
            
            # 质量检查
            quality_check = self._quality_check(processed_content)
            
            # 格式化处理
            formatted_content = self._format_document(processed_content, doc_type)
            
            # 生成元数据
            metadata = self._generate_metadata(
                original_response=response,
                processed_content=formatted_content,
                quality_check=quality_check,
                doc_type=doc_type,
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            # 更新统计信息
            self._update_stats(True, (datetime.utcnow() - start_time).total_seconds())
            
            return ProcessingResult(
                success=True,
                content=formatted_content,
                metadata=metadata,
                warnings=quality_check.get('warnings', []),
                errors=quality_check.get('errors', [])
            )
            
        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            self._update_stats(False, (datetime.utcnow() - start_time).total_seconds())
            
            return ProcessingResult(
                success=False,
                content=response.get('content', ''),
                metadata={},
                warnings=[],
                errors=[str(e)]
            )
    
    def _basic_cleanup(self, content: str) -> str:
        """基础内容清理"""
        try:
            # 移除多余的空行
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # 移除行首尾空白
            lines = [line.strip() for line in content.split('\n')]
            content = '\n'.join(lines)
            
            # 修复常见的Markdown格式问题
            content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', content)  # 粗体
            content = re.sub(r'\*([^*]+)\*', r'*\1*', content)  # 斜体
            
            # 修复代码块格式
            content = re.sub(r'```([^`\n]+)```', r'```\1```', content)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error in basic cleanup: {str(e)}")
            return content
    
    def _process_api_documentation(self, content: str) -> str:
        """处理API文档"""
        try:
            # 确保API接口有正确的标题格式
            content = re.sub(r'^### ([A-Z]+[A-Za-z0-9_ ]+)', r'### \1', content, flags=re.MULTILINE)
            
            # 格式化请求参数表格
            content = re.sub(
                r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|',
                lambda m: self._format_table_row(m.group(0)),
                content
            )
            
            # 确保代码块有语言标识
            content = re.sub(r'```(\w+)?', lambda m: self._fix_code_block_language(m), content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing API documentation: {str(e)}")
            return content
    
    def _process_database_documentation(self, content: str) -> str:
        """处理数据库文档"""
        try:
            # 确保表名有正确的格式
            content = re.sub(r'^#### ([A-Za-z_][A-Za-z0-9_]*)', r'#### \1', content, flags=re.MULTILINE)
            
            # 格式化字段表格
            content = re.sub(
                r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|',
                lambda m: self._format_table_row(m.group(0)),
                content
            )
            
            # 添加SQL语法高亮
            content = re.sub(r'```sql', '```sql', content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing database documentation: {str(e)}")
            return content
    
    def _process_architecture_documentation(self, content: str) -> str:
        """处理架构文档"""
        try:
            # 确保章节标题正确
            content = re.sub(r'^## ([A-Z][A-Za-z0-9_ ]+)', r'## \1', content, flags=re.MULTILINE)
            
            # 格式化技术栈列表
            content = re.sub(r'^- ([^:\n]+):', r'- **\1**:', content, flags=re.MULTILINE)
            
            # 确保图表说明正确
            content = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', r'![\1](\2)', content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing architecture documentation: {str(e)}")
            return content
    
    def _process_overview_documentation(self, content: str) -> str:
        """处理概述文档"""
        try:
            # 确保有主标题
            if not content.startswith('# '):
                content = f"# 项目概述\n\n{content}"
            
            # 格式化特性列表
            content = re.sub(r'^- ([^:\n]+):', r'- **\1**:', content, flags=re.MULTILINE)
            
            # 格式化技术栈部分
            content = re.sub(r'## 技术栈', '## 技术栈', content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing overview documentation: {str(e)}")
            return content
    
    def _format_table_row(self, row: str) -> str:
        """格式化表格行"""
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        return '|' + '|'.join(cells) + '|'
    
    def _fix_code_block_language(self, match: re.Match) -> str:
        """修复代码块语言标识"""
        lang = match.group(1) or ''
        if lang and not lang.strip():
            return '```'
        return match.group(0)
    
    def _quality_check(self, content: str) -> Dict[str, Any]:
        """质量检查"""
        warnings = []
        errors = []
        score = 0.0
        
        try:
            # 长度检查
            if len(content) < 100:
                errors.append("Content too short (< 100 characters)")
            elif len(content) > 50000:
                warnings.append("Content very long (> 50000 characters)")
            else:
                score += 1.0
            
            # 结构检查
            if '#' in content:
                score += 1.0
            else:
                warnings.append("No headings found")
            
            # 代码块检查
            code_blocks = content.count('```')
            if code_blocks > 0 and code_blocks % 2 == 0:
                score += 0.5
            elif code_blocks % 2 != 0:
                errors.append("Unclosed code blocks")
            
            # 表格检查
            tables = content.count('|')
            if tables > 10:
                score += 0.5
            
            # 链接检查
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            if links:
                score += 0.5
            
            # 中文内容检查
            chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
            if chinese_chars > len(content) * 0.1:  # 至少10%中文
                score += 1.0
            else:
                warnings.append("Low Chinese content ratio")
            
            # 格式检查
            markdown_issues = self._check_markdown_format(content)
            warnings.extend(markdown_issues)
            
            return {
                'score': min(score, 5.0),
                'warnings': warnings,
                'errors': errors,
                'checks': {
                    'length': len(content),
                    'headings': '#' in content,
                    'code_blocks': code_blocks,
                    'tables': tables > 0,
                    'links': len(links),
                    'chinese_ratio': chinese_chars / len(content) if len(content) > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in quality check: {str(e)}")
            return {
                'score': 0.0,
                'warnings': [],
                'errors': [str(e)],
                'checks': {}
            }
    
    def _check_markdown_format(self, content: str) -> List[str]:
        """检查Markdown格式"""
        issues = []
        
        try:
            # 检查未闭合的代码块
            if content.count('```') % 2 != 0:
                issues.append("Unclosed code blocks")
            
            # 检查未闭合的链接
            unclosed_links = re.findall(r'\[([^\]]+)(?!\([^)]*\))', content)
            if unclosed_links:
                issues.append(f"Unclosed links: {len(unclosed_links)}")
            
            # 检查标题层级
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    if level > 6:
                        issues.append(f"Invalid heading level {level} at line {i+1}")
            
            return issues
            
        except Exception as e:
            logger.error(f"Error checking markdown format: {str(e)}")
            return [f"Format check error: {str(e)}"]
    
    def _format_document(self, content: str, doc_type: str) -> str:
        """格式化文档"""
        try:
            # 添加文档头部
            header = f"""---
generated_by: CoderWiki LLM Integration
doc_type: {doc_type}
generated_at: {datetime.utcnow().isoformat()}
---

"""
            
            # 添加目录（如果内容足够长）
            if len(content) > 1000:
                toc = self._generate_table_of_contents(content)
                formatted_content = header + toc + '\n\n' + content
            else:
                formatted_content = header + content
            
            # 添加页脚
            footer = f"""

---

*本文档由 CoderWiki 自动生成，生成时间：{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            formatted_content += footer
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error formatting document: {str(e)}")
            return content
    
    def _generate_table_of_contents(self, content: str) -> str:
        """生成目录"""
        try:
            toc_lines = ["## 目录\n"]
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    if level <= 3:  # 只生成到三级标题
                        title = line.lstrip('#').strip()
                        indent = '  ' * (level - 1)
                        toc_lines.append(f"{indent}- [{title}](#{title.lower().replace(' ', '-')})")
            
            return '\n'.join(toc_lines)
            
        except Exception as e:
            logger.error(f"Error generating table of contents: {str(e)}")
            return ""
    
    def _generate_metadata(self, original_response: Dict[str, Any], processed_content: str,
                          quality_check: Dict[str, Any], doc_type: str, processing_time: float) -> Dict[str, Any]:
        """生成元数据"""
        try:
            metadata = {
                'processed_at': datetime.utcnow().isoformat(),
                'doc_type': doc_type,
                'processing_time': processing_time,
                'quality_score': quality_check.get('score', 0),
                'original_length': len(original_response.get('content', '')),
                'processed_length': len(processed_content),
                'compression_ratio': len(processed_content) / len(original_response.get('content', '')) if len(original_response.get('content', '')) > 0 else 1.0
            }
            
            # 添加LLM相关信息
            if 'metrics' in original_response:
                metadata['llm_metrics'] = original_response['metrics']
            
            # 添加质量检查信息
            metadata['quality_check'] = quality_check
            
            # 添加处理统计
            metadata['processing_stats'] = {
                'warnings_count': len(quality_check.get('warnings', [])),
                'errors_count': len(quality_check.get('errors', [])),
                'formatting_applied': True
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating metadata: {str(e)}")
            return {'error': str(e)}
    
    def _update_stats(self, success: bool, processing_time: float):
        """更新处理统计"""
        self.processing_stats['total_processed'] += 1
        
        if success:
            self.processing_stats['successful'] += 1
        else:
            self.processing_stats['failed'] += 1
        
        # 更新平均处理时间
        total = self.processing_stats['total_processed']
        current_avg = self.processing_stats['avg_processing_time']
        self.processing_stats['avg_processing_time'] = (current_avg * (total - 1) + processing_time) / total
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.processing_stats.copy()
    
    def validate_document_structure(self, content: str, doc_type: str) -> Dict[str, Any]:
        """验证文档结构"""
        try:
            validation_rules = {
                'api': {
                    'required_sections': ['接口', '请求参数', '响应格式', '错误码'],
                    'required_elements': ['表格', '代码块']
                },
                'database': {
                    'required_sections': ['数据表', '字段', '索引'],
                    'required_elements': ['表格']
                },
                'architecture': {
                    'required_sections': ['架构', '模块', '技术栈'],
                    'required_elements': []
                },
                'overview': {
                    'required_sections': ['项目', '功能', '技术'],
                    'required_elements': []
                }
            }
            
            rules = validation_rules.get(doc_type, {})
            issues = []
            
            # 检查必需章节
            for section in rules.get('required_sections', []):
                if section not in content:
                    issues.append(f"Missing required section: {section}")
            
            # 检查必需元素
            for element in rules.get('required_elements', []):
                if element == '表格' and '|' not in content:
                    issues.append("Missing tables")
                elif element == '代码块' and '```' not in content:
                    issues.append("Missing code blocks")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'doc_type': doc_type
            }
            
        except Exception as e:
            logger.error(f"Error validating document structure: {str(e)}")
            return {
                'valid': False,
                'issues': [str(e)],
                'doc_type': doc_type
            }