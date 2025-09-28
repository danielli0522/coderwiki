# Backend Testing Environment

This directory contains the comprehensive testing environment for the CoderWiki backend, specifically configured for testing local repository scenarios and code quality analysis functionality.

## Overview

The testing infrastructure supports:
- **Local Repository Testing**: Analysis of repositories stored in `coderwiki-output-docs/repos/`
- **Remote Repository Testing**: Git repository cloning and analysis
- **Mock Services**: Comprehensive mocking for external dependencies
- **Test Data Factories**: Consistent test data generation
- **Multiple Test Types**: Unit, integration, contract, and end-to-end tests

## Directory Structure

```
backend/tests/
├── conftest.py                      # Main pytest configuration and fixtures
├── pytest.ini                      # Pytest configuration file
├── requirements-test.txt            # Test-specific dependencies
├── README.md                       # This file
├── test_local_repository_scenarios.py  # Sample test demonstrating fixture usage
└── fixtures/
    ├── __init__.py                  # Fixtures package
    ├── repository_fixtures.py       # Repository structure creation utilities
    └── test_data_factories.py      # Data factories for consistent test data
```

## Key Features

### 1. Repository Testing Fixtures

#### Local Repository Factory
Creates realistic repository structures for testing:

```python
def test_python_repository(local_repo_factory, temp_dir):
    repo = local_repo_factory(
        name="test-python-repo",
        structure_type="python",
        has_git=True,
        is_valid=True
    )

    assert repo['path'].exists()
    assert (repo['path'] / 'src').exists()
    assert (repo['path'] / 'requirements.txt').exists()
```

#### Supported Repository Types
- **Python**: Complete Python project with src/, tests/, requirements.txt, setup.py, pyproject.toml
- **Node.js**: Express.js application with package.json, src/, tests/, comprehensive structure
- **Java**: Maven project with proper src/main/java and src/test/java structure
- **Mixed**: Multi-language project with backend/, frontend/, Docker configuration
- **Empty**: For negative testing scenarios
- **Corrupted**: For error handling testing

### 2. Database and Model Fixtures

```python
def test_repository_creation(repository_factory, test_user):
    repo = repository_factory(
        name="test-repo",
        is_local=True,
        local_path="/path/to/repo"
    )

    assert repo.user_id == test_user.id
    assert repo.is_local
```

### 3. Mock Services

Pre-configured mocks for external services:
- **Code Quality Service**: Returns realistic analysis results
- **Smart Document Service**: Simulates document generation
- **Git Service**: Mocks repository operations

### 4. Test Data Factories

Consistent data generation for:
- Users with realistic attributes
- Repositories with proper metadata
- Tasks with various statuses
- Code analysis results
- Documents and artifacts

## Quick Start

### 1. Install Dependencies

```bash
cd backend/tests
pip install -r requirements-test.txt
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run local repository tests
pytest -m local_repo

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest test_local_repository_scenarios.py
```

### 3. Test Markers

Use markers to categorize and run specific test types:

```bash
pytest -m "unit and not slow"          # Fast unit tests only
pytest -m "integration or contract"    # Integration and contract tests
pytest -m local_repo                   # Local repository tests
pytest -m git_repo                     # Git-related tests
pytest -m "not slow"                   # Skip slow tests
```

## Configuration

### Environment Variables

Set these environment variables for testing:

```bash
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:
export LOCAL_REPOS_PATH=/path/to/coderwiki-output-docs/repos
```

### Pytest Configuration

The `pytest.ini` file configures:
- Test discovery patterns
- Markers for test categorization
- Coverage settings
- Logging configuration
- Timeout settings

## Writing Tests

### Basic Test Structure

```python
import pytest
from fixtures.test_data_factories import RepositoryFactory

class TestMyFeature:
    def test_something(self, test_user, db_session):
        # Arrange
        repo_data = RepositoryFactory.create_repository_data(
            name="test-repo",
            repo_type="python"
        )

        # Act
        result = my_function(repo_data)

        # Assert
        assert result is not None
```

### Using Repository Fixtures

```python
def test_local_repository_analysis(local_repo_factory, temp_dir):
    # Create a realistic Python repository
    repo = local_repo_factory(
        name="analysis-test",
        structure_type="python",
        has_git=True
    )

    # Test your analysis logic
    result = analyze_repository(repo['path'])
    assert result['success']
```

### Testing Different Scenarios

```python
@pytest.mark.parametrize("repo_type", ["python", "node", "java"])
def test_multiple_languages(local_repo_factory, repo_type):
    repo = local_repo_factory(
        name=f"test-{repo_type}",
        structure_type=repo_type
    )

    result = detect_language(repo['path'])
    assert result is not None
```

## Advanced Features

### Real Repository Testing

Access real repositories for integration testing:

```python
def test_real_repositories(real_local_repos):
    for repo in real_local_repos:
        if repo['is_valid']:
            result = analyze_repository(repo['path'])
            assert result is not None
```

### Mock Service Configuration

```python
def test_with_custom_mock(mock_code_quality_service):
    # Configure mock behavior
    mock_code_quality_service.analyze_local_repository.return_value = {
        'success': True,
        'analysis': {'score': 95}
    }

    # Test your code
    result = my_analysis_function()
    assert result['analysis']['score'] == 95
```

### Test Data Factories

```python
def test_comprehensive_scenario():
    # Create a complete test scenario
    scenario = TestScenarioFactory.create_comprehensive_test_suite()

    users = scenario['users']
    repositories = scenario['repositories']
    mock_services = scenario['mock_services']

    # Use in your tests
    assert len(users) > 0
    assert len(repositories) > 0
```

## Performance Testing

### Parallel Testing

```bash
# Run tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Memory Profiling

```python
@pytest.mark.performance
def test_memory_usage(memory_profiler):
    # Test memory-intensive operations
    result = process_large_repository()
    assert memory_profiler.peak_memory < 100  # MB
```

## Troubleshooting

### Common Issues

1. **Git Repository Initialization Fails**
   - Ensure git is installed and configured
   - Check file permissions in temp directories

2. **Import Errors**
   - Verify all test dependencies are installed
   - Check Python path configuration

3. **Database Issues**
   - Ensure SQLite is available for in-memory testing
   - Check database fixture configuration

4. **File Permission Errors**
   - Run tests with appropriate permissions
   - Check temp directory access

### Debugging

```bash
# Run with verbose output
pytest -v -s

# Run with debugging
pytest --pdb

# Run with logging
pytest --log-cli-level=DEBUG
```

## Best Practices

### Test Organization

1. **Group Related Tests**: Use test classes to organize related functionality
2. **Use Descriptive Names**: Test names should clearly describe what is being tested
3. **Follow AAA Pattern**: Arrange, Act, Assert structure
4. **Use Fixtures**: Leverage fixtures for setup and teardown

### Performance

1. **Use Session-Scoped Fixtures**: For expensive setup operations
2. **Mark Slow Tests**: Use `@pytest.mark.slow` for long-running tests
3. **Parallel Execution**: Use pytest-xdist for parallel test execution
4. **Mock External Services**: Always mock external dependencies

### Maintenance

1. **Keep Fixtures Updated**: Update test data when models change
2. **Review Test Coverage**: Aim for >80% coverage on critical paths
3. **Clean Up Resources**: Ensure proper cleanup in fixtures
4. **Document Complex Tests**: Add docstrings for complex test scenarios

## Contributing

When adding new tests:

1. Use existing fixtures when possible
2. Add new fixtures to appropriate modules
3. Update this README for new features
4. Add appropriate test markers
5. Ensure tests are deterministic and isolated

## Integration with CI/CD

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions configuration
- name: Run Tests
  run: |
    cd backend
    pip install -r tests/requirements-test.txt
    pytest --cov=app --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Future Enhancements

Planned improvements:
- [ ] Visual regression testing for generated documentation
- [ ] Load testing for repository analysis
- [ ] Integration with external code quality tools
- [ ] Automated test data generation from real repositories
- [ ] Cross-platform testing support