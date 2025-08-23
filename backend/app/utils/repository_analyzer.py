"""
Repository information extraction utilities.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Service for analyzing repository structure and extracting information."""
    
    def __init__(self, local_path: str):
        """Initialize repository analyzer with local path."""
        self.local_path = Path(local_path)
    
    def analyze_repository(self) -> Dict[str, Any]:
        """
        Analyze repository structure and extract comprehensive information.
        
        Returns:
            Dictionary with repository analysis results
        """
        try:
            analysis = {
                'structure': self._analyze_structure(),
                'languages': self._detect_languages(),
                'dependencies': self._analyze_dependencies(),
                'configuration': self._analyze_configuration(),
                'documentation': self._analyze_documentation(),
                'metadata': self._extract_metadata()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            return {
                'error': str(e),
                'structure': {},
                'languages': [],
                'dependencies': {},
                'configuration': {},
                'documentation': {},
                'metadata': {}
            }
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze repository file structure."""
        try:
            structure = {
                'total_files': 0,
                'total_directories': 0,
                'file_types': {},
                'directory_tree': self._build_directory_tree(),
                'large_files': [],
                'deep_directories': []
            }
            
            # Walk through all files and directories
            for root, dirs, files in os.walk(self.local_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                structure['total_files'] += len(files)
                structure['total_directories'] += len(dirs)
                
                # Analyze file types
                for file in files:
                    file_ext = Path(file).suffix.lower()
                    if file_ext:
                        structure['file_types'][file_ext] = structure['file_types'].get(file_ext, 0) + 1
                    
                    # Check for large files (> 1MB)
                    file_path = Path(root) / file
                    try:
                        if file_path.stat().st_size > 1024 * 1024:  # 1MB
                            structure['large_files'].append({
                                'path': str(file_path.relative_to(self.local_path)),
                                'size': file_path.stat().st_size
                            })
                    except OSError:
                        continue
                
                # Check for deep directories (> 5 levels)
                depth = root.count(os.sep) - self.local_path.parts[-1].count(os.sep)
                if depth > 5:
                    structure['deep_directories'].append({
                        'path': str(Path(root).relative_to(self.local_path)),
                        'depth': depth
                    })
            
            # Sort large files and deep directories
            structure['large_files'] = sorted(structure['large_files'], 
                                            key=lambda x: x['size'], reverse=True)[:10]
            structure['deep_directories'] = sorted(structure['deep_directories'], 
                                                key=lambda x: x['depth'], reverse=True)[:5]
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
            return {}
    
    def _build_directory_tree(self) -> Dict[str, Any]:
        """Build directory tree structure."""
        def build_tree(path: Path) -> Dict[str, Any]:
            tree = {
                'name': path.name,
                'type': 'directory',
                'children': []
            }
            
            try:
                for item in sorted(path.iterdir()):
                    if item.name == '.git':
                        continue
                    
                    if item.is_dir():
                        tree['children'].append(build_tree(item))
                    else:
                        tree['children'].append({
                            'name': item.name,
                            'type': 'file',
                            'size': item.stat().st_size
                        })
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(self.local_path)
    
    def _detect_languages(self) -> List[Dict[str, Any]]:
        """Detect programming languages used in the repository."""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.cs': 'C#',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.vue': 'Vue',
            '.jsx': 'JSX',
            '.tsx': 'TSX',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.dockerfile': 'Docker',
            '.dockerignore': 'Docker'
        }
        
        language_stats = {}
        
        try:
            for root, dirs, files in os.walk(self.local_path):
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_ext = Path(file).suffix.lower()
                    if file_ext in language_extensions:
                        lang = language_extensions[file_ext]
                        language_stats[lang] = language_stats.get(lang, 0) + 1
                        
                        # Count lines of code for major languages
                        if lang in ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C', 'Go', 'Rust']:
                            try:
                                file_path = Path(root) / file
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    lines = len([line for line in f if line.strip()])
                                    key = f"{lang}_lines"
                                    language_stats[key] = language_stats.get(key, 0) + lines
                            except Exception:
                                continue
            
            # Convert to sorted list
            languages = []
            for lang, count in language_stats.items():
                if not lang.endswith('_lines'):
                    languages.append({
                        'name': lang,
                        'file_count': count,
                        'lines_of_code': language_stats.get(f"{lang}_lines", 0)
                    })
            
            # Sort by file count
            languages.sort(key=lambda x: x['file_count'], reverse=True)
            
            return languages
            
        except Exception as e:
            logger.error(f"Error detecting languages: {str(e)}")
            return []
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            'package_managers': [],
            'dependencies': {},
            'dev_dependencies': {}
        }
        
        try:
            # Python dependencies
            requirements_files = list(self.local_path.glob('**/requirements*.txt'))
            setup_py_files = list(self.local_path.glob('**/setup.py'))
            pyproject_files = list(self.local_path.glob('**/pyproject.toml'))
            
            if requirements_files or setup_py_files or pyproject_files:
                dependencies['package_managers'].append('pip')
                
                for req_file in requirements_files:
                    deps = self._parse_requirements_file(req_file)
                    dependencies['dependencies'].update(deps)
            
            # Node.js dependencies
            package_json_files = list(self.local_path.glob('**/package.json'))
            
            for pkg_file in package_json_files:
                dependencies['package_managers'].append('npm')
                deps = self._parse_package_json(pkg_file)
                dependencies['dependencies'].update(deps['dependencies'])
                dependencies['dev_dependencies'].update(deps['dev_dependencies'])
            
            # Java dependencies
            pom_files = list(self.local_path.glob('**/pom.xml'))
            gradle_files = list(self.local_path.glob('**/build.gradle'))
            
            if pom_files or gradle_files:
                dependencies['package_managers'].append('maven' if pom_files else 'gradle')
            
            # Go dependencies
            go_mod_files = list(self.local_path.glob('**/go.mod'))
            
            if go_mod_files:
                dependencies['package_managers'].append('go')
                deps = self._parse_go_mod(go_mod_files[0])
                dependencies['dependencies'].update(deps)
            
            # Rust dependencies
            cargo_files = list(self.local_path.glob('**/Cargo.toml'))
            
            if cargo_files:
                dependencies['package_managers'].append('cargo')
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
            return {}
    
    def _parse_requirements_file(self, file_path: Path) -> Dict[str, str]:
        """Parse Python requirements.txt file."""
        dependencies = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name and version
                        match = re.match(r'^([a-zA-Z0-9\-_.]+)[>=<==]*(.*)$', line)
                        if match:
                            package, version = match.groups()
                            dependencies[package] = version or 'latest'
        except Exception:
            pass
        
        return dependencies
    
    def _parse_package_json(self, file_path: Path) -> Dict[str, Dict[str, str]]:
        """Parse Node.js package.json file."""
        dependencies = {'dependencies': {}, 'dev_dependencies': {}}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if 'dependencies' in data:
                    dependencies['dependencies'].update(data['dependencies'])
                
                if 'devDependencies' in data:
                    dependencies['dev_dependencies'].update(data['devDependencies'])
        except Exception:
            pass
        
        return dependencies
    
    def _parse_go_mod(self, file_path: Path) -> Dict[str, str]:
        """Parse Go go.mod file."""
        dependencies = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('require ') and not line.startswith('//'):
                        parts = line.split()
                        if len(parts) >= 2:
                            dependencies[parts[1]] = parts[2] if len(parts) > 2 else 'latest'
        except Exception:
            pass
        
        return dependencies
    
    def _analyze_configuration(self) -> Dict[str, Any]:
        """Analyze configuration files."""
        configuration = {
            'frameworks': [],
            'databases': [],
            'testing': [],
            'deployment': [],
            'other': []
        }
        
        # Detect frameworks
        framework_files = {
            'django': ['settings.py', 'wsgi.py'],
            'flask': ['app.py', 'main.py'],
            'express': ['app.js', 'server.js'],
            'react': ['package.json'],
            'vue': ['vue.config.js'],
            'spring': ['application.properties'],
            'rails': ['config/application.rb']
        }
        
        for framework, files in framework_files.items():
            for file in files:
                if list(self.local_path.glob(f'**/{file}')):
                    configuration['frameworks'].append(framework)
                    break
        
        # Detect databases
        db_files = {
            'postgresql': ['postgresql.conf', 'pg_hba.conf'],
            'mysql': ['my.cnf', 'my.ini'],
            'sqlite': ['*.db', '*.sqlite'],
            'mongodb': ['mongod.conf'],
            'redis': ['redis.conf']
        }
        
        for db, patterns in db_files.items():
            for pattern in patterns:
                if list(self.local_path.glob(f'**/{pattern}')):
                    configuration['databases'].append(db)
                    break
        
        # Detect testing frameworks
        test_files = {
            'pytest': ['conftest.py', 'test_*.py'],
            'jest': ['jest.config.js', '*.test.js'],
            'mocha': ['test/*.js'],
            'junit': ['*Test.java'],
            'rspec': ['spec/*_spec.rb']
        }
        
        for test, patterns in test_files.items():
            for pattern in patterns:
                if list(self.local_path.glob(f'**/{pattern}')):
                    configuration['testing'].append(test)
                    break
        
        # Detect deployment
        deploy_files = {
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'kubernetes': ['*.yaml', '*.yml'],
            'github_actions': ['.github/workflows/*.yml'],
            'heroku': ['Procfile', 'runtime.txt']
        }
        
        for deploy, patterns in deploy_files.items():
            for pattern in patterns:
                if list(self.local_path.glob(f'**/{pattern}')):
                    configuration['deployment'].append(deploy)
                    break
        
        return configuration
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation files."""
        documentation = {
            'readme': None,
            'api_docs': [],
            'guides': [],
            'examples': [],
            'total_doc_files': 0
        }
        
        try:
            # Look for README files
            readme_files = list(self.local_path.glob('**/README*'))
            if readme_files:
                readme_file = readme_files[0]
                documentation['readme'] = {
                    'path': str(readme_file.relative_to(self.local_path)),
                    'size': readme_file.stat().st_size,
                    'has_badges': self._check_readme_badges(readme_file)
                }
            
            # Look for API documentation
            api_patterns = ['**/api/**', '**/docs/api/**', '**/*api*.md']
            for pattern in api_patterns:
                api_files = list(self.local_path.glob(pattern))
                for file in api_files:
                    if file.is_file():
                        documentation['api_docs'].append(str(file.relative_to(self.local_path)))
            
            # Look for guides
            guide_patterns = ['**/docs/**', '**/guides/**', '**/*guide*.md']
            for pattern in guide_patterns:
                guide_files = list(self.local_path.glob(pattern))
                for file in guide_files:
                    if file.is_file():
                        documentation['guides'].append(str(file.relative_to(self.local_path)))
            
            # Look for examples
            example_patterns = ['**/examples/**', '**/sample*/**', '**/*example*']
            for pattern in example_patterns:
                example_files = list(self.local_path.glob(pattern))
                for file in example_files:
                    if file.is_file():
                        documentation['examples'].append(str(file.relative_to(self.local_path)))
            
            # Count total documentation files
            doc_extensions = ['.md', '.rst', '.txt', '.html', '.pdf']
            for ext in doc_extensions:
                doc_files = list(self.local_path.glob(f'**/*{ext}'))
                documentation['total_doc_files'] += len(doc_files)
            
            return documentation
            
        except Exception as e:
            logger.error(f"Error analyzing documentation: {str(e)}")
            return {}
    
    def _check_readme_badges(self, readme_file: Path) -> bool:
        """Check if README contains badges."""
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for common badge patterns
                badge_patterns = [
                    r'!\[.*\]\(.*\)',  # Markdown image
                    r'<img.*src=.*>',  # HTML image
                    r'\[!\[.*\]\(.*\)\]\(.*\)',  # Badge with link
                ]
                
                for pattern in badge_patterns:
                    if re.search(pattern, content):
                        return True
            return False
        except Exception:
            return False
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract additional metadata."""
        metadata = {
            'estimated_complexity': 'low',
            'maintenance_score': 0,
            'recommended_documentation': []
        }
        
        try:
            # Calculate complexity based on file count and structure
            total_files = sum(len(files) for _, _, files in os.walk(self.local_path))
            if total_files > 1000:
                metadata['estimated_complexity'] = 'high'
            elif total_files > 100:
                metadata['estimated_complexity'] = 'medium'
            
            # Calculate maintenance score (simple heuristic)
            doc_files = len(list(self.local_path.rglob('*.md'))) + len(list(self.local_path.rglob('*.rst')))
            test_files = len(list(self.local_path.rglob('*test*'))) + len(list(self.local_path.rglob('*spec*')))
            
            if total_files > 0:
                metadata['maintenance_score'] = min(100, (doc_files + test_files) * 10 / total_files * 100)
            
            # Recommend documentation based on analysis
            if not list(self.local_path.glob('**/README*')):
                metadata['recommended_documentation'].append('README.md')
            
            if not list(self.local_path.glob('**/docs/**')):
                metadata['recommended_documentation'].append('docs/ directory')
            
            if not list(self.local_path.glob('**/*test*')):
                metadata['recommended_documentation'].append('test files')
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return metadata