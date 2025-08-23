"""
Progress Tracker Unit Tests
"""
import pytest
import threading
import time
from datetime import datetime, timedelta
from app.utils.progress_tracker import (
    ProgressStage, ProgressStep, ProgressTracker, ProgressTrackerManager,
    get_progress_tracker, update_task_progress_detailed, get_task_progress_details
)
from app import create_app
from config import TestingConfig


class TestProgressStage:
    
    def test_progress_stage_values(self):
        """测试进度阶段值"""
        assert ProgressStage.INITIALIZATION.value == "initialization"
        assert ProgressStage.CLONING_REPOSITORY.value == "cloning_repository"
        assert ProgressStage.ANALYZING_CODE.value == "analyzing_code"
        assert ProgressStage.GENERATING_DOCUMENTATION.value == "generating_documentation"
        assert ProgressStage.SAVING_RESULTS.value == "saving_results"
        assert ProgressStage.CLEANUP.value == "cleanup"
        assert ProgressStage.COMPLETED.value == "completed"


class TestProgressStep:
    
    def test_progress_step_initialization(self):
        """测试进度步骤初始化"""
        step = ProgressStep(
            name="Test Step",
            stage=ProgressStage.INITIALIZATION,
            weight=10.0
        )
        
        assert step.name == "Test Step"
        assert step.stage == ProgressStage.INITIALIZATION
        assert step.weight == 10.0
        assert step.progress == 0.0
        assert step.status == "pending"
        assert step.start_time is None
        assert step.end_time is None
        assert step.error_message is None


class TestProgressTracker:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建进度跟踪器
        self.task_id = 1
        self.task_type = 'generate_document'
        self.tracker = ProgressTracker(self.task_id, self.task_type)
    
    def teardown_method(self):
        """测试后清理"""
        self.app_context.pop()
    
    def test_progress_tracker_initialization(self):
        """测试进度跟踪器初始化"""
        assert self.tracker.task_id == self.task_id
        assert self.tracker.task_type == self.task_type
        assert self.tracker.total_weight == 100.0
        assert len(self.tracker.steps) > 0
        assert self.tracker.current_step == 0
        assert self.tracker.start_time is None
        assert self.tracker.end_time is None
    
    def test_progress_tracker_default_steps(self):
        """测试默认进度步骤"""
        steps = self.tracker.steps
        
        # 验证文档生成任务的默认步骤
        assert len(steps) == 6
        step_names = [step.name for step in steps]
        assert "Initialize" in step_names
        assert "Clone Repository" in step_names
        assert "Analyze Code Structure" in step_names
        assert "Generate Documentation" in step_names
        assert "Save Results" in step_names
        assert "Cleanup" in step_names
        
        # 验证权重总和
        total_weight = sum(step.weight for step in steps)
        assert total_weight == 100.0
    
    def test_progress_tracker_different_task_types(self):
        """测试不同任务类型的进度跟踪器"""
        # 测试仓库同步任务
        sync_tracker = ProgressTracker(2, 'sync_repository')
        sync_steps = sync_tracker.steps
        
        assert len(sync_steps) == 4
        step_names = [step.name for step in sync_steps]
        assert "Initialize" in step_names
        assert "Clone Repository" in step_names
        assert "Update Status" in step_names
        assert "Cleanup" in step_names
        
        # 测试代码分析任务
        analysis_tracker = ProgressTracker(3, 'analyze_code')
        analysis_steps = analysis_tracker.steps
        
        assert len(analysis_steps) == 5
        step_names = [step.name for step in analysis_steps]
        assert "Initialize" in step_names
        assert "Clone Repository" in step_names
        assert "Analyze Code Structure" in step_names
        assert "Save Results" in step_names
        assert "Cleanup" in step_names
    
    def test_progress_tracker_start(self):
        """测试启动进度跟踪"""
        self.tracker.start()
        
        assert self.tracker.start_time is not None
        assert self.tracker.last_update is not None
        assert self.tracker.steps[0].status == "running"
        assert self.tracker.steps[0].start_time is not None
    
    def test_progress_tracker_start_step(self):
        """测试启动特定步骤"""
        self.tracker.start()
        
        # 启动第二个步骤
        self.tracker.start_step(1, {"file_count": 10})
        
        assert self.tracker.current_step == 1
        assert self.tracker.steps[1].status == "running"
        assert self.tracker.steps[1].start_time is not None
        assert self.tracker.steps[1].details["file_count"] == 10
    
    def test_progress_tracker_update_step_progress(self):
        """测试更新步骤进度"""
        self.tracker.start()
        
        # 更新第一个步骤的进度
        self.tracker.update_step_progress(0, 50, {"processed_files": 5})
        
        assert self.tracker.steps[0].progress == 50.0
        assert self.tracker.steps[0].details["processed_files"] == 5
    
    def test_progress_tracker_complete_step(self):
        """测试完成步骤"""
        self.tracker.start()
        
        # 完成第一个步骤
        result = {"files_processed": 10, "time_taken": 5.2}
        self.tracker.complete_step(0, result)
        
        assert self.tracker.steps[0].status == "completed"
        assert self.tracker.steps[0].progress == 100.0
        assert self.tracker.steps[0].end_time is not None
        assert self.tracker.steps[0].details["files_processed"] == 10
    
    def test_progress_tracker_fail_step(self):
        """测试失败步骤"""
        self.tracker.start()
        
        # 使第一个步骤失败
        error_message = "Failed to process files"
        details = {"error_code": 500, "failed_files": 2}
        self.tracker.fail_step(0, error_message, details)
        
        assert self.tracker.steps[0].status == "failed"
        assert self.tracker.steps[0].error_message == error_message
        assert self.tracker.steps[0].end_time is not None
        assert self.tracker.steps[0].details["error_code"] == 500
    
    def test_progress_tracker_get_progress(self):
        """测试获取进度信息"""
        self.tracker.start()
        
        # 完成第一个步骤
        self.tracker.complete_step(0, {"files_processed": 10})
        
        # 启动第二个步骤并更新进度
        self.tracker.start_step(1)
        self.tracker.update_step_progress(1, 50)
        
        progress = self.tracker.get_progress()
        
        assert progress['task_id'] == self.task_id
        assert progress['task_type'] == self.task_type
        assert progress['total_progress'] == 32.5  # 5 + 15*0.5
        assert progress['completed_steps'] == 1
        assert progress['running_steps'] == 1
        assert progress['failed_steps'] == 0
        assert progress['total_steps'] == 6
        
        # 验证当前步骤信息
        assert progress['current_step']['name'] == "Clone Repository"
        assert progress['current_step']['progress'] == 50.0
        assert progress['current_step']['status'] == "running"
    
    def test_progress_tracker_complete(self):
        """测试完成任务"""
        self.tracker.start()
        
        # 完成所有步骤
        for i in range(len(self.tracker.steps)):
            self.tracker.complete_step(i, {"step": i + 1})
        
        result = {"total_files": 100, "success": True}
        self.tracker.complete(result)
        
        assert self.tracker.end_time is not None
        assert self.tracker.last_update is not None
        
        # 验证所有步骤都已完成
        for step in self.tracker.steps:
            assert step.status == "completed"
            assert step.progress == 100.0
            assert step.end_time is not None
    
    def test_progress_tracker_fail(self):
        """测试任务失败"""
        self.tracker.start()
        
        # 使任务失败
        error_message = "Task failed due to network error"
        details = {"error_type": "NetworkError", "retry_possible": True}
        self.tracker.fail(error_message, details)
        
        assert self.tracker.end_time is not None
        assert self.tracker.last_update is not None
        
        # 验证当前步骤已标记为失败
        current_step = self.tracker.steps[self.tracker.current_step]
        assert current_step.status == "failed"
        assert current_step.error_message == error_message
        assert current_step.details["error_type"] == "NetworkError"


class TestProgressTrackerManager:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建进度跟踪器管理器
        self.manager = ProgressTrackerManager()
    
    def teardown_method(self):
        """测试后清理"""
        self.app_context.pop()
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert len(self.manager.trackers) == 0
        assert self.manager.lock is not None
    
    def test_create_tracker(self):
        """测试创建进度跟踪器"""
        tracker = self.manager.create_tracker(1, 'generate_document')
        
        assert tracker.task_id == 1
        assert tracker.task_type == 'generate_document'
        assert 1 in self.manager.trackers
        assert self.manager.trackers[1] == tracker
    
    def test_get_tracker(self):
        """测试获取进度跟踪器"""
        # 创建跟踪器
        created_tracker = self.manager.create_tracker(1, 'generate_document')
        
        # 获取跟踪器
        retrieved_tracker = self.manager.get_tracker(1)
        
        assert retrieved_tracker is not None
        assert retrieved_tracker == created_tracker
        
        # 获取不存在的跟踪器
        nonexistent_tracker = self.manager.get_tracker(999)
        assert nonexistent_tracker is None
    
    def test_remove_tracker(self):
        """测试移除进度跟踪器"""
        # 创建跟踪器
        self.manager.create_tracker(1, 'generate_document')
        
        # 移除跟踪器
        result = self.manager.remove_tracker(1)
        assert result is True
        assert 1 not in self.manager.trackers
        
        # 移除不存在的跟踪器
        result = self.manager.remove_tracker(999)
        assert result is False
    
    def test_get_all_trackers(self):
        """测试获取所有跟踪器"""
        # 创建多个跟踪器
        self.manager.create_tracker(1, 'generate_document')
        self.manager.create_tracker(2, 'sync_repository')
        self.manager.create_tracker(3, 'analyze_code')
        
        # 获取所有跟踪器
        all_trackers = self.manager.get_all_trackers()
        
        assert len(all_trackers) == 3
        assert 1 in all_trackers
        assert 2 in all_trackers
        assert 3 in all_trackers
    
    def test_get_active_trackers(self):
        """测试获取活动跟踪器"""
        # 创建跟踪器并启动
        tracker1 = self.manager.create_tracker(1, 'generate_document')
        tracker1.start()
        
        tracker2 = self.manager.create_tracker(2, 'sync_repository')
        tracker2.start()
        
        # 创建未启动的跟踪器
        self.manager.create_tracker(3, 'analyze_code')
        
        # 获取活动跟踪器
        active_trackers = self.manager.get_active_trackers()
        
        assert len(active_trackers) == 2
        assert 1 in active_trackers
        assert 2 in active_trackers
        assert 3 not in active_trackers
    
    def test_cleanup_old_trackers(self):
        """测试清理旧跟踪器"""
        # 创建已完成的跟踪器
        old_tracker = self.manager.create_tracker(1, 'generate_document')
        old_tracker.start()
        old_tracker.end_time = datetime.utcnow() - timedelta(hours=25)  # 25小时前
        
        # 创建最近完成的跟踪器
        recent_tracker = self.manager.create_tracker(2, 'sync_repository')
        recent_tracker.start()
        recent_tracker.end_time = datetime.utcnow() - timedelta(hours=1)  # 1小时前
        
        # 创建未完成的跟踪器
        active_tracker = self.manager.create_tracker(3, 'analyze_code')
        active_tracker.start()
        # 不设置end_time，保持活动状态
        
        # 清理24小时前的跟踪器
        self.manager.cleanup_old_trackers(max_age_hours=24)
        
        # 验证旧跟踪器已被清理
        assert 1 not in self.manager.trackers
        assert 2 in self.manager.trackers  # 最近的应该保留
        assert 3 in self.manager.trackers  # 活动的应该保留
    
    def test_get_tracker_statistics(self):
        """测试获取跟踪器统计信息"""
        # 创建多个跟踪器
        tracker1 = self.manager.create_tracker(1, 'generate_document')
        tracker1.start()
        tracker1.complete()
        
        tracker2 = self.manager.create_tracker(2, 'sync_repository')
        tracker2.start()
        
        tracker3 = self.manager.create_tracker(3, 'analyze_code')
        tracker3.start()
        tracker3.fail("Test failure")
        
        # 获取统计信息
        stats = self.manager.get_tracker_statistics()
        
        assert stats['total_trackers'] == 3
        assert stats['active_trackers'] == 1  # 只有tracker2还是活动的
        assert stats['completed_trackers'] == 1  # tracker1已完成
        assert stats['average_completion_time'] > 0


class TestProgressTrackerFunctions:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """测试后清理"""
        self.app_context.pop()
    
    def test_get_progress_tracker(self):
        """测试获取进度跟踪器"""
        # 获取新跟踪器
        tracker = get_progress_tracker(1, 'generate_document')
        
        assert tracker.task_id == 1
        assert tracker.task_type == 'generate_document'
        
        # 获取现有跟踪器
        same_tracker = get_progress_tracker(1)
        assert same_tracker == tracker
        
        # 获取不存在的跟踪器但不指定任务类型
        with pytest.raises(ValueError):
            get_progress_tracker(999)
    
    def test_update_task_progress_detailed(self):
        """测试详细更新任务进度"""
        # 创建跟踪器
        tracker = get_progress_tracker(1, 'generate_document')
        tracker.start()
        
        # 更新进度
        details = {"processed_files": 5, "total_files": 10}
        update_task_progress_detailed(1, "Initialize", 50, details)
        
        assert tracker.steps[0].progress == 50.0
        assert tracker.steps[0].details["processed_files"] == 5
    
    def test_get_task_progress_details(self):
        """测试获取任务进度详情"""
        # 创建跟踪器
        tracker = get_progress_tracker(1, 'generate_document')
        tracker.start()
        
        # 完成第一个步骤
        tracker.complete_step(0, {"step": 1})
        
        # 获取进度详情
        progress = get_task_progress_details(1)
        
        assert progress is not None
        assert progress['task_id'] == 1
        assert progress['completed_steps'] == 1
        
        # 获取不存在的任务进度
        nonexistent_progress = get_task_progress_details(999)
        assert nonexistent_progress is None