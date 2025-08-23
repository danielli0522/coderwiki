"""
文档模型单元测试
"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.document import Document
from config import TestingConfig

class TestDocument:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('testpassword123')
        db.session.add(self.user)
        db.session.commit()
        
        # 创建测试仓库
        self.repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository'
        )
        db.session.add(self.repo)
        db.session.commit()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_document(self):
        """测试创建文档"""
        doc = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='# Test Document\n\nThis is a test document.',
            version='1.0.0',
            status='published',
            file_path='README.md',
            language='Markdown'
        )
        
        db.session.add(doc)
        db.session.commit()
        
        # 验证文档创建成功
        assert doc.id is not None
        assert doc.title == 'Test Document'
        assert doc.content == '# Test Document\n\nThis is a test document.'
        assert doc.version == '1.0.0'
        assert doc.status == 'published'
        assert doc.repository_id == self.repo.id
        assert doc.user_id == self.user.id
        assert doc.file_path == 'README.md'
        assert doc.language == 'Markdown'
    
    def test_document_to_dict(self):
        """测试文档转换为字典"""
        doc = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='# Test Document\n\nThis is a test document.',
            version='1.0.0',
            status='published'
        )
        
        db.session.add(doc)
        db.session.commit()
        
        doc_dict = doc.to_dict()
        
        assert doc_dict['id'] == doc.id
        assert doc_dict['repository_id'] == self.repo.id
        assert doc_dict['user_id'] == self.user.id
        assert doc_dict['title'] == 'Test Document'
        assert doc_dict['content'] == '# Test Document\n\nThis is a test document.'
        assert doc_dict['version'] == '1.0.0'
        assert doc_dict['status'] == 'published'
    
    def test_document_repr(self):
        """测试文档字符串表示"""
        doc = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='Test content',
            version='1.0.0'
        )
        
        repr_str = repr(doc)
        assert 'Document' in repr_str
        assert 'Test Document' in repr_str
        assert '1.0.0' in repr_str
    
    def test_document_repository_relationship(self):
        """测试文档与仓库的关系"""
        doc = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='Test content',
            version='1.0.0'
        )
        
        db.session.add(doc)
        db.session.commit()
        
        # 测试从文档访问仓库
        assert doc.repository == self.repo
        assert doc.repository.name == 'test-repo'
        
        # 测试从仓库访问文档
        repo_docs = self.repo.documents.all()
        assert len(repo_docs) == 1
        assert repo_docs[0] == doc
    
    def test_document_user_relationship(self):
        """测试文档与用户的关系"""
        doc = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='Test content',
            version='1.0.0'
        )
        
        db.session.add(doc)
        db.session.commit()
        
        # 测试从文档访问用户
        assert doc.user == self.user
        assert doc.user.username == 'testuser'
        
        # 测试从用户访问文档
        user_docs = self.user.documents.all()
        assert len(user_docs) == 1
        assert user_docs[0] == doc
    
    def test_document_status_enum(self):
        """测试文档状态枚举"""
        # 测试不同状态
        statuses = ['draft', 'published', 'archived']
        
        for status in statuses:
            doc = Document(
                repository_id=self.repo.id,
                user_id=self.user.id,
                title=f'Document {status}',
                content='Test content',
                version='1.0.0',
                status=status
            )
            db.session.add(doc)
        
        db.session.commit()
        
        # 验证所有状态都创建成功
        docs = Document.query.all()
        assert len(docs) == len(statuses)
        
        for doc in docs:
            assert doc.status in statuses
    
    def test_document_version_management(self):
        """测试文档版本管理"""
        # 创建不同版本的文档
        doc1 = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='Version 1 content',
            version='1.0.0'
        )
        
        doc2 = Document(
            repository_id=self.repo.id,
            user_id=self.user.id,
            title='Test Document',
            content='Version 2 content',
            version='2.0.0'
        )
        
        db.session.add(doc1)
        db.session.add(doc2)
        db.session.commit()
        
        # 验证版本创建成功
        assert doc1.version == '1.0.0'
        assert doc2.version == '2.0.0'
        assert doc1.id != doc2.id