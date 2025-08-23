"""
Performance integration tests for task management system.
"""

import pytest
import json
import threading
import time
import psutil
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from app.services.task_service import TaskService
from app.utils.task_queue import TaskQueueManager
from app.utils.task_worker import TaskWorker
from app.utils.task_scheduler import TaskScheduler
from app.utils.progress_tracker import ProgressTrackerManager
from app.utils.task_logging import TaskLoggerManager
from config import TestingConfig


class TestTaskPerformanceIntegration:
    """Performance integration tests for task management system."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user and repository
        self.user = User(username='perfuser', email='perf@example.com')
        self.user.set_password('perfpassword123')
        db.session.add(self.user)
        db.session.commit()
        
        self.repo = Repository(
            user_id=self.user.id,
            name='perf-repo',
            url='https://github.com/test/perf-repo.git',
            description='Performance test repository'
        )
        db.session.add(self.repo)
        db.session.commit()
        
        # Initialize system components
        self.task_service = TaskService()
        self.queue_manager = TaskQueueManager()
        self.worker = None
        self.scheduler = None
        self.progress_manager = ProgressTrackerManager()
        self.logger_manager = TaskLoggerManager()
        
        # Performance monitoring
        self.start_memory = psutil.Process().memory_info().rss
        self.start_time = time.time()
    
    def teardown_method(self):
        """Cleanup test environment."""
        # Stop background processes
        if self.worker and self.worker.is_running():
            self.worker.stop()
        if self.scheduler and self.scheduler.is_running():
            self.scheduler.stop()
        
        # Cleanup
        self.queue_manager.cleanup()
        self.progress_manager.cleanup_all_trackers()
        self.logger_manager.cleanup_all_loggers()
        
        # Performance reporting
        end_memory = psutil.Process().memory_info().rss
        end_time = time.time()
        
        memory_usage = (end_memory - self.start_memory) / 1024 / 1024  # MB
        execution_time = end_time - self.start_time
        
        print(f"\nPerformance Metrics:")
        print(f"Memory Usage: {memory_usage:.2f} MB")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        # Cleanup database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_creation_performance(self):
        """Test task creation performance."""
        num_tasks = 1000
        
        # Measure task creation performance
        start_time = time.time()
        
        tasks = []
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Perf Test Task {i+1}',
                description=f'Performance test task {i+1}'
            )
            tasks.append(task)
        
        creation_time = time.time() - start_time
        
        # Verify all tasks created
        assert len(tasks) == num_tasks
        
        # Check database
        db_count = Task.query.filter_by(user_id=self.user.id).count()
        assert db_count == num_tasks
        
        # Performance assertions
        tasks_per_second = num_tasks / creation_time
        assert tasks_per_second > 100  # Should create at least 100 tasks per second
        
        print(f"Task Creation Performance: {tasks_per_second:.2f} tasks/second")
        print(f"Total Creation Time: {creation_time:.2f} seconds for {num_tasks} tasks")
    
    def test_task_queue_performance(self):
        """Test task queue performance."""
        num_tasks = 500
        
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Queue Test Task {i+1}',
                description=f'Queue performance test task {i+1}'
            )
            tasks.append(task)
        
        # Measure queue operations
        start_time = time.time()
        
        # Add all tasks to queue
        for task in tasks:
            self.queue_manager.add_task(task)
        
        enqueue_time = time.time() - start_time
        
        # Verify queue size
        assert self.queue_manager.get_queue_size() == num_tasks
        
        # Measure dequeue performance
        start_time = time.time()
        
        dequeued_tasks = []
        while self.queue_manager.get_queue_size() > 0:
            task = self.queue_manager.get_next_task()
            dequeued_tasks.append(task)
        
        dequeue_time = time.time() - start_time
        
        # Verify all tasks dequeued
        assert len(dequeued_tasks) == num_tasks
        assert self.queue_manager.get_queue_size() == 0
        
        # Performance assertions
        enqueue_rate = num_tasks / enqueue_time
        dequeue_rate = num_tasks / dequeue_time
        
        assert enqueue_rate > 1000  # Should enqueue at least 1000 tasks per second
        assert dequeue_rate > 1000  # Should dequeue at least 1000 tasks per second
        
        print(f"Queue Enqueue Performance: {enqueue_rate:.2f} tasks/second")
        print(f"Queue Dequeue Performance: {dequeue_rate:.2f} tasks/second")
    
    def test_concurrent_task_processing(self):
        """Test concurrent task processing performance."""
        num_tasks = 100
        num_workers = 4
        
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Concurrent Test Task {i+1}',
                description=f'Concurrent processing test task {i+1}'
            )
            tasks.append(task)
            self.queue_manager.add_task(task)
        
        # Setup worker with multiple threads
        self.worker = TaskWorker(self.queue_manager, max_workers=num_workers)
        
        # Mock handler that simulates work
        def mock_handler(task_obj):
            time.sleep(0.01)  # Simulate 10ms of work
            task_obj.status = 'completed'
            task_obj.progress = 100
            task_obj.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        
        self.worker.register_handler('generate_document', mock_handler)
        
        # Measure processing time
        start_time = time.time()
        
        self.worker.start()
        
        # Wait for all tasks to complete
        while Task.query.filter_by(status='pending').count() > 0:
            time.sleep(0.1)
        
        processing_time = time.time() - start_time
        
        # Stop worker
        self.worker.stop()
        
        # Verify all tasks completed
        completed_count = Task.query.filter_by(status='completed').count()
        assert completed_count == num_tasks
        
        # Performance assertions
        tasks_per_second = num_tasks / processing_time
        expected_time = (num_tasks * 0.01) / num_workers  # Theoretical minimum
        
        # Should be significantly faster than sequential processing
        assert processing_time < expected_time * 2  # Allow some overhead
        
        print(f"Concurrent Processing Performance: {tasks_per_second:.2f} tasks/second")
        print(f"Processing Time: {processing_time:.2f} seconds for {num_tasks} tasks")
        print(f"Speedup vs Sequential: {(num_tasks * 0.01) / processing_time:.2f}x")
    
    def test_memory_usage_scaling(self):
        """Test memory usage scaling with task count."""
        task_counts = [100, 500, 1000]
        memory_usage = []
        
        for count in task_counts:
            # Clear previous tasks
            Task.query.filter_by(user_id=self.user.id).delete()
            db.session.commit()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Measure baseline memory
            baseline_memory = psutil.Process().memory_info().rss
            
            # Create tasks
            start_time = time.time()
            for i in range(count):
                task = self.task_service.create_task(
                    user_id=self.user.id,
                    repository_id=self.repo.id,
                    task_type='generate_document',
                    title=f'Memory Test Task {i+1}',
                    description=f'Memory scaling test task {i+1}'
                )
            
            creation_time = time.time() - start_time
            
            # Measure memory after creation
            after_memory = psutil.Process().memory_info().rss
            memory_increase = (after_memory - baseline_memory) / 1024 / 1024  # MB
            
            memory_usage.append(memory_increase)
            
            print(f"Tasks: {count}, Memory Increase: {memory_increase:.2f} MB, "
                  f"Time: {creation_time:.2f}s")
            
            # Performance assertions
            tasks_per_second = count / creation_time
            assert tasks_per_second > 50  # Should create at least 50 tasks per second
            
            # Memory should scale reasonably (not exponentially)
            if len(memory_usage) > 1:
                memory_ratio = memory_usage[-1] / memory_usage[-2]
                count_ratio = count / task_counts[task_counts.index(count) - 1]
                assert memory_ratio < count_ratio * 1.5  # Memory should grow slower than task count
    
    def test_database_query_performance(self):
        """Test database query performance."""
        num_tasks = 10000
        
        # Create large number of tasks
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Query Test Task {i+1}',
                description=f'Query performance test task {i+1}'
            )
            task.status = ['pending', 'running', 'completed', 'failed'][i % 4]
            task.progress = [0, 25, 50, 75, 100][i % 5]
            if task.status == 'completed':
                task.completed_at = datetime.utcnow() - timedelta(days=i % 30)
            db.session.add(task)
        
        db.session.commit()
        
        # Test various query performance
        queries = [
            ("Simple Filter", lambda: Task.query.filter_by(status='completed').all()),
            ("User Filter", lambda: Task.query.filter_by(user_id=self.user.id).all()),
            ("Type Filter", lambda: Task.query.filter_by(type='generate_document').all()),
            ("Progress Range", lambda: Task.query.filter(Task.progress >= 50).all()),
            ("Date Range", lambda: Task.query.filter(
                Task.completed_at >= datetime.utcnow() - timedelta(days=7)
            ).all()),
            ("Complex Query", lambda: Task.query.filter(
                Task.user_id == self.user.id,
                Task.type == 'generate_document',
                Task.progress >= 25,
                Task.status.in_(['running', 'completed'])
            ).all()),
            ("Count Query", lambda: Task.query.filter_by(status='completed').count()),
            ("Aggregation", lambda: db.session.query(
                Task.status,
                db.func.count(Task.id)
            ).group_by(Task.status).all())
        ]
        
        for query_name, query_func in queries:
            start_time = time.time()
            result = query_func()
            query_time = time.time() - start_time
            
            print(f"{query_name}: {query_time:.4f}s, Result size: {len(result) if isinstance(result, list) else result}")
            
            # Performance assertions
            assert query_time < 1.0  # All queries should complete in under 1 second
    
    def test_scheduler_performance(self):
        """Test task scheduler performance."""
        num_schedules = 50
        
        # Create tasks for scheduling
        tasks = []
        for i in range(num_schedules):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='sync_repository',
                title=f'Schedule Test Task {i+1}',
                description=f'Schedule performance test task {i+1}'
            )
            tasks.append(task)
        
        # Initialize scheduler
        self.scheduler = TaskScheduler()
        
        # Measure schedule creation performance
        start_time = time.time()
        
        schedules = []
        for i, task in enumerate(tasks):
            schedule = self.scheduler.create_schedule(
                task_id=task.id,
                schedule_type='daily',
                start_time=datetime.utcnow() + timedelta(seconds=i*0.1),
                max_executions=1
            )
            schedules.append(schedule)
        
        schedule_creation_time = time.time() - start_time
        
        # Start scheduler
        self.scheduler.start()
        
        # Wait for some schedules to execute
        time.sleep(2)
        
        # Measure schedule execution performance
        start_time = time.time()
        
        executed_count = 0
        for schedule in schedules:
            if schedule.last_execution:
                executed_count += 1
        
        execution_check_time = time.time() - start_time
        
        # Performance assertions
        schedules_per_second = num_schedules / schedule_creation_time
        assert schedules_per_second > 50  # Should create at least 50 schedules per second
        
        print(f"Schedule Creation Performance: {schedules_per_second:.2f} schedules/second")
        print(f"Executed Schedules: {executed_count}/{num_schedules}")
        print(f"Execution Check Time: {execution_check_time:.4f}s")
        
        # Stop scheduler
        self.scheduler.stop()
    
    def test_progress_tracking_performance(self):
        """Test progress tracking performance."""
        num_tasks = 100
        
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Progress Test Task {i+1}',
                description=f'Progress tracking test task {i+1}'
            )
            tasks.append(task)
        
        # Measure progress tracker creation performance
        start_time = time.time()
        
        trackers = []
        for task in tasks:
            tracker = self.progress_manager.create_tracker(task.id, task.type)
            trackers.append(tracker)
        
        tracker_creation_time = time.time() - start_time
        
        # Measure progress update performance
        start_time = time.time()
        
        for tracker in trackers:
            tracker.start()
            for step_idx in range(len(tracker.steps)):
                tracker.start_step(step_idx)
                for progress in [25, 50, 75, 100]:
                    tracker.update_step_progress(step_idx, progress)
                tracker.complete_step(step_idx)
            tracker.complete()
        
        progress_update_time = time.time() - start_time
        
        # Performance assertions
        trackers_per_second = num_tasks / tracker_creation_time
        updates_per_second = (num_tasks * len(trackers[0].steps) * 4) / progress_update_time
        
        assert trackers_per_second > 100  # Should create at least 100 trackers per second
        assert updates_per_second > 1000  # Should make at least 1000 progress updates per second
        
        print(f"Progress Tracker Creation: {trackers_per_second:.2f} trackers/second")
        print(f"Progress Update Performance: {updates_per_second:.2f} updates/second")
    
    def test_logging_performance(self):
        """Test logging performance."""
        num_tasks = 50
        logs_per_task = 100
        
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Logging Test Task {i+1}',
                description=f'Logging performance test task {i+1}'
            )
            tasks.append(task)
        
        # Measure logging performance
        start_time = time.time()
        
        for task in tasks:
            logger = self.logger_manager.get_logger(task.id)
            for i in range(logs_per_task):
                logger.info(f"Log message {i+1}", {"iteration": i+1})
        
        logging_time = time.time() - start_time
        
        # Measure log retrieval performance
        start_time = time.time()
        
        total_logs = 0
        for task in tasks:
            logger = self.logger_manager.get_logger(task.id)
            logs = logger.get_logs()
            total_logs += len(logs)
        
        retrieval_time = time.time() - start_time
        
        # Performance assertions
        total_log_entries = num_tasks * logs_per_task
        logs_per_second = total_log_entries / logging_time
        retrieval_rate = total_log_entries / retrieval_time
        
        assert logs_per_second > 1000  # Should create at least 1000 log entries per second
        assert retrieval_rate > 10000  # Should retrieve at least 10000 log entries per second
        
        print(f"Logging Performance: {logs_per_second:.2f} log entries/second")
        print(f"Log Retrieval Performance: {retrieval_rate:.2f} entries/second")
        print(f"Total Log Entries: {total_log_entries}")
    
    def test_system_throughput(self):
        """Test overall system throughput."""
        num_tasks = 200
        
        # Setup worker
        self.worker = TaskWorker(self.queue_manager, max_workers=4)
        
        # Mock handler
        def mock_handler(task_obj):
            # Simulate work
            time.sleep(0.005)  # 5ms of work
            
            # Create progress tracker and logger
            tracker = self.progress_manager.create_tracker(task_obj.id, task_obj.type)
            logger = self.logger_manager.get_logger(task_obj.id)
            
            # Simulate progress tracking
            tracker.start()
            logger.info("Task started")
            
            for step_idx in range(len(tracker.steps)):
                tracker.start_step(step_idx)
                for progress in [25, 50, 75, 100]:
                    tracker.update_step_progress(step_idx, progress)
                    logger.info(f"Step {step_idx} progress: {progress}%")
                tracker.complete_step(step_idx)
            
            tracker.complete()
            logger.info("Task completed")
            
            # Update task
            task_obj.status = 'completed'
            task_obj.progress = 100
            task_obj.completed_at = datetime.utcnow()
            db.session.commit()
            
            return True
        
        self.worker.register_handler('generate_document', mock_handler)
        
        # Measure end-to-end throughput
        start_time = time.time()
        
        # Start worker
        self.worker.start()
        
        # Create and queue tasks
        for i in range(num_tasks):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Throughput Test Task {i+1}',
                description=f'Throughput test task {i+1}'
            )
            self.queue_manager.add_task(task)
        
        # Wait for all tasks to complete
        while Task.query.filter_by(status='pending').count() > 0:
            time.sleep(0.1)
        
        end_to_end_time = time.time() - start_time
        
        # Stop worker
        self.worker.stop()
        
        # Verify results
        completed_count = Task.query.filter_by(status='completed').count()
        assert completed_count == num_tasks
        
        # Performance assertions
        tasks_per_second = num_tasks / end_to_end_time
        assert tasks_per_second > 50  # Should process at least 50 tasks per second end-to-end
        
        print(f"System Throughput: {tasks_per_second:.2f} tasks/second")
        print(f"End-to-End Time: {end_to_end_time:.2f} seconds for {num_tasks} tasks")
        
        # Calculate theoretical maximum
        theoretical_max = 4 / 0.005  # 4 workers / 5ms per task
        efficiency = (tasks_per_second / theoretical_max) * 100
        
        print(f"Theoretical Maximum: {theoretical_max:.2f} tasks/second")
        print(f"System Efficiency: {efficiency:.1f}%")