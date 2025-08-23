"""
数据库操作集成测试
"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.document import Document
from app.models.task import Task
from config import TestingConfig

class TestDatabaseOperations:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_complete_user_workflow(self):
        """测试完整的用户工作流程"""
        # 1. 创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        # 2. 创建仓库
        repo = Repository(
            user_id=user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository'
        )
        db.session.add(repo)
        db.session.commit()
        
        # 3. 创建文档
        doc = Document(
            repository_id=repo.id,
            user_id=user.id,
            title='Test Document',
            content='# Test Document\n\nThis is a test document.',
            version='1.0.0'
        )
        db.session.add(doc)
        db.session.commit()
        
        # 4. 创建任务
        task = Task(
            user_id=user.id,
            repository_id=repo.id,
            type='generate_document',
            status='completed'
        )
        db.session.add(task)
        db.session.commit()
        
        # 5. 验证数据完整性
        assert user.id is not None
        assert repo.id is not None
        assert doc.id is not None
        assert task.id is not None
        
        # 6. 验证关系
        assert repo.user_id == user.id
        assert doc.repository_id == repo.id
        assert doc.user_id == user.id
        assert task.user_id == user.id
        assert task.repository_id == repo.id
        
        # 7. 验证查询
        user_repos = user.repositories.all()
        assert len(user_repos) == 1
        assert user_repos[0] == repo
        
        repo_docs = repo.documents.all()
        assert len(repo_docs) == 1
        assert repo_docs[0] == doc
        
        user_docs = user.documents.all()
        assert len(user_docs) == 1
        assert user_docs[0] == doc
        
        repo_tasks = repo.tasks.all()
        assert len(repo_tasks) == 1
        assert repo_tasks[0] == task
        
        user_tasks = user.tasks.all()
        assert len(user_tasks) == 1
        assert user_tasks[0] == task
    
    def test_cascade_delete(self):
        """测试级联删除"""
        # 1. 创建用户和相关数据
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        repo = Repository(
            user_id=user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git'
        )
        db.session.add(repo)
        db.session.commit()
        
        doc = Document(
            repository_id=repo.id,
            user_id=user.id,
            title='Test Document',
            content='Test content',
            version='1.0.0'
        )
        db.session.add(doc)
        db.session.commit()
        
        task = Task(
            user_id=user.id,
            repository_id=repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 2. 记录ID
        user_id = user.id
        repo_id = repo.id
        doc_id = doc.id
        task_id = task.id
        
        # 3. 删除用户
        db.session.delete(user)
        db.session.commit()
        
        # 4. 验证级联删除
        assert User.query.get(user_id) is None
        assert Repository.query.get(repo_id) is None
        assert Document.query.get(doc_id) is None
        assert Task.query.get(task_id) is None
    
    def test_database_constraints(self):
        """测试数据库约束"""
        # 1. 创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        # 2. 测试用户名唯一约束
        user2 = User(username='testuser', email='test2@example.com')
        user2.set_password('testpassword123')
        db.session.add(user2)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # 3. 测试邮箱唯一约束
        user3 = User(username='testuser2', email='test@example.com')
        user3.set_password('testpassword123')
        db.session.add(user3)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # 4. 测试仓库URL唯一约束（同一用户）
        repo1 = Repository(
            user_id=user.id,
            name='repo1',
            url='https://github.com/test/same.git'
        )
        db.session.add(repo1)
        db.session.commit()
        
        repo2 = Repository(
            user_id=user.id,
            name='repo2',
            url='https://github.com/test/same.git'
        )
        db.session.add(repo2)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()
    
    def test_bulk_operations(self):
        """测试批量操作"""
        # 1. 创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        # 2. 批量创建仓库
        repositories = []
        for i in range(5):
            repo = Repository(
                user_id=user.id,
                name=f'repo-{i}',
                url=f'https://github.com/test/repo-{i}.git',
                description=f'Repository {i}'
            )
            repositories.append(repo)
        
        db.session.add_all(repositories)
        db.session.commit()
        
        # 3. 验证批量创建
        assert len(user.repositories.all()) == 5
        
        # 4. 批量创建文档
        documents = []
        for i, repo in enumerate(repositories):
            doc = Document(
                repository_id=repo.id,
                user_id=user.id,
                title=f'Document {i}',
                content=f'Content for document {i}',
                version='1.0.0'
            )
            documents.append(doc)
        
        db.session.add_all(documents)
        db.session.commit()
        
        # 5. 验证批量创建
        assert len(user.documents.all()) == 5
        
        # 6. 批量查询
        all_repos = Repository.query.filter_by(user_id=user.id).all()
        assert len(all_repos) == 5
        
        all_docs = Document.query.filter_by(user_id=user.id).all()
        assert len(all_docs) == 5
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        # 1. 创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        user_id = user.id
        
        # 2. 开始事务
        try:
            # 创建正常数据
            repo = Repository(
                user_id=user.id,
                name='test-repo',
                url='https://github.com/test/test-repo.git'
            )
            db.session.add(repo)
            
            # 创建会导致错误的数据
            invalid_repo = Repository(
                user_id=user.id,
                name=None,  # 违反非空约束
                url='https://github.com/test/invalid.git'
            )
            db.session.add(invalid_repo)
            
            db.session.commit()
            
        except Exception:
            # 回滚事务
            db.session.rollback()
        
        # 3. 验证回滚
        assert User.query.get(user_id) is not None  # 用户应该还在
        assert Repository.query.filter_by(user_id=user.id).count() == 0  # 仓库应该被回滚
    
    def test_data_integrity(self):
        """测试数据完整性"""
        # 1. 创建完整的关联数据
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        repo = Repository(
            user_id=user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git'
        )
        db.session.add(repo)
        db.session.commit()
        
        doc = Document(
            repository_id=repo.id,
            user_id=user.id,
            title='Test Document',
            content='Test content',
            version='1.0.0'
        )
        db.session.add(doc)
        db.session.commit()
        
        task = Task(
            user_id=user.id,
            repository_id=repo.id,
            type='generate_document',
            status='completed'
        )
        db.session.add(task)
        db.session.commit()
        
        # 2. 验证非空约束
        invalid_repo = Repository(
            user_id=user.id,
            name=None,  # 违反非空约束
            url='https://github.com/test/invalid.git'
        )
        db.session.add(invalid_repo)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # 3. 验证数据一致性
        assert User.query.count() == 1
        assert Repository.query.count() == 1
        assert Document.query.count() == 1
        assert Task.query.count() == 1
        
        # 4. 验证关系完整性
        saved_repo = Repository.query.first()
        assert saved_repo.user_id == user.id
        
        saved_doc = Document.query.first()
        assert saved_doc.repository_id == repo.id
        assert saved_doc.user_id == user.id
        
        saved_task = Task.query.first()
        assert saved_task.user_id == user.id
        assert saved_task.repository_id == repo.id