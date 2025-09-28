"""
Backend test configuration and utilities for local repository scenarios.
Supports both Git remote and local repository testing with comprehensive fixtures.
"""

import pytest
import tempfile
import os
import shutil
import json
import git
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from app.models.document import Document
# from app.services.smart_doc_service import SmartDocumentService
# from app.services.code_quality_service import CodeQualityService


class BackendTestConfig:
    """Configuration for backend tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'backend-test-secret-key'
    WTF_CSRF_ENABLED = False

    # Flask template/static folders (required by create_app)
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    TEMPLATE_FOLDER = str(PROJECT_ROOT / 'frontend' / 'templates')
    STATIC_FOLDER = str(PROJECT_ROOT / 'frontend' / 'static')

    # Local repository configuration
    LOCAL_REPOS_BASE_PATH = Path(__file__).parent.parent.parent / 'coderwiki-output-docs' / 'repos'

    # Test configuration
    MAX_CONCURRENT_TASKS = 4
    TASK_TIMEOUT = 30
    QUEUE_SIZE_LIMIT = 1000

    # Logging configuration
    LOG_LEVEL = 'DEBUG'
    LOG_TO_FILE = False
    LOG_TO_DB = False


@pytest.fixture(scope='session')
def app():
    """Create application for backend tests."""
    app, socketio = create_app(BackendTestConfig)
    return app


@pytest.fixture(scope='session')
def client(app):
    """Create test client for backend tests."""
    return app.test_client()


@pytest.fixture(scope='session')
def test_db(app):
    """Create database for backend tests."""
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
        username='backend_test_user',
        email='backend@test.com'
    )
    user.set_password('test_password_123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_git_repo(temp_dir):
    """Create mock git repository for testing."""
    repo_dir = temp_dir / 'mock_git_repo'
    repo_dir.mkdir()

    # Initialize git repository
    repo = git.Repo.init(repo_dir)

    # Create basic structure
    (repo_dir / 'README.md').write_text('# Test Repository\nThis is a test repository.')
    (repo_dir / 'src').mkdir()
    (repo_dir / 'src' / 'main.py').write_text('def main():\n    print("Hello World")\n')
    (repo_dir / 'tests').mkdir()
    (repo_dir / 'tests' / 'test_main.py').write_text('def test_main():\n    assert True\n')
    (repo_dir / 'requirements.txt').write_text('pytest>=7.0.0\nflask>=2.0.0\n')

    # Add and commit files
    repo.index.add(['.'])
    repo.index.commit('Initial commit')

    return {
        'path': repo_dir,
        'repo': repo,
        'url': f'file://{repo_dir}'
    }


@pytest.fixture
def local_repo_factory(temp_dir):
    """Factory for creating local repositories with different structures."""
    def _create_local_repo(name, structure_type='python', has_git=True, is_valid=True):
        """
        Create a local repository with specified structure.

        Args:
            name: Repository name
            structure_type: Type of project structure (python, node, java, empty)
            has_git: Whether to initialize as git repository
            is_valid: Whether to create a valid repository structure
        """
        repo_dir = temp_dir / name
        repo_dir.mkdir()

        if not is_valid:
            # Create invalid repository (empty or with errors)
            if structure_type == 'empty':
                pass  # Leave empty
            elif structure_type == 'corrupted':
                (repo_dir / 'corrupted_file.txt').write_text('This is corrupted content\x00\x01\x02')
            return {'path': repo_dir, 'is_valid': False}

        # Create valid repository structure based on type
        if structure_type == 'python':
            _create_python_structure(repo_dir)
        elif structure_type == 'node':
            _create_node_structure(repo_dir)
        elif structure_type == 'java':
            _create_java_structure(repo_dir)
        elif structure_type == 'mixed':
            _create_mixed_structure(repo_dir)

        # Initialize git repository if requested
        git_repo = None
        if has_git:
            git_repo = git.Repo.init(repo_dir)
            git_repo.index.add(['.'])
            git_repo.index.commit('Initial commit')

        return {
            'path': repo_dir,
            'git_repo': git_repo,
            'structure_type': structure_type,
            'has_git': has_git,
            'is_valid': True
        }

    def _create_python_structure(repo_dir):
        """Create Python project structure."""
        # Main source files
        (repo_dir / 'src').mkdir()
        (repo_dir / 'src' / '__init__.py').write_text('')
        (repo_dir / 'src' / 'main.py').write_text('''
"""Main application module."""

import os
import sys
from pathlib import Path


class Application:
    """Main application class."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.initialized = False

    def initialize(self):
        """Initialize the application."""
        if self.config_path and Path(self.config_path).exists():
            self.initialized = True
        return self.initialized

    def run(self):
        """Run the application."""
        if not self.initialized:
            raise RuntimeError("Application not initialized")
        print("Application running...")


def main():
    """Entry point."""
    app = Application()
    app.initialize()
    app.run()


if __name__ == "__main__":
    main()
''')

        (repo_dir / 'src' / 'utils.py').write_text('''
"""Utility functions."""

def format_text(text, uppercase=False):
    """Format text according to specifications."""
    if not text:
        return ""

    formatted = text.strip()
    if uppercase:
        formatted = formatted.upper()

    return formatted


def calculate_metrics(data):
    """Calculate basic metrics for data."""
    if not data:
        return {}

    return {
        'count': len(data),
        'average': sum(data) / len(data) if data else 0,
        'min': min(data) if data else 0,
        'max': max(data) if data else 0
    }
''')

        # Test files
        (repo_dir / 'tests').mkdir()
        (repo_dir / 'tests' / '__init__.py').write_text('')
        (repo_dir / 'tests' / 'test_main.py').write_text('''
"""Tests for main module."""

import pytest
from src.main import Application
from src.utils import format_text, calculate_metrics


class TestApplication:
    """Test Application class."""

    def test_init(self):
        """Test application initialization."""
        app = Application()
        assert not app.initialized

    def test_initialize_without_config(self):
        """Test initialization without config."""
        app = Application()
        assert not app.initialize()

    def test_run_not_initialized(self):
        """Test running without initialization."""
        app = Application()
        with pytest.raises(RuntimeError):
            app.run()


class TestUtils:
    """Test utility functions."""

    def test_format_text(self):
        """Test text formatting."""
        assert format_text("  hello  ") == "hello"
        assert format_text("hello", uppercase=True) == "HELLO"
        assert format_text("") == ""

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        data = [1, 2, 3, 4, 5]
        metrics = calculate_metrics(data)
        assert metrics['count'] == 5
        assert metrics['average'] == 3
        assert metrics['min'] == 1
        assert metrics['max'] == 5
''')

        # Configuration files
        (repo_dir / 'requirements.txt').write_text('''
pytest>=7.0.0
flask>=2.0.0
requests>=2.28.0
pydantic>=1.10.0
''')

        (repo_dir / 'setup.py').write_text('''
from setuptools import setup, find_packages

setup(
    name="test-project",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
)
''')

        (repo_dir / 'pyproject.toml').write_text('''
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
description = "A test project"
requires-python = ">=3.8"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
''')

        (repo_dir / 'README.md').write_text('''
# Test Project

This is a test project for local repository analysis.

## Features

- Basic application structure
- Utility functions
- Comprehensive tests
- Modern Python packaging

## Installation

```bash
pip install -e .
```

## Usage

```python
from src.main import Application

app = Application()
app.initialize()
app.run()
```

## Testing

```bash
pytest tests/
```
''')

    def _create_node_structure(repo_dir):
        """Create Node.js project structure."""
        (repo_dir / 'src').mkdir()
        (repo_dir / 'src' / 'index.js').write_text('''
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.json({ message: 'Hello World!' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

module.exports = app;
''')

        (repo_dir / 'tests').mkdir()
        (repo_dir / 'tests' / 'index.test.js').write_text('''
const request = require('supertest');
const app = require('../src/index');

describe('GET /', () => {
    it('should return hello world', async () => {
        const res = await request(app).get('/');
        expect(res.statusCode).toBe(200);
        expect(res.body.message).toBe('Hello World!');
    });
});
''')

        (repo_dir / 'package.json').write_text(json.dumps({
            "name": "test-node-project",
            "version": "1.0.0",
            "description": "Test Node.js project",
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "test": "jest",
                "dev": "nodemon src/index.js"
            },
            "dependencies": {
                "express": "^4.18.0"
            },
            "devDependencies": {
                "jest": "^28.0.0",
                "supertest": "^6.2.0",
                "nodemon": "^2.0.0"
            }
        }, indent=2))

        (repo_dir / 'README.md').write_text('''
# Test Node.js Project

A simple Express.js application for testing.

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```

## Testing

```bash
npm test
```
''')

    def _create_java_structure(repo_dir):
        """Create Java project structure."""
        (repo_dir / 'src' / 'main' / 'java' / 'com' / 'example').mkdir(parents=True)
        (repo_dir / 'src' / 'test' / 'java' / 'com' / 'example').mkdir(parents=True)

        (repo_dir / 'src' / 'main' / 'java' / 'com' / 'example' / 'Application.java').write_text('''
package com.example;

public class Application {
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }

    public String greet(String name) {
        return "Hello, " + name + "!";
    }
}
''')

        (repo_dir / 'src' / 'test' / 'java' / 'com' / 'example' / 'ApplicationTest.java').write_text('''
package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ApplicationTest {

    @Test
    void testGreet() {
        Application app = new Application();
        String result = app.greet("World");
        assertEquals("Hello, World!", result);
    }
}
''')

        (repo_dir / 'pom.xml').write_text('''
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>test-java-project</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <junit.version>5.8.2</junit.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
''')

    def _create_mixed_structure(repo_dir):
        """Create mixed language project structure."""
        # Python components
        (repo_dir / 'backend').mkdir()
        (repo_dir / 'backend' / 'app.py').write_text('''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Python!"})

if __name__ == '__main__':
    app.run(debug=True)
''')

        # Node.js frontend
        (repo_dir / 'frontend').mkdir()
        (repo_dir / 'frontend' / 'index.js').write_text('''
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('<h1>Hello from Node.js!</h1>');
});

app.listen(3000, () => {
    console.log('Frontend running on port 3000');
});
''')

        # Docker configuration
        (repo_dir / 'Dockerfile').write_text('''
FROM node:16-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
EXPOSE 3000
CMD ["npm", "start"]
''')

        (repo_dir / 'docker-compose.yml').write_text('''
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "3000:3000"
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
''')

    return _create_local_repo


@pytest.fixture
def real_local_repos():
    """Provide access to real local repositories for testing."""
    base_path = BackendTestConfig.LOCAL_REPOS_BASE_PATH

    if not base_path.exists():
        pytest.skip(f"Local repos directory not found: {base_path}")

    repos = []
    for repo_dir in base_path.iterdir():
        if repo_dir.is_dir():
            repos.append({
                'name': repo_dir.name,
                'path': repo_dir,
                'has_git': (repo_dir / '.git').exists(),
                'is_valid': _validate_repo_structure(repo_dir)
            })

    return repos


def _validate_repo_structure(repo_path):
    """Validate if repository has a recognizable structure."""
    indicators = [
        'package.json',     # Node.js
        'requirements.txt', # Python
        'pom.xml',         # Java Maven
        'build.gradle',    # Java Gradle
        'Cargo.toml',      # Rust
        'go.mod',          # Go
        'composer.json',   # PHP
        'README.md',       # General
        'src/',            # Source directory
        'lib/',            # Library directory
    ]

    for indicator in indicators:
        if (repo_path / indicator).exists():
            return True

    return False


@pytest.fixture
def repository_factory(db_session, test_user):
    """Factory for creating repository model instances."""
    def _create_repository(name, url=None, is_local=False, local_path=None, **kwargs):
        """Create a repository model instance."""
        repo_data = {
            'user_id': test_user.id,
            'name': name,
            'url': url or f'https://github.com/test/{name}.git',
            'description': kwargs.get('description', f'Test repository: {name}'),
            'is_local': is_local,
            'local_path': str(local_path) if local_path else None,
            **kwargs
        }

        repository = Repository(**repo_data)
        db_session.add(repository)
        db_session.commit()
        return repository

    return _create_repository


@pytest.fixture
def task_factory(db_session, test_user):
    """Factory for creating task instances."""
    def _create_task(repository, task_type='analyze_code', status='pending', **kwargs):
        """Create a task instance."""
        task_data = {
            'user_id': test_user.id,
            'repository_id': repository.id,
            'type': task_type,
            'status': status,
            'progress': kwargs.get('progress', 0),
            'title': kwargs.get('title', f'Test {task_type} task'),
            'description': kwargs.get('description', f'Test task for {task_type}'),
            'priority': kwargs.get('priority', 'normal'),
            **kwargs
        }

        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()
        return task

    return _create_task


@pytest.fixture
def mock_code_quality_service():
    """Mock code quality service for testing."""
    mock_service = Mock()

    mock_service.analyze_local_repository.return_value = {
        'success': True,
        'analysis': {
            'language_distribution': {'Python': 70, 'JavaScript': 20, 'HTML': 10},
            'complexity_metrics': {'average_complexity': 3.2, 'max_complexity': 8},
            'code_quality_score': 85,
            'issues_found': 12,
            'test_coverage': 78
        }
    }

    mock_service.get_supported_languages.return_value = [
        'Python', 'JavaScript', 'Java', 'TypeScript', 'Go', 'Rust'
    ]

    return mock_service


@pytest.fixture
def mock_smart_doc_service():
    """Mock smart document service for testing."""
    mock_service = Mock()

    mock_service.generate_smart_document.return_value = {
        'success': True,
        'task_id': 123,
        'document_id': 456,
        'session_id': 'test-session-123'
    }

    mock_service.get_task_status.return_value = {
        'status': 'completed',
        'progress': 100,
        'result': {'document_generated': True}
    }

    return mock_service


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for API testing."""
    return {
        'Authorization': f'Bearer test-token-{test_user.id}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def test_scenarios():
    """Provide common test scenarios for repository testing."""
    return {
        'valid_local_repos': [
            {'name': 'python-project', 'type': 'python', 'has_git': True},
            {'name': 'node-project', 'type': 'node', 'has_git': True},
            {'name': 'java-project', 'type': 'java', 'has_git': False},
            {'name': 'mixed-project', 'type': 'mixed', 'has_git': True}
        ],
        'invalid_local_repos': [
            {'name': 'empty-repo', 'type': 'empty', 'is_valid': False},
            {'name': 'corrupted-repo', 'type': 'corrupted', 'is_valid': False}
        ],
        'path_scenarios': [
            {'path': '/nonexistent/path', 'should_exist': False},
            {'path': '/etc/passwd', 'should_exist': True, 'is_file': True},
            {'path': '/tmp', 'should_exist': True, 'is_dir': True}
        ]
    }


class TestHelpers:
    """Helper utilities for backend tests."""

    @staticmethod
    def create_test_file_structure(base_path, structure):
        """
        Create test file structure from dictionary.

        Args:
            base_path: Base directory path
            structure: Dict describing file/dir structure
                Example: {'dir1': {'file1.txt': 'content', 'subdir': {}}}
        """
        for name, content in structure.items():
            path = base_path / name
            if isinstance(content, dict):
                path.mkdir(exist_ok=True)
                TestHelpers.create_test_file_structure(path, content)
            else:
                path.write_text(content)

    @staticmethod
    def assert_repository_valid(repo_path):
        """Assert that repository path contains valid structure."""
        assert repo_path.exists(), f"Repository path does not exist: {repo_path}"
        assert repo_path.is_dir(), f"Repository path is not a directory: {repo_path}"

        # Check for common project files
        common_files = ['README.md', 'requirements.txt', 'package.json', 'pom.xml']
        has_project_file = any((repo_path / f).exists() for f in common_files)
        assert has_project_file, f"No common project files found in: {repo_path}"

    @staticmethod
    def assert_git_repository(repo_path):
        """Assert that path contains a valid git repository."""
        git_dir = repo_path / '.git'
        assert git_dir.exists(), f"Git directory not found: {git_dir}"

        try:
            repo = git.Repo(repo_path)
            assert not repo.bare, "Repository should not be bare"
        except git.exc.InvalidGitRepositoryError:
            pytest.fail(f"Invalid git repository: {repo_path}")

    @staticmethod
    def cleanup_test_repos(base_path):
        """Clean up test repositories after testing."""
        if base_path.exists() and 'test' in str(base_path).lower():
            shutil.rmtree(base_path, ignore_errors=True)


@pytest.fixture
def test_helpers():
    """Test helpers fixture."""
    return TestHelpers()


# Pytest configuration and markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "contract: marks tests as contract tests"
    )
    config.addinivalue_line(
        "markers", "local_repo: marks tests that require local repositories"
    )
    config.addinivalue_line(
        "markers", "git_repo: marks tests that require git repositories"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add appropriate markers."""
    for item in items:
        # Mark based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)

        # Mark based on test name patterns
        if "local_repo" in item.name:
            item.add_marker(pytest.mark.local_repo)
        if "git" in item.name:
            item.add_marker(pytest.mark.git_repo)
        if "performance" in item.name or "load" in item.name:
            item.add_marker(pytest.mark.slow)