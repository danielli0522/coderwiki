"""
Large repository optimization service for handling big codebases.
"""

import os
import time
import threading
from typing import Dict, List, Any, Optional, Iterator, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import psutil
import signal
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed


class AnalysisPriority(Enum):
    """Analysis priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnalysisConfig:
    """Configuration for analysis optimization."""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_directory_depth: int = 8
    max_analysis_time: int = 300  # 5 minutes
    max_memory_usage: int = 512 * 1024 * 1024  # 512MB
    max_workers: int = multiprocessing.cpu_count()
    chunk_size: int = 1000
    enable_caching: bool = True
    enable_incremental: bool = True
    enable_parallel: bool = True


@dataclass
class AnalysisProgress:
    """Analysis progress tracking."""
    total_files: int = 0
    processed_files: int = 0
    current_file: str = ""
    progress_percentage: float = 0.0
    estimated_time_remaining: float = 0.0
    start_time: float = 0.0
    status: str = "pending"
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class LargeRepositoryOptimizer:
    """Optimizer for handling large repository analysis."""
    
    def __init__(self, repository_path: str, config: AnalysisConfig = None):
        self.repository_path = Path(repository_path)
        self.config = config or AnalysisConfig()
        self.progress = AnalysisProgress()
        self.cancel_flag = threading.Event()
        self.memory_monitor = None
        self.timeout_timer = None
        
    def analyze_with_optimization(self, analysis_type: str = "full") -> Dict[str, Any]:
        """Analyze repository with optimization for large codebases."""
        self.progress = AnalysisProgress()
        self.progress.start_time = time.time()
        self.progress.status = "analyzing"
        
        try:
            # Start monitoring
            self._start_monitoring()
            
            # Get repository overview first
            overview = self._get_repository_overview()
            self.progress.total_files = overview['total_files']
            
            # Determine analysis strategy
            strategy = self._determine_analysis_strategy(overview)
            
            # Execute analysis based on strategy
            if strategy['use_incremental']:
                result = self._analyze_incremental(analysis_type, strategy)
            elif strategy['use_parallel']:
                result = self._analyze_parallel(analysis_type, strategy)
            else:
                result = self._analyze_sequential(analysis_type, strategy)
            
            # Add optimization metadata
            result['optimization'] = {
                'strategy': strategy['name'],
                'analysis_time': time.time() - self.progress.start_time,
                'files_processed': self.progress.processed_files,
                'memory_peak': self._get_peak_memory_usage(),
                'errors_encountered': len(self.progress.errors)
            }
            
            self.progress.status = "completed"
            return result
            
        except Exception as e:
            self.progress.status = "failed"
            self.progress.errors.append(f"Analysis failed: {str(e)}")
            return {'error': str(e), 'progress': self.progress.__dict__}
        
        finally:
            self._stop_monitoring()
    
    def _get_repository_overview(self) -> Dict[str, Any]:
        """Get quick overview of repository to determine optimization strategy."""
        overview = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'directory_structure': {},
            'large_files': [],
            'deep_directories': []
        }
        
        try:
            # Quick scan to gather statistics
            for root, dirs, files in os.walk(self.repository_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Track directory depth
                current_depth = root.count(os.sep) - str(self.repository_path).count(os.sep)
                if current_depth > self.config.max_directory_depth:
                    overview['deep_directories'].append(root)
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = Path(root) / file
                        try:
                            file_size = file_path.stat().st_size
                            overview['total_files'] += 1
                            overview['total_size'] += file_size
                            
                            # Track file types
                            ext = file_path.suffix.lower()
                            overview['file_types'][ext] = overview['file_types'].get(ext, 0) + 1
                            
                            # Track large files
                            if file_size > self.config.max_file_size:
                                overview['large_files'].append({
                                    'path': str(file_path),
                                    'size': file_size
                                })
                        
                        except (OSError, PermissionError):
                            continue
        
        except Exception as e:
            overview['error'] = str(e)
        
        return overview
    
    def _determine_analysis_strategy(self, overview: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal analysis strategy based on repository characteristics."""
        strategy = {
            'name': 'sequential',
            'use_incremental': False,
            'use_parallel': False,
            'chunk_size': self.config.chunk_size,
            'skip_large_files': False,
            'memory_optimization': False
        }
        
        # Large repository - use incremental analysis
        if overview['total_files'] > 10000:
            strategy['name'] = 'incremental'
            strategy['use_incremental'] = True
            strategy['chunk_size'] = 5000
        
        # Medium repository with many files - use parallel analysis
        elif overview['total_files'] > 1000 and self.config.enable_parallel:
            strategy['name'] = 'parallel'
            strategy['use_parallel'] = True
        
        # Repository with large files - skip or handle specially
        if len(overview['large_files']) > 10:
            strategy['skip_large_files'] = True
        
        # Deep directory structure - optimize memory
        if len(overview['deep_directories']) > 5:
            strategy['memory_optimization'] = True
        
        # Large total size - be conservative
        if overview['total_size'] > 1024 * 1024 * 1024:  # 1GB
            strategy['memory_optimization'] = True
            strategy['chunk_size'] = min(strategy['chunk_size'], 1000)
        
        return strategy
    
    def _analyze_incremental(self, analysis_type: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Perform incremental analysis for large repositories."""
        results = {
            'chunks': [],
            'summary': {},
            'errors': []
        }
        
        chunk_files = []
        chunk_number = 0
        
        # Process files in chunks
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    
                    # Skip large files if configured
                    if strategy['skip_large_files']:
                        try:
                            file_size = file_path.stat().st_size
                            if file_size > self.config.max_file_size:
                                results['errors'].append(f"Skipped large file: {file_path}")
                                continue
                        except (OSError, PermissionError):
                            continue
                    
                    chunk_files.append(str(file_path))
                    
                    # Process chunk when it reaches size limit
                    if len(chunk_files) >= strategy['chunk_size']:
                        chunk_result = self._process_chunk(chunk_files, chunk_number, analysis_type)
                        results['chunks'].append(chunk_result)
                        chunk_files = []
                        chunk_number += 1
                        
                        # Update progress
                        self.progress.processed_files += len(chunk_result['files_processed'])
                        self._update_progress()
                        
                        # Check cancellation
                        if self.cancel_flag.is_set():
                            break
        
        # Process remaining files
        if chunk_files and not self.cancel_flag.is_set():
            chunk_result = self._process_chunk(chunk_files, chunk_number, analysis_type)
            results['chunks'].append(chunk_result)
            self.progress.processed_files += len(chunk_result['files_processed'])
            self._update_progress()
        
        # Generate summary
        results['summary'] = self._generate_chunk_summary(results['chunks'])
        
        return results
    
    def _analyze_parallel(self, analysis_type: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Perform parallel analysis for medium-sized repositories."""
        results = {
            'parallel_results': [],
            'summary': {},
            'errors': []
        }
        
        # Collect all files to process
        files_to_process = []
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    
                    # Skip large files if configured
                    if strategy['skip_large_files']:
                        try:
                            file_size = file_path.stat().st_size
                            if file_size > self.config.max_file_size:
                                results['errors'].append(f"Skipped large file: {file_path}")
                                continue
                        except (OSError, PermissionError):
                            continue
                    
                    files_to_process.append(str(file_path))
        
        # Split files into batches for parallel processing
        batch_size = max(1, len(files_to_process) // self.config.max_workers)
        file_batches = [files_to_process[i:i + batch_size] for i in range(0, len(files_to_process), batch_size)]
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_batch = {
                executor.submit(self._process_batch, batch, i, analysis_type): i
                for i, batch in enumerate(file_batches)
            }
            
            for future in as_completed(future_to_batch):
                batch_id = future_to_batch[future]
                try:
                    batch_result = future.result()
                    results['parallel_results'].append(batch_result)
                    self.progress.processed_files += len(batch_result['files_processed'])
                    self._update_progress()
                    
                except Exception as e:
                    results['errors'].append(f"Batch {batch_id} failed: {str(e)}")
        
        # Generate summary
        results['summary'] = self._generate_parallel_summary(results['parallel_results'])
        
        return results
    
    def _analyze_sequential(self, analysis_type: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sequential analysis for small repositories."""
        results = {
            'files_analyzed': [],
            'summary': {},
            'errors': []
        }
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    
                    try:
                        # Basic file analysis
                        file_info = {
                            'path': str(file_path),
                            'name': file,
                            'size': file_path.stat().st_size,
                            'extension': file_path.suffix.lower()
                        }
                        
                        # Add language-specific analysis if needed
                        if analysis_type == "full":
                            file_info.update(self._analyze_file_content(file_path))
                        
                        results['files_analyzed'].append(file_info)
                        self.progress.processed_files += 1
                        self._update_progress()
                        
                    except (OSError, PermissionError) as e:
                        results['errors'].append(f"Failed to analyze {file_path}: {str(e)}")
                    
                    # Check cancellation
                    if self.cancel_flag.is_set():
                        break
            
            if self.cancel_flag.is_set():
                break
        
        # Generate summary
        results['summary'] = self._generate_sequential_summary(results['files_analyzed'])
        
        return results
    
    def _process_chunk(self, files: List[str], chunk_number: int, analysis_type: str) -> Dict[str, Any]:
        """Process a chunk of files."""
        chunk_result = {
            'chunk_number': chunk_number,
            'files_processed': [],
            'summary': {
                'total_files': len(files),
                'total_size': 0,
                'file_types': {}
            }
        }
        
        for file_path in files:
            try:
                path = Path(file_path)
                file_info = {
                    'path': file_path,
                    'name': path.name,
                    'size': path.stat().st_size,
                    'extension': path.suffix.lower()
                }
                
                # Add basic analysis
                if analysis_type == "full":
                    file_info.update(self._analyze_file_content(path))
                
                chunk_result['files_processed'].append(file_info)
                chunk_result['summary']['total_size'] += file_info['size']
                
                # Track file types
                ext = file_info['extension']
                chunk_result['summary']['file_types'][ext] = chunk_result['summary']['file_types'].get(ext, 0) + 1
                
            except (OSError, PermissionError) as e:
                chunk_result['summary']['errors'] = chunk_result['summary'].get('errors', [])
                chunk_result['summary']['errors'].append(f"Failed to process {file_path}: {str(e)}")
        
        return chunk_result
    
    def _process_batch(self, files: List[str], batch_id: int, analysis_type: str) -> Dict[str, Any]:
        """Process a batch of files (similar to chunk but for parallel processing)."""
        return self._process_chunk(files, batch_id, analysis_type)
    
    def _analyze_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file content for basic metrics."""
        analysis = {
            'lines': 0,
            'language': 'unknown',
            'encoding': 'unknown'
        }
        
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)  # Read first 1KB for encoding detection
                analysis['encoding'] = self._detect_encoding(raw_data)
            
            # Count lines and detect language
            with open(file_path, 'r', encoding=analysis['encoding'], errors='ignore') as f:
                content = f.read()
                analysis['lines'] = len(content.split('\n'))
                analysis['language'] = self._detect_language(file_path, content)
        
        except (UnicodeDecodeError, OSError):
            pass
        
        return analysis
    
    def _detect_encoding(self, raw_data: bytes) -> str:
        """Detect file encoding."""
        try:
            import chardet
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
        except ImportError:
            # Fallback to simple detection
            try:
                raw_data.decode('utf-8')
                return 'utf-8'
            except UnicodeDecodeError:
                try:
                    raw_data.decode('latin-1')
                    return 'latin-1'
                except UnicodeDecodeError:
                    return 'ascii'
    
    def _detect_language(self, file_path: Path, content: str) -> str:
        """Detect programming language from file extension and content."""
        ext = file_path.suffix.lower()
        
        # Simple language detection based on extension
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown'
        }
        
        return language_map.get(ext, 'unknown')
    
    def _generate_chunk_summary(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from chunk results."""
        summary = {
            'total_chunks': len(chunks),
            'total_files': sum(chunk['summary']['total_files'] for chunk in chunks),
            'total_size': sum(chunk['summary']['total_size'] for chunk in chunks),
            'file_types': {},
            'errors': []
        }
        
        # Aggregate file types
        for chunk in chunks:
            for ext, count in chunk['summary']['file_types'].items():
                summary['file_types'][ext] = summary['file_types'].get(ext, 0) + count
            
            # Collect errors
            if 'errors' in chunk['summary']:
                summary['errors'].extend(chunk['summary']['errors'])
        
        return summary
    
    def _generate_parallel_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from parallel results."""
        return self._generate_chunk_summary(results)
    
    def _generate_sequential_summary(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from sequential results."""
        summary = {
            'total_files': len(files),
            'total_size': sum(f['size'] for f in files),
            'file_types': {},
            'languages': {}
        }
        
        for file_info in files:
            # Track file types
            ext = file_info['extension']
            summary['file_types'][ext] = summary['file_types'].get(ext, 0) + 1
            
            # Track languages
            lang = file_info.get('language', 'unknown')
            summary['languages'][lang] = summary['languages'].get(lang, 0) + 1
        
        return summary
    
    def _update_progress(self):
        """Update analysis progress."""
        if self.progress.total_files > 0:
            self.progress.progress_percentage = (self.progress.processed_files / self.progress.total_files) * 100
            
            # Calculate estimated time remaining
            elapsed_time = time.time() - self.progress.start_time
            if self.progress.progress_percentage > 0:
                total_estimated_time = elapsed_time / (self.progress.progress_percentage / 100)
                self.progress.estimated_time_remaining = total_estimated_time - elapsed_time
    
    def _start_monitoring(self):
        """Start resource monitoring."""
        # Start memory monitoring
        self.memory_monitor = threading.Thread(target=self._monitor_memory_usage)
        self.memory_monitor.daemon = True
        self.memory_monitor.start()
        
        # Start timeout timer
        self.timeout_timer = threading.Timer(self.config.max_analysis_time, self._timeout_handler)
        self.timeout_timer.start()
    
    def _stop_monitoring(self):
        """Stop resource monitoring."""
        if self.timeout_timer:
            self.timeout_timer.cancel()
        
        self.cancel_flag.set()
    
    def _monitor_memory_usage(self):
        """Monitor memory usage and cancel if exceeds limit."""
        while not self.cancel_flag.is_set():
            try:
                memory_usage = psutil.Process().memory_info().rss
                if memory_usage > self.config.max_memory_usage:
                    self.progress.errors.append(f"Memory usage exceeded limit: {memory_usage} bytes")
                    self.cancel_flag.set()
                    break
                
                time.sleep(1)  # Check every second
                
            except Exception:
                break
    
    def _timeout_handler(self):
        """Handle analysis timeout."""
        self.progress.errors.append(f"Analysis timed out after {self.config.max_analysis_time} seconds")
        self.cancel_flag.set()
    
    def _get_peak_memory_usage(self) -> int:
        """Get peak memory usage during analysis."""
        try:
            return psutil.Process().memory_info().rss
        except Exception:
            return 0
    
    def cancel_analysis(self):
        """Cancel ongoing analysis."""
        self.cancel_flag.set()
        self.progress.status = "cancelled"
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current analysis progress."""
        return self.progress.__dict__