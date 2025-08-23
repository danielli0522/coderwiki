"""
API integration tests for task management system.
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
from config import TestingConfig


class TestTaskAPIIntegration:
    """Integration tests for task API endpoints."""
    
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
        
        # Initialize task system
        self.task_service = TaskService()
        self.queue_manager = TaskQueueManager()
        self.worker = TaskWorker(self.queue_manager, max_workers=1)
        
        # Mock task handler
        def mock_handler(task_obj):
            time.sleep(0.1)  # Simulate work
            task_obj.status = 'completed'
            task_obj.progress = 100
            task_obj.result = json.dumps({"success": True, "files_processed": 5})
            task_obj.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        
        self.worker.register_handler('generate_document', mock_handler)
        self.worker.register_handler('sync_repository', mock_handler)
        self.worker.register_handler('analyze_code', mock_handler)
        
        # Start worker
        self.worker.start()
    
    def teardown_method(self):
        """Cleanup test environment."""
        # Stop worker
        if self.worker.is_running():
            self.worker.stop()
        
        # Cleanup
        self.queue_manager.cleanup()
        
        # Cleanup database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def get_auth_headers(self):
        """Get authentication headers for API requests."""
        with self.app.test_client() as client:
            # Login
            response = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Get session cookie
            session_cookie = None
            for cookie in client.cookie_jar:
                if cookie.name == 'session':
                    session_cookie = cookie.value
                    break
            
            return {'Cookie': f'session={session_cookie}'}
    
    def test_create_task_api(self):
        """Test task creation via API."""
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Create task
            response = client.post('/api/tasks', json={
                'repository_id': self.repo.id,
                'type': 'generate_document',
                'title': 'API Created Task',
                'description': 'Task created via API endpoint'
            })
            
            assert response.status_code == 201
            task_data = response.get_json()
            
            # Verify response data
            assert 'id' in task_data
            assert task_data['title'] == 'API Created Task'
            assert task_data['type'] == 'generate_document'
            assert task_data['status'] == 'pending'
            assert task_data['progress'] == 0
            assert task_data['user_id'] == self.user.id
            assert task_data['repository_id'] == self.repo.id
            
            # Verify task in database
            task = Task.query.get(task_data['id'])
            assert task is not None
            assert task.title == 'API Created Task'
    
    def test_create_task_validation(self):
        """Test task creation validation."""
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Test missing required fields
            response = client.post('/api/tasks', json={
                'title': 'Invalid Task'
            })
            
            assert response.status_code == 400
            
            # Test invalid task type
            response = client.post('/api/tasks', json={
                'repository_id': self.repo.id,
                'type': 'invalid_type',
                'title': 'Invalid Type Task'
            })
            
            assert response.status_code == 400
            
            # Test invalid repository ID
            response = client.post('/api/tasks', json={
                'repository_id': 99999,
                'type': 'generate_document',
                'title': 'Invalid Repository Task'
            })
            
            assert response.status_code == 404
    
    def test_get_task_api(self):
        """Test getting task details via API."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='API Get Task',
            description='Task for testing get endpoint'
        )
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Get task
            response = client.get(f'/api/tasks/{task.id}')
            
            assert response.status_code == 200
            task_data = response.get_json()
            
            # Verify response data
            assert task_data['id'] == task.id
            assert task_data['title'] == 'API Get Task'
            assert task_data['type'] == 'generate_document'
            assert 'status_info' in task_data
            assert 'can_retry' in task_data
            assert 'duration' in task_data
    
    def test_get_task_not_found(self):
        """Test getting non-existent task."""
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Get non-existent task
            response = client.get('/api/tasks/99999')
            
            assert response.status_code == 404
    
    def test_get_task_unauthorized(self):
        """Test getting task without authentication."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Unauthorized Task',
            description='Task for testing unauthorized access'
        )
        
        with self.app.test_client() as client:
            # Get task without login
            response = client.get(f'/api/tasks/{task.id}')
            
            assert response.status_code == 401
    
    def test_list_tasks_api(self):
        """Test listing tasks via API."""
        # Create multiple tasks
        tasks = []
        for i in range(5):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'List Task {i+1}',
                description=f'Task {i+1} for testing list endpoint'
            )
            tasks.append(task)
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # List tasks
            response = client.get('/api/tasks')
            
            assert response.status_code == 200
            task_list = response.get_json()
            
            # Verify response
            assert isinstance(task_list, list)
            assert len(task_list) >= 5
            
            # Verify task data
            for task_data in task_list:
                assert 'id' in task_data
                assert 'title' in task_data
                assert 'status' in task_data
                assert 'progress' in task_data
            
            # Test filtering
            response = client.get('/api/tasks?status=pending')
            filtered_tasks = response.get_json()
            
            assert all(t['status'] == 'pending' for t in filtered_tasks)
            
            # Test pagination
            response = client.get('/api/tasks?page=1&per_page=2')
            paginated_tasks = response.get_json()
            
            assert len(paginated_tasks) <= 2
    
    def test_update_task_api(self):
        """Test updating task via API."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Update Task',
            description='Task for testing update endpoint'
        )
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Update task
            response = client.put(f'/api/tasks/{task.id}', json={
                'title': 'Updated Task Title',
                'description': 'Updated description',
                'priority': 'high'
            })
            
            assert response.status_code == 200
            updated_data = response.get_json()
            
            # Verify update
            assert updated_data['title'] == 'Updated Task Title'
            assert updated_data['description'] == 'Updated description'
            assert updated_data['priority'] == 'high'
            
            # Verify in database
            db_task = Task.query.get(task.id)
            assert db_task.title == 'Updated Task Title'
            assert db_task.description == 'Updated description'
    
    def test_delete_task_api(self):
        """Test deleting task via API."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Delete Task',
            description='Task for testing delete endpoint'
        )
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Delete task
            response = client.delete(f'/api/tasks/{task.id}')
            
            assert response.status_code == 200
            
            # Verify deletion
            deleted_task = Task.query.get(task.id)
            assert deleted_task is None
    
    def test_execute_task_api(self):
        """Test task execution via API."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Execute Task',
            description='Task for testing execution endpoint'
        )
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Execute task
            response = client.post(f'/api/tasks/{task.id}/execute')
            
            assert response.status_code == 200
            execute_data = response.get_json()
            
            # Verify execution response
            assert 'message' in execute_data
            assert 'task_id' in execute_data
            
            # Wait for execution to complete
            time.sleep(0.5)
            
            # Verify task completion
            completed_task = Task.query.get(task.id)
            assert completed_task.status == 'completed'
            assert completed_task.progress == 100
    
    def test_retry_task_api(self):
        """Test task retry via API."""
        # Create failed task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Retry Task',
            description='Task for testing retry endpoint'
        )
        task.status = 'failed'
        task.error_message = 'Simulated failure'
        db.session.commit()
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Retry task
            response = client.post(f'/api/tasks/{task.id}/retry')
            
            assert response.status_code == 200
            retry_data = response.get_json()
            
            # Verify retry response
            assert 'message' in retry_data
            assert 'task_id' in retry_data
            
            # Verify task status reset
            retried_task = Task.query.get(task.id)
            assert retried_task.status == 'pending'
            assert retried_task.error_message is None
    
    def test_cancel_task_api(self):
        """Test task cancellation via API."""
        # Create running task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Cancel Task',
            description='Task for testing cancellation endpoint'
        )
        task.status = 'running'
        db.session.commit()
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Cancel task
            response = client.post(f'/api/tasks/{task.id}/cancel')
            
            assert response.status_code == 200
            cancel_data = response.get_json()
            
            # Verify cancellation response
            assert 'message' in cancel_data
            assert 'task_id' in cancel_data
            
            # Verify task status
            cancelled_task = Task.query.get(task.id)
            assert cancelled_task.status == 'cancelled'
    
    def test_task_statistics_api(self):
        """Test task statistics via API."""
        # Create tasks with different statuses
        statuses = ['pending', 'running', 'completed', 'failed']
        for status in statuses:
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Stats Task {status}',
                description=f'Task with status: {status}'
            )
            task.status = status
            if status == 'completed':
                task.progress = 100
                task.completed_at = datetime.utcnow()
            db.session.commit()
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Get statistics
            response = client.get('/api/tasks/statistics')
            
            assert response.status_code == 200
            stats = response.get_json()
            
            # Verify statistics
            assert 'total_tasks' in stats
            assert 'completed_tasks' in stats
            assert 'running_tasks' in stats
            assert 'pending_tasks' in stats
            assert 'failed_tasks' in stats
            assert 'average_progress' in stats
            assert 'task_type_distribution' in stats
            
            # Verify counts
            assert stats['total_tasks'] == 4
            assert stats['completed_tasks'] == 1
            assert stats['running_tasks'] == 1
            assert stats['pending_tasks'] == 1
            assert stats['failed_tasks'] == 1
    
    def test_task_logs_api(self):
        """Test task logs via API."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Logs Task',
            description='Task for testing logs endpoint'
        )
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Get task logs
            response = client.get(f'/api/tasks/{task.id}/logs')
            
            assert response.status_code == 200
            logs_data = response.get_json()
            
            # Verify logs structure
            assert isinstance(logs_data, list)
            # Note: Logs might be empty initially depending on implementation
    
    def test_task_progress_api(self):
        """Test task progress via API."""
        # Create task
        task = self.task_service.create_task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            task_type='generate_document',
            title='Progress Task',
            description='Task for testing progress endpoint'
        )
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Get task progress
            response = client.get(f'/api/tasks/{task.id}/progress')
            
            assert response.status_code == 200
            progress_data = response.get_json()
            
            # Verify progress structure
            assert 'task_id' in progress_data
            assert 'total_progress' in progress_data
            assert 'completed_steps' in progress_data
            assert 'running_steps' in progress_data
            assert 'failed_steps' in progress_data
            assert 'current_step' in progress_data
    
    def test_batch_operations_api(self):
        """Test batch operations via API."""
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = self.task_service.create_task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                task_type='generate_document',
                title=f'Batch Task {i+1}',
                description=f'Task {i+1} for batch operations'
            )
            tasks.append(task)
        
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Batch execute tasks
            task_ids = [task.id for task in tasks]
            response = client.post('/api/tasks/batch/execute', json={
                'task_ids': task_ids
            })
            
            assert response.status_code == 200
            batch_data = response.get_json()
            
            # Verify batch execution
            assert 'message' in batch_data
            assert 'executed_count' in batch_data
            assert batch_data['executed_count'] == 3
            
            # Wait for execution
            time.sleep(0.5)
            
            # Verify all tasks completed
            for task in tasks:
                completed_task = Task.query.get(task.id)
                assert completed_task.status == 'completed'
    
    def test_api_error_handling(self):
        """Test API error handling."""
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Test invalid JSON
            response = client.post('/api/tasks', 
                                 data='invalid json',
                                 content_type='application/json')
            
            assert response.status_code == 400
            
            # Test missing authentication
            client.cookie_jar.clear()
            response = client.get('/api/tasks')
            
            assert response.status_code == 401
            
            # Test invalid task ID
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            response = client.get('/api/tasks/invalid_id')
            
            assert response.status_code == 404
    
    def test_api_rate_limiting(self):
        """Test API rate limiting."""
        with self.app.test_client() as client:
            # Login
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword123'
            })
            
            # Make many requests to test rate limiting
            for i in range(100):  # Adjust based on your rate limit
                response = client.get('/api/tasks')
                if response.status_code == 429:
                    # Rate limit hit
                    break
            
            # Note: Rate limiting behavior depends on your specific implementation
            # This test is a placeholder for rate limiting verification