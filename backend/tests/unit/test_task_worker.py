"""
Task Worker Unit Tests
"""
import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.task_worker import TaskWorker, TaskHandlerRegistry
from app.models.task import Task
from app import create_app, db
from config import TestingConfig


class TestTaskHandlerRegistry:
    
    def test_handler_registry_initialization(self):
        """测试处理器注册表初始化"""
        registry = TaskHandlerRegistry()
        assert len(registry.handlers) == 0
    
    def test_register_handler(self):
        """测试注册处理器"""
        registry = TaskHandlerRegistry()
        
        def test_handler(task):
            return True
        
        # 注册处理器
        registry.register('test_task', test_handler)
        assert 'test_task' in registry.handlers
        assert registry.handlers['test_task'] == test_handler
    
    def test_register_invalid_handler(self):
        """测试注册无效处理器"""
        registry = TaskHandlerRegistry()
        
        # 测试注册非函数处理器
        with pytest.raises(ValueError):
            registry.register('test_task', 'not_a_function')
        
        # 测试注册None处理器
        with pytest.raises(ValueError):
            registry.register('test_task', None)
    
    def test_get_handler(self):
        """测试获取处理器"""
        registry = TaskHandlerRegistry()
        
        def test_handler(task):
            return True
        
        registry.register('test_task', test_handler)
        
        # 获取已注册的处理器
        handler = registry.get_handler('test_task')
        assert handler == test_handler
        
        # 获取未注册的处理器
        handler = registry.get_handler('nonexistent_task')
        assert handler is None
    
    def test_unregister_handler(self):
        """测试注销处理器"""
        registry = TaskHandlerRegistry()
        
        def test_handler(task):
            return True
        
        registry.register('test_task', test_handler)
        assert 'test_task' in registry.handlers
        
        # 注销处理器
        registry.unregister('test_task')
        assert 'test_task' not in registry.handlers
        
        # 注销不存在的处理器
        registry.unregister('nonexistent_task')  # 不应该抛出异常


class TestTaskWorker:
    
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
        
        # 创建任务处理器
        self.test_handler = Mock(return_value=True)
        self.registry = TaskHandlerRegistry()
        self.registry.register('generate_document', self.test_handler)
        self.registry.register('sync_repository', self.test_handler)
        self.registry.register('analyze_code', self.test_handler)
        
        # 创建任务工作器
        self.worker = TaskWorker(
            max_concurrent_tasks=2,
            task_timeout=30,
            handler_registry=self.registry
        )
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'worker'):
            self.worker.stop()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_worker_initialization(self):
        """测试任务工作器初始化"""
        assert self.worker.max_concurrent_tasks == 2
        assert self.worker.task_timeout == 30
        assert self.worker.is_running is False
        assert len(self.worker.active_tasks) == 0
        assert self.worker.handler_registry is not None
    
    def test_task_worker_start_stop(self):
        """测试任务工作器启动和停止"""
        # 启动工作器
        self.worker.start()
        assert self.worker.is_running is True
        
        # 停止工作器
        self.worker.stop()
        assert self.worker.is_running is False
    
    def test_task_worker_process_task_success(self):
        """测试处理任务成功"""
        self.worker.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is True
        assert self.test_handler.called
        
        # 验证任务状态更新
        db.session.refresh(task)
        assert task.status == 'completed'
        assert task.progress == 100
        assert task.completed_at is not None
    
    def test_task_worker_process_task_failure(self):
        """测试处理任务失败"""
        self.worker.start()
        
        # 设置处理器返回失败
        self.test_handler.side_effect = Exception("Task processing failed")
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is False
        
        # 验证任务状态更新
        db.session.refresh(task)
        assert task.status == 'failed'
        assert task.error_message is not None
        assert 'Task processing failed' in task.error_message
    
    def test_task_worker_process_task_timeout(self):
        """测试任务处理超时"""
        self.worker = TaskWorker(
            max_concurrent_tasks=2,
            task_timeout=0.1,  # 短超时
            handler_registry=self.registry
        )
        self.worker.start()
        
        # 设置处理器执行时间超过超时时间
        def slow_handler(task):
            time.sleep(0.2)  # 超过超时时间
            return True
        
        self.registry.register('slow_task', slow_handler)
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='slow_task',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is False
        
        # 验证任务状态更新
        db.session.refresh(task)
        assert task.status == 'failed'
        assert 'timeout' in task.error_message.lower()
    
    def test_task_worker_process_task_invalid_type(self):
        """测试处理无效任务类型"""
        self.worker.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='invalid_task_type',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is False
        
        # 验证任务状态更新
        db.session.refresh(task)
        assert task.status == 'failed'
        assert 'No handler registered' in task.error_message
    
    def test_task_worker_concurrent_task_limit(self):
        """测试并发任务限制"""
        self.worker.start()
        
        def long_running_handler(task):
            time.sleep(0.1)  # 模拟长时间运行
            return True
        
        self.registry.register('long_task', long_running_handler)
        
        # 创建多个任务
        tasks = []
        for i in range(3):  # 超过最大并发数
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='long_task',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            tasks.append(task)
        
        # 处理任务（前两个应该成功，第三个应该因为并发限制而失败）
        results = []
        for task in tasks:
            result = self.worker.process_task(task)
            results.append(result)
        
        # 验证结果
        assert results[0] is True  # 第一个任务成功
        assert results[1] is True  # 第二个任务成功
        assert results[2] is False  # 第三个任务因为并发限制失败
    
    def test_task_worker_retry_mechanism(self):
        """测试重试机制"""
        self.worker = TaskWorker(
            max_concurrent_tasks=1,
            task_timeout=30,
            max_retries=2,
            handler_registry=self.registry
        )
        self.worker.start()
        
        # 设置处理器第一次失败，第二次成功
        self.test_handler.side_effect = [Exception("First failure"), True]
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is True
        assert self.test_handler.call_count == 2  # 调用了两次
        
        # 验证任务状态
        db.session.refresh(task)
        assert task.status == 'completed'
        assert task.retry_count == 1
    
    def test_task_worker_retry_limit_exceeded(self):
        """测试重试次数限制"""
        self.worker = TaskWorker(
            max_concurrent_tasks=1,
            task_timeout=30,
            max_retries=2,
            handler_registry=self.registry
        )
        self.worker.start()
        
        # 设置处理器总是失败
        self.test_handler.side_effect = Exception("Persistent failure")
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is False
        assert self.test_handler.call_count == 3  # 初始调用 + 2次重试
        
        # 验证任务状态
        db.session.refresh(task)
        assert task.status == 'failed'
        assert task.retry_count == 2
        assert 'exceeded maximum retries' in task.error_message
    
    def test_task_worker_get_status(self):
        """测试获取工作器状态"""
        self.worker.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        self.worker.process_task(task)
        
        # 获取状态
        status = self.worker.get_status()
        
        assert status['is_running'] is True
        assert status['max_concurrent_tasks'] == 2
        assert status['task_timeout'] == 30
        assert status['active_tasks'] == 0
        assert 'total_processed' in status
        assert 'successful_tasks' in status
        assert 'failed_tasks' in status
        assert 'retry_count' in status
    
    def test_task_worker_progress_tracking(self):
        """测试进度跟踪"""
        self.worker.start()
        
        # 设置处理器更新进度
        def progress_handler(task):
            # 模拟进度更新
            task.progress = 25
            time.sleep(0.01)
            task.progress = 50
            time.sleep(0.01)
            task.progress = 75
            time.sleep(0.01)
            task.progress = 100
            return True
        
        self.registry.register('progress_task', progress_handler)
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='progress_task',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证结果
        assert result is True
        
        # 验证进度更新
        db.session.refresh(task)
        assert task.progress == 100
    
    def test_task_worker_cleanup_completed_tasks(self):
        """测试清理已完成任务"""
        self.worker.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        self.worker.process_task(task)
        
        # 验证任务已从活动任务中移除
        assert len(self.worker.active_tasks) == 0
    
    def test_task_worker_error_logging(self):
        """测试错误日志记录"""
        self.worker.start()
        
        # 设置处理器抛出异常
        self.test_handler.side_effect = Exception("Test error for logging")
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 处理任务
        result = self.worker.process_task(task)
        
        # 验证错误被记录
        assert result is False
        db.session.refresh(task)
        assert task.error_message is not None
        assert 'Test error for logging' in task.error_message
    
    def test_task_worker_graceful_shutdown(self):
        """测试优雅关闭"""
        self.worker.start()
        
        # 创建长时间运行的任务
        def long_handler(task):
            time.sleep(0.1)  # 模拟长时间运行
            return True
        
        self.registry.register('long_task', long_handler)
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='long_task',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 在另一个线程中处理任务
        def process_task():
            self.worker.process_task(task)
        
        thread = threading.Thread(target=process_task)
        thread.start()
        
        # 等待一小段时间然后停止工作器
        time.sleep(0.05)
        self.worker.stop()
        
        # 等待线程完成
        thread.join()
        
        # 验证工作器已停止
        assert self.worker.is_running is False