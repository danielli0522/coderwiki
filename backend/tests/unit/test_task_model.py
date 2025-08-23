"""
任务模型单元测试
"""
import pytest
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from config import TestingConfig

class TestTask:
    
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
    
    def test_create_task(self):
        """测试创建任务"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0,
            title='Test Task',
            description='Test task description'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 验证任务创建成功
        assert task.id is not None
        assert task.user_id == self.user.id
        assert task.repository_id == self.repo.id
        assert task.type == 'generate_document'
        assert task.status == 'pending'
        assert task.progress == 0
    
    def test_task_to_dict(self):
        """测试任务转换为字典"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0,
            title='Test Task',
            description='Test task description'
        )
        
        db.session.add(task)
        db.session.commit()
        
        task_dict = task.to_dict()
        
        assert task_dict['id'] == task.id
        assert task_dict['user_id'] == self.user.id
        assert task_dict['repository_id'] == self.repo.id
        assert task_dict['type'] == 'generate_document'
        assert task_dict['status'] == 'pending'
        assert task_dict['progress'] == 0
    
    def test_task_repr(self):
        """测试任务字符串表示"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        repr_str = repr(task)
        assert 'Task' in repr_str
        assert 'generate_document' in repr_str
        assert 'pending' in repr_str
    
    def test_task_user_relationship(self):
        """测试任务与用户的关系"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 测试从任务访问用户
        assert task.user == self.user
        assert task.user.username == 'testuser'
        
        # 测试从用户访问任务
        user_tasks = self.user.tasks.all()
        assert len(user_tasks) == 1
        assert user_tasks[0] == task
    
    def test_task_repository_relationship(self):
        """测试任务与仓库的关系"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 测试从任务访问仓库
        assert task.repository == self.repo
        assert task.repository.name == 'test-repo'
        
        # 测试从仓库访问任务
        repo_tasks = self.repo.tasks.all()
        assert len(repo_tasks) == 1
        assert repo_tasks[0] == task
    
    def test_task_type_enum(self):
        """测试任务类型枚举"""
        # 测试不同类型
        task_types = ['generate_document', 'sync_repository', 'analyze_code']
        
        for task_type in task_types:
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type=task_type,
                status='pending'
            )
            db.session.add(task)
        
        db.session.commit()
        
        # 验证所有类型都创建成功
        tasks = Task.query.all()
        assert len(tasks) == len(task_types)
        
        for task in tasks:
            assert task.type in task_types
    
    def test_task_status_enum(self):
        """测试任务状态枚举"""
        # 测试不同状态
        statuses = ['pending', 'running', 'completed', 'failed']
        
        for status in statuses:
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status=status
            )
            db.session.add(task)
        
        db.session.commit()
        
        # 验证所有状态都创建成功
        tasks = Task.query.all()
        assert len(tasks) == len(statuses)
        
        for task in tasks:
            assert task.status in statuses
    
    def test_task_progress_validation(self):
        """测试任务进度验证"""
        # 测试进度范围
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=50
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 验证进度在有效范围内
        assert 0 <= task.progress <= 100
    
    def test_task_result_storage(self):
        """测试任务结果存储"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='completed',
            progress=100,
            result='{"document_id": 1, "file_path": "/docs/generated.md"}'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 验证结果存储成功
        assert task.result == '{"document_id": 1, "file_path": "/docs/generated.md"}'
        assert task.status == 'completed'
        assert task.progress == 100
    
    def test_task_error_handling(self):
        """测试任务错误处理"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='failed',
            progress=75,
            error_message='Failed to generate document: File not found'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 验证错误信息存储成功
        assert task.error_message == 'Failed to generate document: File not found'
        assert task.status == 'failed'
        assert task.progress == 75
    
    def test_task_timestamps(self):
        """测试任务时间戳"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 验证创建时间设置
        assert task.created_at is not None
        assert task.updated_at is not None
        
        # 模拟任务开始和完成
        task.started_at = datetime.utcnow()
        task.completed_at = datetime.utcnow()
        db.session.commit()
        
        # 验证时间戳更新
        assert task.started_at is not None
        assert task.completed_at is not None
    
    def test_task_validation_methods(self):
        """测试任务验证方法"""
        # 测试有效任务类型 - 通过实例验证
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        assert task.type in task.VALID_TYPES
        
        # 测试有效状态
        assert task.status in task.VALID_STATUSES
        
        # 测试状态转换
        assert task.can_transition_to('running') is True
        assert task.can_transition_to('failed') is True
        assert task.can_transition_to('pending') is False
        
        # 测试进度更新验证
        task.update_progress(50)
        assert task.progress == 50
    
    def test_task_status_transitions(self):
        """测试任务状态转换"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 测试有效状态转换
        assert task.can_transition_to('running') is True
        assert task.can_transition_to('failed') is True
        
        # 测试无效状态转换
        assert task.can_transition_to('pending') is False  # 不能从pending转到pending
        
        # 转换到running状态
        task.update_status('running')
        assert task.status == 'running'
        assert task.started_at is not None
        
        # 从running状态的转换
        assert task.can_transition_to('completed') is True
        assert task.can_transition_to('failed') is True
        assert task.can_transition_to('pending') is False
        
        # 转换到completed状态
        task.update_status('completed')
        assert task.status == 'completed'
        assert task.completed_at is not None
    
    def test_task_duration_methods(self):
        """测试任务持续时间方法"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 测试未开始任务的持续时间
        duration = task.get_duration()
        assert duration is not None
        assert duration >= 0
        
        # 模拟任务开始
        start_time = datetime.utcnow()
        task.started_at = start_time
        task.status = 'running'
        db.session.commit()
        
        # 测试运行中任务的持续时间
        duration = task.get_duration()
        assert duration is not None
        assert duration >= 0
        
        # 模拟任务完成
        end_time = datetime.utcnow()
        task.completed_at = end_time
        task.status = 'completed'
        db.session.commit()
        
        # 测试已完成任务的持续时间
        duration = task.get_duration()
        assert duration is not None
        assert duration >= 0
    
    def test_task_status_check_methods(self):
        """测试任务状态检查方法"""
        # 测试pending状态
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        assert task.is_pending() is True
        assert task.is_running() is False
        assert task.is_completed() is False
        assert task.is_failed() is False
        
        # 测试running状态
        task.status = 'running'
        assert task.is_pending() is False
        assert task.is_running() is True
        assert task.is_completed() is False
        assert task.is_failed() is False
        
        # 测试completed状态
        task.status = 'completed'
        assert task.is_pending() is False
        assert task.is_running() is False
        assert task.is_completed() is True
        assert task.is_failed() is False
        
        # 测试failed状态
        task.status = 'failed'
        assert task.is_pending() is False
        assert task.is_running() is False
        assert task.is_completed() is False
        assert task.is_failed() is True
        assert task.is_cancelled() is False
        
        # 测试cancelled状态
        task.status = 'cancelled'
        assert task.is_pending() is False
        assert task.is_running() is False
        assert task.is_completed() is False
        assert task.is_failed() is False
        assert task.is_cancelled() is True
    
    def test_task_retry_methods(self):
        """测试任务重试方法"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        # 测试pending任务的重试
        assert task.can_retry() is False
        
        # 测试running任务的重试
        task.status = 'running'
        assert task.can_retry() is False
        
        # 测试completed任务的重试
        task.status = 'completed'
        assert task.can_retry() is True  # completed tasks can be retried
        
        # 测试failed任务的重试
        task.status = 'failed'
        assert task.can_retry() is True  # failed tasks can be retried
        
        # 测试cancelled任务的重试
        task.status = 'cancelled'
        assert task.can_retry() is True  # cancelled tasks can be retried
    
    def test_task_status_info(self):
        """测试任务状态信息"""
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending',
            progress=0
        )
        
        status_info = task.get_status_info()
        
        assert isinstance(status_info, dict)
        assert status_info['status'] == 'pending'
        assert status_info['is_running'] is False
        assert status_info['is_completed'] is False
        assert status_info['is_failed'] is False
        assert 'can_retry' in status_info
        assert 'progress' in status_info
        assert status_info['progress'] == 0