"""
Integration test configuration and utilities.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from app.services.task_service import TaskService
from app.utils.task_utils import create_batch_tasks, validate_task_permissions
from app.utils.progress_tracker import ProgressTracker, ProgressTrackerManager
from app.utils.task_logging import TaskLogger, TaskLoggerManager


class IntegrationTestConfig:
    """Configuration for integration tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False

    # Template and static folders
    TEMPLATE_FOLDER = Path(__file__).parent.parent.parent / 'frontend' / 'templates'
    STATIC_FOLDER = Path(__file__).parent.parent.parent / 'frontend' / 'static'

    # Task system configuration
    MAX_CONCURRENT_TASKS = 4
    TASK_TIMEOUT = 30
    QUEUE_SIZE_LIMIT = 1000

    # Logging configuration
    LOG_LEVEL = 'DEBUG'
    LOG_TO_FILE = False
    LOG_TO_DB = False

    # Performance test settings
    PERFORMANCE_TEST_TASK_COUNT = 100
    PERFORMANCE_TEST_TIMEOUT = 60


@pytest.fixture(scope='session')
def app():
    """Create application for integration tests."""
    app = create_app(IntegrationTestConfig)
    return app


@pytest.fixture(scope='session')
def client(app):
    """Create test client for integration tests."""
    return app.test_client()


@pytest.fixture(scope='session')
def test_db(app):
    """Create database for integration tests."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def db_session(app, test_db):
    """Create database session for each test."""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        username='integration_test_user',
        email='integration@test.com'
    )
    user.set_password('test_password_123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_repository(db_session, test_user):
    """Create test repository."""
    repo = Repository(
        user_id=test_user.id,
        name='integration-test-repo',
        url='https://github.com/test/integration-test-repo.git',
        description='Integration test repository'
    )
    db_session.add(repo)
    db_session.commit()
    return repo


@pytest.fixture
def task_service(db_session):
    """Create task service instance."""
    return TaskService()


# Simple queue and worker fixtures for basic testing
@pytest.fixture
def simple_queue():
    """Create simple task queue for testing."""
    return []

@pytest.fixture
def simple_worker():
    """Create simple worker for testing."""
    class SimpleWorker:
        def __init__(self):
            self.running = False
            self.handlers = {}

        def register_handler(self, task_type, handler):
            self.handlers[task_type] = handler

        def start(self):
            self.running = True

        def stop(self):
            self.running = False

        def is_running(self):
            return self.running

    return SimpleWorker()

@pytest.fixture
def simple_scheduler():
    """Create simple scheduler for testing."""
    class SimpleScheduler:
        def __init__(self):
            self.running = False
            self.schedules = []

        def create_schedule(self, task_id, schedule_type, start_time, max_executions=1):
            schedule = {
                'id': len(self.schedules) + 1,
                'task_id': task_id,
                'schedule_type': schedule_type,
                'start_time': start_time,
                'max_executions': max_executions,
                'last_execution': None
            }
            self.schedules.append(schedule)
            return schedule

        def start(self):
            self.running = True

        def stop(self):
            self.running = False

        def is_running(self):
            return self.running

        def get_schedule_stats(self, schedule_id):
            schedule = next((s for s in self.schedules if s['id'] == schedule_id), None)
            if schedule:
                return {
                    'total_executions': 1 if schedule['last_execution'] else 0,
                    'schedule_id': schedule_id
                }
            return None

    return SimpleScheduler()


@pytest.fixture
def progress_manager():
    """Create progress tracker manager."""
    return ProgressTrackerManager()


@pytest.fixture
def logger_manager():
    """Create task logger manager."""
    return TaskLoggerManager()


@pytest.fixture
def sample_tasks(db_session, test_user, test_repository):
    """Create sample tasks for testing."""
    tasks = []
    task_data = [
        ('generate_document', 'pending', 0, 'Document Generation Task'),
        ('sync_repository', 'running', 25, 'Repository Sync Task'),
        ('analyze_code', 'completed', 100, 'Code Analysis Task'),
        ('generate_document', 'failed', 75, 'Failed Document Task'),
        ('sync_repository', 'completed', 100, 'Completed Sync Task')
    ]

    for task_type, status, progress, title in task_data:
        task = Task(
            user_id=test_user.id,
            repository_id=test_repository.id,
            type=task_type,
            status=status,
            progress=progress,
            title=title,
            description=f'Sample {task_type} task',
            priority='normal'
        )
        if status == 'completed':
            task.completed_at = datetime.utcnow()
        db_session.add(task)
        tasks.append(task)

    db_session.commit()
    return tasks


@pytest.fixture
def auth_client(app, test_user):
    """Create authenticated test client."""
    with app.test_client() as client:
        # Login user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'test_password_123'
        })
        yield client


@pytest.fixture
def performance_test_data(db_session, test_user, test_repository):
    """Create performance test data."""
    num_tasks = 100
    tasks = []

    for i in range(num_tasks):
        task = Task(
            user_id=test_user.id,
            repository_id=test_repository.id,
            type=['generate_document', 'sync_repository', 'analyze_code'][i % 3],
            status=['pending', 'running', 'completed', 'failed'][i % 4],
            progress=[0, 25, 50, 75, 100][i % 5],
            title=f'Performance Test Task {i+1}',
            description=f'Performance test task {i+1}',
            priority='normal'
        )
        if task.status == 'completed':
            task.completed_at = datetime.utcnow() - timedelta(days=i % 30)
        db_session.add(task)
        tasks.append(task)

    db_session.commit()
    return tasks


class IntegrationTestHelpers:
    """Helper utilities for integration tests."""

    @staticmethod
    def create_task_with_progress(db_session, user, repository, task_type, title, progress_steps=None):
        """Create a task with progress tracking setup."""
        task = Task(
            user_id=user.id,
            repository_id=repository.id,
            type=task_type,
            status='pending',
            progress=0,
            title=title,
            description=f'Task for {title}',
            priority='normal'
        )
        db_session.add(task)
        db_session.commit()

        return task

    @staticmethod
    def simulate_task_execution(task, worker_func, execution_time=0.1):
        """Simulate task execution with progress tracking."""
        import time

        try:
            # Simulate task work
            time.sleep(execution_time)

            # Execute worker function
            result = worker_func(task)

            # Update task status
            task.status = 'completed'
            task.progress = 100
            task.completed_at = datetime.utcnow()

            return result

        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            raise e
        finally:
            db.session.commit()

    @staticmethod
    def measure_performance(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time

    @staticmethod
    def create_concurrent_tasks(db_session, user, repository, count, task_type='generate_document'):
        """Create multiple tasks concurrently."""
        import threading

        tasks = []
        lock = threading.Lock()

        def create_task(i):
            task = Task(
                user_id=user.id,
                repository_id=repository.id,
                type=task_type,
                status='pending',
                progress=0,
                title=f'Concurrent Task {i+1}',
                description=f'Concurrent task {i+1}'
            )
            with lock:
                db_session.add(task)
                tasks.append(task)

        threads = []
        for i in range(count):
            thread = threading.Thread(target=create_task, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        db.session.commit()
        return tasks

    @staticmethod
    def verify_task_completion(task, expected_status='completed', expected_progress=100):
        """Verify task completion status."""
        assert task.status == expected_status
        assert task.progress == expected_progress
        if expected_status == 'completed':
            assert task.completed_at is not None

    @staticmethod
    def cleanup_old_resources(progress_manager, logger_manager, max_age_hours=24):
        """Clean up old resources."""
        progress_manager.cleanup_old_trackers(max_age_hours=max_age_hours)
        logger_manager.cleanup_old_loggers(max_age_hours=max_age_hours)

    @staticmethod
    def get_system_memory_usage():
        """Get current memory usage."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB

    @staticmethod
    def assert_performance_metric(metric_value, expected_min, metric_name):
        """Assert performance metric meets minimum requirement."""
        assert metric_value >= expected_min, (
            f"{metric_name} performance: {metric_value:.2f} < expected minimum: {expected_min:.2f}"
        )

    @staticmethod
    def create_task_batch(db_session, user, repository, batch_size, task_types=None):
        """Create a batch of tasks with different types."""
        if task_types is None:
            task_types = ['generate_document', 'sync_repository', 'analyze_code']

        tasks = []
        for i in range(batch_size):
            task_type = task_types[i % len(task_types)]
            task = Task(
                user_id=user.id,
                repository_id=repository.id,
                type=task_type,
                status='pending',
                progress=0,
                title=f'Batch Task {i+1}',
                description=f'Batch task {i+1} of type {task_type}'
            )
            db.session.add(task)
            tasks.append(task)

        db.session.commit()
        return tasks


@pytest.fixture
def test_helpers():
    """Integration test helpers fixture."""
    return IntegrationTestHelpers()


# Custom markers for integration tests
pytest.mark.slow = pytest.mark.slow
pytest.mark.performance = pytest.mark.performance
pytest.mark.database = pytest.mark.database
pytest.mark.api = pytest.mark.api


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests as database integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark slow tests
        if "performance" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)

        # Mark performance tests
        if "performance" in item.name:
            item.add_marker(pytest.mark.performance)

        # Mark database tests
        if "database" in item.name or "query" in item.name:
            item.add_marker(pytest.mark.database)

        # Mark API tests
        if "api" in item.name or "client" in item.name:
            item.add_marker(pytest.mark.api)
