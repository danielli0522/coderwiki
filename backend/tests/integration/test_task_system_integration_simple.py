"""
Simplified integration tests for task management system.
"""

import pytest
import json
import threading
import time
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from app.services.task_service import TaskService
from app.utils.progress_tracker import ProgressTracker, ProgressTrackerManager
from app.utils.task_logging import TaskLogger, TaskLoggerManager
from config import TestingConfig


class TestTaskSystemIntegration:
    """Integration tests for the task management system."""
    
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
        self.progress_manager = ProgressTrackerManager()
        self.logger_manager = TaskLoggerManager()
    
    def teardown_method(self):
        """Cleanup test environment."""
        # Cleanup managers
        self.progress_manager.cleanup_old_trackers(max_age_hours=0)
        for logger in self.logger_manager.get_all_loggers().values():
            logger.cleanup()
        self.logger_manager.cleanup_old_loggers(max_age_hours=0)
        
        # Cleanup database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_service_integration(self):
        """Test task service integration."""
        # Create task through service
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document'
        )
        
        # Update task with title and description
        task.title = 'Service Integration Test'
        task.description = 'Task created through service'
        db.session.commit()
        
        # Verify task creation
        assert task.id is not None
        assert task.status == 'pending'
        assert task.user_id == self.user.id
        assert task.repository_id == self.repo.id
        
        # Get task statistics
        stats = self.task_service.get_task_statistics(self.user.id)
        assert stats['total_tasks'] >= 1
        assert stats['pending_tasks'] >= 1
        
        # Update task status
        updated_task = self.task_service.update_task_status(task.id, 'running')
        assert updated_task.status == 'running'
        
        # Complete task
        completed_task = self.task_service.update_task_status(task.id, 'completed')
        assert completed_task.status == 'completed'
        
        # Get updated statistics
        updated_stats = self.task_service.get_task_statistics(self.user.id)
        assert updated_stats['completed_tasks'] >= 1
    
    def test_progress_tracking_integration(self):
        """Test progress tracking integration."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document'
        )
        
        # Update task with title and description
        task.title = 'Progress Tracking Test'
        task.description = 'Task for testing progress tracking'
        db.session.commit()
        
        # Create progress tracker
        tracker = self.progress_manager.create_tracker(task.id, task.type)
        
        # Start tracking
        tracker.start()
        
        # Simulate progress updates
        for i in range(4):
            step_idx = tracker.current_step
            if step_idx < len(tracker.steps):
                tracker.start_step(step_idx)
                
                # Update progress
                for progress in [25, 50, 75, 100]:
                    tracker.update_step_progress(step_idx, progress)
                    time.sleep(0.01)  # Small delay
                
                tracker.complete_step(step_idx)
        
        # Complete tracking
        tracker.complete()
        
        # Verify progress
        progress = tracker.get_progress()
        assert progress['total_progress'] == 100.0
        assert progress['completed_steps'] == len(tracker.steps)
        
        # Verify tracker can be retrieved
        retrieved_tracker = self.progress_manager.get_tracker(task.id)
        assert retrieved_tracker is not None
        assert retrieved_tracker.get_progress()['total_progress'] == 100.0
    
    def test_logging_integration(self):
        """Test logging integration."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document'
        )
        
        # Update task with title and description
        task.title = 'Logging Test'
        task.description = 'Task for testing logging'
        db.session.commit()
        
        # Create logger
        logger = self.logger_manager.get_logger(task.id)
        
        # Add logs
        logger.info("Task started", {"task_id": task.id})
        logger.warning("Processing warning", {"severity": "low"})
        logger.error("Processing error", {"error_code": 500})
        
        # Test step logging
        logger.start_step("analysis", {"files": 10})
        logger.update_progress(50, "analysis", {"processed": 5})
        logger.complete_step("analysis", {"processed": 10})
        
        # Verify logs
        logs = logger.get_logs()
        assert len(logs) >= 4  # At least 4 log entries
        
        # Verify error logs
        error_logs = logger.get_error_logs()
        assert len(error_logs) >= 1
        
        # Verify step logs
        step_logs = logger.get_step_logs("analysis")
        assert len(step_logs) >= 3  # Start, progress, complete
        
        # Test log export
        json_export = logger.export_logs('json')
        assert isinstance(json_export, str)
        parsed_logs = json.loads(json_export)
        assert len(parsed_logs) == len(logs)
        
        # Test log summary
        summary = logger.get_summary()
        assert summary['task_id'] == task.id
        assert summary['total_logs'] == len(logs)
        assert summary['error_count'] >= 1
    
    def test_task_with_progress_and_logging(self):
        """Test task with both progress tracking and logging."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document'
        )
        
        # Update task with title and description
        task.title = 'Integrated Test'
        task.description = 'Task with progress tracking and logging'
        db.session.commit()
        
        # Create progress tracker and logger
        tracker = self.progress_manager.create_tracker(task.id, task.type)
        logger = self.logger_manager.get_logger(task.id)
        
        # Start both
        tracker.start()
        logger.info("Task started", {"task_id": task.id})
        
        # Simulate task execution with progress and logging
        steps = [
            ("initialization", "Setting up task environment"),
            ("analysis", "Analyzing repository structure"),
            ("generation", "Generating documentation"),
            ("finalization", "Finalizing generated content")
        ]
        
        for step_name, description in steps:
            logger.start_step(step_name, {"description": description})
            tracker.start_step(tracker.current_step)
            
            # Simulate work with progress updates
            for progress in [25, 50, 75, 100]:
                time.sleep(0.02)
                tracker.update_step_progress(tracker.current_step, progress)
                logger.info(f"Step {step_name} progress: {progress}%", {
                    "step": step_name,
                    "progress": progress
                })
            
            tracker.complete_step(tracker.current_step)
            logger.complete_step(step_name, {"completed": True})
        
        # Complete task
        tracker.complete({"total_steps": len(steps), "success": True})
        logger.info("Task completed successfully", {"total_steps": len(steps)})
        
        # Verify task state
        task.status = 'completed'
        task.progress = 100
        task.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Verify progress tracking
        progress = tracker.get_progress()
        assert progress['total_progress'] == 100.0
        assert progress['completed_steps'] == len(steps)
        
        # Verify logging
        logs = logger.get_logs()
        assert len(logs) >= len(steps) * 4 + 2  # 4 progress updates per step + start + complete
        
        # Verify no errors
        error_logs = logger.get_error_logs()
        assert len(error_logs) == 0
        
        # Verify manager cleanup
        assert len(self.progress_manager.get_all_trackers()) == 1
        assert len(self.logger_manager.get_all_loggers()) == 1
    
    def test_concurrent_task_operations(self):
        """Test concurrent task operations."""
        results = []
        errors = []
        
        def create_and_process_task(task_id):
            """Create and process a task in a separate thread."""
            try:
                # Create task
                task = self.task_service.create_task(
                    user_id=self.user.id,
                    repository_id=self.repo.id,
                    task_type='generate_document'
                )
                
                # Update task with title and description
                task.title = f'Concurrent Task {task_id}'
                task.description = f'Concurrent task {task_id}'
                db.session.commit()
                
                # Create progress tracker and logger
                tracker = self.progress_manager.create_tracker(task.id, task.type)
                logger = self.logger_manager.get_logger(task.id)
                
                # Simulate processing
                tracker.start()
                logger.info(f"Task {task_id} started")
                
                time.sleep(0.05)  # Simulate work
                
                tracker.complete()
                logger.info(f"Task {task_id} completed")
                
                # Update task
                task.status = 'completed'
                task.progress = 100
                task.completed_at = datetime.utcnow()
                db.session.commit()
                
                results.append(task_id)
                
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_and_process_task, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent operations failed: {errors}"
        assert len(results) == 5
        
        # Verify all tasks were created and completed
        completed_tasks = Task.query.filter_by(status='completed').count()
        assert completed_tasks >= 5
        
        # Verify managers have all trackers and loggers
        assert len(self.progress_manager.get_all_trackers()) == 5
        assert len(self.logger_manager.get_all_loggers()) == 5
    
    def test_task_statistics_integration(self):
        """Test task statistics integration."""
        # Create tasks with different statuses
        task_data = [
            ('generate_document', 'pending', 0),
            ('sync_repository', 'running', 25),
            ('analyze_code', 'completed', 100),
            ('generate_document', 'failed', 75),
            ('sync_repository', 'completed', 100)
        ]
        
        created_tasks = []
        for task_type, status, progress in task_data:
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type=task_type
            )
            
            # Update task with title and description
            task.title = f'Stats Test {status}'
            task.description = f'Task for statistics: {status}'
            db.session.commit()
            task.status = status
            task.progress = progress
            if status == 'completed':
                task.completed_at = datetime.utcnow()
            db.session.commit()
            created_tasks.append(task)
        
        # Get statistics
        stats = self.task_service.get_task_statistics(self.user.id)
        
        # Verify statistics
        assert stats['total_tasks'] == 5
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
        expected_avg = sum(progress for _, _, progress in task_data) / len(task_data)
        assert abs(avg_progress - expected_avg) < 0.1
    
    def test_manager_cleanup(self):
        """Test manager cleanup functionality."""
        # Create multiple tasks with trackers and loggers
        for i in range(3):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document'
            )
            
            # Update task with title and description
            task.title = f'Cleanup Test {i+1}'
            task.description = f'Task for cleanup testing {i+1}'
            db.session.commit()
            
            # Create tracker and logger
            tracker = self.progress_manager.create_tracker(task.id, task.type)
            logger = self.logger_manager.get_logger(task.id)
            
            # Set old start time for cleanup testing
            import datetime as dt
            tracker.start_time = dt.datetime.utcnow() - dt.timedelta(hours=25)
            logger.start_time = dt.datetime.utcnow() - dt.timedelta(hours=25)
        
        # Verify managers have trackers and loggers
        assert len(self.progress_manager.get_all_trackers()) == 3
        assert len(self.logger_manager.get_all_loggers()) == 3
        
        # Cleanup old resources
        self.progress_manager.cleanup_old_trackers(max_age_hours=24)
        self.logger_manager.cleanup_old_loggers(max_age_hours=24)
        
        # Verify cleanup
        assert len(self.progress_manager.get_all_trackers()) == 0
        assert len(self.logger_manager.get_all_loggers()) == 0
    
    def test_task_workflow_integration(self):
        """Test complete task workflow integration."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document'
        )
        
        # Update task with title and description
        task.title = 'Workflow Test'
        task.description = 'Complete workflow test'
        db.session.commit()
        
        # Verify initial state
        assert task.status == 'pending'
        assert task.progress == 0
        
        # Create progress tracker and logger
        tracker = self.progress_manager.create_tracker(task.id, task.type)
        logger = self.logger_manager.get_logger(task.id)
        
        # Start workflow
        tracker.start()
        logger.info("Workflow started", {"task_id": task.id})
        
        # Update task status through service
        task = self.task_service.update_task_status(task.id, 'running')
        assert task.status == 'running'
        
        # Simulate workflow steps
        workflow_steps = [
            ("validation", "Validating input parameters"),
            ("preprocessing", "Preprocessing repository data"),
            ("generation", "Generating documentation"),
            ("postprocessing", "Postprocessing generated content"),
            ("validation", "Validating generated output")
        ]
        
        for step_name, description in workflow_steps:
            logger.start_step(step_name, {"description": description})
            
            # Update progress tracker
            if tracker.current_step < len(tracker.steps):
                tracker.start_step(tracker.current_step)
                
                # Simulate step work
                for progress in [0, 25, 50, 75, 100]:
                    tracker.update_step_progress(tracker.current_step, progress)
                    logger.info(f"Step {step_name} progress: {progress}%", {
                        "step": step_name,
                        "progress": progress
                    })
                    time.sleep(0.01)
                
                tracker.complete_step(tracker.current_step)
            
            logger.complete_step(step_name, {"completed": True})
        
        # Complete workflow
        tracker.complete({"workflow_steps": len(workflow_steps), "success": True})
        logger.info("Workflow completed successfully", {"steps": len(workflow_steps)})
        
        # Update task through service
        task = self.task_service.update_task_status(task.id, 'completed')
        assert task.status == 'completed'
        
        # Verify final state
        progress = tracker.get_progress()
        assert progress['total_progress'] == 100.0
        
        logs = logger.get_logs()
        assert len(logs) >= len(workflow_steps) * 5 + 2  # 5 progress updates per step + start + complete
        
        # Get final statistics
        stats = self.task_service.get_task_statistics(self.user.id)
        assert stats['completed_tasks'] >= 1
        assert stats['total_tasks'] >= 1