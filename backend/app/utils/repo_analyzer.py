"""
Repository analyzer utility for extracting repository metadata and statistics.
"""

import os
import re
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import requests


class RepositoryAnalyzer:
    """Utility class for analyzing Git repositories and extracting metadata."""
    
    def __init__(self):
        """Initialize the repository analyzer."""
        self.github_api_base = "https://api.github.com"
    
    def analyze_repository(self, repo_url: str, local_path: str) -> Dict[str, Any]:
        """Analyze a repository and extract comprehensive metadata.
        
        Args:
            repo_url: Repository URL
            local_path: Local path to the cloned repository
            
        Returns:
            Dictionary containing repository analysis results
        """
        analysis_result = {
            'basic_info': {},
            'github_stats': {},
            'code_stats': {},
            'language_stats': {},
            'contributors': [],
            'recent_commits': [],
            'branches': [],
            'tags': []
        }
        
        # Extract basic repository information
        analysis_result['basic_info'] = self._extract_basic_info(repo_url, local_path)
        
        # Get GitHub statistics if it's a GitHub repository
        if 'github.com' in repo_url:
            analysis_result['github_stats'] = self._get_github_stats(repo_url)
        
        # Analyze local repository code
        if local_path and os.path.exists(local_path):
            analysis_result['code_stats'] = self._analyze_code_stats(local_path)
            analysis_result['language_stats'] = self._analyze_languages(local_path)
            analysis_result['recent_commits'] = self._get_recent_commits(local_path)
            analysis_result['branches'] = self._get_branches(local_path)
            analysis_result['tags'] = self._get_tags(local_path)
        
        return analysis_result
    
    def _extract_basic_info(self, repo_url: str, local_path: str) -> Dict[str, Any]:
        """Extract basic repository information."""
        info = {
            'name': self._extract_repo_name(repo_url),
            'url': repo_url,
            'is_github': 'github.com' in repo_url,
            'owner': self._extract_owner(repo_url),
            'clone_url': self._get_clone_url(repo_url),
            'local_path': local_path
        }
        
        # Extract repository from URL
        if info['is_github']:
            repo_parts = repo_url.split('/')
            if len(repo_parts) >= 2:
                info['owner'] = repo_parts[-2]
                info['name'] = repo_parts[-1].replace('.git', '')
        
        return info
    
    def _get_github_stats(self, repo_url: str) -> Dict[str, Any]:
        """Get repository statistics from GitHub API."""
        if 'github.com' not in repo_url:
            return {}
        
        try:
            # Extract owner and repo name from URL
            repo_path = self._extract_github_repo_path(repo_url)
            if not repo_path:
                return {}
            
            api_url = f"{self.github_api_base}/repos/{repo_path}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'default_branch': data.get('default_branch', 'main'),
                    'description': data.get('description', ''),
                    'homepage': data.get('homepage', ''),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'pushed_at': data.get('pushed_at'),
                    'size': data.get('size', 0),  # Size in KB
                    'language': data.get('language', ''),
                    'license': data.get('license', {}).get('name', '') if data.get('license') else '',
                    'is_private': data.get('private', False),
                    'has_issues': data.get('has_issues', False),
                    'has_projects': data.get('has_projects', False),
                    'has_wiki': data.get('has_wiki', False),
                    'archived': data.get('archived', False)
                }
        except Exception as e:
            print(f"Error fetching GitHub stats: {e}")
        
        return {}
    
    def _analyze_code_stats(self, local_path: str) -> Dict[str, Any]:
        """Analyze code statistics from local repository."""
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'file_extensions': {},
            'directory_structure': {}
        }
        
        if not os.path.exists(local_path):
            return stats
        
        try:
            for root, dirs, files in os.walk(local_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    stats['total_files'] += 1
                    
                    # Get file extension
                    _, ext = os.path.splitext(file)
                    ext = ext.lower() if ext else 'no_extension'
                    stats['file_extensions'][ext] = stats['file_extensions'].get(ext, 0) + 1
                    
                    # Count lines in file
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            stats['total_lines'] += lines
                    except Exception:
                        pass
                    
                    # Directory structure
                    rel_path = os.path.relpath(root, local_path)
                    if rel_path != '.':
                        stats['directory_structure'][rel_path] = \
                            stats['directory_structure'].get(rel_path, 0) + 1
        
        except Exception as e:
            print(f"Error analyzing code stats: {e}")
        
        return stats
    
    def _analyze_languages(self, local_path: str) -> Dict[str, float]:
        """Analyze programming languages used in the repository."""
        language_stats = {}
        
        if not os.path.exists(local_path):
            return language_stats
        
        # Language detection based on file extensions
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.hs': 'Haskell',
            '.elm': 'Elm',
            '.dart': 'Dart',
            '.lua': 'Lua',
            '.r': 'R',
            '.m': 'Objective-C',
            '.sh': 'Shell',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.vue': 'Vue',
            '.jsx': 'React/JSX',
            '.tsx': 'React/TSX',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.dockerfile': 'Docker',
            '.dockerignore': 'Docker',
            '.gitignore': 'Git',
            '.editorconfig': 'EditorConfig',
            '.env': 'Environment',
            '.ini': 'INI',
            '.toml': 'TOML',
            '.cfg': 'Config',
            '.conf': 'Config'
        }
        
        try:
            for root, dirs, files in os.walk(local_path):
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    
                    if ext in language_map:
                        language = language_map[ext]
                        language_stats[language] = language_stats.get(language, 0) + 1
        
        except Exception as e:
            print(f"Error analyzing languages: {e}")
        
        return language_stats
    
    def _get_recent_commits(self, local_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits from the repository."""
        commits = []
        
        if not os.path.exists(local_path):
            return commits
        
        try:
            # Use git log to get recent commits
            result = subprocess.run(
                ['git', 'log', f'--pretty=format:%H|%an|%ae|%ad|%s', '--date=short', f'-{limit}'],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 4)
                        if len(parts) == 5:
                            commits.append({
                                'hash': parts[0],
                                'author': parts[1],
                                'email': parts[2],
                                'date': parts[3],
                                'message': parts[4]
                            })
        
        except Exception as e:
            print(f"Error getting recent commits: {e}")
        
        return commits
    
    def _get_branches(self, local_path: str) -> List[str]:
        """Get list of branches in the repository."""
        branches = []
        
        if not os.path.exists(local_path):
            return branches
        
        try:
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().replace('* ', '').replace('remotes/', '')
                    if branch and 'HEAD' not in branch:
                        branches.append(branch)
        
        except Exception as e:
            print(f"Error getting branches: {e}")
        
        return branches
    
    def _get_tags(self, local_path: str) -> List[str]:
        """Get list of tags in the repository."""
        tags = []
        
        if not os.path.exists(local_path):
            return tags
        
        try:
            result = subprocess.run(
                ['git', 'tag', '-l'],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
        
        except Exception as e:
            print(f"Error getting tags: {e}")
        
        return tags
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        parsed = urlparse(repo_url)
        path_parts = parsed.path.split('/')
        if path_parts:
            return path_parts[-1].replace('.git', '')
        return 'unknown'
    
    def _extract_owner(self, repo_url: str) -> str:
        """Extract repository owner from URL."""
        parsed = urlparse(repo_url)
        path_parts = parsed.path.split('/')
        if len(path_parts) >= 2:
            return path_parts[-2]
        return 'unknown'
    
    def _extract_github_repo_path(self, repo_url: str) -> Optional[str]:
        """Extract GitHub repository path for API calls."""
        if 'github.com' not in repo_url:
            return None
        
        parsed = urlparse(repo_url)
        path = parsed.path.strip('/')
        
        # Remove .git suffix if present
        if path.endswith('.git'):
            path = path[:-4]
        
        return path
    
    def _get_clone_url(self, repo_url: str) -> str:
        """Get clone URL for the repository."""
        if repo_url.startswith('https://'):
            return repo_url
        elif repo_url.startswith('http://'):
            return repo_url.replace('http://', 'https://')
        elif repo_url.startswith('git@'):
            # Convert SSH URL to HTTPS
            return repo_url.replace('git@github.com:', 'https://github.com/')
        
        return repo_url
    
    def get_repository_size(self, local_path: str) -> int:
        """Get repository size in bytes."""
        if not os.path.exists(local_path):
            return 0
        
        try:
            total_size = 0
            for root, dirs, files in os.walk(local_path):
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        pass
            
            return total_size
        except Exception as e:
            print(f"Error calculating repository size: {e}")
            return 0
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"