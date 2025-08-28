"""
File structure analyzer for repository analysis.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ProjectPattern(Enum):
    """Project architecture patterns."""
    MVC = "mvc"
    MICROSERVICE = "microservice"
    MONOLITH = "monolith"
    LIBRARY = "library"
    SERVERLESS = "serverless"
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    """File information data class."""
    path: str
    name: str
    extension: str
    size: int
    language: str
    is_directory: bool = False
    depth: int = 0


class StructureAnalyzer:
    """Analyzer for file structure and project patterns."""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.cs': 'csharp',
            '.vue': 'vue',
            '.svelte': 'svelte',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.sql': 'sql',
            '.sh': 'shell',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.dockerfile': 'docker',
            'dockerfile': 'docker',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'config',
            '.conf': 'config',
            '.md': 'markdown',
            '.txt': 'text',
            '.log': 'log'
        }
        
        self.config_files = {
            'package.json': 'nodejs',
            'requirements.txt': 'python',
            'pipfile': 'python',
            'pyproject.toml': 'python',
            'setup.py': 'python',
            'pom.xml': 'java',
            'build.gradle': 'java',
            'gradle.properties': 'java',
            'go.mod': 'go',
            'cargo.toml': 'rust',
            'composer.json': 'php',
            'gemfile': 'ruby',
            'mix.exs': 'elixir',
            'rebar.config': 'erlang',
            'dub.json': 'd',
            'pubspec.yaml': 'dart',
            'cargo.lock': 'rust',
            'package-lock.json': 'nodejs',
            'yarn.lock': 'nodejs',
            'pipfile.lock': 'python',
            'composer.lock': 'php',
            'gemfile.lock': 'ruby'
        }
        
        self.framework_patterns = {
            'django': {
                'files': ['manage.py', 'settings.py', 'urls.py', 'wsgi.py'],
                'dirs': ['apps', 'templates', 'static', 'migrations']
            },
            'flask': {
                'files': ['app.py', 'run.py', 'config.py'],
                'dirs': ['templates', 'static', 'routes']
            },
            'react': {
                'files': ['package.json', 'index.js', 'app.js'],
                'dirs': ['src', 'public', 'components']
            },
            'angular': {
                'files': ['angular.json', 'package.json'],
                'dirs': ['src', 'app', 'components', 'services']
            },
            'vue': {
                'files': ['package.json', 'vue.config.js'],
                'dirs': ['src', 'components', 'views', 'assets']
            },
            'spring': {
                'files': ['pom.xml', 'build.gradle', 'application.properties'],
                'dirs': ['src/main/java', 'src/main/resources', 'src/test/java']
            },
            'express': {
                'files': ['package.json', 'app.js', 'server.js'],
                'dirs': ['routes', 'controllers', 'models', 'middleware']
            },
            'rails': {
                'files': ['gemfile', 'config.ru'],
                'dirs': ['app', 'config', 'db', 'public', 'test']
            }
        }
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze method compatible with CodeAnalysisEngine interface."""
        return self.analyze_structure()
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze the complete file structure."""
        if not self.repository_path.exists():
            return {'error': f'Repository path does not exist: {self.repository_path}'}
        
        analysis = {
            'repository_path': str(self.repository_path),
            'directory_tree': self._generate_directory_tree(),
            'file_statistics': self._analyze_file_statistics(),
            'language_distribution': self._analyze_language_distribution(),
            'project_pattern': self._identify_project_pattern(),
            'framework_detection': self._detect_frameworks(),
            'architecture_indicators': self._analyze_architecture_indicators(),
            'configuration_files': self._analyze_configuration_files(),
            'directory_structure': self._analyze_directory_structure(),
            'file_depth_analysis': self._analyze_file_depth(),
            'size_analysis': self._analyze_file_sizes(),
            'metadata': {
                'total_files': 0,
                'total_directories': 0,
                'total_size': 0,
                'max_depth': 0,
                'analysis_timestamp': self._get_timestamp()
            }
        }
        
        # Update metadata
        analysis['metadata']['total_files'] = len(analysis['file_statistics']['files'])
        analysis['metadata']['total_directories'] = len(analysis['file_statistics']['directories'])
        analysis['metadata']['total_size'] = analysis['size_analysis']['total_size']
        analysis['metadata']['max_depth'] = analysis['file_depth_analysis']['max_depth']
        
        return analysis
    
    def _generate_directory_tree(self, max_depth: int = 5) -> Dict[str, Any]:
        """Generate directory tree structure."""
        def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {}
            
            tree = {
                'name': path.name,
                'path': str(path),
                'type': 'directory' if path.is_dir() else 'file',
                'size': path.stat().st_size if path.is_file() else 0,
                'children': []
            }
            
            if path.is_dir():
                try:
                    sorted_children = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                    for child in sorted_children:
                        if not child.name.startswith('.'):
                            tree['children'].append(build_tree(child, current_depth + 1))
                except PermissionError:
                    tree['error'] = 'Permission denied'
            
            return tree
        
        return build_tree(self.repository_path)
    
    def _analyze_file_statistics(self) -> Dict[str, Any]:
        """Analyze basic file statistics."""
        files = []
        directories = []
        
        for root, dirs, filenames in os.walk(self.repository_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    file_path = Path(root) / filename
                    files.append({
                        'name': filename,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'extension': file_path.suffix.lower(),
                        'language': self._get_file_language(file_path)
                    })
            
            for dirname in dirs:
                dir_path = Path(root) / dirname
                directories.append({
                    'name': dirname,
                    'path': str(dir_path)
                })
        
        return {
            'files': files,
            'directories': directories,
            'file_count': len(files),
            'directory_count': len(directories)
        }
    
    def _analyze_language_distribution(self) -> Dict[str, Any]:
        """Analyze programming language distribution."""
        language_stats = {}
        total_lines = 0
        total_files = 0
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    language = self._get_file_language(file_path)
                    
                    if language != 'unknown':
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = len(f.readlines())
                                total_lines += lines
                                total_files += 1
                                
                                if language not in language_stats:
                                    language_stats[language] = {
                                        'files': 0,
                                        'lines': 0,
                                        'percentage': 0
                                    }
                                
                                language_stats[language]['files'] += 1
                                language_stats[language]['lines'] += lines
                        except (UnicodeDecodeError, PermissionError):
                            continue
        
        # Calculate percentages
        for lang in language_stats:
            language_stats[lang]['percentage'] = round(
                (language_stats[lang]['lines'] / total_lines * 100) if total_lines > 0 else 0, 2
            )
        
        return {
            'languages': language_stats,
            'total_lines': total_lines,
            'total_files': total_files,
            'dominant_language': max(language_stats.items(), key=lambda x: x[1]['lines'])[0] if language_stats else 'unknown'
        }
    
    def _identify_project_pattern(self) -> Dict[str, Any]:
        """Identify project architecture pattern."""
        pattern_scores = {pattern: 0 for pattern in ProjectPattern}
        indicators = []
        
        # Check for MVC pattern
        if self._has_mvc_structure():
            pattern_scores[ProjectPattern.MVC] += 3
            indicators.append('mvc_structure_detected')
        
        # Check for microservice pattern
        if self._has_microservice_structure():
            pattern_scores[ProjectPattern.MICROSERVICE] += 3
            indicators.append('microservice_structure_detected')
        
        # Check for library pattern
        if self._has_library_structure():
            pattern_scores[ProjectPattern.LIBRARY] += 3
            indicators.append('library_structure_detected')
        
        # Check for serverless pattern
        if self._has_serverless_structure():
            pattern_scores[ProjectPattern.SERVERLESS] += 3
            indicators.append('serverless_structure_detected')
        
        # Determine dominant pattern
        dominant_pattern = max(pattern_scores.items(), key=lambda x: x[1])[0]
        confidence = pattern_scores[dominant_pattern] / 3.0
        
        return {
            'pattern': dominant_pattern.value,
            'confidence': confidence,
            'scores': {pattern.value: score for pattern, score in pattern_scores.items()},
            'indicators': indicators
        }
    
    def _detect_frameworks(self) -> Dict[str, Any]:
        """Detect used frameworks."""
        detected_frameworks = []
        framework_evidence = {}
        
        for framework, patterns in self.framework_patterns.items():
            evidence = {'files': [], 'dirs': [], 'score': 0}
            
            # Check for framework files
            for file_pattern in patterns['files']:
                if (self.repository_path / file_pattern).exists():
                    evidence['files'].append(file_pattern)
                    evidence['score'] += 1
            
            # Check for framework directories
            for dir_pattern in patterns['dirs']:
                if (self.repository_path / dir_pattern).exists():
                    evidence['dirs'].append(dir_pattern)
                    evidence['score'] += 1
            
            if evidence['score'] > 0:
                detected_frameworks.append(framework)
                framework_evidence[framework] = evidence
        
        return {
            'frameworks': detected_frameworks,
            'evidence': framework_evidence,
            'primary_framework': detected_frameworks[0] if detected_frameworks else None
        }
    
    def _analyze_architecture_indicators(self) -> Dict[str, Any]:
        """Analyze architecture indicators."""
        indicators = {
            'has_tests': False,
            'has_documentation': False,
            'has_ci_cd': False,
            'has_docker': False,
            'has_config_management': False,
            'has_database_layer': False,
            'has_api_layer': False,
            'has_frontend': False,
            'has_backend': False
        }
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Check for tests
            if any('test' in d.lower() or 'spec' in d.lower() for d in dirs):
                indicators['has_tests'] = True
            
            # Check for documentation
            if 'docs' in dirs or 'documentation' in dirs or any(f.endswith('.md') for f in files):
                indicators['has_documentation'] = True
            
            # Check for CI/CD
            if any(f in ['.github', '.gitlab-ci.yml', 'jenkinsfile', 'travis.yml'] for f in files + dirs):
                indicators['has_ci_cd'] = True
            
            # Check for Docker
            if any('docker' in f.lower() for f in files) or 'dockerfile' in [f.lower() for f in files]:
                indicators['has_docker'] = True
            
            # Check for config management
            if any(f in ['config', 'conf', 'settings'] for f in dirs):
                indicators['has_config_management'] = True
            
            # Check for database layer
            if any(d in ['migrations', 'models', 'database', 'db'] for d in dirs):
                indicators['has_database_layer'] = True
            
            # Check for API layer
            if any(d in ['api', 'routes', 'controllers', 'endpoints'] for d in dirs):
                indicators['has_api_layer'] = True
            
            # Check for frontend
            if any(d in ['frontend', 'client', 'ui', 'web'] for d in dirs):
                indicators['has_frontend'] = True
            
            # Check for backend
            if any(d in ['backend', 'server', 'api'] for d in dirs):
                indicators['has_backend'] = True
        
        return indicators
    
    def _analyze_configuration_files(self) -> Dict[str, Any]:
        """Analyze configuration files."""
        config_files = []
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_lower = file.lower()
                if file_lower in self.config_files:
                    file_path = Path(root) / file
                    config_files.append({
                        'name': file,
                        'path': str(file_path),
                        'type': self.config_files[file_lower],
                        'size': file_path.stat().st_size
                    })
        
        return {
            'config_files': config_files,
            'count': len(config_files),
            'types': list(set(cf['type'] for cf in config_files))
        }
    
    def _analyze_directory_structure(self) -> Dict[str, Any]:
        """Analyze directory structure patterns."""
        structure_analysis = {
            'top_level_dirs': [],
            'common_patterns': [],
            'organization_score': 0
        }
        
        # Get top-level directories
        try:
            top_level_dirs = [d.name for d in self.repository_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            structure_analysis['top_level_dirs'] = top_level_dirs
            
            # Check for common patterns
            patterns = {
                'src_based': 'src' in top_level_dirs,
                'mvc_based': any(d in ['models', 'views', 'controllers'] for d in top_level_dirs),
                'feature_based': any(d in ['features', 'modules', 'components'] for d in top_level_dirs),
                'layered': any(d in ['api', 'service', 'data', 'domain'] for d in top_level_dirs)
            }
            
            structure_analysis['common_patterns'] = [pattern for pattern, exists in patterns.items() if exists]
            structure_analysis['organization_score'] = sum(patterns.values()) / len(patterns)
            
        except PermissionError:
            structure_analysis['error'] = 'Permission denied'
        
        return structure_analysis
    
    def _analyze_file_depth(self) -> Dict[str, Any]:
        """Analyze file depth distribution."""
        depth_stats = {}
        max_depth = 0
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            current_depth = root.count(os.sep) - str(self.repository_path).count(os.sep)
            max_depth = max(max_depth, current_depth)
            
            if current_depth not in depth_stats:
                depth_stats[current_depth] = {'files': 0, 'directories': 0}
            
            depth_stats[current_depth]['files'] += len(files)
            depth_stats[current_depth]['directories'] += len(dirs)
        
        return {
            'depth_distribution': depth_stats,
            'max_depth': max_depth,
            'average_depth': sum(depth * stats['files'] for depth, stats in depth_stats.items()) / sum(stats['files'] for stats in depth_stats.values()) if depth_stats else 0
        }
    
    def _analyze_file_sizes(self) -> Dict[str, Any]:
        """Analyze file size distribution."""
        sizes = []
        total_size = 0
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                try:
                    file_path = Path(root) / file
                    size = file_path.stat().st_size
                    sizes.append(size)
                    total_size += size
                except (PermissionError, OSError):
                    continue
        
        # Calculate size distribution
        size_ranges = {
            'small': 0,    # < 1KB
            'medium': 0,   # 1KB - 100KB
            'large': 0,    # 100KB - 1MB
            'huge': 0      # > 1MB
        }
        
        for size in sizes:
            if size < 1024:
                size_ranges['small'] += 1
            elif size < 102400:
                size_ranges['medium'] += 1
            elif size < 1048576:
                size_ranges['large'] += 1
            else:
                size_ranges['huge'] += 1
        
        return {
            'total_size': total_size,
            'file_count': len(sizes),
            'average_size': total_size / len(sizes) if sizes else 0,
            'largest_file': max(sizes) if sizes else 0,
            'size_distribution': size_ranges,
            'size_ranges': size_ranges
        }
    
    def _get_file_language(self, file_path: Path) -> str:
        """Get programming language from file extension."""
        extension = file_path.suffix.lower()
        return self.supported_languages.get(extension, 'unknown')
    
    def _has_mvc_structure(self) -> bool:
        """Check if project has MVC structure."""
        mvc_indicators = ['models', 'views', 'controllers']
        return any((self.repository_path / indicator).exists() for indicator in mvc_indicators)
    
    def _has_microservice_structure(self) -> bool:
        """Check if project has microservice structure."""
        # Look for multiple service directories
        service_dirs = []
        for item in self.repository_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if 'service' in item.name.lower() or item.name in ['user', 'product', 'order']:
                    service_dirs.append(item)
        return len(service_dirs) >= 2
    
    def _has_library_structure(self) -> bool:
        """Check if project has library structure."""
        lib_indicators = ['lib', 'src', 'include', 'dist']
        return any((self.repository_path / indicator).exists() for indicator in lib_indicators)
    
    def _has_serverless_structure(self) -> bool:
        """Check if project has serverless structure."""
        serverless_indicators = ['functions', 'lambdas', 'serverless.yml']
        return any((self.repository_path / indicator).exists() for indicator in serverless_indicators)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()