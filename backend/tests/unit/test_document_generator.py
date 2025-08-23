"""
Unit tests for document generator service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app import create_app, db
from config import TestingConfig
from app.models.user import User
from app.models.repository import Repository
from app.models.llm_config import LLMConfig
from app.models.task import Task
from app.models.document import Document
from app.services.document_generator import DocumentGenerator
from app.services.llm_service import LLMService
from app.services.repository_service import RepositoryService

class TestDocumentGenerator:
    """文档生成器测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试用户
        self.user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(self.user)
        db.session.flush()  # Ensure user has an ID
        
        # 创建测试仓库
        self.repository = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            local_path='/tmp/test-repo',
            description='Test repository',
            language='Python',
            status='active'
        )
        db.session.add(self.repository)
        
        # 创建测试LLM配置
        from werkzeug.security import generate_password_hash
        self.llm_config = LLMConfig(
            user_id=self.user.id,
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key_encrypted=generate_password_hash('test-api-key', method='pbkdf2:sha256:100000')
        )
        db.session.add(self.llm_config)
        
        db.session.commit()
        
        self.document_generator = DocumentGenerator()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_generate_document_success(self):
        """测试成功生成文档"""
        with patch('app.services.document_generator.LLMService') as mock_llm_service:
            with patch('app.services.document_generator.Repository') as mock_repository_model:
                with patch('app.utils.repository_analyzer.RepositoryAnalyzer') as mock_analyzer:
                    # Mock LLM服务
                    mock_llm_instance = Mock()
                    mock_llm_instance.get_llm_client_for_user.return_value = Mock()
                    mock_llm_service.return_value = mock_llm_instance
                    
                    # Mock Repository model query
                    mock_repository_model.query.filter_by.return_value.first.return_value = self.repository
                    
                    # Mock repository analyzer
                    mock_analyzer_instance = Mock()
                    mock_analyzer_instance.analyze_repository.return_value = {
                        'project_name': 'test-repo',
                        'tech_stack': 'Python, Flask',
                        'project_type': 'Web Application',
                        'analysis_results': 'Simple web application'
                    }
                    mock_analyzer.return_value = mock_analyzer_instance
                    
                    # Mock LLM客户端
                    mock_client = Mock()
                    mock_client.chat.return_value = """
# 项目概述

## 项目简介
test-repo 是一个基于 Python, Flask 的 Web 应用程序。

## 技术栈
- **后端**: Python, Flask
- **数据库**: SQLite
- **前端**: HTML, CSS, JavaScript

## 主要功能
- 用户管理
- 数据存储
- API接口

## 项目特点
- 简单易用
- 扩展性强
- 性能良好
"""
                    mock_llm_instance.get_llm_client_for_user.return_value = mock_client
                
                # 生成文档
                result = self.document_generator.generate_document(
                    repository_id=self.repository.id,
                    user_id=self.user.id,
                    llm_config_id=self.llm_config.id,
                    doc_type='overview',
                    doc_title='Test Project Overview'
                )
                
                assert result['success'] is True
                assert 'task_id' in result
                assert 'message' in result
                assert result['doc_type'] == 'overview'
                
                # 验证任务已创建
                task = Task.query.filter_by(
                    user_id=self.user.id,
                    task_type='document_generation'
                ).first()
                assert task is not None
                assert task.status == 'pending'
    
    def test_generate_document_invalid_config(self):
        """测试使用无效配置生成文档"""
        # 使用不存在的配置ID
        result = self.document_generator.generate_document(
            repository_id=self.repository.id,
            user_id=self.user.id,
            llm_config_id=999,
            doc_type='overview'
        )
        
        assert result['success'] is False
        assert 'LLM configuration not found' in result['error']
    
    def test_generate_document_invalid_repository(self):
        """测试使用无效仓库生成文档"""
        # 使用不存在的仓库ID
        result = self.document_generator.generate_document(
            repository_id=999,
            user_id=self.user.id,
            llm_config_id=self.llm_config.id,
            doc_type='overview'
        )
        
        assert result['success'] is False
        assert 'Repository not found' in result['error']
    
    def test_generate_document_invalid_doc_type(self):
        """测试使用无效文档类型生成文档"""
        result = self.document_generator.generate_document(
            repository_id=self.repository.id,
            user_id=self.user.id,
            llm_config_id=self.llm_config.id,
            doc_type='invalid_type'
        )
        
        assert result['success'] is False
        assert 'Invalid document type' in result['error']
    
    def test_get_generation_status_success(self):
        """测试获取生成状态成功"""
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            task_type='document_generation',
            status='processing',
            progress=50,
            result_data={'doc_id': 1}
        )
        db.session.add(task)
        db.session.commit()
        
        # 获取状态
        result = self.document_generator.get_generation_status(task.id, self.user.id)
        
        assert result['success'] is True
        assert result['status'] == 'processing'
        assert result['progress'] == 50
        assert result['result_data']['doc_id'] == 1
    
    def test_get_generation_status_not_found(self):
        """测试获取不存在的任务状态"""
        result = self.document_generator.get_generation_status(999, self.user.id)
        
        assert result['success'] is False
        assert 'Task not found' in result['error']
    
    def test_get_generation_status_unauthorized(self):
        """测试获取其他用户的任务状态"""
        # 创建其他用户的任务
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password_hash='hashed_password'
        )
        db.session.add(other_user)
        
        task = Task(
            user_id=other_user.id,
            task_type='document_generation',
            status='completed'
        )
        db.session.add(task)
        db.session.commit()
        
        # 尝试获取其他用户的任务
        result = self.document_generator.get_generation_status(task.id, self.user.id)
        
        assert result['success'] is False
        assert 'Task not found' in result['error']
    
    def test_get_user_documents_success(self):
        """测试获取用户文档成功"""
        # 创建测试文档
        doc1 = Document(
            user_id=self.user.id,
            repository_id=self.repository.id,
            title='Document 1',
            content='Content 1',
            doc_type='overview',
            llm_config_id=self.llm_config.id
        )
        doc2 = Document(
            user_id=self.user.id,
            repository_id=self.repository.id,
            title='Document 2',
            content='Content 2',
            doc_type='api',
            llm_config_id=self.llm_config.id
        )
        
        db.session.add(doc1)
        db.session.add(doc2)
        db.session.commit()
        
        # 获取所有文档
        documents = self.document_generator.get_user_documents(self.user.id)
        assert len(documents) == 2
        
        # 按仓库过滤
        repo_docs = self.document_generator.get_user_documents(
            self.user.id,
            repository_id=self.repository.id
        )
        assert len(repo_docs) == 2
        
        # 按类型过滤
        overview_docs = self.document_generator.get_user_documents(
            self.user.id,
            doc_type='overview'
        )
        assert len(overview_docs) == 1
        assert overview_docs[0].doc_type == 'overview'
        
        # 限制数量
        limited_docs = self.document_generator.get_user_documents(
            self.user.id,
            limit=1
        )
        assert len(limited_docs) == 1
    
    def test_get_document_by_id_success(self):
        """测试根据ID获取文档成功"""
        # 创建测试文档
        doc = Document(
            user_id=self.user.id,
            repository_id=self.repository.id,
            title='Test Document',
            content='Test Content',
            doc_type='overview',
            llm_config_id=self.llm_config.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # 获取文档
        document = self.document_generator.get_document_by_id(doc.id, self.user.id)
        
        assert document is not None
        assert document.id == doc.id
        assert document.title == 'Test Document'
        assert document.user_id == self.user.id
    
    def test_get_document_by_id_not_found(self):
        """测试获取不存在的文档"""
        document = self.document_generator.get_document_by_id(999, self.user.id)
        assert document is None
    
    def test_get_document_by_id_unauthorized(self):
        """测试获取其他用户的文档"""
        # 创建其他用户的文档
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password_hash='hashed_password'
        )
        db.session.add(other_user)
        
        doc = Document(
            user_id=other_user.id,
            repository_id=self.repository.id,
            title='Other Document',
            content='Other Content',
            doc_type='overview',
            llm_config_id=self.llm_config.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # 尝试获取其他用户的文档
        document = self.document_generator.get_document_by_id(doc.id, self.user.id)
        assert document is None
    
    @patch('app.services.document_generator.threading.Thread')
    def test_background_document_generation(self, mock_thread):
        """测试后台文档生成"""
        with patch('app.services.document_generator.LLMService') as mock_llm_service:
            with patch('app.services.document_generator.Repository') as mock_repository_model:
                # Mock服务
                mock_llm_instance = Mock()
                mock_llm_instance.get_llm_client_for_user.return_value = Mock()
                mock_llm_service.return_value = mock_llm_instance
                
                # Mock Repository model query
                mock_repository_model.query.filter_by.return_value.first.return_value = self.repository
                
                # 生成文档
                result = self.document_generator.generate_document(
                    repository_id=self.repository.id,
                    user_id=self.user.id,
                    llm_config_id=self.llm_config.id,
                    doc_type='overview'
                )
                
                # 验证线程已启动
                mock_thread.assert_called_once()
                assert result['success'] is True
    
    def test_process_document_generation_success(self):
        """测试处理文档生成成功"""
        with patch('app.services.document_generator.LLMService') as mock_llm_service:
            with patch('app.services.document_generator.Repository') as mock_repository_model:
                # Mock服务
                mock_llm_instance = Mock()
                mock_llm_service.return_value = mock_llm_instance
                
                # Mock Repository model query
                mock_repository_model.query.filter_by.return_value.first.return_value = self.repository
                
                # Mock LLM客户端
                mock_client = Mock()
                mock_client.chat.return_value = """
# 项目概述

## 项目简介
test-repo 是一个基于 Python, Flask 的 Web 应用程序。

## 主要功能
- 用户管理
- 数据存储
"""
                mock_llm_instance.get_llm_client_for_user.return_value = mock_client
                
                # 创建任务
                task = Task(
                    user_id=self.user.id,
                    task_type='document_generation',
                    status='pending',
                    task_data={
                        'repository_id': self.repository.id,
                        'llm_config_id': self.llm_config.id,
                        'doc_type': 'overview',
                        'doc_title': 'Test Document'
                    }
                )
                db.session.add(task)
                db.session.commit()
                
                # 处理生成
                self.document_generator._process_document_generation(task.id)
                
                # 验证任务状态
                updated_task = Task.query.get(task.id)
                assert updated_task.status == 'completed'
                assert updated_task.progress == 100
                
                # 验证文档已创建
                document = Document.query.filter_by(
                    user_id=self.user.id,
                    repository_id=self.repository.id,
                    doc_type='overview'
                ).first()
                assert document is not None
                assert document.title == 'Test Document'
                assert 'test-repo' in document.content
    
    def test_process_document_generation_failure(self):
        """测试处理文档生成失败"""
        with patch('app.services.document_generator.LLMService') as mock_llm_service:
            with patch('app.services.document_generator.Repository') as mock_repository_model:
                # Mock服务失败
                mock_llm_instance = Mock()
                mock_llm_instance.get_llm_client_for_user.return_value = None
                mock_llm_service.return_value = mock_llm_instance
                
                mock_repo_instance = Mock()
                mock_repo_instance.get_repository.return_value = self.repository
                mock_repository_model.return_value = mock_repo_instance
                
                # 创建任务
                task = Task(
                    user_id=self.user.id,
                    task_type='document_generation',
                    status='pending',
                    task_data={
                        'repository_id': self.repository.id,
                        'llm_config_id': self.llm_config.id,
                        'doc_type': 'overview'
                    }
                )
                db.session.add(task)
                db.session.commit()
                
                # 处理生成
                self.document_generator._process_document_generation(task.id)
                
                # 验证任务状态
                updated_task = Task.query.get(task.id)
                assert updated_task.status == 'failed'
                assert 'error' in updated_task.result_data
    
    def test_get_prompt_template_success(self):
        """测试获取提示词模板成功"""
        template = self.document_generator._get_prompt_template('overview')
        
        assert template is not None
        assert 'project_name' in template
        assert 'tech_stack' in template
        assert 'project_type' in template
        assert 'analysis_results' in template
    
    def test_get_prompt_template_invalid_type(self):
        """测试获取无效类型的提示词模板"""
        template = self.document_generator._get_prompt_template('invalid_type')
        assert template is None
    
    def test_create_document_from_content_success(self):
        """测试从内容创建文档成功"""
        content = """
# Test Document

This is a test document content.
"""
        
        document = self.document_generator._create_document_from_content(
            content=content,
            user_id=self.user.id,
            repository_id=self.repository.id,
            doc_type='overview',
            doc_title='Test Document',
            llm_config_id=self.llm_config.id
        )
        
        assert document is not None
        assert document.title == 'Test Document'
        assert document.content == content
        assert document.doc_type == 'overview'
        assert document.user_id == self.user.id
        assert document.repository_id == self.repository.id
        assert document.llm_config_id == self.llm_config.id
    
    def test_update_task_status_success(self):
        """测试更新任务状态成功"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            task_type='document_generation',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 更新状态
        self.document_generator._update_task_status(
            task_id=task.id,
            status='processing',
            progress=50,
            result_data={'current_step': 'analyzing'}
        )
        
        # 验证更新
        updated_task = Task.query.get(task.id)
        assert updated_task.status == 'processing'
        assert updated_task.progress == 50
        assert updated_task.result_data['current_step'] == 'analyzing'
    
    def test_update_task_status_not_found(self):
        """测试更新不存在的任务状态"""
        # 应该不抛出异常
        self.document_generator._update_task_status(
            task_id=999,
            status='processing'
        )
    
    def test_validate_task_data_success(self):
        """测试验证任务数据成功"""
        task_data = {
            'repository_id': self.repository.id,
            'llm_config_id': self.llm_config.id,
            'doc_type': 'overview'
        }
        
        is_valid = self.document_generator._validate_task_data(task_data)
        assert is_valid is True
    
    def test_validate_task_data_missing_fields(self):
        """测试验证任务数据缺少字段"""
        task_data = {
            'repository_id': self.repository.id
            # 缺少 llm_config_id 和 doc_type
        }
        
        is_valid = self.document_generator._validate_task_data(task_data)
        assert is_valid is False
    
    def test_validate_task_data_invalid_values(self):
        """测试验证任务数据无效值"""
        task_data = {
            'repository_id': 999,  # 不存在的仓库
            'llm_config_id': self.llm_config.id,
            'doc_type': 'invalid_type'  # 无效类型
        }
        
        is_valid = self.document_generator._validate_task_data(task_data)
        assert is_valid is False