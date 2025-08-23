"""
Database integration tests for task management system.
"""

import pytest
import json
import threading
import time
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from app.models.task_log import TaskLog
from app.models.task_schedule import TaskSchedule
from app.services.task_service import TaskService
from config import TestingConfig


class TestTaskDatabaseIntegration:
    """Integration tests for database operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test users
        self.users = []
        for i in range(3):
            user = User(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com'
            )
            user.set_password(f'password{i+1}')
            db.session.add(user)
            self.users.append(user)
        
        db.session.commit()
        
        # Create test repositories
        self.repositories = []
        for i, user in enumerate(self.users):
            for j in range(2):
                repo = Repository(
                    user_id=user.id,
                    name=f'user{i+1}-repo{j+1}',
                    url=f'https://github.com/user{i+1}/repo{j+1}.git',
                    description=f'Repository {j+1} for user {i+1}'
                )
                db.session.add(repo)
                self.repositories.append(repo)
        
        db.session.commit()
        
        # Initialize task service
        self.task_service = TaskService()
    
    def teardown_method(self):
        """Cleanup test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_crud_operations(self):
        """Test task CRUD operations."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create task
        task = self.task_service.create_task(
            user_id=user.id,
            repository_id=repo.id,
            task_type='generate_document',
            title='CRUD Test Task',
            description='Task for CRUD testing'
        )
        
        # Verify creation
        assert task.id is not None
        assert task.user_id == user.id
        assert task.repository_id == repo.id
        assert task.type == 'generate_document'
        assert task.status == 'pending'
        
        # Read task
        retrieved_task = Task.query.get(task.id)
        assert retrieved_task is not None
        assert retrieved_task.title == 'CRUD Test Task'
        
        # Update task
        task.title = 'Updated CRUD Task'
        task.status = 'running'
        task.progress = 50
        db.session.commit()
        
        updated_task = Task.query.get(task.id)
        assert updated_task.title == 'Updated CRUD Task'
        assert updated_task.status == 'running'
        assert updated_task.progress == 50
        
        # Delete task
        db.session.delete(task)
        db.session.commit()
        
        deleted_task = Task.query.get(task.id)
        assert deleted_task is None
    
    def test_task_relationships(self):
        """Test task relationships with other models."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create task
        task = self.task_service.create_task(
            user_id=user.id,
            repository_id=repo.id,
            task_type='generate_document',
            title='Relationship Test Task',
            description='Task for relationship testing'
        )
        
        # Test user relationship
        assert task.user == user
        assert task.user.username == user.username
        
        # Test repository relationship
        assert task.repository == repo
        assert task.repository.name == repo.name
        
        # Test reverse relationships
        user_tasks = user.tasks.all()
        assert len(user_tasks) == 1
        assert user_tasks[0] == task
        
        repo_tasks = repo.tasks.all()
        assert len(repo_tasks) == 1
        assert repo_tasks[0] == task
    
    def test_task_querying(self):
        """Test task querying and filtering."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create multiple tasks
        tasks = []
        task_data = [
            ('generate_document', 'pending', 0),
            ('sync_repository', 'running', 25),
            ('analyze_code', 'completed', 100),
            ('generate_document', 'failed', 75),
            ('sync_repository', 'completed', 100)
        ]
        
        for task_type, status, progress in task_data:
            task = self.task_service.create_task(
                user_id=user.id,
                repository_id=repo.id,
                task_type=task_type,
                title=f'{task_type} - {status}',
                description=f'Task with status: {status}'
            )
            task.status = status
            task.progress = progress
            if status == 'completed':
                task.completed_at = datetime.utcnow()
            db.session.add(task)
            tasks.append(task)
        
        db.session.commit()
        
        # Test filtering by status
        pending_tasks = Task.query.filter_by(status='pending').all()
        assert len(pending_tasks) == 1
        assert pending_tasks[0].status == 'pending'
        
        # Test filtering by type
        doc_tasks = Task.query.filter_by(type='generate_document').all()
        assert len(doc_tasks) == 2
        
        # Test filtering by user
        user_tasks = Task.query.filter_by(user_id=user.id).all()
        assert len(user_tasks) == len(task_data)
        
        # Test complex queries
        completed_doc_tasks = Task.query.filter(
            and_(
                Task.type == 'generate_document',
                Task.status == 'completed'
            )
        ).all()
        assert len(completed_doc_tasks) == 0
        
        running_or_failed_tasks = Task.query.filter(
            or_(
                Task.status == 'running',
                Task.status == 'failed'
            )
        ).all()
        assert len(running_or_failed_tasks) == 2
        
        # Test ordering
        tasks_by_progress = Task.query.order_by(Task.progress.desc()).all()
        assert tasks_by_progress[0].progress == 100
        assert tasks_by_progress[-1].progress == 0
        
        # Test pagination
        page1 = Task.query.paginate(page=1, per_page=2)
        assert len(page1.items) == 2
        assert page1.page == 1
        assert page1.per_page == 2
    
    def test_task_aggregation_queries(self):
        """Test task aggregation queries."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create tasks for aggregation
        task_types = ['generate_document', 'sync_repository', 'analyze_code']
        statuses = ['pending', 'running', 'completed', 'failed']
        
        for task_type in task_types:
            for status in statuses:
                task = self.task_service.create_task(
                    user_id=user.id,
                    repository_id=repo.id,
                    task_type=task_type,
                    title=f'{task_type} - {status}',
                    description=f'Task for aggregation: {status}'
                )
                task.status = status
                task.progress = 25 if status == 'running' else (100 if status == 'completed' else 0)
                if status == 'completed':
                    task.completed_at = datetime.utcnow()
                db.session.add(task)
        
        db.session.commit()
        
        # Count tasks by status
        status_counts = db.session.query(
            Task.status,
            func.count(Task.id).label('count')
        ).group_by(Task.status).all()
        
        status_dict = dict(status_counts)
        assert status_dict['pending'] == 3
        assert status_dict['running'] == 3
        assert status_dict['completed'] == 3
        assert status_dict['failed'] == 3
        
        # Count tasks by type
        type_counts = db.session.query(
            Task.type,
            func.count(Task.id).label('count')
        ).group_by(Task.type).all()
        
        type_dict = dict(type_counts)
        assert type_dict['generate_document'] == 4
        assert type_dict['sync_repository'] == 4
        assert type_dict['analyze_code'] == 4
        
        # Calculate average progress
        avg_progress = db.session.query(
            func.avg(Task.progress).label('avg_progress')
        ).scalar()
        
        expected_avg = (0 * 3 + 25 * 3 + 100 * 3 + 0 * 3) / 12  # 3 tasks each status
        assert abs(avg_progress - expected_avg) < 0.1
        
        # Get task counts by date
        today = datetime.utcnow().date()
        daily_counts = db.session.query(
            func.date(Task.created_at).label('date'),
            func.count(Task.id).label('count')
        ).filter(
            func.date(Task.created_at) == today
        ).group_by(func.date(Task.created_at)).all()
        
        assert len(daily_counts) == 1
        assert daily_counts[0].count == 12
    
    def test_task_performance_queries(self):
        """Test task performance-related queries."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create tasks with different performance characteristics
        base_time = datetime.utcnow()
        
        for i in range(10):
            task = self.task_service.create_task(
                user_id=user.id,
                repository_id=repo.id,
                task_type='generate_document',
                title=f'Performance Task {i+1}',
                description=f'Task {i+1} for performance testing'
            )
            
            # Set different completion times
            task.status = 'completed'
            task.progress = 100
            task.started_at = base_time + timedelta(minutes=i*5)
            task.completed_at = base_time + timedelta(minutes=i*5+2)
            db.session.add(task)
        
        db.session.commit()
        
        # Get fastest tasks
        fastest_tasks = db.session.query(
            Task,
            (Task.completed_at - Task.started_at).label('duration')
        ).filter(
            Task.status == 'completed'
        ).order_by(
            (Task.completed_at - Task.started_at)
        ).limit(3).all()
        
        assert len(fastest_tasks) == 3
        
        # Get tasks completed in last hour
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_tasks = Task.query.filter(
            Task.completed_at >= hour_ago
        ).all()
        
        # All tasks should be recent since we just created them
        assert len(recent_tasks) == 10
        
        # Get tasks with longest duration
        longest_tasks = db.session.query(
            Task,
            (Task.completed_at - Task.started_at).label('duration')
        ).filter(
            Task.status == 'completed'
        ).order_by(
            (Task.completed_at - Task.started_at).desc()
        ).limit(3).all()
        
        assert len(longest_tasks) == 3
    
    def test_task_concurrent_operations(self):
        """Test concurrent database operations."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create base task
        task = self.task_service.create_task(
            user_id=user.id,
            repository_id=repo.id,
            task_type='generate_document',
            title='Concurrent Test Task',
            description='Task for concurrent testing'
        )
        
        results = []
        errors = []
        
        def update_task_status(task_id, status, progress):
            """Update task status in a separate thread."""
            try:
                # Create new session for thread
                with self.app.app_context():
                    task_obj = Task.query.get(task_id)
                    if task_obj:
                        task_obj.status = status
                        task_obj.progress = progress
                        db.session.commit()
                        results.append((status, progress))
                    else:
                        errors.append(f"Task {task_id} not found")
            except Exception as e:
                errors.append(f"Error updating task: {str(e)}")
        
        # Create multiple threads to update the same task
        threads = []
        for i, (status, progress) in enumerate([
            ('running', 25),
            ('running', 50),
            ('running', 75),
            ('completed', 100)
        ]):
            thread = threading.Thread(
                target=update_task_status,
                args=(task.id, status, progress)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent updates failed: {errors}"
        assert len(results) == 4
        
        # Check final task state
        final_task = Task.query.get(task.id)
        assert final_task.status == 'completed'
        assert final_task.progress == 100
    
    def test_task_transaction_rollback(self):
        """Test transaction rollback on errors."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create initial task
        task = self.task_service.create_task(
            user_id=user.id,
            repository_id=repo.id,
            task_type='generate_document',
            title='Transaction Test Task',
            description='Task for transaction testing'
        )
        
        initial_task_count = Task.query.count()
        
        # Try to create task with invalid data (should rollback)
        try:
            invalid_task = Task(
                user_id=user.id,
                repository_id=repo.id,
                type='invalid_type',  # This should cause validation error
                status='pending',
                title='Invalid Task'
            )
            db.session.add(invalid_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        
        # Verify no new task was created
        final_task_count = Task.query.count()
        assert final_task_count == initial_task_count
        
        # Verify original task still exists
        original_task = Task.query.get(task.id)
        assert original_task is not None
        assert original_task.title == 'Transaction Test Task'
    
    def test_task_bulk_operations(self):
        """Test bulk task operations."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create multiple tasks
        tasks = []
        for i in range(20):
            task = self.task_service.create_task(
                user_id=user.id,
                repository_id=repo.id,
                task_type='generate_document',
                title=f'Bulk Task {i+1}',
                description=f'Task {i+1} for bulk operations'
            )
            tasks.append(task)
        
        # Bulk update status
        db.session.query(Task).filter(
            Task.user_id == user.id
        ).update({'status': 'running'})
        db.session.commit()
        
        # Verify bulk update
        running_tasks = Task.query.filter_by(status='running').all()
        assert len(running_tasks) == 20
        
        # Bulk delete by status
        db.session.query(Task).filter(
            Task.status == 'running'
        ).delete(synchronize_session=False)
        db.session.commit()
        
        # Verify bulk deletion
        remaining_tasks = Task.query.filter_by(user_id=user.id).all()
        assert len(remaining_tasks) == 0
    
    def test_task_database_constraints(self):
        """Test database constraints."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Test not null constraints
        with pytest.raises(Exception):
            invalid_task = Task(
                user_id=None,  # Should fail not null constraint
                repository_id=repo.id,
                type='generate_document',
                status='pending',
                title='Invalid Task'
            )
            db.session.add(invalid_task)
            db.session.commit()
        
        db.session.rollback()
        
        # Test foreign key constraints
        with pytest.raises(Exception):
            invalid_task = Task(
                user_id=user.id,
                repository_id=99999,  # Invalid foreign key
                type='generate_document',
                status='pending',
                title='Invalid Task'
            )
            db.session.add(invalid_task)
            db.session.commit()
        
        db.session.rollback()
        
        # Test enum constraints
        with pytest.raises(Exception):
            invalid_task = Task(
                user_id=user.id,
                repository_id=repo.id,
                type='invalid_type',  # Invalid enum value
                status='pending',
                title='Invalid Task'
            )
            db.session.add(invalid_task)
            db.session.commit()
        
        db.session.rollback()
    
    def test_task_indexing_performance(self):
        """Test database indexing performance."""
        user = self.users[0]
        repo = self.repositories[0]
        
        # Create many tasks
        start_time = time.time()
        for i in range(1000):
            task = self.task_service.create_task(
                user_id=user.id,
                repository_id=repo.id,
                task_type='generate_document',
                title=f'Index Test Task {i+1}',
                description=f'Task {i+1} for indexing testing'
            )
            task.status = 'completed' if i % 4 == 0 else 'pending'
            task.progress = 100 if task.status == 'completed' else 0
            if task.status == 'completed':
                task.completed_at = datetime.utcnow()
            db.session.add(task)
        
        db.session.commit()
        creation_time = time.time() - start_time
        
        # Test indexed query performance
        start_time = time.time()
        completed_tasks = Task.query.filter_by(status='completed').all()
        query_time = time.time() - start_time
        
        assert len(completed_tasks) == 250  # 1000 / 4
        assert query_time < 1.0  # Should be fast with indexing
        
        # Test user-indexed query
        start_time = time.time()
        user_tasks = Task.query.filter_by(user_id=user.id).all()
        user_query_time = time.time() - start_time
        
        assert len(user_tasks) == 1000
        assert user_query_time < 1.0  # Should be fast with indexing
        
        # Test type-indexed query
        start_time = time.time()
        doc_tasks = Task.query.filter_by(type='generate_document').all()
        type_query_time = time.time() - start_time
        
        assert len(doc_tasks) == 1000
        assert type_query_time < 1.0  # Should be fast with indexing