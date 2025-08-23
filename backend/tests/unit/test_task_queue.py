"""
Task Queue Manager Unit Tests
"""
import pytest
import threading
import time
from datetime import datetime
from unittest.mock import Mock, patch
from app.services.task_queue import TaskQueue, TaskQueueManager, TaskPriority
from app.models.task import Task
from app import create_app, db
from config import TestingConfig


class TestTaskQueue:
    
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
        
        # 创建任务队列管理器
        self.queue_manager = TaskQueueManager()
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'queue_manager'):
            self.queue_manager.stop()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_queue_initialization(self):
        """测试任务队列初始化"""
        queue = TaskQueue(max_size=100, timeout=30)
        
        assert queue.max_size == 100
        assert queue.timeout == 30
        assert len(queue.queue) == 0
        assert queue.is_running is False
        assert queue.current_size == 0
    
    def test_task_queue_start_stop(self):
        """测试任务队列启动和停止"""
        queue = TaskQueue(max_size=10, timeout=5)
        
        # 测试启动
        queue.start()
        assert queue.is_running is True
        
        # 测试停止
        queue.stop()
        assert queue.is_running is False
    
    def test_task_queue_add_task(self):
        """测试添加任务到队列"""
        queue = TaskQueue(max_size=10, timeout=5)
        queue.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务到队列
        result = queue.add_task(task, priority=TaskPriority.NORMAL)
        assert result is True
        assert queue.current_size == 1
        
        # 测试队列已满的情况
        queue.max_size = 1
        another_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='sync_repository',
            status='pending'
        )
        db.session.add(another_task)
        db.session.commit()
        
        result = queue.add_task(another_task, priority=TaskPriority.NORMAL)
        assert result is False
    
    def test_task_queue_get_task(self):
        """测试从队列获取任务"""
        queue = TaskQueue(max_size=10, timeout=5)
        queue.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务到队列
        queue.add_task(task, priority=TaskPriority.HIGH)
        
        # 获取任务
        retrieved_task = queue.get_task()
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert queue.current_size == 0
        
        # 测试空队列
        empty_task = queue.get_task()
        assert empty_task is None
    
    def test_task_queue_priority_ordering(self):
        """测试任务优先级排序"""
        queue = TaskQueue(max_size=10, timeout=5)
        queue.start()
        
        # 创建不同优先级的任务
        tasks = []
        priorities = [TaskPriority.LOW, TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.CRITICAL]
        
        for i, priority in enumerate(priorities):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            tasks.append(task)
            queue.add_task(task, priority=priority)
        
        # 验证任务按优先级排序
        retrieved_order = []
        while queue.current_size > 0:
            task = queue.get_task()
            if task:
                retrieved_order.append(task)
        
        # 应该按优先级顺序：CRITICAL, HIGH, NORMAL, LOW
        expected_order = [tasks[3], tasks[1], tasks[2], tasks[0]]
        assert retrieved_order == expected_order
    
    def test_task_queue_statistics(self):
        """测试队列统计信息"""
        queue = TaskQueue(max_size=10, timeout=5)
        queue.start()
        
        # 创建测试任务
        tasks = []
        for i in range(3):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            tasks.append(task)
        
        # 添加任务到队列
        queue.add_task(tasks[0], priority=TaskPriority.HIGH)
        queue.add_task(tasks[1], priority=TaskPriority.NORMAL)
        queue.add_task(tasks[2], priority=TaskPriority.LOW)
        
        # 获取统计信息
        stats = queue.get_statistics()
        
        assert stats['current_size'] == 3
        assert stats['max_size'] == 10
        assert stats['is_running'] is True
        assert stats['priority_distribution']['HIGH'] == 1
        assert stats['priority_distribution']['NORMAL'] == 1
        assert stats['priority_distribution']['LOW'] == 1
    
    def test_task_queue_clear(self):
        """测试清空队列"""
        queue = TaskQueue(max_size=10, timeout=5)
        queue.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务到队列
        queue.add_task(task, priority=TaskPriority.NORMAL)
        assert queue.current_size == 1
        
        # 清空队列
        cleared_count = queue.clear()
        assert cleared_count == 1
        assert queue.current_size == 0
    
    def test_task_queue_manager_initialization(self):
        """测试任务队列管理器初始化"""
        assert self.queue_manager.is_running is False
        assert len(self.queue_manager.queues) == 0
        assert self.queue_manager.max_concurrent_tasks == 3
    
    def test_task_queue_manager_start_stop(self):
        """测试任务队列管理器启动和停止"""
        # 启动管理器
        self.queue_manager.start()
        assert self.queue_manager.is_running is True
        assert len(self.queue_manager.queues) > 0
        
        # 停止管理器
        self.queue_manager.stop()
        assert self.queue_manager.is_running is False
    
    def test_task_queue_manager_queue_creation(self):
        """测试队列管理器创建队列"""
        self.queue_manager.start()
        
        # 验证默认队列创建
        assert 'default' in self.queue_manager.queues
        assert 'high_priority' in self.queue_manager.queues
        assert 'low_priority' in self.queue_manager.queues
        
        # 验证队列属性
        default_queue = self.queue_manager.queues['default']
        assert default_queue.max_size == 1000
        assert default_queue.timeout == 300
    
    def test_task_queue_manager_add_task_by_type(self):
        """测试按任务类型添加任务"""
        self.queue_manager.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务
        result = self.queue_manager.add_task(task)
        assert result is True
        
        # 验证任务在正确的队列中
        default_queue = self.queue_manager.queues['default']
        assert default_queue.current_size == 1
    
    def test_task_queue_manager_get_task_from_any_queue(self):
        """测试从任意队列获取任务"""
        self.queue_manager.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务
        self.queue_manager.add_task(task)
        
        # 获取任务
        retrieved_task = self.queue_manager.get_task()
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
    
    def test_task_queue_manager_get_status(self):
        """测试队列管理器状态"""
        self.queue_manager.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务
        self.queue_manager.add_task(task)
        
        # 获取状态
        status = self.queue_manager.get_status()
        
        assert status['is_running'] is True
        assert status['max_concurrent_tasks'] == 3
        assert status['total_tasks'] == 1
        assert len(status['queues']) == 3
        assert status['queues']['default']['current_size'] == 1
    
    def test_task_queue_manager_concurrent_access(self):
        """测试并发访问"""
        self.queue_manager.start()
        
        def worker_function():
            """工作线程函数"""
            for i in range(5):
                task = Task(
                    user_id=self.user.id,
                    repository_id=self.repo.id,
                    type='generate_document',
                    status='pending'
                )
                db.session.add(task)
                db.session.commit()
                self.queue_manager.add_task(task)
                time.sleep(0.01)
        
        # 创建多个工作线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有任务都已添加
        status = self.queue_manager.get_status()
        assert status['total_tasks'] == 15
    
    def test_task_queue_error_handling(self):
        """测试错误处理"""
        queue = TaskQueue(max_size=10, timeout=5)
        
        # 测试添加None任务
        result = queue.add_task(None)
        assert result is False
        
        # 测试在未启动状态下获取任务
        task = queue.get_task()
        assert task is None
    
    def test_task_queue_timeout_handling(self):
        """测试超时处理"""
        queue = TaskQueue(max_size=10, timeout=0.1)  # 短超时
        
        # 创建一个会阻塞的任务处理器
        def slow_task_handler(task):
            time.sleep(0.2)  # 超过队列超时时间
            return True
        
        queue.start()
        
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 添加任务到队列
        queue.add_task(task, priority=TaskPriority.NORMAL)
        
        # 获取任务（应该正常工作）
        retrieved_task = queue.get_task()
        assert retrieved_task is not None
        assert retrieved_task.id == task.id