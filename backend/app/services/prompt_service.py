"""
Prompt service for managing prompt templates and operations.
"""

import logging
from typing import Dict, List, Any, Optional
from app.utils.prompt_templates import PromptTemplateManager, PromptTemplate

logger = logging.getLogger(__name__)

class PromptService:
    """提示词服务类"""
    
    def __init__(self):
        self.template_manager = PromptTemplateManager()
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """获取可用的提示词模板"""
        templates = self.template_manager.get_all_templates()
        return [self.template_manager.get_template_info(t.name) for t in templates]
    
    def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取模板"""
        template = self.template_manager.get_template(name)
        if template:
            return {
                'name': template.name,
                'description': template.description,
                'template': template.template,
                'variables': template.variables,
                'category': template.category,
                'version': template.version
            }
        return None
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别获取模板"""
        templates = self.template_manager.get_templates_by_category(category)
        return [self.template_manager.get_template_info(t.name) for t in templates]
    
    def get_categories(self) -> List[str]:
        """获取所有模板类别"""
        categories = set()
        for template in self.template_manager.get_all_templates():
            categories.add(template.category)
        return sorted(list(categories))
    
    def format_prompt(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """格式化提示词"""
        try:
            # 验证变量
            validation = self.template_manager.validate_template_variables(template_name, variables)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Missing required variables',
                    'missing_variables': validation['missing_variables']
                }
            
            # 格式化模板
            formatted_prompt = self.template_manager.format_template(template_name, **variables)
            
            return {
                'success': True,
                'prompt': formatted_prompt,
                'template_name': template_name,
                'variables_used': list(variables.keys())
            }
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_technical_documentation_prompt(self, analysis_results: Dict[str, Any], 
                                           doc_type: str = 'overview') -> Dict[str, Any]:
        """创建技术文档生成提示词"""
        try:
            # 根据文档类型选择模板
            template_mapping = {
                'overview': 'project_overview',
                'api': 'api_documentation',
                'database': 'database_design',
                'architecture': 'architecture_design',
                'quality': 'code_quality_analysis',
                'testing': 'test_case_generation'
            }
            
            template_name = template_mapping.get(doc_type, 'project_overview')
            
            # 准备变量
            variables = self._prepare_documentation_variables(analysis_results, doc_type)
            
            # 格式化提示词
            result = self.format_prompt(template_name, variables)
            
            if result['success']:
                result['doc_type'] = doc_type
                result['analysis_summary'] = self._create_analysis_summary(analysis_results)
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating documentation prompt: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_documentation_variables(self, analysis_results: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """准备文档生成变量"""
        variables = {
            'project_name': analysis_results.get('project_name', 'Unknown Project'),
            'tech_stack': analysis_results.get('tech_stack', 'Unknown'),
            'project_type': analysis_results.get('project_type', 'General'),
            'language': analysis_results.get('language', 'Unknown'),
            'file_count': analysis_results.get('file_count', 0),
            'line_count': analysis_results.get('line_count', 0),
            'analysis_time': analysis_results.get('analysis_time', 'Unknown')
        }
        
        # 根据文档类型添加特定变量
        if doc_type == 'overview':
            variables['analysis_results'] = self._format_analysis_results(analysis_results)
        
        elif doc_type == 'api':
            variables['api_analysis'] = self._format_api_analysis(analysis_results)
            variables['request_params_table'] = self._generate_request_params_table(analysis_results)
            variables['response_format'] = self._generate_response_format(analysis_results)
            variables['error_codes_table'] = self._generate_error_codes_table(analysis_results)
            variables['usage_example'] = self._generate_usage_example(analysis_results)
        
        elif doc_type == 'database':
            variables['database_analysis'] = self._format_database_analysis(analysis_results)
            variables['database_name'] = analysis_results.get('database_name', 'Unknown')
            variables['database_type'] = analysis_results.get('database_type', 'Unknown')
            variables['charset'] = analysis_results.get('charset', 'utf8')
        
        elif doc_type == 'architecture':
            variables['architecture_analysis'] = self._format_architecture_analysis(analysis_results)
            variables['system_name'] = analysis_results.get('system_name', 'Unknown System')
            variables['architecture_style'] = analysis_results.get('architecture_style', 'Unknown')
            variables['deployment_environment'] = analysis_results.get('deployment_environment', 'Unknown')
        
        elif doc_type == 'quality':
            variables['code_content'] = analysis_results.get('code_content', '')
            variables['score'] = analysis_results.get('quality_score', 5)
            variables['advantages'] = analysis_results.get('advantages', '')
            variables['improvements'] = analysis_results.get('improvements', '')
            variables['suggestions'] = analysis_results.get('suggestions', '')
        
        elif doc_type == 'testing':
            variables['code_to_test'] = analysis_results.get('code_content', '')
            variables['function_name'] = analysis_results.get('function_name', 'Unknown')
            variables['code_type'] = analysis_results.get('code_type', 'function')
        
        return variables
    
    def _format_analysis_results(self, analysis_results: Dict[str, Any]) -> str:
        """格式化分析结果"""
        formatted_parts = []
        
        if 'tech_stack' in analysis_results:
            formatted_parts.append(f"**技术栈**: {analysis_results['tech_stack']}")
        
        if 'project_type' in analysis_results:
            formatted_parts.append(f"**项目类型**: {analysis_results['project_type']}")
        
        if 'file_count' in analysis_results:
            formatted_parts.append(f"**文件数量**: {analysis_results['file_count']}")
        
        if 'line_count' in analysis_results:
            formatted_parts.append(f"**代码行数**: {analysis_results['line_count']}")
        
        if 'main_features' in analysis_results:
            formatted_parts.append(f"**主要功能**: {analysis_results['main_features']}")
        
        return '\n'.join(formatted_parts)
    
    def _format_api_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """格式化API分析结果"""
        apis = analysis_results.get('apis', [])
        if not apis:
            return "未发现API接口"
        
        formatted = []
        for api in apis:
            formatted.append(f"- {api.get('method', 'GET')} {api.get('path', '/unknown')}: {api.get('description', 'No description')}")
        
        return '\n'.join(formatted)
    
    def _generate_request_params_table(self, analysis_results: Dict[str, Any]) -> str:
        """生成请求参数表格"""
        # 简化的参数表格生成
        return "| name | string | 是 | - | 参数名称 |"
    
    def _generate_response_format(self, analysis_results: Dict[str, Any]) -> str:
        """生成响应格式"""
        return '''{
    "success": true,
    "data": {},
    "message": "操作成功"
}'''
    
    def _generate_error_codes_table(self, analysis_results: Dict[str, Any]) -> str:
        """生成错误码表格"""
        return "| 200 | 成功 | - |\n| 400 | 请求参数错误 | 检查参数 |\n| 500 | 服务器错误 | 联系管理员 |"
    
    def _generate_usage_example(self, analysis_results: Dict[str, Any]) -> str:
        """生成使用示例"""
        return '''import requests

response = requests.get('https://api.example.com/users')
data = response.json()
print(data)'''
    
    def _format_database_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """格式化数据库分析结果"""
        tables = analysis_results.get('tables', [])
        if not tables:
            return "未发现数据库表"
        
        formatted = []
        for table in tables:
            formatted.append(f"- {table.get('name', 'unknown')}: {table.get('description', 'No description')}")
        
        return '\n'.join(formatted)
    
    def _format_architecture_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """格式化架构分析结果"""
        components = analysis_results.get('components', [])
        if not components:
            return "未发现架构组件"
        
        formatted = []
        for component in components:
            formatted.append(f"- {component.get('name', 'unknown')}: {component.get('description', 'No description')}")
        
        return '\n'.join(formatted)
    
    def _create_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """创建分析摘要"""
        summary_parts = []
        
        if 'project_name' in analysis_results:
            summary_parts.append(f"项目: {analysis_results['project_name']}")
        
        if 'tech_stack' in analysis_results:
            summary_parts.append(f"技术栈: {analysis_results['tech_stack']}")
        
        if 'file_count' in analysis_results:
            summary_parts.append(f"文件数: {analysis_results['file_count']}")
        
        return ' | '.join(summary_parts)
    
    def create_custom_template(self, name: str, description: str, template: str, 
                             variables: List[str], category: str) -> Dict[str, Any]:
        """创建自定义模板"""
        try:
            custom_template = self.template_manager.create_custom_template(
                name=name,
                description=description,
                template=template,
                variables=variables,
                category=category
            )
            
            return {
                'success': True,
                'template': {
                    'name': custom_template.name,
                    'description': custom_template.description,
                    'variables': custom_template.variables,
                    'category': custom_template.category,
                    'version': custom_template.version
                }
            }
        except Exception as e:
            logger.error(f"Error creating custom template: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_template_variables(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """验证模板变量"""
        return self.template_manager.validate_template_variables(template_name, variables)
    
    def export_templates(self, category: str = None) -> Dict[str, Any]:
        """导出模板"""
        try:
            export_data = self.template_manager.export_templates(category)
            return {
                'success': True,
                'data': export_data,
                'message': 'Templates exported successfully'
            }
        except Exception as e:
            logger.error(f"Error exporting templates: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_templates(self, json_data: str) -> Dict[str, Any]:
        """导入模板"""
        try:
            result = self.template_manager.import_templates(json_data)
            return result
        except Exception as e:
            logger.error(f"Error importing templates: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }