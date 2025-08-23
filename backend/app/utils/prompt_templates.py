"""
Prompt template system for generating structured technical documentation.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from string import Template

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:
    """提示词模板数据类"""
    name: str
    description: str
    template: str
    variables: List[str]
    category: str
    version: str = "1.0"
    
    def format(self, **kwargs) -> str:
        """格式化模板"""
        try:
            template = Template(self.template)
            return template.safe_substitute(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable in template {self.name}: {e}")
            raise ValueError(f"Missing required variable: {e}")
        except Exception as e:
            logger.error(f"Error formatting template {self.name}: {e}")
            raise

class PromptTemplateManager:
    """提示词模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        # 项目概述模板
        self.add_template(PromptTemplate(
            name="project_overview",
            description="生成项目概述文档",
            category="overview",
            template="""请为以下代码项目生成一个全面的项目概述文档：

## 项目信息
- 项目名称：${project_name}
- 主要技术栈：${tech_stack}
- 项目类型：${project_type}

## 代码分析结果
${analysis_results}

## 文档要求
请生成包含以下内容的项目概述：
1. **项目简介**：简要描述项目的功能和目标
2. **技术架构**：主要技术栈和架构模式
3. **核心功能**：项目的主要功能模块
4. **项目特点**：技术亮点和创新点
5. **适用场景**：项目的应用场景和目标用户

请使用中文编写，保持专业和技术准确性。""",
            variables=["project_name", "tech_stack", "project_type", "analysis_results"]
        ))
        
        # API文档模板
        self.add_template(PromptTemplate(
            name="api_documentation",
            description="生成API接口文档",
            category="api",
            template="""请为以下API接口生成详细的接口文档：

## API分析结果
${api_analysis}

## 文档要求
请为每个API接口生成包含以下信息的文档：

### 接口名称
**描述**：接口的功能说明  
**请求方法**：GET/POST/PUT/DELETE  
**接口路径**：API的完整路径  
**认证方式**：需要的认证类型  

#### 请求参数
| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| ${request_params_table}

#### 响应格式
```json
${response_format}
```

#### 错误码
| 状态码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| ${error_codes_table}

#### 使用示例
```python
${usage_example}
```

请确保文档的准确性和完整性。""",
            variables=["api_analysis", "request_params_table", "response_format", "error_codes_table", "usage_example"]
        ))
        
        # 数据库设计文档模板
        self.add_template(PromptTemplate(
            name="database_design",
            description="生成数据库设计文档",
            category="database",
            template="""请为以下数据库设计生成详细的设计文档：

## 数据库分析结果
${database_analysis}

## 文档要求
请生成包含以下内容的数据库设计文档：

### 数据库概览
- 数据库名称：${database_name}
- 数据库类型：${database_type}
- 字符集：${charset}

### 数据表设计

#### ${table_name}
**表说明**：${table_description}

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 主键 | 外键 | 描述 |
|--------|------|------|----------|--------|------|------|------|
| ${fields_table}

#### 索引设计
| 索引名 | 字段 | 索引类型 | 描述 |
|--------|------|----------|------|
| ${indexes_table}

#### 关系图
${relationship_diagram}

### 数据库优化建议
${optimization_suggestions}

请确保文档的准确性和完整性。""",
            variables=["database_analysis", "database_name", "database_type", "charset", "table_name", "table_description", "fields_table", "indexes_table", "relationship_diagram", "optimization_suggestions"]
        ))
        
        # 架构设计文档模板
        self.add_template(PromptTemplate(
            name="architecture_design",
            description="生成系统架构设计文档",
            category="architecture",
            template="""请为以下系统架构生成详细的设计文档：

## 架构分析结果
${architecture_analysis}

## 文档要求
请生成包含以下内容的架构设计文档：

### 系统概述
- 系统名称：${system_name}
- 架构风格：${architecture_style}
- 部署环境：${deployment_environment}

### 架构设计

#### 整体架构
${overall_architecture}

#### 模块设计
${module_design}

#### 技术栈选择
${tech_stack_choices}

#### 数据流设计
${data_flow_design}

#### 接口设计
${interface_design}

### 部署架构
${deployment_architecture}

### 性能考虑
${performance_considerations}

### 安全考虑
${security_considerations}

### 扩展性设计
${scalability_design}

请使用中文编写，保持专业性和技术准确性。""",
            variables=["architecture_analysis", "system_name", "architecture_style", "deployment_environment", "overall_architecture", "module_design", "tech_stack_choices", "data_flow_design", "interface_design", "deployment_architecture", "performance_considerations", "security_considerations", "scalability_design"]
        ))
        
        # 代码质量分析模板
        self.add_template(PromptTemplate(
            name="code_quality_analysis",
            description="生成代码质量分析报告",
            category="analysis",
            template="""请对以下代码进行质量分析并生成详细报告：

## 代码基本信息
- 语言：${language}
- 文件数：${file_count}
- 代码行数：${line_count}
- 分析时间：${analysis_time}

## 代码内容
${code_content}

## 分析要求
请从以下几个方面分析代码质量：

### 1. 代码结构
- 模块划分是否合理
- 函数/类的职责是否单一
- 代码组织是否清晰

### 2. 编码规范
- 命名规范是否符合标准
- 注释是否完整和准确
- 代码格式是否一致

### 3. 错误处理
- 异常处理是否完善
- 错误信息是否清晰
- 资源释放是否正确

### 4. 性能优化
- 算法复杂度是否合理
- 是否存在性能瓶颈
- 内存使用是否高效

### 5. 安全性
- 输入验证是否充分
- 是否存在安全漏洞
- 权限控制是否合理

### 6. 可维护性
- 代码可读性如何
- 扩展性是否良好
- 测试覆盖率如何

## 评分建议
请根据分析结果给出综合评分（1-10分）和改进建议。

### 综合评分：${score}/10

### 主要优点
${advantages}

### 需要改进的地方
${improvements}

### 具体建议
${suggestions}

请确保分析客观、专业，并提供有建设性的意见。""",
            variables=["language", "file_count", "line_count", "analysis_time", "code_content", "score", "advantages", "improvements", "suggestions"]
        ))
        
        # 测试用例生成模板
        self.add_template(PromptTemplate(
            name="test_case_generation",
            description="生成测试用例",
            category="testing",
            template="""请为以下代码生成完整的测试用例：

## 代码信息
- 语言：${language}
- 函数/类名：${function_name}
- 代码类型：${code_type}

## 待测试代码
${code_to_test}

## 测试要求
请生成包含以下内容的测试用例：

### 单元测试
${unit_tests}

### 集成测试
${integration_tests}

### 边界条件测试
${boundary_tests}

### 异常情况测试
${exception_tests}

### 性能测试
${performance_tests}

## 测试用例格式要求
每个测试用例应该包含：
1. **测试目的**：说明测试的目标
2. **测试数据**：输入数据和预期输出
3. **测试步骤**：具体的测试执行步骤
4. **预期结果**：测试应该达到的结果
5. **通过标准**：判断测试是否通过的标准

请确保测试用例的完整性和可执行性。""",
            variables=["language", "function_name", "code_type", "code_to_test", "unit_tests", "integration_tests", "boundary_tests", "exception_tests", "performance_tests"]
        ))
    
    def add_template(self, template: PromptTemplate):
        """添加模板"""
        self.templates[template.name] = template
        logger.info(f"Added prompt template: {template.name}")
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """按类别获取模板"""
        return [template for template in self.templates.values() if template.category == category]
    
    def get_all_templates(self) -> List[PromptTemplate]:
        """获取所有模板"""
        return list(self.templates.values())
    
    def format_template(self, name: str, **kwargs) -> str:
        """格式化模板"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        return template.format(**kwargs)
    
    def validate_template_variables(self, name: str, provided_vars: Dict[str, Any]) -> Dict[str, Any]:
        """验证模板变量"""
        template = self.get_template(name)
        if not template:
            return {'valid': False, 'error': f'Template not found: {name}'}
        
        required_vars = set(template.variables)
        provided_vars_set = set(provided_vars.keys())
        
        missing_vars = required_vars - provided_vars_set
        extra_vars = provided_vars_set - required_vars
        
        return {
            'valid': len(missing_vars) == 0,
            'missing_variables': list(missing_vars),
            'extra_variables': list(extra_vars)
        }
    
    def get_template_info(self, name: str) -> Dict[str, Any]:
        """获取模板信息"""
        template = self.get_template(name)
        if not template:
            return {}
        
        return {
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'variables': template.variables,
            'version': template.version
        }
    
    def create_custom_template(self, name: str, description: str, template: str, 
                             variables: List[str], category: str, version: str = "1.0") -> PromptTemplate:
        """创建自定义模板"""
        custom_template = PromptTemplate(
            name=name,
            description=description,
            template=template,
            variables=variables,
            category=category,
            version=version
        )
        
        self.add_template(custom_template)
        return custom_template
    
    def export_templates(self, category: str = None) -> str:
        """导出模板配置"""
        templates_to_export = self.get_all_templates()
        if category:
            templates_to_export = self.get_templates_by_category(category)
        
        export_data = {
            'templates': [
                {
                    'name': t.name,
                    'description': t.description,
                    'template': t.template,
                    'variables': t.variables,
                    'category': t.category,
                    'version': t.version
                }
                for t in templates_to_export
            ]
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def import_templates(self, json_data: str) -> Dict[str, Any]:
        """导入模板配置"""
        try:
            data = json.loads(json_data)
            imported_count = 0
            
            for template_data in data.get('templates', []):
                template = PromptTemplate(**template_data)
                self.add_template(template)
                imported_count += 1
            
            return {
                'success': True,
                'imported_count': imported_count,
                'message': f'Successfully imported {imported_count} templates'
            }
        except Exception as e:
            logger.error(f"Error importing templates: {e}")
            return {
                'success': False,
                'error': str(e)
            }