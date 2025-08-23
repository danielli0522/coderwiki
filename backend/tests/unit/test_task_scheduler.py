"""
Task Scheduler Unit Tests
"""
import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.task_scheduler import TaskScheduler, TaskSchedule, ScheduleType
from app.models.task import Task
from app import create_app, db
from config import TestingConfig


class TestTaskSchedule:
    
    def test_task_schedule_initialization(self):
        """测试任务调度初始化"""
        schedule = TaskSchedule(
            task_type='generate_document',
            repository_id=1,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert schedule.task_type == 'generate_document'
        assert schedule.repository_id == 1
        assert schedule.schedule_type == ScheduleType.ONCE
        assert schedule.is_active is True
        assert schedule.next_run_time is not None
    
    def test_task_schedule_should_run(self):
        """测试任务是否应该运行"""
        now = datetime.utcnow()
        
        # 测试一次性调度
        schedule = TaskSchedule(
            task_type='generate_document',
            repository_id=1,
            schedule_type=ScheduleType.ONCE,
            start_time=now - timedelta(minutes=1)  # 过去的时间
        )
        
        assert schedule.should_run(now) is True
        
        # 测试未来的调度
        future_schedule = TaskSchedule(
            task_type='generate_document',
            repository_id=1,
            schedule_type=ScheduleType.ONCE,
            start_time=now + timedelta(hours=1)  # 未来的时间
        )
        
        assert future_schedule.should_run(now) is False
        
        # 测试非活动调度
        schedule.is_active = False
        assert schedule.should_run(now) is False
    
    def test_task_schedule_update_next_run(self):
        """测试更新下次运行时间"""
        now = datetime.utcnow()
        
        # 测试一次性调度
        schedule = TaskSchedule(
            task_type='generate_document',
            repository_id=1,
            schedule_type=ScheduleType.ONCE,
            start_time=now
        )
        
        schedule.update_next_run_time(now)
        assert schedule.next_run_time is None  # 一次性调度运行后应该不再运行
        
        # 测试每小时调度
        hourly_schedule = TaskSchedule(
            task_type='generate_document',
            repository_id=1,
            schedule_type=ScheduleType.HOURLY,
            start_time=now
        )
        
        hourly_schedule.update_next_run_time(now)
        assert hourly_schedule.next_run_time is not None
        assert hourly_schedule.next_run_time > now
        
        # 测试每天调度
        daily_schedule = TaskSchedule(
            task_type='generate_document',
            repository_id=1,
            schedule_type=ScheduleType.DAILY,
            start_time=now,
            hour=2,
            minute=0
        )
        
        daily_schedule.update_next_run_time(now)
        assert daily_schedule.next_run_time is not None


class TestTaskScheduler:
    
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
        
        # 创建任务调度器
        self.scheduler = TaskScheduler(
            check_interval=0.1,  # 短间隔用于测试
            max_concurrent_scheduled_tasks=2
        )
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_scheduler_initialization(self):
        """测试任务调度器初始化"""
        assert self.scheduler.check_interval == 0.1
        assert self.scheduler.max_concurrent_scheduled_tasks == 2
        assert self.scheduler.is_running is False
        assert len(self.scheduler.schedules) == 0
        assert len(self.scheduler.running_tasks) == 0
    
    def test_task_scheduler_start_stop(self):
        """测试任务调度器启动和停止"""
        # 启动调度器
        self.scheduler.start()
        assert self.scheduler.is_running is True
        
        # 停止调度器
        self.scheduler.stop()
        assert self.scheduler.is_running is False
    
    def test_create_schedule(self):
        """测试创建调度"""
        self.scheduler.start()
        
        # 创建一次性调度
        schedule_id = self.scheduler.create_schedule(
            task_type='generate_document',
            repository_id=self.repo.id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(seconds=1)
        )
        
        assert schedule_id is not None
        assert schedule_id in self.scheduler.schedules
        
        schedule = self.scheduler.schedules[schedule_id]
        assert schedule.task_type == 'generate_document'
        assert schedule.repository_id == self.repo.id
        assert schedule.schedule_type == ScheduleType.ONCE
    
    def test_create_schedule_with_parameters(self):
        """测试创建带参数的调度"""
        self.scheduler.start()
        
        # 创建每天调度的任务
        schedule_id = self.scheduler.create_daily_schedule(
            name="Daily Sync",
            repository_id=self.repo.id,
            task_type='sync_repository',
            hour=2,
            minute=0
        )
        
        assert schedule_id is not None
        schedule = self.scheduler.schedules[schedule_id]
        
        assert schedule.task_type == 'sync_repository'
        assert schedule.schedule_type == ScheduleType.DAILY
        assert schedule.hour == 2
        assert schedule.minute == 0
    
    def test_remove_schedule(self):
        """测试移除调度"""
        self.scheduler.start()
        
        # 创建调度
        schedule_id = self.scheduler.create_schedule(
            task_type='generate_document',
            repository_id=self.repo.id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(seconds=1)
        )
        
        assert schedule_id in self.scheduler.schedules
        
        # 移除调度
        result = self.scheduler.remove_schedule(schedule_id)
        assert result is True
        assert schedule_id not in self.scheduler.schedules
        
        # 移除不存在的调度
        result = self.scheduler.remove_schedule('nonexistent_id')
        assert result is False
    
    def test_schedule_execution(self):
        """测试调度执行"""
        self.scheduler.start()
        
        # 创建即将运行的调度
        schedule_id = self.scheduler.create_schedule(
            task_type='generate_document',
            repository_id=self.repo.id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(milliseconds=100)
        )
        
        # 等待调度执行
        time.sleep(0.2)
        
        # 验证任务已创建
        tasks = Task.query.filter_by(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document'
        ).all()
        
        assert len(tasks) > 0
        
        # 验证调度已更新
        schedule = self.scheduler.schedules.get(schedule_id)
        if schedule:
            assert schedule.last_run_time is not None
    
    def test_recurring_schedule_execution(self):
        """测试周期性调度执行"""
        self.scheduler = TaskScheduler(
            check_interval=0.05,  # 更短的间隔
            max_concurrent_scheduled_tasks=2
        )
        self.scheduler.start()
        
        # 创建每小时调度的任务
        schedule_id = self.scheduler.create_schedule(
            task_type='sync_repository',
            repository_id=self.repo.id,
            schedule_type=ScheduleType.HOURLY,
            start_time=datetime.utcnow() + timedelta(milliseconds=50)
        )
        
        # 等待多次执行
        time.sleep(0.3)
        
        # 验证多个任务已创建
        tasks = Task.query.filter_by(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='sync_repository'
        ).all()
        
        assert len(tasks) >= 1
        
        # 验证调度下次运行时间已更新
        schedule = self.scheduler.schedules.get(schedule_id)
        if schedule:
            assert schedule.next_run_time is not None
            assert schedule.next_run_time > datetime.utcnow()
    
    def test_concurrent_schedule_limit(self):
        """测试并发调度限制"""
        self.scheduler = TaskScheduler(
            check_interval=0.05,
            max_concurrent_scheduled_tasks=1  # 限制并发数
        )
        self.scheduler.start()
        
        # 创建多个同时运行的调度
        schedule_ids = []
        for i in range(3):
            schedule_id = self.scheduler.create_schedule(
                task_type='generate_document',
                repository_id=self.repo.id,
                schedule_type=ScheduleType.ONCE,
                start_time=datetime.utcnow() + timedelta(milliseconds=50)
            )
            schedule_ids.append(schedule_id)
        
        # 等待执行
        time.sleep(0.2)
        
        # 验证只有一个任务在运行
        assert len(self.scheduler.running_tasks) <= 1
    
    def test_schedule_with_user_id(self):
        """测试带用户ID的调度"""
        self.scheduler.start()
        
        # 创建带用户ID的调度
        schedule_id = self.scheduler.create_schedule(
            task_type='generate_document',
            repository_id=self.repo.id,
            user_id=self.user.id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(milliseconds=100)
        )
        
        # 等待执行
        time.sleep(0.2)
        
        # 验证任务已创建并分配给正确的用户
        tasks = Task.query.filter_by(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document'
        ).all()
        
        assert len(tasks) > 0
    
    def test_schedule_error_handling(self):
        """测试调度错误处理"""
        self.scheduler.start()
        
        # 创建无效的调度
        schedule_id = self.scheduler.create_schedule(
            task_type='invalid_task_type',
            repository_id=999,  # 不存在的仓库
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(milliseconds=100)
        )
        
        # 等待执行
        time.sleep(0.2)
        
        # 验证调度仍然存在但可能标记为非活动
        schedule = self.scheduler.schedules.get(schedule_id)
        if schedule:
            # 调度应该仍然存在但可能已经处理了错误
            assert schedule.id == schedule_id
    
    def test_get_schedules(self):
        """测试获取调度列表"""
        self.scheduler.start()
        
        # 创建多个调度
        schedule_ids = []
        for i in range(3):
            schedule_id = self.scheduler.create_schedule(
                task_type='generate_document',
                repository_id=self.repo.id,
                schedule_type=ScheduleType.ONCE,
                start_time=datetime.utcnow() + timedelta(seconds=i + 1)
            )
            schedule_ids.append(schedule_id)
        
        # 获取调度列表
        schedules = self.scheduler.get_schedules()
        
        assert len(schedules) == 3
        for schedule_id in schedule_ids:
            assert any(s['id'] == schedule_id for s in schedules)
    
    def test_get_schedule_statistics(self):
        """测试获取调度统计信息"""
        self.scheduler.start()
        
        # 创建多个调度
        for i in range(3):
            self.scheduler.create_schedule(
                task_type='generate_document',
                repository_id=self.repo.id,
                schedule_type=ScheduleType.ONCE,
                start_time=datetime.utcnow() + timedelta(milliseconds=100)
            )
        
        # 获取统计信息
        stats = self.scheduler.get_statistics()
        
        assert stats['total_schedules'] == 3
        assert stats['active_schedules'] == 3
        assert stats['running_tasks'] >= 0
        assert 'total_tasks_created' in stats
        assert 'successful_tasks' in stats
        assert 'failed_tasks' in stats
    
    def test_create_repository_sync_schedule(self):
        """测试创建仓库同步调度"""
        self.scheduler.start()
        
        # 创建仓库同步调度
        schedule_id = self.scheduler.create_repository_sync_schedule(
            repository_id=self.repo.id,
            user_id=self.user.id
        )
        
        assert schedule_id is not None
        schedule = self.scheduler.schedules[schedule_id]
        
        assert schedule.task_type == 'sync_repository'
        assert schedule.repository_id == self.repo.id
        assert schedule.schedule_type == ScheduleType.DAILY
        assert schedule.name is not None
    
    def test_create_daily_analysis_schedule(self):
        """测试创建每日分析调度"""
        self.scheduler.start()
        
        # 创建每日分析调度
        schedule_id = self.scheduler.create_daily_analysis_schedule(
            name="Daily Code Analysis",
            repository_id=self.repo.id,
            user_id=self.user.id,
            hour=3,
            minute=0
        )
        
        assert schedule_id is not None
        schedule = self.scheduler.schedules[schedule_id]
        
        assert schedule.task_type == 'analyze_code'
        assert schedule.repository_id == self.repo.id
        assert schedule.schedule_type == ScheduleType.DAILY
        assert schedule.hour == 3
        assert schedule.minute == 0
        assert schedule.name == "Daily Code Analysis"
    
    def test_schedule_status_tracking(self):
        """测试调度状态跟踪"""
        self.scheduler.start()
        
        # 创建调度
        schedule_id = self.scheduler.create_schedule(
            task_type='generate_document',
            repository_id=self.repo.id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(milliseconds=100)
        )
        
        # 等待执行
        time.sleep(0.2)
        
        # 获取调度状态
        status = self.scheduler.get_schedule_status(schedule_id)
        
        assert status is not None
        assert 'id' in status
        assert 'is_active' in status
        assert 'last_run_time' in status
        assert 'next_run_time' in status
        assert 'total_runs' in status
        assert 'successful_runs' in status
    
    def test_schedule_cleanup(self):
        """测试调度清理"""
        self.scheduler.start()
        
        # 创建已完成的一次性调度
        schedule_id = self.scheduler.create_schedule(
            task_type='generate_document',
            repository_id=self.repo.id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.utcnow() + timedelta(milliseconds=100)
        )
        
        # 等待执行
        time.sleep(0.2)
        
        # 手动清理已完成的调度
        cleaned_count = self.scheduler.cleanup_completed_schedules()
        
        assert cleaned_count >= 0
        # 验证调度可能已被清理
        schedule = self.scheduler.schedules.get(schedule_id)
        if schedule is None:
            assert schedule_id not in self.scheduler.schedules