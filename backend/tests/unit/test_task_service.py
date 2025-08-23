"""
Task Service Unit Tests
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.task_service import TaskService
from app.models.task import Task
from app import create_app, db
from config import TestingConfig


class TestTaskService:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户
        from app.models.user import User
        from app.models.repository import Repository
        
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('testpassword123')
        db.session.add(self.user)
        
        # 创建测试仓库
        self.repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository'
        )
        db.session.add(self.repo)
        db.session.commit()
        
        # 创建任务服务
        self.task_service = TaskService()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_task(self):
        """测试创建任务"""
        # 创建任务
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document'
        )
        
        # 验证任务创建成功
        assert task.id is not None
        assert task.user_id == self.user.id
        assert task.repository_id == self.repo.id
        assert task.type == 'generate_document'
        assert task.status == 'pending'
        assert task.progress == 0
    
    def test_create_task_invalid_type(self):
        """测试创建无效类型的任务"""
        with pytest.raises(ValueError):
            self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='invalid_type'
            )
    
    def test_create_task_invalid_repository(self):
        """测试创建无效仓库的任务"""
        with pytest.raises(ValueError):
            self.task_service.create_task(
                user_id=self.user.id,
                repository_id=999,  # 不存在的仓库
                task_type='generate_document'
            )
    
    def test_get_task_by_id(self):
        """测试根据ID获取任务"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 获取任务
        retrieved_task = self.task_service.get_task_by_id(task.id, self.user.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.user_id == self.user.id
    
    def test_get_task_by_id_unauthorized(self):
        """测试获取未授权的任务"""
        # 创建另一个用户
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 尝试用其他用户获取任务
        retrieved_task = self.task_service.get_task_by_id(task.id, other_user.id)
        
        assert retrieved_task is None
    
    def test_get_user_tasks(self):
        """测试获取用户任务"""
        # 创建多个任务
        tasks = []
        for i in range(3):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='pending'
            )
            db.session.add(task)
            tasks.append(task)
        
        # 创建其他用户的任务
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        
        other_task = Task(
            user_id=other_user.id,
            repository_id=self.repo.id,
            type='sync_repository',
            status='pending'
        )
        db.session.add(other_task)
        db.session.commit()
        
        # 获取用户任务
        user_tasks = self.task_service.get_user_tasks(self.user.id)
        
        assert len(user_tasks) == 3
        for task in user_tasks:
            assert task.user_id == self.user.id
    
    def test_get_user_tasks_with_filters(self):
        """测试带过滤条件获取用户任务"""
        # 创建不同状态的任务
        tasks = [
            Task(user_id=self.user.id, repository_id=self.repo.id, type='generate_document', status='pending'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='sync_repository', status='running'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='analyze_code', status='completed')
        ]
        
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        
        # 按状态过滤
        pending_tasks = self.task_service.get_user_tasks(
            user_id=self.user.id,
            status='pending'
        )
        assert len(pending_tasks) == 1
        assert pending_tasks[0].status == 'pending'
        
        # 按类型过滤
        sync_tasks = self.task_service.get_user_tasks(
            user_id=self.user.id,
            task_type='sync_repository'
        )
        assert len(sync_tasks) == 1
        assert sync_tasks[0].type == 'sync_repository'
        
        # 按仓库过滤
        repo_tasks = self.task_service.get_user_tasks(
            user_id=self.user.id,
            repository_id=self.repo.id
        )
        assert len(repo_tasks) == 3
    
    def test_update_task_status(self):
        """测试更新任务状态"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 更新状态
        updated_task = self.task_service.update_task_status(
            task.id,
            'running',
            user_id=self.user.id
        )
        
        assert updated_task is not None
        assert updated_task.status == 'running'
        assert updated_task.started_at is not None
    
    def test_update_task_progress(self):
        """测试更新任务进度"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            progress=0
        )
        db.session.add(task)
        db.session.commit()
        
        # 更新进度
        updated_task = self.task_service.update_task_progress(
            task.id,
            50,
            user_id=self.user.id
        )
        
        assert updated_task is not None
        assert updated_task.progress == 50
    
    def test_update_task_progress_invalid_value(self):
        """测试更新无效进度值"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            progress=0
        )
        db.session.add(task)
        db.session.commit()
        
        # 测试无效进度值
        with pytest.raises(ValueError):
            self.task_service.update_task_progress(
                task.id,
                -1,
                user_id=self.user.id
            )
        
        with pytest.raises(ValueError):
            self.task_service.update_task_progress(
                task.id,
                101,
                user_id=self.user.id
            )
    
    def test_complete_task(self):
        """测试完成任务"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            progress=50
        )
        db.session.add(task)
        db.session.commit()
        
        # 完成任务
        result = '{"document_id": 1, "file_path": "/docs/generated.md"}'
        completed_task = self.task_service.complete_task(
            task.id,
            result,
            user_id=self.user.id
        )
        
        assert completed_task is not None
        assert completed_task.status == 'completed'
        assert completed_task.progress == 100
        assert completed_task.result == result
        assert completed_task.completed_at is not None
    
    def test_fail_task(self):
        """测试任务失败"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            progress=50
        )
        db.session.add(task)
        db.session.commit()
        
        # 标记任务失败
        error_message = "Failed to generate document"
        failed_task = self.task_service.fail_task(
            task.id,
            error_message,
            user_id=self.user.id
        )
        
        assert failed_task is not None
        assert failed_task.status == 'failed'
        assert failed_task.error_message == error_message
        assert failed_task.completed_at is not None
    
    def test_delete_task(self):
        """测试删除任务"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        task_id = task.id
        
        # 删除任务
        result = self.task_service.delete_task(task_id, self.user.id)
        
        assert result is True
        
        # 验证任务已删除
        deleted_task = Task.query.get(task_id)
        assert deleted_task is None
    
    def test_delete_task_unauthorized(self):
        """测试删除未授权的任务"""
        # 创建另一个用户
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 尝试用其他用户删除任务
        result = self.task_service.delete_task(task.id, other_user.id)
        
        assert result is False
        
        # 验证任务仍然存在
        existing_task = Task.query.get(task.id)
        assert existing_task is not None
    
    def test_get_pending_tasks(self):
        """测试获取待处理任务"""
        # 创建多个待处理任务
        pending_tasks = []
        for i in range(3):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='pending'
            )
            db.session.add(task)
            pending_tasks.append(task)
        
        # 创建其他状态的任务
        running_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='sync_repository',
            status='running'
        )
        db.session.add(running_task)
        db.session.commit()
        
        # 获取待处理任务
        retrieved_tasks = self.task_service.get_pending_tasks(limit=5)
        
        assert len(retrieved_tasks) == 3
        for task in retrieved_tasks:
            assert task.status == 'pending'
    
    def test_get_running_tasks(self):
        """测试获取运行中的任务"""
        # 创建多个运行中的任务
        running_tasks = []
        for i in range(2):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='running'
            )
            db.session.add(task)
            running_tasks.append(task)
        
        # 创建其他状态的任务
        pending_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='sync_repository',
            status='pending'
        )
        db.session.add(pending_task)
        db.session.commit()
        
        # 获取运行中的任务
        retrieved_tasks = self.task_service.get_running_tasks(limit=5)
        
        assert len(retrieved_tasks) == 2
        for task in retrieved_tasks:
            assert task.status == 'running'
    
    def test_get_task_statistics(self):
        """测试获取任务统计信息"""
        # 创建不同状态的任务
        tasks = [
            Task(user_id=self.user.id, repository_id=self.repo.id, type='generate_document', status='pending'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='sync_repository', status='running'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='analyze_code', status='completed'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='generate_document', status='failed')
        ]
        
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        
        # 获取统计信息
        stats = self.task_service.get_task_statistics(user_id=self.user.id)
        
        assert stats['total_tasks'] == 4
        assert stats['pending_tasks'] == 1
        assert stats['running_tasks'] == 1
        assert stats['completed_tasks'] == 1
        assert stats['failed_tasks'] == 1
        assert stats['success_rate'] == 25.0  # 1/4 * 100
    
    def test_get_task_performance_metrics(self):
        """测试获取任务性能指标"""
        # 创建已完成的任务
        now = datetime.utcnow()
        tasks = [
            Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='completed',
                created_at=now - timedelta(minutes=5),
                started_at=now - timedelta(minutes=4),
                completed_at=now - timedelta(minutes=2),
                progress=100
            ),
            Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='sync_repository',
                status='completed',
                created_at=now - timedelta(minutes=10),
                started_at=now - timedelta(minutes=9),
                completed_at=now - timedelta(minutes=8),
                progress=100
            )
        ]
        
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        
        # 获取性能指标
        metrics = self.task_service.get_task_performance_metrics(user_id=self.user.id)
        
        assert metrics['total_completed_tasks'] == 2
        assert metrics['average_duration'] > 0
        assert metrics['success_rate'] == 100.0
        assert 'tasks_by_type' in metrics
        assert 'tasks_by_status' in metrics
    
    def test_get_task_queue_info(self):
        """测试获取任务队列信息"""
        # 创建不同状态的任务
        tasks = [
            Task(user_id=self.user.id, repository_id=self.repo.id, type='generate_document', status='pending'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='sync_repository', status='running'),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='analyze_code', status='completed')
        ]
        
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        
        # 获取队列信息
        queue_info = self.task_service.get_task_queue_info()
        
        assert queue_info['pending_tasks'] == 1
        assert queue_info['running_tasks'] == 1
        assert queue_info['completed_tasks'] == 1
        assert queue_info['total_tasks'] == 3
    
    def test_cleanup_old_tasks(self):
        """测试清理旧任务"""
        # 创建旧任务
        old_time = datetime.utcnow() - timedelta(days=35)
        old_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='completed',
            created_at=old_time,
            completed_at=old_time
        )
        db.session.add(old_task)
        
        # 创建新任务
        new_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='sync_repository',
            status='completed',
            created_at=datetime.utcnow() - timedelta(days=1),
            completed_at=datetime.utcnow()
        )
        db.session.add(new_task)
        db.session.commit()
        
        # 清理30天前的任务
        cleaned_count = self.task_service.cleanup_old_tasks(days=30)
        
        assert cleaned_count == 1
        
        # 验证旧任务已删除
        deleted_task = Task.query.get(old_task.id)
        assert deleted_task is None
        
        # 验证新任务仍然存在
        existing_task = Task.query.get(new_task.id)
        assert existing_task is not None
    
    def test_retry_task(self):
        """测试重试任务"""
        # 创建失败的任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='failed',
            retry_count=1,
            error_message="Previous error"
        )
        db.session.add(task)
        db.session.commit()
        
        # 重试任务
        retried_task = self.task_service.retry_task(task.id, self.user.id)
        
        assert retried_task is not None
        assert retried_task.status == 'pending'
        assert retried_task.progress == 0
        assert retried_task.retry_count == 2
        assert retried_task.error_message is None
    
    def test_retry_task_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        # 创建失败的任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='failed',
            retry_count=Task.MAX_RETRIES,
            error_message="Previous error"
        )
        db.session.add(task)
        db.session.commit()
        
        # 尝试重试任务
        with pytest.raises(ValueError):
            self.task_service.retry_task(task.id, self.user.id)
    
    def test_retry_task_not_failed(self):
        """测试重试未失败的任务"""
        # 创建运行中的任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running'
        )
        db.session.add(task)
        db.session.commit()
        
        # 尝试重试任务
        with pytest.raises(ValueError):
            self.task_service.retry_task(task.id, self.user.id)