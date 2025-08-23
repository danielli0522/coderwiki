"""
Integration tests for task management system.
"""

import pytest
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from app.services.task_service import TaskService
from app.utils.task_queue import TaskQueueManager
from app.utils.task_worker import TaskWorker
from app.utils.task_scheduler import TaskScheduler
from app.utils.progress_tracker import ProgressTracker, ProgressTrackerManager
from app.utils.task_logging import TaskLogger, TaskLoggerManager
from config import TestingConfig


class TestTaskSystemIntegration:
    """Integration tests for the complete task management system."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('testpassword123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create test repository
        self.repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository'
        )
        db.session.add(self.repo)
        db.session.commit()
        
        # Initialize system components
        self.task_service = TaskService()
        self.queue_manager = TaskQueueManager()
        self.worker = TaskWorker(self.queue_manager, max_workers=2)
        self.scheduler = TaskScheduler()
        self.progress_manager = ProgressTrackerManager()
        self.logger_manager = TaskLoggerManager()
    
    def teardown_method(self):
        """Cleanup test environment."""
        # Stop all background processes
        if self.worker.is_running():
            self.worker.stop()
        if self.scheduler.is_running():
            self.scheduler.stop()
        
        # Cleanup managers
        self.queue_manager.cleanup()
        self.progress_manager.cleanup_all_trackers()
        self.logger_manager.cleanup_all_loggers()
        
        # Cleanup database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_complete_task_lifecycle(self):
        """Test complete task lifecycle from creation to completion."""
        # Create task through service
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Test Document Generation',
            description='Generate documentation for test repository'
        )
        
        # Verify task creation
        assert task.id is not None
        assert task.status == 'pending'
        assert task.user_id == self.user.id
        assert task.repository_id == self.repo.id
        
        # Get task from database
        db_task = Task.query.get(task.id)
        assert db_task is not None
        assert db_task.status == 'pending'
        
        # Add task to queue
        queue_result = self.queue_manager.add_task(task)
        assert queue_result is True
        
        # Verify queue state
        assert self.queue_manager.get_queue_size() == 1
        assert self.queue_manager.get_next_task() == task
        
        # Process task through worker
        def mock_task_handler(task_obj):
            """Mock task handler that simulates document generation."""
            # Get progress tracker
            tracker = self.progress_manager.get_tracker(task_obj.id)
            if not tracker:
                tracker = self.progress_manager.create_tracker(task_obj.id, task_obj.type)
            
            # Get task logger
            logger = self.logger_manager.get_logger(task_obj.id)
            if not logger:
                logger = self.logger_manager.get_logger(task_obj.id)
            
            # Start progress tracking
            tracker.start()
            logger.start_step("document_generation", {"files": 5})
            
            # Simulate processing
            time.sleep(0.1)
            tracker.update_step_progress(0, 25, {"processed": 1})
            logger.info("Processed 1/5 files")
            
            time.sleep(0.1)
            tracker.update_step_progress(0, 50, {"processed": 2})
            logger.info("Processed 2/5 files")
            
            time.sleep(0.1)
            tracker.update_step_progress(0, 75, {"processed": 3})
            logger.info("Processed 3/5 files")
            
            time.sleep(0.1)
            tracker.update_step_progress(0, 100, {"processed": 5})
            logger.complete_step("document_generation", {"processed": 5})
            
            # Complete task
            tracker.complete({"total_files": 5, "success": True})
            
            # Update task in database
            task_obj.status = 'completed'
            task_obj.progress = 100
            task_obj.result = json.dumps({
                "document_id": 1,
                "file_path": "/docs/generated.md",
                "files_processed": 5
            })
            task_obj.completed_at = datetime.utcnow()
            db.session.commit()
            
            return True
        
        # Register mock handler
        self.worker.register_handler('generate_document', mock_task_handler)
        
        # Start worker
        self.worker.start()
        
        # Wait for task processing
        time.sleep(1)
        
        # Verify task completion
        completed_task = Task.query.get(task.id)
        assert completed_task.status == 'completed'
        assert completed_task.progress == 100
        assert completed_task.result is not None
        
        # Verify progress tracking
        tracker = self.progress_manager.get_tracker(task.id)
        assert tracker is not None
        progress = tracker.get_progress()
        assert progress['total_progress'] == 100.0
        assert progress['completed_steps'] == len(tracker.steps)
        
        # Verify logging
        logger = self.logger_manager.get_logger(task.id)
        assert logger is not None
        logs = logger.get_logs()
        assert len(logs) > 0
        
        # Verify queue is empty
        assert self.queue_manager.get_queue_size() == 0
        
        # Stop worker
        self.worker.stop()
    
    def test_concurrent_task_processing(self):
        """Test concurrent processing of multiple tasks."""
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Test Task {i+1}',
                description=f'Task {i+1} for concurrent processing'
            )
            tasks.append(task)
            self.queue_manager.add_task(task)
        
        # Verify queue state
        assert self.queue_manager.get_queue_size() == 3
        
        # Mock handler that simulates work
        def mock_handler(task_obj):
            time.sleep(0.2)  # Simulate work
            task_obj.status = 'completed'
            task_obj.progress = 100
            task_obj.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        
        # Register handler
        self.worker.register_handler('generate_document', mock_handler)
        
        # Start worker
        self.worker.start()
        
        # Wait for processing
        time.sleep(1)
        
        # Verify all tasks completed
        for task in tasks:
            completed_task = Task.query.get(task.id)
            assert completed_task.status == 'completed'
            assert completed_task.progress == 100
        
        # Verify queue is empty
        assert self.queue_manager.get_queue_size() == 0
        
        # Stop worker
        self.worker.stop()
    
    def test_task_error_handling_and_retry(self):
        """Test error handling and retry mechanism."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Failing Task',
            description='Task that will fail and retry'
        )
        
        # Add to queue
        self.queue_manager.add_task(task)
        
        # Track attempt count
        attempt_count = 0
        
        def failing_handler(task_obj):
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 3:
                # Simulate failure
                raise Exception(f"Simulated failure attempt {attempt_count}")
            else:
                # Succeed on third attempt
                task_obj.status = 'completed'
                task_obj.progress = 100
                task_obj.completed_at = datetime.utcnow()
                db.session.commit()
                return True
        
        # Register handler
        self.worker.register_handler('generate_document', failing_handler)
        
        # Start worker
        self.worker.start()
        
        # Wait for processing with retries
        time.sleep(2)
        
        # Verify task eventually completed
        completed_task = Task.query.get(task.id)
        assert completed_task.status == 'completed'
        assert completed_task.progress == 100
        assert attempt_count == 3
        
        # Stop worker
        self.worker.stop()
    
    def test_task_scheduling_integration(self):
        """Test task scheduling integration."""
        # Create scheduled task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='sync_repository',
            title='Scheduled Sync',
            description='Repository sync task'
        )
        
        # Create schedule
        schedule = self.scheduler.create_schedule(
            task_id=task.id,
            schedule_type='daily',
            start_time=datetime.utcnow() + timedelta(seconds=1),
            max_executions=2
        )
        
        # Verify schedule creation
        assert schedule.id is not None
        assert schedule.task_id == task.id
        assert schedule.schedule_type == 'daily'
        
        # Mock handler
        def sync_handler(task_obj):
            task_obj.status = 'completed'
            task_obj.progress = 100
            task_obj.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        
        # Register handler
        self.worker.register_handler('sync_repository', sync_handler)
        
        # Start scheduler and worker
        self.scheduler.start()
        self.worker.start()
        
        # Wait for scheduled execution
        time.sleep(3)
        
        # Verify task was executed
        executed_task = Task.query.get(task.id)
        # Task should be completed after scheduled execution
        assert executed_task.status in ['completed', 'running']
        
        # Verify schedule statistics
        stats = self.scheduler.get_schedule_stats(schedule.id)
        assert stats['total_executions'] >= 1
        
        # Stop scheduler and worker
        self.scheduler.stop()
        self.worker.stop()
    
    def test_task_progress_and_logging_integration(self):
        """Test progress tracking and logging integration."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Progress Test Task',
            description='Task for testing progress and logging'
        )
        
        # Get progress tracker and logger
        tracker = self.progress_manager.create_tracker(task.id, task.type)
        logger = self.logger_manager.get_logger(task.id)
        
        # Start tracking
        tracker.start()
        logger.info("Task started", {"task_id": task.id})
        
        # Simulate progress steps
        steps = [
            ("initialization", 10),
            ("analysis", 30),
            ("generation", 50),
            ("finalization", 10)
        ]
        
        for step_name, weight in steps:
            logger.start_step(step_name, {"weight": weight})
            
            # Simulate step progress
            for progress in [25, 50, 75, 100]:
                time.sleep(0.05)
                tracker.update_step_progress(tracker.current_step, progress, 
                                          {"step_progress": progress})
                logger.info(f"Step {step_name} progress: {progress}%")
            
            logger.complete_step(step_name, {"weight": weight, "completed": True})
        
        # Complete task
        tracker.complete({"total_steps": len(steps), "success": True})
        logger.info("Task completed successfully")
        
        # Verify progress tracking
        progress = tracker.get_progress()
        assert progress['total_progress'] == 100.0
        assert progress['completed_steps'] == len(steps)
        
        # Verify logging
        logs = logger.get_logs()
        assert len(logs) > len(steps) * 4  # Multiple log entries per step
        
        # Verify error logs
        error_logs = logger.get_error_logs()
        assert len(error_logs) == 0  # No errors in successful run
        
        # Verify log export
        json_logs = logger.export_logs('json')
        assert isinstance(json_logs, str)
        parsed_logs = json.loads(json_logs)
        assert len(parsed_logs) == len(logs)
    
    def test_task_statistics_integration(self):
        """Test task statistics integration."""
        # Create multiple tasks with different statuses
        tasks_data = [
            ('generate_document', 'completed', 100),
            ('sync_repository', 'running', 50),
            ('analyze_code', 'pending', 0),
            ('generate_document', 'failed', 75),
            ('sync_repository', 'completed', 100)
        ]
        
        created_tasks = []
        for task_type, status, progress in tasks_data:
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type=task_type,
                title=f'{task_type} - {status}',
                description=f'Task with status: {status}'
            )
            task.status = status
            task.progress = progress
            if status == 'completed':
                task.completed_at = datetime.utcnow()
            db.session.commit()
            created_tasks.append(task)
        
        # Get statistics
        stats = self.task_service.get_task_statistics(self.user.id)
        
        # Verify statistics
        assert stats['total_tasks'] == len(tasks_data)
        assert stats['completed_tasks'] == 2
        assert stats['running_tasks'] == 1
        assert stats['pending_tasks'] == 1
        assert stats['failed_tasks'] == 1
        
        # Verify type distribution
        type_counts = stats['task_type_distribution']
        assert type_counts['generate_document'] == 2
        assert type_counts['sync_repository'] == 2
        assert type_counts['analyze_code'] == 1
        
        # Verify average progress
        avg_progress = stats['average_progress']
        expected_avg = sum(progress for _, _, progress in tasks_data) / len(tasks_data)
        assert abs(avg_progress - expected_avg) < 0.1
    
    def test_task_queue_prioritization(self):
        """Test task queue prioritization."""
        # Create tasks with different priorities
        tasks = []
        priorities = ['high', 'medium', 'low', 'high', 'medium']
        
        for i, priority in enumerate(priorities):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Priority Task {i+1}',
                description=f'Task with {priority} priority'
            )
            task.priority = priority
            db.session.commit()
            tasks.append(task)
            self.queue_manager.add_task(task)
        
        # Verify queue ordering (high priority first)
        queued_tasks = []
        while self.queue_manager.get_queue_size() > 0:
            next_task = self.queue_manager.get_next_task()
            queued_tasks.append(next_task)
        
        # Verify high priority tasks come first
        high_priority_indices = [i for i, task in enumerate(queued_tasks) 
                               if task.priority == 'high']
        medium_priority_indices = [i for i, task in enumerate(queued_tasks) 
                                 if task.priority == 'medium']
        low_priority_indices = [i for i, task in enumerate(queued_tasks) 
                              if task.priority == 'low']
        
        # All high priority tasks should come before medium and low
        assert all(i < min(medium_priority_indices + low_priority_indices) 
                  for i in high_priority_indices)
        
        # All medium priority tasks should come before low
        assert all(i < min(low_priority_indices) for i in medium_priority_indices)
    
    def test_system_resource_cleanup(self):
        """Test system resource cleanup."""
        # Create and process tasks
        for i in range(5):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Cleanup Test Task {i+1}',
                description=f'Task {i+1} for testing cleanup'
            )
            
            # Add to queue and process
            self.queue_manager.add_task(task)
            
            # Create progress tracker and logger
            tracker = self.progress_manager.create_tracker(task.id, task.type)
            logger = self.logger_manager.get_logger(task.id)
            
            # Simulate task completion
            task.status = 'completed'
            task.progress = 100
            task.completed_at = datetime.utcnow()
            db.session.commit()
            
            tracker.complete()
            logger.info("Task completed")
        
        # Verify cleanup
        assert self.queue_manager.get_queue_size() == 0
        
        # Simulate old task cleanup
        old_time = datetime.utcnow() - timedelta(hours=25)
        for tracker in self.progress_manager.get_all_trackers().values():
            tracker.end_time = old_time
        
        for logger in self.logger_manager.get_all_loggers().values():
            logger.start_time = old_time
        
        # Cleanup old resources
        self.progress_manager.cleanup_old_trackers(max_age_hours=24)
        self.logger_manager.cleanup_old_loggers(max_age_hours=24)
        
        # Verify cleanup
        assert len(self.progress_manager.get_all_trackers()) == 0
        assert len(self.logger_manager.get_all_loggers()) == 0
    
    def test_api_integration(self):
        """Test API integration with task system."""
        with self.app.test_client() as client:
            # Login user
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Create task via API
            response = client.post('/api/tasks', json={
                'repository_id': self.repo.id,
                'type': 'generate_document',
                'title': 'API Test Task',
                'description': 'Task created via API'
            })
            
            assert response.status_code == 201
            task_data = response.get_json()
            task_id = task_data['id']
            
            # Verify task in database
            task = Task.query.get(task_id)
            assert task is not None
            assert task.title == 'API Test Task'
            
            # Get task via API
            response = client.get(f'/api/tasks/{task_id}')
            assert response.status_code == 200
            retrieved_data = response.get_json()
            assert retrieved_data['id'] == task_id
            assert retrieved_data['title'] == 'API Test Task'
            
            # Get task list via API
            response = client.get('/api/tasks')
            assert response.status_code == 200
            task_list = response.get_json()
            assert len(task_list) >= 1
            assert any(t['id'] == task_id for t in task_list)
            
            # Get user statistics via API
            response = client.get('/api/users/stats')
            assert response.status_code == 200
            stats = response.get_json()
            assert 'total_tasks' in stats
            assert 'total_repositories' in stats