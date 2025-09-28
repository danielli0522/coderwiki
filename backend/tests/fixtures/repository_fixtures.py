"""
Repository fixture utilities for creating mock repository structures.
Supports various programming languages and project types.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
import git


class RepositoryFixture:
    """Base class for repository fixtures."""

    def __init__(self, name: str, base_path: Path):
        self.name = name
        self.base_path = base_path
        self.repo_path = base_path / name
        self.git_repo = None

    def create(self, initialize_git: bool = True) -> Path:
        """Create the repository structure."""
        self.repo_path.mkdir(parents=True, exist_ok=True)

        # Create project structure
        self._create_structure()

        # Initialize git if requested
        if initialize_git:
            self._initialize_git()

        return self.repo_path

    def cleanup(self):
        """Remove the repository directory."""
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path, ignore_errors=True)

    def _create_structure(self):
        """Override in subclasses to create specific structure."""
        raise NotImplementedError

    def _initialize_git(self):
        """Initialize git repository."""
        try:
            self.git_repo = git.Repo.init(self.repo_path)
            self.git_repo.index.add(['.'])
            self.git_repo.index.commit('Initial commit')
        except Exception as e:
            print(f"Warning: Failed to initialize git repository: {e}")

    def add_commit(self, message: str, files: Optional[List[str]] = None):
        """Add files and create a commit."""
        if not self.git_repo:
            return

        if files:
            self.git_repo.index.add(files)
        else:
            self.git_repo.index.add(['.'])

        self.git_repo.index.commit(message)


class PythonRepositoryFixture(RepositoryFixture):
    """Fixture for Python project repositories."""

    def _create_structure(self):
        """Create Python project structure."""
        # Main application code
        src_dir = self.repo_path / 'src'
        src_dir.mkdir(exist_ok=True)

        # Package initialization
        (src_dir / '__init__.py').write_text('')

        # Main application module
        (src_dir / 'app.py').write_text('''
"""Main application module."""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class DataProcessor:
    """Processes various types of data."""

    def __init__(self, config: Dict):
        self.config = config
        self.processed_items = 0

    def validate_config(self) -> bool:
        """Validate processor configuration."""
        required_keys = ['input_dir', 'output_dir', 'format']
        return all(key in self.config for key in required_keys)

    def process_files(self, files: List[Path]) -> Dict:
        """Process a list of files."""
        results = {'processed': 0, 'errors': 0, 'skipped': 0}

        for file_path in files:
            try:
                if self._should_process_file(file_path):
                    self._process_single_file(file_path)
                    results['processed'] += 1
                else:
                    results['skipped'] += 1
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results['errors'] += 1

        return results

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        if not file_path.exists():
            return False

        allowed_extensions = self.config.get('allowed_extensions', ['.txt', '.py'])
        return file_path.suffix.lower() in allowed_extensions

    def _process_single_file(self, file_path: Path):
        """Process a single file."""
        content = file_path.read_text(encoding='utf-8')
        processed_content = self._transform_content(content)

        output_path = Path(self.config['output_dir']) / file_path.name
        output_path.write_text(processed_content, encoding='utf-8')

    def _transform_content(self, content: str) -> str:
        """Transform file content based on configuration."""
        transformations = self.config.get('transformations', [])

        for transform in transformations:
            if transform == 'uppercase':
                content = content.upper()
            elif transform == 'remove_comments':
                lines = [line for line in content.split('\\n')
                        if not line.strip().startswith('#')]
                content = '\\n'.join(lines)

        return content


class Application:
    """Main application class."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = {}
        self.processor = None

    def load_config(self):
        """Load application configuration."""
        if not self.config_file:
            self.config = self._get_default_config()
        else:
            config_path = Path(self.config_file)
            if not config_path.exists():
                raise ConfigurationError(f"Config file not found: {config_path}")

            import json
            self.config = json.loads(config_path.read_text())

        # Validate configuration
        if not self._validate_config():
            raise ConfigurationError("Invalid configuration")

    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            'input_dir': './input',
            'output_dir': './output',
            'format': 'text',
            'allowed_extensions': ['.txt', '.py', '.md'],
            'transformations': []
        }

    def _validate_config(self) -> bool:
        """Validate the loaded configuration."""
        required_fields = ['input_dir', 'output_dir', 'format']
        return all(field in self.config for field in required_fields)

    def initialize(self):
        """Initialize the application."""
        self.load_config()
        self.processor = DataProcessor(self.config)

        # Create directories if they don't exist
        Path(self.config['input_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['output_dir']).mkdir(parents=True, exist_ok=True)

    def run(self):
        """Run the application."""
        if not self.processor:
            raise RuntimeError("Application not initialized")

        input_dir = Path(self.config['input_dir'])
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return

        # Find files to process
        files_to_process = list(input_dir.glob('**/*'))
        files_to_process = [f for f in files_to_process if f.is_file()]

        if not files_to_process:
            logger.info("No files found to process")
            return

        logger.info(f"Processing {len(files_to_process)} files...")
        results = self.processor.process_files(files_to_process)

        logger.info(f"Processing complete: {results}")


def main():
    """Application entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Data Processing Application')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        app = Application(args.config)
        app.initialize()
        app.run()
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
''')

        # Utility modules
        (src_dir / 'utils.py').write_text('''
"""Utility functions for the application."""

import os
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """Calculate SHA256 hash of a file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    hash_sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_json_file(file_path: Union[str, Path]) -> Dict:
    """Read and parse JSON file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def write_json_file(data: Dict, file_path: Union[str, Path], indent: int = 2):
    """Write data to JSON file."""
    path = Path(file_path)
    ensure_directory(path.parent)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_file_stats(file_path: Union[str, Path]) -> Dict:
    """Get file statistics."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    stat = path.stat()
    return {
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
        'extension': path.suffix.lower(),
        'name': path.name
    }


def filter_files_by_extension(directory: Union[str, Path],
                            extensions: List[str],
                            recursive: bool = True) -> List[Path]:
    """Filter files in directory by extensions."""
    path = Path(directory)
    if not path.exists() or not path.is_dir():
        return []

    pattern = '**/*' if recursive else '*'
    all_files = path.glob(pattern)

    filtered_files = []
    for file_path in all_files:
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            filtered_files.append(file_path)

    return sorted(filtered_files)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def is_text_file(file_path: Union[str, Path]) -> bool:
    """Check if file is likely a text file."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return False

    # Check by extension first
    text_extensions = {
        '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml',
        '.md', '.rst', '.cfg', '.ini', '.log', '.sql', '.csv', '.sh', '.bat'
    }

    if path.suffix.lower() in text_extensions:
        return True

    # Check by reading first few bytes
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            # If no null bytes and mostly printable characters
            if b'\\x00' not in chunk:
                text_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
                return text_chars / len(chunk) > 0.75 if chunk else True
    except (IOError, OSError):
        pass

    return False


class FileProcessor:
    """Generic file processing utility."""

    def __init__(self, input_dir: Union[str, Path], output_dir: Union[str, Path]):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        ensure_directory(self.output_dir)

    def process_all_files(self, extensions: List[str] = None) -> Dict:
        """Process all files in input directory."""
        if extensions is None:
            extensions = ['.txt', '.py', '.md']

        files = filter_files_by_extension(self.input_dir, extensions)
        results = {'processed': 0, 'errors': 0, 'total': len(files)}

        for file_path in files:
            try:
                self.process_file(file_path)
                results['processed'] += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results['errors'] += 1

        return results

    def process_file(self, file_path: Path):
        """Process a single file - override in subclasses."""
        # Default implementation: copy file to output directory
        relative_path = file_path.relative_to(self.input_dir)
        output_path = self.output_dir / relative_path

        ensure_directory(output_path.parent)
        output_path.write_text(file_path.read_text(encoding='utf-8'),
                             encoding='utf-8')
''')

        # Database models
        models_dir = src_dir / 'models'
        models_dir.mkdir(exist_ok=True)
        (models_dir / '__init__.py').write_text('')

        (models_dir / 'base.py').write_text('''
"""Base model classes."""

from datetime import datetime
from typing import Dict, Any


class BaseModel:
    """Base class for all models."""

    def __init__(self):
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def update(self, **kwargs):
        """Update model attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class Repository(BaseModel):
    """Repository model."""

    def __init__(self, name: str, url: str, description: str = None):
        super().__init__()
        self.id = None
        self.name = name
        self.url = url
        self.description = description
        self.is_active = True

    def __repr__(self):
        return f"Repository(name='{self.name}', url='{self.url}')"
''')

        # Tests directory
        tests_dir = self.repo_path / 'tests'
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / '__init__.py').write_text('')

        (tests_dir / 'test_app.py').write_text('''
"""Tests for main application."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.app import Application, DataProcessor, ConfigurationError


class TestApplication:
    """Test cases for Application class."""

    def test_init_without_config(self):
        """Test application initialization without config file."""
        app = Application()
        assert app.config_file is None
        assert app.config == {}
        assert app.processor is None

    def test_init_with_config(self):
        """Test application initialization with config file."""
        app = Application('config.json')
        assert app.config_file == 'config.json'

    def test_default_config(self):
        """Test default configuration."""
        app = Application()
        default_config = app._get_default_config()

        assert 'input_dir' in default_config
        assert 'output_dir' in default_config
        assert 'format' in default_config
        assert default_config['format'] == 'text'

    def test_load_config_default(self):
        """Test loading default configuration."""
        app = Application()
        app.load_config()

        assert app.config is not None
        assert 'input_dir' in app.config

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        app = Application('nonexistent.json')

        with pytest.raises(ConfigurationError, match="Config file not found"):
            app.load_config()

    def test_initialize_success(self):
        """Test successful application initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            app = Application()
            app.config = {
                'input_dir': str(tmp_path / 'input'),
                'output_dir': str(tmp_path / 'output'),
                'format': 'text',
                'allowed_extensions': ['.txt']
            }

            app.initialize()

            assert app.processor is not None
            assert Path(app.config['input_dir']).exists()
            assert Path(app.config['output_dir']).exists()

    def test_run_not_initialized(self):
        """Test running application without initialization."""
        app = Application()

        with pytest.raises(RuntimeError, match="Application not initialized"):
            app.run()

    @patch('src.app.logger')
    def test_run_no_input_dir(self, mock_logger):
        """Test running with non-existent input directory."""
        app = Application()
        app.processor = Mock()
        app.config = {'input_dir': '/nonexistent/path'}

        app.run()

        mock_logger.error.assert_called_once()

    def test_run_empty_directory(self):
        """Test running with empty input directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_dir = tmp_path / 'input'
            input_dir.mkdir()

            app = Application()
            app.processor = Mock()
            app.config = {'input_dir': str(input_dir)}

            with patch('src.app.logger') as mock_logger:
                app.run()
                mock_logger.info.assert_called_with("No files found to process")


class TestDataProcessor:
    """Test cases for DataProcessor class."""

    def test_init(self):
        """Test processor initialization."""
        config = {'input_dir': '/test', 'output_dir': '/output', 'format': 'text'}
        processor = DataProcessor(config)

        assert processor.config == config
        assert processor.processed_items == 0

    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        config = {'input_dir': '/test', 'output_dir': '/output', 'format': 'text'}
        processor = DataProcessor(config)

        assert processor.validate_config() is True

    def test_validate_config_invalid(self):
        """Test configuration validation with invalid config."""
        config = {'input_dir': '/test'}  # Missing required keys
        processor = DataProcessor(config)

        assert processor.validate_config() is False

    def test_should_process_file_valid(self):
        """Test file processing check with valid file."""
        config = {
            'input_dir': '/test',
            'output_dir': '/output',
            'format': 'text',
            'allowed_extensions': ['.txt', '.py']
        }

        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp_file:
            processor = DataProcessor(config)
            result = processor._should_process_file(Path(tmp_file.name))
            assert result is True

    def test_should_process_file_wrong_extension(self):
        """Test file processing check with wrong extension."""
        config = {
            'input_dir': '/test',
            'output_dir': '/output',
            'format': 'text',
            'allowed_extensions': ['.txt']
        }

        with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp_file:
            processor = DataProcessor(config)
            result = processor._should_process_file(Path(tmp_file.name))
            assert result is False

    def test_transform_content_uppercase(self):
        """Test content transformation with uppercase."""
        config = {
            'input_dir': '/test',
            'output_dir': '/output',
            'format': 'text',
            'transformations': ['uppercase']
        }

        processor = DataProcessor(config)
        result = processor._transform_content('hello world')
        assert result == 'HELLO WORLD'

    def test_transform_content_remove_comments(self):
        """Test content transformation removing comments."""
        config = {
            'input_dir': '/test',
            'output_dir': '/output',
            'format': 'text',
            'transformations': ['remove_comments']
        }

        content = 'line1\\n# comment\\nline2\\n# another comment'
        processor = DataProcessor(config)
        result = processor._transform_content(content)

        lines = result.split('\\n')
        assert 'line1' in lines
        assert 'line2' in lines
        assert not any('comment' in line for line in lines)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'input_dir': '/tmp/test/input',
        'output_dir': '/tmp/test/output',
        'format': 'text',
        'allowed_extensions': ['.txt', '.py', '.md'],
        'transformations': []
    }


@pytest.fixture
def temp_directory():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


def test_integration_full_workflow(temp_directory, sample_config):
    """Test full application workflow integration."""
    # Setup directories
    input_dir = temp_directory / 'input'
    output_dir = temp_directory / 'output'
    input_dir.mkdir(parents=True)

    # Create test files
    (input_dir / 'test1.txt').write_text('Hello World')
    (input_dir / 'test2.py').write_text('print("Hello Python")')

    # Update config with real paths
    config = sample_config.copy()
    config['input_dir'] = str(input_dir)
    config['output_dir'] = str(output_dir)

    # Run application
    app = Application()
    app.config = config
    app.initialize()
    app.run()

    # Verify results
    assert output_dir.exists()
    assert (output_dir / 'test1.txt').exists()
    assert (output_dir / 'test2.py').exists()

    # Verify content
    assert (output_dir / 'test1.txt').read_text() == 'Hello World'
    assert (output_dir / 'test2.py').read_text() == 'print("Hello Python")'
''')

        (tests_dir / 'test_utils.py').write_text('''
"""Tests for utility functions."""

import pytest
import tempfile
import json
from pathlib import Path
from src.utils import (
    calculate_file_hash, ensure_directory, read_json_file, write_json_file,
    get_file_stats, filter_files_by_extension, format_file_size,
    is_text_file, FileProcessor
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write('test content')
            tmp_path = Path(tmp_file.name)

        try:
            hash_value = calculate_file_hash(tmp_path)
            assert isinstance(hash_value, str)
            assert len(hash_value) == 64  # SHA256 hex length

            # Same content should produce same hash
            hash_value2 = calculate_file_hash(tmp_path)
            assert hash_value == hash_value2
        finally:
            tmp_path.unlink()

    def test_calculate_file_hash_not_found(self):
        """Test hash calculation for non-existent file."""
        with pytest.raises(FileNotFoundError):
            calculate_file_hash('/nonexistent/file.txt')

    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_path = Path(tmp_dir) / 'new' / 'nested' / 'directory'

            result = ensure_directory(test_path)

            assert result.exists()
            assert result.is_dir()
            assert result == test_path

    def test_read_json_file(self):
        """Test JSON file reading."""
        test_data = {'key': 'value', 'number': 42, 'nested': {'inner': True}}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_path = Path(tmp_file.name)

        try:
            result = read_json_file(tmp_path)
            assert result == test_data
        finally:
            tmp_path.unlink()

    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with pytest.raises(FileNotFoundError):
            read_json_file('/nonexistent/file.json')

    def test_read_json_file_invalid(self):
        """Test reading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write('invalid json content')
            tmp_path = Path(tmp_file.name)

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                read_json_file(tmp_path)
        finally:
            tmp_path.unlink()

    def test_write_json_file(self):
        """Test JSON file writing."""
        test_data = {'test': True, 'values': [1, 2, 3]}

        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = Path(tmp_dir) / 'test.json'

            write_json_file(test_data, json_path)

            assert json_path.exists()
            with open(json_path) as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data

    def test_get_file_stats(self):
        """Test file statistics retrieval."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write('test content for stats')
            tmp_path = Path(tmp_file.name)

        try:
            stats = get_file_stats(tmp_path)

            assert 'size' in stats
            assert 'created' in stats
            assert 'modified' in stats
            assert 'is_file' in stats
            assert 'is_dir' in stats
            assert stats['is_file'] is True
            assert stats['is_dir'] is False
            assert stats['size'] > 0
        finally:
            tmp_path.unlink()

    def test_filter_files_by_extension(self):
        """Test file filtering by extension."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir)

            # Create test files
            (test_dir / 'file1.txt').write_text('content')
            (test_dir / 'file2.py').write_text('content')
            (test_dir / 'file3.jpg').write_text('content')
            (test_dir / 'subdir').mkdir()
            (test_dir / 'subdir' / 'file4.txt').write_text('content')

            # Test filtering
            txt_files = filter_files_by_extension(test_dir, ['.txt'])
            py_files = filter_files_by_extension(test_dir, ['.py'])
            multiple_files = filter_files_by_extension(test_dir, ['.txt', '.py'])

            assert len(txt_files) == 2  # file1.txt and subdir/file4.txt
            assert len(py_files) == 1   # file2.py
            assert len(multiple_files) == 3  # all txt and py files

            # Test non-recursive
            non_recursive = filter_files_by_extension(test_dir, ['.txt'], recursive=False)
            assert len(non_recursive) == 1  # only file1.txt

    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0B"
        assert format_file_size(1023) == "1023B"
        assert format_file_size(1024) == "1.0KB"
        assert format_file_size(1048576) == "1.0MB"
        assert format_file_size(1073741824) == "1.0GB"

    def test_is_text_file(self):
        """Test text file detection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir)

            # Create text file
            text_file = test_dir / 'test.txt'
            text_file.write_text('This is a text file')

            # Create Python file
            py_file = test_dir / 'test.py'
            py_file.write_text('print("Hello World")')

            # Create binary file
            binary_file = test_dir / 'test.bin'
            binary_file.write_bytes(b'\\x00\\x01\\x02\\x03\\x04\\x05')

            assert is_text_file(text_file) is True
            assert is_text_file(py_file) is True
            assert is_text_file(binary_file) is False
            assert is_text_file('/nonexistent/file') is False


class TestFileProcessor:
    """Test FileProcessor class."""

    def test_init(self):
        """Test FileProcessor initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir) / 'input'
            output_dir = Path(tmp_dir) / 'output'

            processor = FileProcessor(input_dir, output_dir)

            assert processor.input_dir == input_dir
            assert processor.output_dir == output_dir
            assert output_dir.exists()

    def test_process_all_files(self):
        """Test processing all files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir) / 'input'
            output_dir = Path(tmp_dir) / 'output'
            input_dir.mkdir()

            # Create test files
            (input_dir / 'file1.txt').write_text('content 1')
            (input_dir / 'file2.py').write_text('print("hello")')
            (input_dir / 'file3.jpg').write_text('not processed')

            processor = FileProcessor(input_dir, output_dir)
            results = processor.process_all_files(['.txt', '.py'])

            assert results['total'] == 2
            assert results['processed'] == 2
            assert results['errors'] == 0

            # Check output files
            assert (output_dir / 'file1.txt').exists()
            assert (output_dir / 'file2.py').exists()
            assert not (output_dir / 'file3.jpg').exists()

            # Check content
            assert (output_dir / 'file1.txt').read_text() == 'content 1'
            assert (output_dir / 'file2.py').read_text() == 'print("hello")'
''')

        # Configuration files
        (self.repo_path / 'requirements.txt').write_text('''
# Core dependencies
flask>=2.0.0
requests>=2.28.0
pydantic>=1.10.0
click>=8.0.0

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991

# Optional dependencies
redis>=4.0.0
celery>=5.2.0
''')

        (self.repo_path / 'setup.py').write_text('''
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="python-test-project",
    version="0.1.0",
    author="Test Author",
    author_email="test@example.com",
    description="A comprehensive Python test project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "redis": [
            "redis>=4.0.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio>=3.4.3",
        ]
    },
    entry_points={
        "console_scripts": [
            "myapp=src.app:main",
        ],
    },
)
''')

        (self.repo_path / 'pyproject.toml').write_text('''
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[project]
name = "python-test-project"
dynamic = ["version"]
description = "A comprehensive Python test project"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Test Author", email = "test@example.com"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    "flask>=2.0.0",
    "requests>=2.28.0",
    "pydantic>=1.10.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
]
redis = [
    "redis>=4.0.0",
]
async = [
    "aiohttp>=3.8.0",
]

[project.scripts]
myapp = "src.app:main"

[project.urls]
Homepage = "https://github.com/example/python-test-project"
Repository = "https://github.com/example/python-test-project.git"
Documentation = "https://python-test-project.readthedocs.io"
"Bug Tracker" = "https://github.com/example/python-test-project/issues"
''')

        # Documentation
        (self.repo_path / 'README.md').write_text('''
# Python Test Project

A comprehensive Python test project for demonstrating code analysis capabilities.

## Features

- Modular application architecture
- Comprehensive test suite
- Modern Python packaging (setuptools + pyproject.toml)
- Code quality tools configuration
- Utility functions and models
- CLI interface

## Installation

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e .[dev]

# Install with all optional dependencies
pip install -e .[dev,redis,async]
```

## Usage

Run the application:

```bash
# Using the installed script
myapp --config config.json

# Or directly
python src/app.py --config config.json --verbose
```

## Development

Install development dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest tests/
```

Run code quality checks:

```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Project Structure

```
src/
├── __init__.py
├── app.py              # Main application
├── utils.py            # Utility functions
└── models/
    ├── __init__.py
    └── base.py         # Base model classes

tests/
├── __init__.py
├── test_app.py         # Application tests
└── test_utils.py       # Utility tests

requirements.txt        # Dependencies
setup.py               # Legacy packaging
pyproject.toml          # Modern packaging
README.md              # This file
```

## License

MIT License
''')


class NodeRepositoryFixture(RepositoryFixture):
    """Fixture for Node.js project repositories."""

    def _create_structure(self):
        """Create Node.js project structure."""
        # Package.json
        package_json = {
            "name": "node-test-project",
            "version": "1.0.0",
            "description": "A Node.js test project for code analysis",
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "dev": "nodemon src/index.js",
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage",
                "lint": "eslint src/ tests/",
                "lint:fix": "eslint src/ tests/ --fix",
                "build": "webpack --mode production",
                "build:dev": "webpack --mode development"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^6.0.0",
                "morgan": "^1.10.0",
                "dotenv": "^16.0.3"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "supertest": "^6.3.0",
                "nodemon": "^2.0.20",
                "eslint": "^8.0.0",
                "webpack": "^5.75.0",
                "webpack-cli": "^5.0.0"
            },
            "engines": {
                "node": ">=16.0.0",
                "npm": ">=8.0.0"
            }
        }

        (self.repo_path / 'package.json').write_text(json.dumps(package_json, indent=2))

        # Source files
        src_dir = self.repo_path / 'src'
        src_dir.mkdir(exist_ok=True)

        (src_dir / 'index.js').write_text('''
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
    res.json({
        message: 'Node.js Test API',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage()
    });
});

app.get('/api/users', (req, res) => {
    const users = [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
    ];
    res.json(users);
});

app.post('/api/users', (req, res) => {
    const { name, email } = req.body;

    if (!name || !email) {
        return res.status(400).json({
            error: 'Name and email are required'
        });
    }

    const newUser = {
        id: Date.now(),
        name,
        email,
        created: new Date().toISOString()
    };

    res.status(201).json(newUser);
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Something went wrong!',
        message: err.message
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Endpoint not found'
    });
});

if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
    });
}

module.exports = app;
''')

        # Tests
        tests_dir = self.repo_path / 'tests'
        tests_dir.mkdir(exist_ok=True)

        (tests_dir / 'app.test.js').write_text('''
const request = require('supertest');
const app = require('../src/index');

describe('API Endpoints', () => {
    describe('GET /', () => {
        it('should return API information', async () => {
            const response = await request(app).get('/');

            expect(response.status).toBe(200);
            expect(response.body.message).toBe('Node.js Test API');
            expect(response.body.version).toBe('1.0.0');
            expect(response.body.timestamp).toBeDefined();
        });
    });

    describe('GET /health', () => {
        it('should return health status', async () => {
            const response = await request(app).get('/health');

            expect(response.status).toBe(200);
            expect(response.body.status).toBe('healthy');
            expect(response.body.uptime).toBeDefined();
            expect(response.body.memory).toBeDefined();
        });
    });

    describe('GET /api/users', () => {
        it('should return list of users', async () => {
            const response = await request(app).get('/api/users');

            expect(response.status).toBe(200);
            expect(Array.isArray(response.body)).toBe(true);
            expect(response.body.length).toBeGreaterThan(0);
            expect(response.body[0]).toHaveProperty('id');
            expect(response.body[0]).toHaveProperty('name');
            expect(response.body[0]).toHaveProperty('email');
        });
    });

    describe('POST /api/users', () => {
        it('should create a new user', async () => {
            const userData = {
                name: 'Test User',
                email: 'test@example.com'
            };

            const response = await request(app)
                .post('/api/users')
                .send(userData);

            expect(response.status).toBe(201);
            expect(response.body.name).toBe(userData.name);
            expect(response.body.email).toBe(userData.email);
            expect(response.body.id).toBeDefined();
            expect(response.body.created).toBeDefined();
        });

        it('should return error for missing data', async () => {
            const response = await request(app)
                .post('/api/users')
                .send({});

            expect(response.status).toBe(400);
            expect(response.body.error).toBeDefined();
        });
    });

    describe('404 handling', () => {
        it('should return 404 for non-existent endpoints', async () => {
            const response = await request(app).get('/non-existent');

            expect(response.status).toBe(404);
            expect(response.body.error).toBe('Endpoint not found');
        });
    });
});
''')

        # Documentation
        (self.repo_path / 'README.md').write_text('''
# Node.js Test Project

A comprehensive Node.js/Express test project for demonstrating code analysis capabilities.

## Features

- RESTful API with Express.js
- Comprehensive test suite with Jest
- Security middleware (Helmet, CORS)
- Request logging with Morgan
- Environment configuration with dotenv
- Error handling
- Development tools (ESLint, Nodemon)

## Installation

```bash
npm install
```

## Usage

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm start
```

## Testing

Run tests:
```bash
npm test
```

Run tests with coverage:
```bash
npm run test:coverage
```

Watch mode:
```bash
npm run test:watch
```

## Linting

Check code style:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user

## Environment Variables

Create a `.env` file:

```
PORT=3000
NODE_ENV=development
```

## License

MIT License
''')


class JavaRepositoryFixture(RepositoryFixture):
    """Fixture for Java project repositories."""

    def _create_structure(self):
        """Create Java project structure."""
        # Maven structure
        src_main = self.repo_path / 'src' / 'main' / 'java' / 'com' / 'example' / 'testproject'
        src_test = self.repo_path / 'src' / 'test' / 'java' / 'com' / 'example' / 'testproject'
        src_main.mkdir(parents=True, exist_ok=True)
        src_test.mkdir(parents=True, exist_ok=True)

        # pom.xml
        (self.repo_path / 'pom.xml').write_text('''
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>java-test-project</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>Java Test Project</name>
    <description>A comprehensive Java test project for code analysis</description>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.9.0</junit.version>
        <spring.version>5.3.23</spring.version>
    </properties>

    <dependencies>
        <!-- Core dependencies -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>${spring.version}</version>
        </dependency>

        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-context</artifactId>
            <version>${spring.version}</version>
        </dependency>

        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.14.2</version>
        </dependency>

        <!-- Test dependencies -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>4.8.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.10.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M7</version>
            </plugin>

            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>0.8.8</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>prepare-agent</goal>
                        </goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals>
                            <goal>report</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
''')

        # Main Java classes
        (src_main / 'Application.java').write_text('''
package com.example.testproject;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

@Configuration
@ComponentScan(basePackages = "com.example.testproject")
public class Application {

    public static void main(String[] args) {
        ApplicationContext context = new AnnotationConfigApplicationContext(Application.class);

        UserService userService = context.getBean(UserService.class);
        DataProcessor processor = context.getBean(DataProcessor.class);

        System.out.println("Java Test Application Started");

        // Demonstrate functionality
        User user = userService.createUser("John Doe", "john@example.com");
        System.out.println("Created user: " + user);

        String data = "sample,data,for,processing";
        String processed = processor.processData(data);
        System.out.println("Processed data: " + processed);
    }
}
''')

        # Additional classes
        (src_main / 'User.java').write_text('''
package com.example.testproject;

import java.time.LocalDateTime;
import java.util.Objects;

public class User {
    private Long id;
    private String name;
    private String email;
    private LocalDateTime createdAt;
    private boolean active;

    public User() {
        this.createdAt = LocalDateTime.now();
        this.active = true;
    }

    public User(String name, String email) {
        this();
        this.name = name;
        this.email = email;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(id, user.id) &&
               Objects.equals(email, user.email);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, email);
    }

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\\'' +
                ", email='" + email + '\\'' +
                ", createdAt=" + createdAt +
                ", active=" + active +
                '}';
    }
}
''')

        # Test classes
        (src_test / 'ApplicationTest.java').write_text('''
package com.example.testproject;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

class ApplicationTest {

    @Test
    void testApplicationExists() {
        Application app = new Application();
        assertNotNull(app);
    }

    @Test
    void testMainMethod() {
        // Test that main method exists and can be called
        assertDoesNotThrow(() -> {
            Application.main(new String[]{});
        });
    }
}
''')

        (src_test / 'UserTest.java').write_text('''
package com.example.testproject;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

class UserTest {

    private User user;

    @BeforeEach
    void setUp() {
        user = new User("Test User", "test@example.com");
    }

    @Test
    void testUserCreation() {
        assertNotNull(user);
        assertEquals("Test User", user.getName());
        assertEquals("test@example.com", user.getEmail());
        assertTrue(user.isActive());
        assertNotNull(user.getCreatedAt());
    }

    @Test
    void testUserEquality() {
        User user1 = new User("John", "john@example.com");
        User user2 = new User("John", "john@example.com");

        user1.setId(1L);
        user2.setId(1L);

        assertEquals(user1, user2);
        assertEquals(user1.hashCode(), user2.hashCode());
    }

    @Test
    void testUserToString() {
        user.setId(1L);
        String userString = user.toString();

        assertTrue(userString.contains("Test User"));
        assertTrue(userString.contains("test@example.com"));
        assertTrue(userString.contains("id=1"));
    }

    @Test
    void testUserSetters() {
        user.setName("Updated Name");
        user.setEmail("updated@example.com");
        user.setActive(false);

        assertEquals("Updated Name", user.getName());
        assertEquals("updated@example.com", user.getEmail());
        assertFalse(user.isActive());
    }
}
''')

        # Documentation
        (self.repo_path / 'README.md').write_text('''
# Java Test Project

A comprehensive Java test project for demonstrating code analysis capabilities.

## Features

- Spring Framework integration
- Maven build system
- JUnit 5 testing
- JaCoCo code coverage
- Modern Java 11+ features
- Dependency injection
- Domain models

## Requirements

- Java 11 or higher
- Maven 3.6 or higher

## Building

Compile the project:
```bash
mvn compile
```

Run tests:
```bash
mvn test
```

Generate coverage report:
```bash
mvn jacoco:report
```

Package the application:
```bash
mvn package
```

## Running

Run the application:
```bash
java -cp target/classes com.example.testproject.Application
```

Or using Maven:
```bash
mvn exec:java -Dexec.mainClass="com.example.testproject.Application"
```

## Project Structure

```
src/
├── main/java/com/example/testproject/
│   ├── Application.java      # Main application class
│   ├── User.java            # User domain model
│   ├── UserService.java     # User service
│   └── DataProcessor.java   # Data processing utility
└── test/java/com/example/testproject/
    ├── ApplicationTest.java  # Application tests
    ├── UserTest.java        # User model tests
    ├── UserServiceTest.java # Service tests
    └── DataProcessorTest.java # Utility tests

pom.xml                      # Maven configuration
README.md                   # This file
```

## Dependencies

- Spring Framework 5.3.x
- Jackson for JSON processing
- JUnit 5 for testing
- Mockito for mocking

## License

MIT License
''')


class EmptyRepositoryFixture(RepositoryFixture):
    """Fixture for empty repositories (for negative testing)."""

    def _create_structure(self):
        """Create empty repository structure."""
        # Create only a basic README to make it a valid directory
        (self.repo_path / 'README.md').write_text('# Empty Repository\\n\\nThis is an empty repository for testing.')


class CorruptedRepositoryFixture(RepositoryFixture):
    """Fixture for corrupted repositories (for negative testing)."""

    def _create_structure(self):
        """Create corrupted repository structure."""
        # Create files with binary content and weird names
        (self.repo_path / 'corrupted_file.txt').write_bytes(b'\\x00\\x01\\x02\\x03\\xFF\\xFE')
        (self.repo_path / 'file with spaces.txt').write_text('Content with issues\\x00null bytes')

        # Create directory with permission issues (this might not work on all systems)
        restricted_dir = self.repo_path / 'restricted'
        restricted_dir.mkdir()
        (restricted_dir / 'hidden_file').write_text('hidden content')


# Factory function to create different repository types
def create_repository_fixture(repo_type: str, name: str, base_path: Path) -> RepositoryFixture:
    """
    Create a repository fixture of the specified type.

    Args:
        repo_type: Type of repository ('python', 'node', 'java', 'empty', 'corrupted')
        name: Repository name
        base_path: Base path for repositories

    Returns:
        Repository fixture instance
    """
    fixture_classes = {
        'python': PythonRepositoryFixture,
        'node': NodeRepositoryFixture,
        'java': JavaRepositoryFixture,
        'empty': EmptyRepositoryFixture,
        'corrupted': CorruptedRepositoryFixture
    }

    fixture_class = fixture_classes.get(repo_type)
    if not fixture_class:
        raise ValueError(f"Unknown repository type: {repo_type}")

    return fixture_class(name, base_path)

