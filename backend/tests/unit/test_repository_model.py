"""
仓库模型单元测试
"""
import pytest
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from config import TestingConfig

class TestRepository:
    
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
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_repository(self):
        """测试创建仓库"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository',
            language='Python'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        # 验证仓库创建成功
        assert repo.id is not None
        assert repo.name == 'test-repo'
        assert repo.url == 'https://github.com/test/test-repo.git'
        assert repo.description == 'Test repository'
        assert repo.language == 'Python'
        assert repo.status == 'active'
        assert repo.user_id == self.user.id
    
    def test_repository_to_dict(self):
        """测试仓库转换为字典"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository',
            language='Python'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        repo_dict = repo.to_dict()
        
        assert repo_dict['id'] == repo.id
        assert repo_dict['user_id'] == self.user.id
        assert repo_dict['name'] == 'test-repo'
        assert repo_dict['url'] == 'https://github.com/test/test-repo.git'
        assert repo_dict['description'] == 'Test repository'
        assert repo_dict['language'] == 'Python'
        assert repo_dict['status'] == 'active'
    
    def test_repository_repr(self):
        """测试仓库字符串表示"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git'
        )
        
        repr_str = repr(repo)
        assert 'Repository' in repr_str
        assert 'test-repo' in repr_str
    
    def test_repository_user_relationship(self):
        """测试仓库与用户的关系"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        # 测试从仓库访问用户
        assert repo.user == self.user
        assert repo.user.username == 'testuser'
        
        # 测试从用户访问仓库
        user_repos = self.user.repositories.all()
        assert len(user_repos) == 1
        assert user_repos[0] == repo
    
    def test_unique_constraint_per_user(self):
        """测试用户唯一仓库约束"""
        # 创建第一个仓库
        repo1 = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git'
        )
        
        db.session.add(repo1)
        db.session.commit()
        
        # 尝试创建相同URL的仓库
        repo2 = Repository(
            user_id=self.user.id,
            name='test-repo-2',
            url='https://github.com/test/test-repo.git'
        )
        
        db.session.add(repo2)
        
        # 应该抛出完整性错误
        with pytest.raises(Exception):
            db.session.commit()
    
    def test_different_users_same_url(self):
        """测试不同用户可以使用相同URL"""
        # 创建另一个用户
        user2 = User(username='user2', email='user2@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        db.session.commit()
        
        # 两个用户创建相同URL的仓库
        repo1 = Repository(
            user_id=self.user.id,
            name='repo1',
            url='https://github.com/test/same-repo.git'
        )
        
        repo2 = Repository(
            user_id=user2.id,
            name='repo2',
            url='https://github.com/test/same-repo.git'
        )
        
        db.session.add(repo1)
        db.session.add(repo2)
        db.session.commit()
        
        # 应该成功
        assert repo1.id is not None
        assert repo2.id is not None
        assert repo1.user_id != repo2.user_id
    
    def test_validate_github_url(self):
        """测试GitHub URL验证"""
        # 有效的GitHub URLs
        assert Repository.validate_github_url('https://github.com/user/repo')
        assert Repository.validate_github_url('http://github.com/user/repo')
        assert Repository.validate_github_url('https://github.com/user/repo/')
        
        # 无效的GitHub URLs
        assert not Repository.validate_github_url('https://gitlab.com/user/repo')
        assert not Repository.validate_github_url('invalid-url')
        assert not Repository.validate_github_url('')
    
    def test_validate_git_url(self):
        """测试Git URL验证"""
        # 有效的Git URLs
        assert Repository.validate_git_url('https://github.com/user/repo.git')
        assert Repository.validate_git_url('http://github.com/user/repo.git')
        assert Repository.validate_git_url('git://github.com/user/repo.git')
        
        # 无效的Git URLs
        assert not Repository.validate_git_url('https://github.com/user/repo')
        assert not Repository.validate_git_url('invalid-url')
        assert not Repository.validate_git_url('')
    
    def test_update_clone_status(self):
        """测试克隆状态更新"""
        import time
        
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        original_updated_at = repo.updated_at
        
        # 等待一小段时间确保时间戳不同
        time.sleep(0.01)
        
        # 更新状态（无错误）
        repo.update_clone_status('cloning')
        db.session.commit()
        
        assert repo.clone_status == 'cloning'
        assert repo.clone_error is None
        assert repo.updated_at is not None
        
        # 更新状态（有错误）
        repo.update_clone_status('failed', '克隆失败')
        db.session.commit()
        
        assert repo.clone_status == 'failed'
        assert repo.clone_error == '克隆失败'
    
    def test_update_repository_info(self):
        """测试仓库信息更新"""
        import time
        
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        original_updated_at = repo.updated_at
        
        # 等待一小段时间确保时间戳不同
        time.sleep(0.01)
        
        metadata = {'language': 'Python', 'framework': 'Flask'}
        repo.update_repository_info(
            commit_hash='abc123',
            repo_size=1024,
            file_count=10,
            metadata=metadata
        )
        db.session.commit()
        
        assert repo.commit_hash == 'abc123'
        assert repo.repo_size == 1024
        assert repo.file_count == 10
        assert repo.repo_metadata == metadata
        assert repo.updated_at is not None
    
    def test_is_ready_for_analysis(self):
        """测试仓库分析准备状态检查"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        # 未准备好 - 缺少必需字段
        assert not repo.is_ready_for_analysis()
        
        # 仍然未准备好 - 只有本地路径
        repo.local_path = '/path/to/repo'
        db.session.commit()
        assert not repo.is_ready_for_analysis()
        
        # 仍然未准备好 - 只有提交哈希
        repo.local_path = None
        repo.commit_hash = 'abc123'
        db.session.commit()
        assert not repo.is_ready_for_analysis()
        
        # 准备好 - 所有必需字段都存在
        repo.local_path = '/path/to/repo'
        repo.clone_status = 'completed'
        db.session.commit()
        assert repo.is_ready_for_analysis()
    
    def test_get_repository_name_from_url(self):
        """测试从URL提取仓库名称"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        
        # 测试GitHub URL
        repo.url = 'https://github.com/user/my-repo'
        assert repo.get_repository_name_from_url() == 'my-repo'
        
        # 测试带.git的GitHub URL
        repo.url = 'https://github.com/user/my-repo.git'
        assert repo.get_repository_name_from_url() == 'my-repo'
        
        # 测试非GitHub URL
        repo.url = 'https://gitlab.com/user/my-repo.git'
        assert repo.get_repository_name_from_url() == 'my-repo'
    
    def test_new_fields_defaults(self):
        """测试新字段的默认值"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo'
        )
        db.session.add(repo)
        db.session.commit()
        
        # 检查新字段的默认值
        assert repo.branch == 'main'
        assert repo.is_private is False
        assert repo.clone_status == 'pending'
        assert repo.local_path is None
        assert repo.commit_hash is None
        assert repo.repo_size is None
        assert repo.file_count is None
        assert repo.clone_error is None
        assert repo.repo_metadata is None
    
    def test_to_dict_with_new_fields(self):
        """测试包含新字段的to_dict方法"""
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            description='Test repository',
            local_path='/path/to/repo',
            branch='main',
            commit_hash='abc123',
            repo_size=1024,
            file_count=10,
            is_private=False,
            clone_status='completed',
            repo_metadata={'language': 'Python'}
        )
        db.session.add(repo)
        db.session.commit()
        
        repo_dict = repo.to_dict()
        
        # 验证新字段包含在字典中
        assert 'local_path' in repo_dict
        assert 'branch' in repo_dict
        assert 'commit_hash' in repo_dict
        assert 'repo_size' in repo_dict
        assert 'file_count' in repo_dict
        assert 'is_private' in repo_dict
        assert 'clone_status' in repo_dict
        assert 'clone_error' in repo_dict
        assert 'metadata' in repo_dict
        
        # 验证字段值
        assert repo_dict['local_path'] == '/path/to/repo'
        assert repo_dict['branch'] == 'main'
        assert repo_dict['commit_hash'] == 'abc123'
        assert repo_dict['repo_size'] == 1024
        assert repo_dict['file_count'] == 10
        assert repo_dict['is_private'] is False
        assert repo_dict['clone_status'] == 'completed'
        assert repo_dict['metadata'] == {'language': 'Python'}