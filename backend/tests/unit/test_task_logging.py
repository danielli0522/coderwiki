"""
Task Logging Unit Tests
"""
import pytest
import json
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from app.utils.task_logging import (
    LogLevel, TaskLogEntry, TaskLogger, TaskLoggerManager,
    get_task_logger, log_task_event, get_task_logs
)
from app import create_app
from config import TestingConfig


class TestLogLevel:
    
    def test_log_level_values(self):
        """测试日志级别值"""
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARNING.value == "warning"
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.CRITICAL.value == "critical"


class TestTaskLogEntry:
    
    def test_task_log_entry_initialization(self):
        """测试任务日志条目初始化"""
        timestamp = datetime.utcnow()
        entry = TaskLogEntry(
            task_id=1,
            timestamp=timestamp,
            level=LogLevel.INFO,
            message="Test message",
            details={"key": "value"},
            step_name="test_step",
            progress=50.0,
            duration=1.5
        )
        
        assert entry.task_id == 1
        assert entry.timestamp == timestamp
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.details == {"key": "value"}
        assert entry.step_name == "test_step"
        assert entry.progress == 50.0
        assert entry.duration == 1.5
    
    def test_task_log_entry_to_dict(self):
        """测试任务日志条目转字典"""
        timestamp = datetime.utcnow()
        entry = TaskLogEntry(
            task_id=1,
            timestamp=timestamp,
            level=LogLevel.INFO,
            message="Test message",
            details={"key": "value"},
            step_name="test_step",
            progress=50.0,
            duration=1.5
        )
        
        entry_dict = entry.to_dict()
        
        assert entry_dict['task_id'] == 1
        assert entry_dict['timestamp'] == timestamp.isoformat()
        assert entry_dict['level'] == "info"
        assert entry_dict['message'] == "Test message"
        assert entry_dict['details'] == {"key": "value"}
        assert entry_dict['step_name'] == "test_step"
        assert entry_dict['progress'] == 50.0
        assert entry_dict['duration'] == 1.5


class TestTaskLogger:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建临时日志目录
        self.temp_dir = tempfile.mkdtemp()
        self.original_logs_dir = Path("logs")
        
        # 重定向日志目录到临时目录
        import app.utils.task_logging
        app.utils.task_logging.Path = lambda x: Path(self.temp_dir) / x
        
        # 创建任务日志器
        self.task_id = 1
        self.logger = TaskLogger(self.task_id, log_to_file=True, log_to_db=False)
    
    def teardown_method(self):
        """测试后清理"""
        self.logger.cleanup()
        
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir)
        
        self.app_context.pop()
    
    def test_task_logger_initialization(self):
        """测试任务日志器初始化"""
        assert self.logger.task_id == self.task_id
        assert self.logger.log_to_file is True
        assert self.logger.log_to_db is False
        assert len(self.logger.entries) == 0
        assert self.logger.start_time is not None
    
    def test_task_logger_debug(self):
        """测试调试日志"""
        self.logger.debug("Debug message", {"debug": True}, "test_step")
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.DEBUG
        assert entry.message == "Debug message"
        assert entry.details == {"debug": True}
        assert entry.step_name == "test_step"
    
    def test_task_logger_info(self):
        """测试信息日志"""
        self.logger.info("Info message", {"info": "data"}, "test_step")
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.INFO
        assert entry.message == "Info message"
        assert entry.details == {"info": "data"}
        assert entry.step_name == "test_step"
    
    def test_task_logger_warning(self):
        """测试警告日志"""
        self.logger.warning("Warning message", {"warning": True}, "test_step")
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.WARNING
        assert entry.message == "Warning message"
        assert entry.details == {"warning": True}
        assert entry.step_name == "test_step"
    
    def test_task_logger_error(self):
        """测试错误日志"""
        self.logger.error("Error message", {"error": "data"}, "test_step")
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.ERROR
        assert entry.message == "Error message"
        assert entry.details == {"error": "data"}
        assert entry.step_name == "test_step"
    
    def test_task_logger_critical(self):
        """测试严重错误日志"""
        self.logger.critical("Critical message", {"critical": True}, "test_step")
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.CRITICAL
        assert entry.message == "Critical message"
        assert entry.details == {"critical": True}
        assert entry.step_name == "test_step"
    
    def test_task_logger_step_methods(self):
        """测试步骤相关方法"""
        # 开始步骤
        self.logger.start_step("test_step", {"files": 10})
        
        # 完成步骤
        self.logger.complete_step("test_step", {"processed": 10})
        
        # 失败步骤
        self.logger.fail_step("test_step", "Step failed", {"error_code": 500})
        
        # 验证日志条目
        assert len(self.logger.entries) == 3
        
        # 验证开始步骤日志
        start_entry = self.logger.entries[0]
        assert start_entry.level == LogLevel.INFO
        assert "Starting step" in start_entry.message
        
        # 验证完成步骤日志
        complete_entry = self.logger.entries[1]
        assert complete_entry.level == LogLevel.INFO
        assert "Completed step" in complete_entry.message
        
        # 验证失败步骤日志
        fail_entry = self.logger.entries[2]
        assert fail_entry.level == LogLevel.ERROR
        assert "Failed step" in fail_entry.message
    
    def test_task_logger_progress_update(self):
        """测试进度更新日志"""
        self.logger.update_progress(50, "test_step", {"processed": 5})
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.INFO
        assert "Progress updated" in entry.message
        assert entry.details["progress"] == 50
        assert entry.details["processed"] == 5
    
    def test_task_logger_performance_logging(self):
        """测试性能日志"""
        self.logger.log_performance("file_processing", 1.5, {"files": 10})
        
        assert len(self.logger.entries) == 1
        entry = self.logger.entries[0]
        assert entry.level == LogLevel.INFO
        assert "Performance" in entry.message
        assert entry.details["operation"] == "file_processing"
        assert entry.details["duration_seconds"] == 1.5
        assert entry.details["files"] == 10
    
    def test_task_logger_get_logs(self):
        """测试获取日志"""
        # 添加不同级别的日志
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        
        # 获取所有日志
        all_logs = self.logger.get_logs()
        assert len(all_logs) == 5
        
        # 按级别过滤
        error_logs = self.logger.get_logs(level=LogLevel.ERROR)
        assert len(error_logs) == 1
        assert error_logs[0].level == LogLevel.ERROR
        
        # 按步骤名称过滤
        step_logs = self.logger.get_logs(step_name="test_step")
        assert len(step_logs) == 0  # 没有指定步骤名称的日志
        
        # 限制数量
        limited_logs = self.logger.get_logs(limit=3)
        assert len(limited_logs) == 3
    
    def test_task_logger_get_error_logs(self):
        """测试获取错误日志"""
        # 添加错误和严重错误日志
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        self.logger.info("Info message")
        
        error_logs = self.logger.get_error_logs()
        
        assert len(error_logs) == 2
        assert any(log.level == LogLevel.ERROR for log in error_logs)
        assert any(log.level == LogLevel.CRITICAL for log in error_logs)
    
    def test_task_logger_get_step_logs(self):
        """测试获取步骤日志"""
        # 添加步骤日志
        self.logger.start_step("step1")
        self.logger.complete_step("step1")
        self.logger.start_step("step2")
        self.logger.info("General info")
        
        step1_logs = self.logger.get_step_logs("step1")
        assert len(step1_logs) == 2
        
        step2_logs = self.logger.get_step_logs("step2")
        assert len(step2_logs) == 1
    
    def test_task_logger_export_logs(self):
        """测试导出日志"""
        # 添加日志
        self.logger.info("Test message", {"key": "value"}, "test_step")
        
        # 导出为JSON
        json_export = self.logger.export_logs('json')
        assert isinstance(json_export, str)
        parsed_data = json.loads(json_export)
        assert len(parsed_data) == 1
        
        # 导出为TXT
        txt_export = self.logger.export_logs('txt')
        assert isinstance(txt_export, str)
        assert "Test message" in txt_export
        
        # 导出为CSV
        csv_export = self.logger.export_logs('csv')
        assert isinstance(csv_export, str)
        assert "Timestamp,Level,Message" in csv_export
        
        # 测试无效格式
        with pytest.raises(ValueError):
            self.logger.export_logs('invalid_format')
    
    def test_task_logger_get_summary(self):
        """测试获取日志摘要"""
        # 添加不同级别的日志
        self.logger.debug("Debug 1")
        self.logger.debug("Debug 2")
        self.logger.info("Info 1")
        self.logger.info("Info 2")
        self.logger.info("Info 3")
        self.logger.warning("Warning 1")
        self.logger.error("Error 1")
        self.logger.critical("Critical 1")
        
        # 添加步骤日志
        self.logger.start_step("step1")
        self.logger.complete_step("step1")
        self.logger.start_step("step2")
        
        summary = self.logger.get_summary()
        
        assert summary['task_id'] == self.task_id
        assert summary['total_logs'] == 10
        assert summary['level_counts']['debug'] == 2
        assert summary['level_counts']['info'] == 4  # 包括步骤日志
        assert summary['level_counts']['warning'] == 1
        assert summary['level_counts']['error'] == 1
        assert summary['level_counts']['critical'] == 1
        assert summary['error_count'] == 2  # error + critical
        assert summary['step_counts']['step1'] == 2
        assert summary['step_counts']['step2'] == 1
    
    def test_task_logger_thread_safety(self):
        """测试线程安全"""
        def worker_function():
            for i in range(10):
                self.logger.info(f"Worker message {i}")
                time.sleep(0.001)
        
        # 创建多个工作线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有日志都已添加
        assert len(self.logger.entries) == 30


class TestTaskLoggerManager:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建日志管理器
        self.manager = TaskLoggerManager()
    
    def teardown_method(self):
        """测试后清理"""
        # 清理所有日志器
        for logger in self.manager.get_all_loggers().values():
            logger.cleanup()
        
        self.app_context.pop()
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert len(self.manager.loggers) == 0
        assert self.manager.lock is not None
    
    def test_get_logger(self):
        """测试获取日志器"""
        # 获取新日志器
        logger = self.manager.get_logger(1)
        
        assert logger is not None
        assert logger.task_id == 1
        assert 1 in self.manager.loggers
        
        # 获取现有日志器
        same_logger = self.manager.get_logger(1)
        assert same_logger == logger
        
        # 获取不存在的日志器但不创建
        nonexistent_logger = self.manager.get_logger(999, create_if_missing=False)
        assert nonexistent_logger is None
    
    def test_remove_logger(self):
        """测试移除日志器"""
        # 创建日志器
        self.manager.get_logger(1)
        
        # 移除日志器
        result = self.manager.remove_logger(1)
        assert result is True
        assert 1 not in self.manager.loggers
        
        # 移除不存在的日志器
        result = self.manager.remove_logger(999)
        assert result is False
    
    def test_get_all_loggers(self):
        """测试获取所有日志器"""
        # 创建多个日志器
        self.manager.get_logger(1)
        self.manager.get_logger(2)
        self.manager.get_logger(3)
        
        # 获取所有日志器
        all_loggers = self.manager.get_all_loggers()
        
        assert len(all_loggers) == 3
        assert 1 in all_loggers
        assert 2 in all_loggers
        assert 3 in all_loggers
    
    def test_cleanup_old_loggers(self):
        """测试清理旧日志器"""
        # 创建旧日志器
        old_logger = self.manager.get_logger(1)
        old_logger.start_time = datetime.utcnow() - timedelta(hours=25)
        
        # 创建新日志器
        new_logger = self.manager.get_logger(2)
        new_logger.start_time = datetime.utcnow() - timedelta(hours=1)
        
        # 清理24小时前的日志器
        self.manager.cleanup_old_loggers(max_age_hours=24)
        
        # 验证旧日志器已被清理
        assert 1 not in self.manager.loggers
        assert 2 in self.manager.loggers  # 新的应该保留
    
    def test_get_logger_statistics(self):
        """测试获取日志器统计信息"""
        # 创建多个日志器并添加日志
        logger1 = self.manager.get_logger(1)
        logger1.info("Info 1")
        logger1.error("Error 1")
        
        logger2 = self.manager.get_logger(2)
        logger2.info("Info 2")
        logger2.info("Info 3")
        logger2.warning("Warning 1")
        
        # 获取统计信息
        stats = self.manager.get_logger_statistics()
        
        assert stats['total_loggers'] == 2
        assert stats['total_logs'] == 5
        assert stats['level_counts']['info'] == 3
        assert stats['level_counts']['error'] == 1
        assert stats['level_counts']['warning'] == 1
        assert stats['average_logs_per_logger'] == 2.5


class TestTaskLoggingFunctions:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """测试后清理"""
        # 清理全局日志管理器
        from app.utils.task_logging import task_logger_manager
        for logger in task_logger_manager.get_all_loggers().values():
            logger.cleanup()
        
        self.app_context.pop()
    
    def test_get_task_logger(self):
        """测试获取任务日志器"""
        logger = get_task_logger(1)
        
        assert logger is not None
        assert logger.task_id == 1
        
        # 获取现有日志器
        same_logger = get_task_logger(1)
        assert same_logger == logger
    
    def test_log_task_event(self):
        """测试记录任务事件"""
        # 记录不同级别的事件
        log_task_event(1, 'debug', 'Debug message', {'debug': True}, 'step1')
        log_task_event(1, 'info', 'Info message', {'info': 'data'}, 'step2')
        log_task_event(1, 'warning', 'Warning message', {'warning': True})
        log_task_event(1, 'error', 'Error message', {'error': 'data'})
        log_task_event(1, 'critical', 'Critical message', {'critical': True})
        
        # 获取日志器验证
        logger = get_task_logger(1)
        assert len(logger.entries) == 5
        
        # 验证日志级别
        levels = [entry.level.value for entry in logger.entries]
        assert 'debug' in levels
        assert 'info' in levels
        assert 'warning' in levels
        assert 'error' in levels
        assert 'critical' in levels
    
    def test_get_task_logs(self):
        """测试获取任务日志"""
        # 添加日志
        log_task_event(1, 'info', 'Info 1', {}, 'step1')
        log_task_event(1, 'error', 'Error 1', {}, 'step2')
        log_task_event(1, 'info', 'Info 2', {}, 'step1')
        
        # 获取所有日志
        all_logs = get_task_logs(1)
        assert len(all_logs) == 3
        
        # 按级别过滤
        error_logs = get_task_logs(1, level='error')
        assert len(error_logs) == 1
        assert error_logs[0]['level'] == 'error'
        
        # 按步骤名称过滤
        step1_logs = get_task_logs(1, step_name='step1')
        assert len(step1_logs) == 2
        
        # 限制数量
        limited_logs = get_task_logs(1, limit=1)
        assert len(limited_logs) == 1
        
        # 获取不存在的任务日志
        nonexistent_logs = get_task_logs(999)
        assert len(nonexistent_logs) == 0