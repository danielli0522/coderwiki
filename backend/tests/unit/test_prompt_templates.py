"""
Unit tests for prompt template system.
"""

import pytest
from app.utils.prompt_templates import PromptTemplate, PromptTemplateManager

class TestPromptTemplate:
    """提示词模板测试"""
    
    def test_prompt_template_creation(self):
        """测试创建提示词模板"""
        template = PromptTemplate(
            name="test_template",
            description="Test template",
            template="Hello ${name}!",
            variables=["name"],
            category="test"
        )
        
        assert template.name == "test_template"
        assert template.description == "Test template"
        assert template.template == "Hello ${name}!"
        assert template.variables == ["name"]
        assert template.category == "test"
        assert template.version == "1.0"
    
    def test_template_formatting(self):
        """测试模板格式化"""
        template = PromptTemplate(
            name="test_template",
            description="Test template",
            template="Hello ${name}! You are ${age} years old.",
            variables=["name", "age"],
            category="test"
        )
        
        # 测试正确格式化
        result = template.format(name="Alice", age=25)
        assert result == "Hello Alice! You are 25 years old."
        
        # 测试缺少变量
        with pytest.raises(ValueError, match="Missing required variable"):
            template.format(name="Alice")  # 缺少age变量
    
    def test_template_manager_initialization(self):
        """测试模板管理器初始化"""
        manager = PromptTemplateManager()
        
        # 验证默认模板已加载
        assert len(manager.templates) > 0
        
        # 验证特定模板存在
        assert 'project_overview' in manager.templates
        assert 'api_documentation' in manager.templates
        assert 'database_design' in manager.templates
    
    def test_get_template(self):
        """测试获取模板"""
        manager = PromptTemplateManager()
        
        # 测试获取存在的模板
        template = manager.get_template('project_overview')
        assert template is not None
        assert template.name == 'project_overview'
        assert len(template.variables) > 0
        
        # 测试获取不存在的模板
        template = manager.get_template('nonexistent_template')
        assert template is None
    
    def test_get_templates_by_category(self):
        """测试按类别获取模板"""
        manager = PromptTemplateManager()
        
        # 测试获取overview类别
        overview_templates = manager.get_templates_by_category('overview')
        assert len(overview_templates) > 0
        assert all(t.category == 'overview' for t in overview_templates)
        
        # 测试获取不存在的类别
        empty_templates = manager.get_templates_by_category('nonexistent_category')
        assert len(empty_templates) == 0
    
    def test_get_all_templates(self):
        """测试获取所有模板"""
        manager = PromptTemplateManager()
        
        all_templates = manager.get_all_templates()
        assert len(all_templates) > 0
        assert len(all_templates) == len(manager.templates)
    
    def test_format_template(self):
        """测试格式化模板"""
        manager = PromptTemplateManager()
        
        # 测试格式化project_overview模板
        variables = {
            'project_name': 'Test Project',
            'tech_stack': 'Python, Flask',
            'project_type': 'Web Application',
            'analysis_results': 'Simple web application'
        }
        
        result = manager.format_template('project_overview', **variables)
        assert 'Test Project' in result
        assert 'Python, Flask' in result
        assert 'Web Application' in result
    
    def test_validate_template_variables(self):
        """测试验证模板变量"""
        manager = PromptTemplateManager()
        
        # 测试正确变量
        template_name = 'project_overview'
        provided_vars = {
            'project_name': 'Test',
            'tech_stack': 'Python',
            'project_type': 'Web',
            'analysis_results': 'Analysis'
        }
        
        validation = manager.validate_template_variables(template_name, provided_vars)
        assert validation['valid'] is True
        assert len(validation['missing_variables']) == 0
        
        # 测试缺少变量
        incomplete_vars = {
            'project_name': 'Test',
            'tech_stack': 'Python'
            # 缺少project_type和analysis_results
        }
        
        validation = manager.validate_template_variables(template_name, incomplete_vars)
        assert validation['valid'] is False
        assert len(validation['missing_variables']) > 0
        
        # 测试不存在的模板
        validation = manager.validate_template_variables('nonexistent_template', {})
        assert validation['valid'] is False
        assert 'Template not found' in validation['error']
    
    def test_get_template_info(self):
        """测试获取模板信息"""
        manager = PromptTemplateManager()
        
        # 测试获取存在的模板信息
        info = manager.get_template_info('project_overview')
        assert info['name'] == 'project_overview'
        assert info['category'] == 'overview'
        assert 'variables' in info
        assert 'description' in info
        
        # 测试获取不存在的模板信息
        info = manager.get_template_info('nonexistent_template')
        assert info == {}
    
    def test_create_custom_template(self):
        """测试创建自定义模板"""
        manager = PromptTemplateManager()
        
        # 创建自定义模板
        custom_template = manager.create_custom_template(
            name='custom_test',
            description='Custom test template',
            template='Custom: ${variable}',
            variables=['variable'],
            category='custom'
        )
        
        # 验证模板已创建
        assert custom_template.name == 'custom_test'
        assert 'custom_test' in manager.templates
        
        # 验证可以获取和使用模板
        retrieved_template = manager.get_template('custom_test')
        assert retrieved_template is not None
        
        result = manager.format_template('custom_test', variable='test_value')
        assert result == 'Custom: test_value'
    
    def test_export_templates(self):
        """测试导出模板"""
        manager = PromptTemplateManager()
        
        # 导出所有模板
        export_data = manager.export_templates()
        assert 'templates' in export_data
        assert len(export_data['templates']) > 0
        
        # 验证导出数据结构
        template_data = export_data['templates'][0]
        assert 'name' in template_data
        assert 'description' in template_data
        assert 'template' in template_data
        assert 'variables' in template_data
        assert 'category' in template_data
        
        # 测试按类别导出
        overview_export = manager.export_templates('overview')
        assert len(overview_export['templates']) > 0
        assert all(t['category'] == 'overview' for t in overview_export['templates'])
    
    def test_import_templates(self):
        """测试导入模板"""
        manager = PromptTemplateManager()
        
        # 准备导入数据
        import_data = {
            'templates': [
                {
                    'name': 'imported_template',
                    'description': 'Imported template',
                    'template': 'Imported: ${test_var}',
                    'variables': ['test_var'],
                    'category': 'imported',
                    'version': '1.0'
                }
            ]
        }
        
        import_json = str(import_data).replace("'", '"')
        
        # 执行导入
        result = manager.import_templates(import_json)
        assert result['success'] is True
        assert result['imported_count'] == 1
        
        # 验证模板已导入
        imported_template = manager.get_template('imported_template')
        assert imported_template is not None
        assert imported_template.category == 'imported'
    
    def test_import_invalid_json(self):
        """测试导入无效JSON"""
        manager = PromptTemplateManager()
        
        # 测试无效JSON
        result = manager.import_templates('invalid json')
        assert result['success'] is False
        assert 'error' in result
    
    def test_template_variable_substitution(self):
        """测试模板变量替换"""
        manager = PromptTemplateManager()
        
        # 测试API文档模板
        api_vars = {
            'api_analysis': 'Test API analysis',
            'request_params_table': '| name | type | required |',
            'response_format': '{"success": true}',
            'error_codes_table': '| 200 | OK |',
            'usage_example': 'requests.get("/api")'
        }
        
        result = manager.format_template('api_documentation', **api_vars)
        assert 'Test API analysis' in result
        assert 'name | type | required |' in result
        assert '{"success": true}' in result
        
        # 测试数据库设计模板
        db_vars = {
            'database_analysis': 'Test DB analysis',
            'database_name': 'test_db',
            'database_type': 'PostgreSQL',
            'charset': 'utf8',
            'table_name': 'users',
            'table_description': 'User table',
            'fields_table': '| id | integer | primary key |',
            'indexes_table': '| idx_users_id | id | btree |',
            'relationship_diagram': 'users -> posts',
            'optimization_suggestions': 'Add indexes'
        }
        
        result = manager.format_template('database_design', **db_vars)
        assert 'test_db' in result
        assert 'PostgreSQL' in result
        assert 'users' in result