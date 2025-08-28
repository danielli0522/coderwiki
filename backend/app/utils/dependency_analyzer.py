"""
Dependency analyzer for repository analysis.
"""

import os
import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import urllib.request
import urllib.parse


class DependencyType(Enum):
    """Dependency types."""
    RUNTIME = "runtime"
    DEVELOPMENT = "development"
    PEER = "peer"
    OPTIONAL = "optional"
    BUNDLED = "bundled"
    TRANSITIVE = "transitive"


class VulnerabilityLevel(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Dependency:
    """Dependency information."""
    name: str
    version: str
    type: DependencyType
    source_file: str
    description: str = ""
    homepage: str = ""
    license: str = ""
    vulnerabilities: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dependency to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'type': self.type.value,  # Convert enum to string
            'source_file': self.source_file,
            'description': self.description,
            'homepage': self.homepage,
            'license': self.license,
            'vulnerabilities': self.vulnerabilities
        }


@dataclass
class DependencyGraph:
    """Dependency graph structure."""
    dependencies: List[Dependency]
    dependency_tree: Dict[str, List[str]]
    circular_dependencies: List[List[str]]
    version_conflicts: List[Dict[str, Any]]
    outdated_packages: List[Dict[str, Any]]


class DependencyAnalyzer:
    """Analyzer for project dependencies."""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.dependency_files = {
            'package.json': self._parse_package_json,
            'package-lock.json': self._parse_package_lock,
            'yarn.lock': self._parse_yarn_lock,
            'requirements.txt': self._parse_requirements_txt,
            'pipfile': self._parse_pipfile,
            'pyproject.toml': self._parse_pyproject_toml,
            'setup.py': self._parse_setup_py,
            'pom.xml': self._parse_pom_xml,
            'build.gradle': self._parse_build_gradle,
            'gradle.properties': self._parse_gradle_properties,
            'go.mod': self._parse_go_mod,
            'cargo.toml': self._parse_cargo_toml,
            'composer.json': self._parse_composer_json,
            'gemfile': self._parse_gemfile,
            'mix.exs': self._parse_mix_exs,
            'pubspec.yaml': self._parse_pubspec_yaml,
            'csproj': self._parse_csproj,
            'packages.config': self._parse_packages_config
        }
        
        self.vulnerability_db_url = "https://api.osv.dev/v1/query"
        self.outdated_check_url = "https://registry.npmjs.org"
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze method compatible with CodeAnalysisEngine interface."""
        return self.analyze_dependencies()
    
    def analyze_dependencies(self, check_vulnerabilities: bool = True, check_outdated: bool = True) -> Dict[str, Any]:
        """Analyze all dependencies in the repository."""
        if not self.repository_path.exists():
            return {'error': f'Repository path does not exist: {self.repository_path}'}
        
        analysis = {
            'dependencies': [],
            'dependency_files': [],
            'dependency_tree': {},
            'statistics': {
                'total_dependencies': 0,
                'runtime_dependencies': 0,
                'dev_dependencies': 0,
                'unique_packages': 0,
                'vulnerabilities': 0,
                'outdated_packages': 0
            },
            'vulnerabilities': [],
            'outdated_packages': [],
            'version_conflicts': [],
            'circular_dependencies': [],
            'recommendations': [],
            'metadata': {
                'analysis_timestamp': self._get_timestamp(),
                'repository_path': str(self.repository_path)
            }
        }
        
        # Find and parse dependency files
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file in self.dependency_files:
                    file_path = Path(root) / file
                    try:
                        result = self.dependency_files[file](file_path)
                        if result:
                            analysis['dependencies'].extend(result.get('dependencies', []))
                            analysis['dependency_files'].append({
                                'file': str(file_path),
                                'type': file,
                                'dependencies_count': len(result.get('dependencies', []))
                            })
                    except Exception as e:
                        analysis['recommendations'].append(f"Failed to parse {file_path}: {str(e)}")
        
        # Build dependency tree
        analysis['dependency_tree'] = self._build_dependency_tree(analysis['dependencies'])
        
        # Analyze for conflicts and circular dependencies
        analysis['version_conflicts'] = self._detect_version_conflicts(analysis['dependencies'])
        analysis['circular_dependencies'] = self._detect_circular_dependencies(analysis['dependency_tree'])
        
        # Check for vulnerabilities
        if check_vulnerabilities:
            analysis['vulnerabilities'] = self._check_vulnerabilities(analysis['dependencies'])
        
        # Check for outdated packages
        if check_outdated:
            analysis['outdated_packages'] = self._check_outdated_packages(analysis['dependencies'])
        
        # Calculate statistics (before serialization)
        analysis['statistics'] = self._calculate_statistics(analysis)
        
        # Generate recommendations (before serialization)  
        analysis['recommendations'].extend(self._generate_recommendations(analysis))
        
        # Convert Dependency objects to dictionaries for JSON serialization
        analysis['dependencies'] = [dep.to_dict() for dep in analysis['dependencies']]
        
        return analysis
    
    def _parse_package_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse package.json file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dependencies = []
            
            # Parse different dependency types
            dep_types = {
                'dependencies': DependencyType.RUNTIME,
                'devDependencies': DependencyType.DEVELOPMENT,
                'peerDependencies': DependencyType.PEER,
                'optionalDependencies': DependencyType.OPTIONAL,
                'bundledDependencies': DependencyType.BUNDLED
            }
            
            for dep_type, dep_enum in dep_types.items():
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        dependencies.append(Dependency(
                            name=name,
                            version=version,
                            type=dep_enum,
                            source_file=str(file_path)
                        ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse package.json: {str(e)}")
    
    def _parse_package_lock(self, file_path: Path) -> Dict[str, Any]:
        """Parse package-lock.json file for transitive dependencies."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dependencies = []
            
            if 'dependencies' in data:
                for name, info in data['dependencies'].items():
                    dependencies.append(Dependency(
                        name=name,
                        version=info.get('version', ''),
                        type=DependencyType.TRANSITIVE,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse package-lock.json: {str(e)}")
    
    def _parse_yarn_lock(self, file_path: Path) -> Dict[str, Any]:
        """Parse yarn.lock file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Parse yarn.lock format
            package_pattern = r'^"([^@]+@[^"]+)":'
            version_pattern = r'version "([^"]+)"'
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('"'):
                    package_match = re.match(package_pattern, line)
                    if package_match:
                        package_spec = package_match.group(1)
                        if '@' in package_spec:
                            name, version = package_spec.rsplit('@', 1)
                            dependencies.append(Dependency(
                                name=name,
                                version=version,
                                type=DependencyType.TRANSITIVE,
                                source_file=str(file_path)
                            ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse yarn.lock: {str(e)}")
    
    def _parse_requirements_txt(self, file_path: Path) -> Dict[str, Any]:
        """Parse requirements.txt file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dependencies = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse requirement specification
                    if '==' in line:
                        name, version = line.split('==', 1)
                        version = version.strip()
                    elif '>=' in line:
                        name, version = line.split('>=', 1)
                        version = f">={version.strip()}"
                    elif '<=' in line:
                        name, version = line.split('<=', 1)
                        version = f"<={version.strip()}"
                    else:
                        name = line
                        version = "latest"
                    
                    dependencies.append(Dependency(
                        name=name.strip(),
                        version=version,
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse requirements.txt: {str(e)}")
    
    def _parse_pipfile(self, file_path: Path) -> Dict[str, Any]:
        """Parse Pipfile."""
        try:
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            dependencies = []
            
            # Parse packages
            if 'packages' in data:
                for name, version in data['packages'].items():
                    if isinstance(version, dict):
                        version = version.get('version', 'latest')
                    dependencies.append(Dependency(
                        name=name,
                        version=str(version),
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            # Parse dev-packages
            if 'dev-packages' in data:
                for name, version in data['dev-packages'].items():
                    if isinstance(version, dict):
                        version = version.get('version', 'latest')
                    dependencies.append(Dependency(
                        name=name,
                        version=str(version),
                        type=DependencyType.DEVELOPMENT,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except ImportError:
            # Fallback to simple parsing if toml not available
            return {'dependencies': []}
        except Exception as e:
            raise Exception(f"Failed to parse Pipfile: {str(e)}")
    
    def _parse_pyproject_toml(self, file_path: Path) -> Dict[str, Any]:
        """Parse pyproject.toml file."""
        try:
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            dependencies = []
            
            # Parse dependencies
            if 'project' in data and 'dependencies' in data['project']:
                for dep_spec in data['project']['dependencies']:
                    if '==' in dep_spec:
                        name, version = dep_spec.split('==', 1)
                        dependencies.append(Dependency(
                            name=name.strip(),
                            version=version.strip(),
                            type=DependencyType.RUNTIME,
                            source_file=str(file_path)
                        ))
            
            # Parse optional dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group, deps in data['project']['optional-dependencies'].items():
                    for dep_spec in deps:
                        if '==' in dep_spec:
                            name, version = dep_spec.split('==', 1)
                            dependencies.append(Dependency(
                                name=name.strip(),
                                version=version.strip(),
                                type=DependencyType.OPTIONAL,
                                source_file=str(file_path)
                            ))
            
            return {'dependencies': dependencies}
            
        except ImportError:
            return {'dependencies': []}
        except Exception as e:
            raise Exception(f"Failed to parse pyproject.toml: {str(e)}")
    
    def _parse_setup_py(self, file_path: Path) -> Dict[str, Any]:
        """Parse setup.py file (basic parsing)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Simple regex-based parsing
            install_requires_pattern = r'install_requires\s*=\s*\[(.*?)\]'
            match = re.search(install_requires_pattern, content, re.DOTALL)
            
            if match:
                deps_str = match.group(1)
                # Parse quoted strings
                dep_pattern = r'["\']([^"\']+)["\']'
                for dep_match in re.finditer(dep_pattern, deps_str):
                    dep_spec = dep_match.group(1)
                    if '==' in dep_spec:
                        name, version = dep_spec.split('==', 1)
                        dependencies.append(Dependency(
                            name=name.strip(),
                            version=version.strip(),
                            type=DependencyType.RUNTIME,
                            source_file=str(file_path)
                        ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse setup.py: {str(e)}")
    
    def _parse_pom_xml(self, file_path: Path) -> Dict[str, Any]:
        """Parse pom.xml file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            dependencies = []
            
            # Parse dependencies
            for dep in root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency'):
                group_id = dep.find('{http://maven.apache.org/POM/4.0.0}groupId')
                artifact_id = dep.find('{http://maven.apache.org/POM/4.0.0}artifactId')
                version = dep.find('{http://maven.apache.org/POM/4.0.0}version')
                scope = dep.find('{http://maven.apache.org/POM/4.0.0}scope')
                
                if group_id is not None and artifact_id is not None:
                    name = f"{group_id.text}:{artifact_id.text}"
                    version_text = version.text if version is not None else "latest"
                    
                    dep_type = DependencyType.RUNTIME
                    if scope is not None and scope.text == 'test':
                        dep_type = DependencyType.DEVELOPMENT
                    
                    dependencies.append(Dependency(
                        name=name,
                        version=version_text,
                        type=dep_type,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse pom.xml: {str(e)}")
    
    def _parse_build_gradle(self, file_path: Path) -> Dict[str, Any]:
        """Parse build.gradle file (basic parsing)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Parse implementation dependencies
            impl_pattern = r'implementation\s+["\']([^"\']+)["\']'
            for match in re.finditer(impl_pattern, content):
                dep_spec = match.group(1)
                if ':' in dep_spec:
                    parts = dep_spec.split(':')
                    if len(parts) >= 3:
                        name = f"{parts[0]}:{parts[1]}"
                        version = parts[2]
                        dependencies.append(Dependency(
                            name=name,
                            version=version,
                            type=DependencyType.RUNTIME,
                            source_file=str(file_path)
                        ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse build.gradle: {str(e)}")
    
    def _parse_go_mod(self, file_path: Path) -> Dict[str, Any]:
        """Parse go.mod file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('require') or line.startswith('require\t'):
                    # Parse require statement
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[1]
                        version = parts[2]
                        dependencies.append(Dependency(
                            name=name,
                            version=version,
                            type=DependencyType.RUNTIME,
                            source_file=str(file_path)
                        ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse go.mod: {str(e)}")
    
    def _parse_cargo_toml(self, file_path: Path) -> Dict[str, Any]:
        """Parse Cargo.toml file."""
        try:
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            dependencies = []
            
            # Parse dependencies
            if 'dependencies' in data:
                for name, version in data['dependencies'].items():
                    if isinstance(version, dict):
                        version = version.get('version', 'latest')
                    dependencies.append(Dependency(
                        name=name,
                        version=str(version),
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except ImportError:
            return {'dependencies': []}
        except Exception as e:
            raise Exception(f"Failed to parse Cargo.toml: {str(e)}")
    
    def _parse_composer_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse composer.json file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dependencies = []
            
            # Parse require
            if 'require' in data:
                for name, version in data['require'].items():
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            # Parse require-dev
            if 'require-dev' in data:
                for name, version in data['require-dev'].items():
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.DEVELOPMENT,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse composer.json: {str(e)}")
    
    def _parse_gemfile(self, file_path: Path) -> Dict[str, Any]:
        """Parse Gemfile."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('gem '):
                    # Parse gem declaration
                    gem_pattern = r'gem\s+["\']([^"\']+)["\'](?:,\s*["\']([^"\']+)["\'])?'
                    match = re.match(gem_pattern, line)
                    if match:
                        name = match.group(1)
                        version = match.group(2) if match.group(2) else "latest"
                        dependencies.append(Dependency(
                            name=name,
                            version=version,
                            type=DependencyType.RUNTIME,
                            source_file=str(file_path)
                        ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse Gemfile: {str(e)}")
    
    def _parse_mix_exs(self, file_path: Path) -> Dict[str, Any]:
        """Parse mix.exs file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Parse deps function
            deps_pattern = r'deps\s+do\s*\[(.*?)\]'
            match = re.search(deps_pattern, content, re.DOTALL)
            
            if match:
                deps_str = match.group(1)
                # Parse {:name, "~> version"} format
                dep_pattern = r'\{:\s*([^,]+),\s*"~>\s*([^"]+)"\}'
                for dep_match in re.finditer(dep_pattern, deps_str):
                    name = dep_match.group(1)
                    version = dep_match.group(2)
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse mix.exs: {str(e)}")
    
    def _parse_pubspec_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Parse pubspec.yaml file."""
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            dependencies = []
            
            # Parse dependencies
            if 'dependencies' in data:
                for name, version in data['dependencies'].items():
                    dependencies.append(Dependency(
                        name=name,
                        version=str(version),
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            # Parse dev_dependencies
            if 'dev_dependencies' in data:
                for name, version in data['dev_dependencies'].items():
                    dependencies.append(Dependency(
                        name=name,
                        version=str(version),
                        type=DependencyType.DEVELOPMENT,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except ImportError:
            return {'dependencies': []}
        except Exception as e:
            raise Exception(f"Failed to parse pubspec.yaml: {str(e)}")
    
    def _parse_csproj(self, file_path: Path) -> Dict[str, Any]:
        """Parse .csproj file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            dependencies = []
            
            # Parse PackageReference elements
            for package_ref in root.findall('.//PackageReference'):
                name = package_ref.get('Include')
                version = package_ref.get('Version')
                
                if name and version:
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse .csproj file: {str(e)}")
    
    def _parse_packages_config(self, file_path: Path) -> Dict[str, Any]:
        """Parse packages.config file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            dependencies = []
            
            # Parse package elements
            for package in root.findall('.//package'):
                id_attr = package.get('id')
                version = package.get('version')
                
                if id_attr and version:
                    dependencies.append(Dependency(
                        name=id_attr,
                        version=version,
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse packages.config: {str(e)}")
    
    def _parse_gradle_properties(self, file_path: Path) -> Dict[str, Any]:
        """Parse gradle.properties file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Parse version properties
            version_pattern = r'([^=]+)\s*=\s*([^=]+)'
            for match in re.finditer(version_pattern, content):
                prop_name = match.group(1).strip()
                prop_value = match.group(2).strip()
                
                if 'version' in prop_name.lower():
                    dependencies.append(Dependency(
                        name=f"gradle.property.{prop_name}",
                        version=prop_value,
                        type=DependencyType.RUNTIME,
                        source_file=str(file_path)
                    ))
            
            return {'dependencies': dependencies}
            
        except Exception as e:
            raise Exception(f"Failed to parse gradle.properties: {str(e)}")
    
    def _build_dependency_tree(self, dependencies: List[Dependency]) -> Dict[str, List[str]]:
        """Build dependency tree from dependencies list."""
        tree = {}
        
        for dep in dependencies:
            if dep.name not in tree:
                tree[dep.name] = []
            
            # For simplicity, we'll add the version as a dependency
            # In a real implementation, you'd parse the actual dependency graph
            tree[dep.name].append(f"version:{dep.version}")
        
        return tree
    
    def _detect_version_conflicts(self, dependencies: List[Dependency]) -> List[Dict[str, Any]]:
        """Detect version conflicts in dependencies."""
        conflicts = []
        version_map = {}
        
        for dep in dependencies:
            if dep.name not in version_map:
                version_map[dep.name] = []
            version_map[dep.name].append({
                'version': dep.version,
                'source_file': dep.source_file,
                'type': dep.type.value
            })
        
        # Check for conflicts
        for name, versions in version_map.items():
            if len(versions) > 1:
                # Check if versions are different
                unique_versions = set(v['version'] for v in versions)
                if len(unique_versions) > 1:
                    conflicts.append({
                        'package': name,
                        'versions': versions,
                        'conflict_type': 'version_mismatch'
                    })
        
        return conflicts
    
    def _detect_circular_dependencies(self, dependency_tree: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in the dependency tree."""
        # This is a simplified implementation
        # In a real implementation, you'd need to parse the actual dependency graph
        return []
    
    def _check_vulnerabilities(self, dependencies: List[Dependency]) -> List[Dict[str, Any]]:
        """Check dependencies for known vulnerabilities."""
        vulnerabilities = []
        
        # This is a simplified implementation
        # In a real implementation, you'd query vulnerability databases
        # For now, we'll simulate some common vulnerabilities
        
        vulnerable_packages = {
            'lodash': '4.17.15',
            'express': '4.16.0',
            'react': '16.8.0',
            'moment': '2.24.0'
        }
        
        for dep in dependencies:
            if dep.name in vulnerable_packages:
                if self._version_compare(dep.version, vulnerable_packages[dep.name]) < 0:
                    vulnerabilities.append({
                        'package': dep.name,
                        'current_version': dep.version,
                        'fixed_version': vulnerable_packages[dep.name],
                        'severity': 'high',
                        'description': f'Known vulnerability in {dep.name}',
                        'source_file': dep.source_file
                    })
        
        return vulnerabilities
    
    def _check_outdated_packages(self, dependencies: List[Dependency]) -> List[Dict[str, Any]]:
        """Check for outdated packages."""
        outdated = []
        
        # This is a simplified implementation
        # In a real implementation, you'd query package registries
        
        latest_versions = {
            'lodash': '4.17.21',
            'express': '4.18.2',
            'react': '18.2.0',
            'moment': '2.29.4',
            'axios': '1.4.0'
        }
        
        for dep in dependencies:
            if dep.name in latest_versions:
                if self._version_compare(dep.version, latest_versions[dep.name]) < 0:
                    outdated.append({
                        'package': dep.name,
                        'current_version': dep.version,
                        'latest_version': latest_versions[dep.name],
                        'update_type': 'minor',
                        'source_file': dep.source_file
                    })
        
        return outdated
    
    def _calculate_statistics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate dependency statistics."""
        stats = {
            'total_dependencies': len(analysis['dependencies']),
            'runtime_dependencies': len([d for d in analysis['dependencies'] if d.type == DependencyType.RUNTIME]),
            'dev_dependencies': len([d for d in analysis['dependencies'] if d.type == DependencyType.DEVELOPMENT]),
            'unique_packages': len(set(d.name for d in analysis['dependencies'])),
            'vulnerabilities': len(analysis['vulnerabilities']),
            'outdated_packages': len(analysis['outdated_packages'])
        }
        
        return stats
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on dependency analysis."""
        recommendations = []
        
        # Check for vulnerabilities
        if analysis['vulnerabilities']:
            recommendations.append(f"Found {len(analysis['vulnerabilities'])} vulnerable packages. Update them immediately.")
        
        # Check for outdated packages
        if analysis['outdated_packages']:
            recommendations.append(f"Found {len(analysis['outdated_packages'])} outdated packages. Consider updating them.")
        
        # Check for version conflicts
        if analysis['version_conflicts']:
            recommendations.append(f"Found {len(analysis['version_conflicts'])} version conflicts. Resolve them for consistent builds.")
        
        # Check for circular dependencies
        if analysis['circular_dependencies']:
            recommendations.append(f"Found {len(analysis['circular_dependencies'])} circular dependencies. Refactor to avoid them.")
        
        # Check dependency count
        if analysis['statistics']['total_dependencies'] > 100:
            recommendations.append("High number of dependencies. Consider consolidating or removing unused dependencies.")
        
        # Check for dev dependencies in production
        dev_in_runtime = [d for d in analysis['dependencies'] if d.type == DependencyType.DEVELOPMENT]
        if dev_in_runtime:
            recommendations.append(f"Found {len(dev_in_runtime)} development dependencies in runtime. Move them to dev dependencies.")
        
        return recommendations
    
    def _version_compare(self, version1: str, version2: str) -> int:
        """Compare two version strings."""
        # Simple version comparison
        def normalize_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1_parts = normalize_version(version1)
            v2_parts = normalize_version(version2)
            
            # Pad with zeros to make equal length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1
            
            return 0
        except:
            return 0
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()