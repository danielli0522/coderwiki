"""
Code complexity analyzer for repository analysis.
"""

import os
import re
import ast
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor


class ComplexityLevel(Enum):
    """Complexity level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CodeSmell(Enum):
    """Code smell types."""
    LONG_METHOD = "long_method"
    LONG_CLASS = "long_class"
    COMPLEX_METHOD = "complex_method"
    DUPLICATE_CODE = "duplicate_code"
    LARGE_CLASS = "large_class"
    TOO_MANY_PARAMETERS = "too_many_parameters"
    TOO_MANY_METHODS = "too_many_methods"
    DEEP_NESTING = "deep_nesting"
    FEATURE_ENVY = "feature_envy"
    GOD_CLASS = "god_class"
    SPAGHETTI_CODE = "spaghetti_code"


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    comment_lines: int
    blank_lines: int
    maintainability_index: float
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    
    def get_complexity_level(self) -> ComplexityLevel:
        """Get overall complexity level."""
        # Weighted complexity score
        complexity_score = (
            self.cyclomatic_complexity * 0.3 +
            self.cognitive_complexity * 0.3 +
            (self.lines_of_code / 50) * 0.2 +
            (10 - self.maintainability_index) * 0.2
        )
        
        if complexity_score <= 5:
            return ComplexityLevel.LOW
        elif complexity_score <= 15:
            return ComplexityLevel.MEDIUM
        elif complexity_score <= 25:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.VERY_HIGH


@dataclass
class CodeSmellInfo:
    """Code smell information."""
    smell_type: CodeSmell
    severity: ComplexityLevel
    description: str
    location: str
    line_number: int
    suggestion: str


@dataclass
class FileComplexity:
    """File-level complexity analysis."""
    file_path: str
    language: str
    metrics: ComplexityMetrics
    smells: List[CodeSmellInfo]
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    overall_complexity: ComplexityLevel


class ComplexityAnalyzer:
    """Analyzer for code complexity and quality metrics."""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.thresholds = {
            'max_method_length': 50,
            'max_class_length': 500,
            'max_method_complexity': 10,
            'max_method_parameters': 5,
            'max_class_methods': 20,
            'max_nesting_depth': 4,
            'min_maintainability_index': 65,
            'duplicate_code_threshold': 6
        }
        
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze method compatible with CodeAnalysisEngine interface."""
        return self.analyze_complexity()
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity across the repository."""
        if not self.repository_path.exists():
            return {'error': f'Repository path does not exist: {self.repository_path}'}
        
        analysis = {
            'files': [],
            'summary': {
                'total_files': 0,
                'analyzed_files': 0,
                'complexity_distribution': {
                    'low': 0,
                    'medium': 0,
                    'high': 0,
                    'very_high': 0
                },
                'total_lines_of_code': 0,
                'total_comment_lines': 0,
                'average_complexity': 0,
                'average_maintainability': 0,
                'code_smells': {
                    'total': 0,
                    'by_type': {}
                }
            },
            'quality_metrics': {
                'maintainability_distribution': {},
                'complexity_hotspots': [],
                'duplicate_code_blocks': [],
                'technical_debt_estimate': 0
            },
            'recommendations': [],
            'metadata': {
                'analysis_timestamp': self._get_timestamp(),
                'repository_path': str(self.repository_path)
            }
        }
        
        # Collect all files to analyze
        files_to_analyze = []
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.supported_languages:
                        files_to_analyze.append(file_path)
        
        analysis['summary']['total_files'] = len(files_to_analyze)
        
        # Analyze files in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self._analyze_file_complexity, file_path): file_path
                for file_path in files_to_analyze
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    if file_result:
                        analysis['files'].append(file_result)
                        analysis['summary']['analyzed_files'] += 1
                        
                        # Update summary statistics
                        self._update_summary_stats(analysis, file_result)
                        
                except Exception as e:
                    # Log error but continue
                    continue
        
        # Calculate aggregate metrics
        analysis['quality_metrics'] = self._calculate_quality_metrics(analysis['files'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_complexity_recommendations(analysis)
        
        return analysis
    
    def _analyze_file_complexity(self, file_path: Path) -> Optional[FileComplexity]:
        """Analyze complexity of a single file."""
        try:
            language = self.supported_languages.get(file_path.suffix.lower(), 'unknown')
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Calculate basic metrics
            lines = content.split('\n')
            total_lines = len(lines)
            comment_lines = self._count_comment_lines(content, language)
            blank_lines = self._count_blank_lines(content)
            
            # Language-specific analysis
            if language == 'python':
                return self._analyze_python_file(file_path, content, language, total_lines, comment_lines, blank_lines)
            elif language in ['javascript', 'typescript']:
                return self._analyze_js_file(file_path, content, language, total_lines, comment_lines, blank_lines)
            else:
                return self._analyze_generic_file(file_path, content, language, total_lines, comment_lines, blank_lines)
        
        except Exception as e:
            return None
    
    def _analyze_python_file(self, file_path: Path, content: str, language: str, 
                           total_lines: int, comment_lines: int, blank_lines: int) -> FileComplexity:
        """Analyze Python file complexity."""
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            smells = []
            
            # Analyze functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_analysis = self._analyze_python_function(node, content)
                    functions.append(func_analysis)
                    smells.extend(func_analysis['smells'])
                
                elif isinstance(node, ast.ClassDef):
                    class_analysis = self._analyze_python_class(node, content)
                    classes.append(class_analysis)
                    smells.extend(class_analysis['smells'])
            
            # Calculate file-level metrics
            metrics = self._calculate_python_metrics(tree, content, total_lines, comment_lines, blank_lines)
            
            # Detect duplicate code
            duplicate_smells = self._detect_duplicate_code(content, str(file_path))
            smells.extend(duplicate_smells)
            
            return FileComplexity(
                file_path=str(file_path),
                language=language,
                metrics=metrics,
                smells=smells,
                functions=functions,
                classes=classes,
                overall_complexity=metrics.get_complexity_level()
            )
        
        except SyntaxError:
            # Handle syntax errors gracefully
            return self._create_error_file_complexity(file_path, language, total_lines, comment_lines, blank_lines)
    
    def _analyze_js_file(self, file_path: Path, content: str, language: str,
                       total_lines: int, comment_lines: int, blank_lines: int) -> FileComplexity:
        """Analyze JavaScript/TypeScript file complexity."""
        functions = []
        classes = []
        smells = []
        
        # Simple JavaScript analysis using regex
        function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{'
        class_pattern = r'class\s+(\w+)\s*\{'
        method_pattern = r'(\w+)\s*\(([^)]*)\)\s*\{'
        
        # Find functions
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1)
            func_params = match.group(2)
            func_start = match.start()
            func_end = self._find_closing_brace(content, func_start)
            
            if func_end > func_start:
                func_content = content[func_start:func_end]
                func_lines = func_content.count('\n')
                
                func_analysis = {
                    'name': func_name,
                    'parameters': len([p.strip() for p in func_params.split(',') if p.strip()]),
                    'lines': func_lines,
                    'complexity': self._calculate_js_complexity(func_content),
                    'smells': self._detect_function_smells(func_name, func_lines, len([p.strip() for p in func_params.split(',') if p.strip()]), str(file_path))
                }
                functions.append(func_analysis)
                smells.extend(func_analysis['smells'])
        
        # Find classes
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_start = match.start()
            class_end = self._find_closing_brace(content, class_start)
            
            if class_end > class_start:
                class_content = content[class_start:class_end]
                class_lines = class_content.count('\n')
                
                class_analysis = {
                    'name': class_name,
                    'lines': class_lines,
                    'methods': self._extract_js_methods(class_content),
                    'smells': self._detect_class_smells(class_name, class_lines, len(self._extract_js_methods(class_content)), str(file_path))
                }
                classes.append(class_analysis)
                smells.extend(class_analysis['smells'])
        
        # Calculate metrics
        metrics = self._calculate_generic_metrics(total_lines, comment_lines, blank_lines, len(functions), len(classes))
        
        # Detect duplicate code
        duplicate_smells = self._detect_duplicate_code(content, str(file_path))
        smells.extend(duplicate_smells)
        
        return FileComplexity(
            file_path=str(file_path),
            language=language,
            metrics=metrics,
            smells=smells,
            functions=functions,
            classes=classes,
            overall_complexity=metrics.get_complexity_level()
        )
    
    def _analyze_generic_file(self, file_path: Path, content: str, language: str,
                            total_lines: int, comment_lines: int, blank_lines: int) -> FileComplexity:
        """Analyze generic file complexity."""
        # Basic analysis for unsupported languages
        metrics = self._calculate_generic_metrics(total_lines, comment_lines, blank_lines, 0, 0)
        
        # Detect basic smells
        smells = []
        
        if total_lines > self.thresholds['max_class_length']:
            smells.append(CodeSmellInfo(
                smell_type=CodeSmell.LONG_CLASS,
                severity=ComplexityLevel.HIGH,
                description=f"File is too long: {total_lines} lines",
                location=str(file_path),
                line_number=1,
                suggestion="Consider splitting the file into smaller modules"
            ))
        
        # Detect duplicate code
        duplicate_smells = self._detect_duplicate_code(content, str(file_path))
        smells.extend(duplicate_smells)
        
        return FileComplexity(
            file_path=str(file_path),
            language=language,
            metrics=metrics,
            smells=smells,
            functions=[],
            classes=[],
            overall_complexity=metrics.get_complexity_level()
        )
    
    def _analyze_python_function(self, node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """Analyze Python function complexity."""
        func_name = node.name
        func_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        func_params = len(node.args.args)
        
        # Calculate cyclomatic complexity
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        smells = self._detect_function_smells(func_name, func_lines, func_params, content.split('\n')[node.lineno-1], node.lineno)
        
        return {
            'name': func_name,
            'parameters': func_params,
            'lines': func_lines,
            'complexity': complexity,
            'start_line': node.lineno,
            'end_line': node.end_lineno,
            'docstring': ast.get_docstring(node) is not None,
            'smells': smells
        }
    
    def _analyze_python_class(self, node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """Analyze Python class complexity."""
        class_name = node.name
        class_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        
        methods = []
        total_complexity = 0
        
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                method_analysis = self._analyze_python_function(child, content)
                methods.append(method_analysis)
                total_complexity += method_analysis['complexity']
        
        smells = self._detect_class_smells(class_name, class_lines, len(methods), content.split('\n')[node.lineno-1], node.lineno)
        
        return {
            'name': class_name,
            'lines': class_lines,
            'methods': methods,
            'total_complexity': total_complexity,
            'average_complexity': total_complexity / len(methods) if methods else 0,
            'start_line': node.lineno,
            'end_line': node.end_lineno,
            'smells': smells
        }
    
    def _calculate_python_metrics(self, tree: ast.AST, content: str, total_lines: int,
                                 comment_lines: int, blank_lines: int) -> ComplexityMetrics:
        """Calculate Python-specific complexity metrics."""
        # Count functions and classes
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Calculate cyclomatic complexity
        cyclomatic_complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                cyclomatic_complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                cyclomatic_complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                cyclomatic_complexity += 1
        
        cyclomatic_complexity = max(1, cyclomatic_complexity)
        
        # Calculate cognitive complexity (simplified)
        cognitive_complexity = self._calculate_cognitive_complexity(content)
        
        # Calculate maintainability index
        maintainability = self._calculate_maintainability_index(
            total_lines, comment_lines, cyclomatic_complexity, len(functions)
        )
        
        # Calculate Halstead metrics (simplified)
        halstead_volume = self._calculate_halstead_volume(content)
        halstead_difficulty = self._calculate_halstead_difficulty(content)
        halstead_effort = halstead_volume * halstead_difficulty
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cognitive_complexity,
            lines_of_code=total_lines - comment_lines - blank_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            maintainability_index=maintainability,
            halstead_volume=halstead_volume,
            halstead_difficulty=halstead_difficulty,
            halstead_effort=halstead_effort
        )
    
    def _calculate_generic_metrics(self, total_lines: int, comment_lines: int, blank_lines: int,
                                  function_count: int, class_count: int) -> ComplexityMetrics:
        """Calculate generic complexity metrics."""
        code_lines = total_lines - comment_lines - blank_lines
        
        # Estimate complexity based on structure
        cyclomatic_complexity = max(1, function_count + class_count)
        cognitive_complexity = max(1, int(code_lines / 10))
        
        maintainability = self._calculate_maintainability_index(
            total_lines, comment_lines, cyclomatic_complexity, function_count
        )
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cognitive_complexity,
            lines_of_code=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            maintainability_index=maintainability,
            halstead_volume=code_lines * 1.5,  # Simplified
            halstead_difficulty=1.0,  # Simplified
            halstead_effort=code_lines * 1.5  # Simplified
        )
    
    def _count_comment_lines(self, content: str, language: str) -> int:
        """Count comment lines based on language."""
        comment_lines = 0
        
        if language == 'python':
            # Python comments
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('#') and not line.startswith('"""'):
                    comment_lines += 1
                elif '"""' in line and line.count('"""') == 2:
                    comment_lines += 1
        
        elif language in ['javascript', 'typescript']:
            # JS/TS comments
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('//'):
                    comment_lines += 1
                elif line.startswith('/*') or line.startswith('*'):
                    comment_lines += 1
                elif line.endswith('*/'):
                    comment_lines += 1
        
        return comment_lines
    
    def _count_blank_lines(self, content: str) -> int:
        """Count blank lines."""
        return sum(1 for line in content.split('\n') if not line.strip())
    
    def _calculate_cognitive_complexity(self, content: str) -> int:
        """Calculate cognitive complexity (simplified)."""
        complexity = 1  # Base complexity
        
        # Count nesting levels
        nesting_level = 0
        for line in content.split('\n'):
            stripped = line.strip()
            
            if stripped.startswith(('if ', 'for ', 'while ', 'with ', 'try:', 'except', 'elif ')):
                nesting_level += 1
                complexity += nesting_level
            elif stripped.startswith(('else:', 'finally:', 'except ')):
                complexity += nesting_level
            elif stripped and not stripped.startswith('#'):
                # Reset nesting level for non-indented lines
                if not line.startswith(' ') and not line.startswith('\t'):
                    nesting_level = 0
        
        return complexity
    
    def _calculate_maintainability_index(self, total_lines: int, comment_lines: int,
                                        cyclomatic_complexity: int, function_count: int) -> float:
        """Calculate maintainability index."""
        if total_lines == 0:
            return 100.0
        
        # Simplified maintainability index calculation
        loc = total_lines
        cc = cyclomatic_complexity
        cm = function_count
        
        # Maintainability Index (original formula)
        mi = 171 - 5.2 * (loc ** 0.23) - 0.23 * cc - 16.2 * (cm ** 0.15)
        
        # Adjust for comment density
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        mi += comment_ratio * 50
        
        return max(0, min(100, mi))
    
    def _calculate_halstead_volume(self, content: str) -> float:
        """Calculate Halstead volume (simplified)."""
        # Count unique operators and operands
        operators = set(re.findall(r'[\+\-\*/%=<>!&|^~?:]', content))
        operands = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b', content))
        
        n1 = len(operators)  # Unique operators
        n2 = len(operands)  # Unique operands
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        # Total operators and operands
        N1 = len(re.findall(r'[\+\-\*/%=<>!&|^~?:]', content))
        N2 = len(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b', content))
        
        if N1 == 0 or N2 == 0:
            return 0.0
        
        # Halstead volume
        vocabulary = n1 + n2
        length = N1 + N2
        
        if vocabulary == 0:
            return 0.0
        
        return length * (2 ** (vocabulary / length))
    
    def _calculate_halstead_difficulty(self, content: str) -> float:
        """Calculate Halstead difficulty (simplified)."""
        operators = set(re.findall(r'[\+\-\*/%=<>!&|^~?:]', content))
        operands = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b', content))
        
        n1 = len(operators)
        n2 = len(operands)
        
        if n1 == 0 or n2 == 0:
            return 1.0
        
        # Total unique operands
        N2 = len(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b', content))
        
        if N2 == 0:
            return 1.0
        
        return (n1 / 2) * (N2 / n2)
    
    def _detect_function_smells(self, func_name: str, lines: int, parameters: int,
                               location: str, line_number: int = 1) -> List[CodeSmellInfo]:
        """Detect function-level code smells."""
        smells = []
        
        # Long method
        if lines > self.thresholds['max_method_length']:
            smells.append(CodeSmellInfo(
                smell_type=CodeSmell.LONG_METHOD,
                severity=ComplexityLevel.HIGH,
                description=f"Function '{func_name}' is too long: {lines} lines",
                location=location,
                line_number=line_number,
                suggestion="Consider breaking down into smaller functions"
            ))
        
        # Too many parameters
        if parameters > self.thresholds['max_method_parameters']:
            smells.append(CodeSmellInfo(
                smell_type=CodeSmell.TOO_MANY_PARAMETERS,
                severity=ComplexityLevel.MEDIUM,
                description=f"Function '{func_name}' has too many parameters: {parameters}",
                location=location,
                line_number=line_number,
                suggestion="Consider using a parameter object or refactoring"
            ))
        
        return smells
    
    def _detect_class_smells(self, class_name: str, lines: int, method_count: int,
                            location: str, line_number: int = 1) -> List[CodeSmellInfo]:
        """Detect class-level code smells."""
        smells = []
        
        # Large class
        if lines > self.thresholds['max_class_length']:
            smells.append(CodeSmellInfo(
                smell_type=CodeSmell.LARGE_CLASS,
                severity=ComplexityLevel.HIGH,
                description=f"Class '{class_name}' is too large: {lines} lines",
                location=location,
                line_number=line_number,
                suggestion="Consider splitting into smaller classes"
            ))
        
        # Too many methods
        if method_count > self.thresholds['max_class_methods']:
            smells.append(CodeSmellInfo(
                smell_type=CodeSmell.TOO_MANY_METHODS,
                severity=ComplexityLevel.MEDIUM,
                description=f"Class '{class_name}' has too many methods: {method_count}",
                location=location,
                line_number=line_number,
                suggestion="Consider applying Single Responsibility Principle"
            ))
        
        return smells
    
    def _detect_duplicate_code(self, content: str, file_path: str) -> List[CodeSmellInfo]:
        """Detect duplicate code blocks."""
        smells = []
        
        # Simple duplicate detection using line sequences
        lines = content.split('\n')
        line_sequences = {}
        
        for i in range(len(lines) - self.thresholds['duplicate_code_threshold']):
            sequence = '\n'.join(lines[i:i + self.thresholds['duplicate_code_threshold']])
            sequence_hash = hash(sequence)
            
            if sequence_hash in line_sequences:
                smells.append(CodeSmellInfo(
                    smell_type=CodeSmell.DUPLICATE_CODE,
                    severity=ComplexityLevel.MEDIUM,
                    description=f"Duplicate code detected starting at line {i + 1}",
                    location=file_path,
                    line_number=i + 1,
                    suggestion="Extract duplicate code into a shared function"
                ))
            else:
                line_sequences[sequence_hash] = i
        
        return smells
    
    def _calculate_js_complexity(self, content: str) -> int:
        """Calculate JavaScript complexity using regex."""
        complexity = 1  # Base complexity
        
        # Count control structures
        complexity += len(re.findall(r'\bif\b', content))
        complexity += len(re.findall(r'\bwhile\b', content))
        complexity += len(re.findall(r'\bfor\b', content))
        complexity += len(re.findall(r'\bcatch\b', content))
        complexity += len(re.findall(r'\&\&|\|\|', content))  # Logical operators
        
        return complexity
    
    def _find_closing_brace(self, content: str, start_pos: int) -> int:
        """Find the closing brace for a given opening brace."""
        brace_count = 0
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i
        return len(content)
    
    def _extract_js_methods(self, class_content: str) -> List[str]:
        """Extract method names from JavaScript class content."""
        methods = []
        method_pattern = r'(\w+)\s*\([^)]*\)\s*\{'
        
        for match in re.finditer(method_pattern, class_content):
            methods.append(match.group(1))
        
        return methods
    
    def _create_error_file_complexity(self, file_path: Path, language: str,
                                    total_lines: int, comment_lines: int, blank_lines: int) -> FileComplexity:
        """Create file complexity for files with parsing errors."""
        metrics = self._calculate_generic_metrics(total_lines, comment_lines, blank_lines, 0, 0)
        
        return FileComplexity(
            file_path=str(file_path),
            language=language,
            metrics=metrics,
            smells=[],
            functions=[],
            classes=[],
            overall_complexity=metrics.get_complexity_level()
        )
    
    def _update_summary_stats(self, analysis: Dict[str, Any], file_result: FileComplexity):
        """Update summary statistics with file analysis results."""
        # Update complexity distribution
        complexity = file_result.overall_complexity.value
        analysis['summary']['complexity_distribution'][complexity] += 1
        
        # Update line counts
        analysis['summary']['total_lines_of_code'] += file_result.metrics.lines_of_code
        analysis['summary']['total_comment_lines'] += file_result.metrics.comment_lines
        
        # Update code smells
        analysis['summary']['code_smells']['total'] += len(file_result.smells)
        for smell in file_result.smells:
            smell_type = smell.smell_type.value
            if smell_type not in analysis['summary']['code_smells']['by_type']:
                analysis['summary']['code_smells']['by_type'][smell_type] = 0
            analysis['summary']['code_smells']['by_type'][smell_type] += 1
    
    def _calculate_quality_metrics(self, files: List[FileComplexity]) -> Dict[str, Any]:
        """Calculate aggregate quality metrics."""
        if not files:
            return {}
        
        metrics = {
            'maintainability_distribution': {
                'excellent': 0,
                'good': 0,
                'moderate': 0,
                'poor': 0
            },
            'complexity_hotspots': [],
            'duplicate_code_blocks': [],
            'technical_debt_estimate': 0
        }
        
        # Calculate maintainability distribution
        for file in files:
            mi = file.metrics.maintainability_index
            if mi >= 85:
                metrics['maintainability_distribution']['excellent'] += 1
            elif mi >= 70:
                metrics['maintainability_distribution']['good'] += 1
            elif mi >= 50:
                metrics['maintainability_distribution']['moderate'] += 1
            else:
                metrics['maintainability_distribution']['poor'] += 1
        
        # Find complexity hotspots
        complexity_scores = []
        for file in files:
            score = (
                file.metrics.cyclomatic_complexity * 0.4 +
                file.metrics.cognitive_complexity * 0.3 +
                (file.metrics.lines_of_code / 100) * 0.3
            )
            complexity_scores.append((file.file_path, score))
        
        # Top 5 complexity hotspots
        complexity_scores.sort(key=lambda x: x[1], reverse=True)
        metrics['complexity_hotspots'] = complexity_scores[:5]
        
        # Count duplicate code blocks
        duplicate_count = sum(len([s for s in f.smells if s.smell_type == CodeSmell.DUPLICATE_CODE]) for f in files)
        metrics['duplicate_code_blocks'] = duplicate_count
        
        # Estimate technical debt (simplified)
        total_smells = sum(len(f.smells) for f in files)
        metrics['technical_debt_estimate'] = total_smells * 8  # 8 hours per smell
        
        return metrics
    
    def _generate_complexity_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate complexity-based recommendations."""
        recommendations = []
        
        # Overall complexity recommendations
        high_complexity_files = analysis['summary']['complexity_distribution']['high'] + analysis['summary']['complexity_distribution']['very_high']
        total_files = analysis['summary']['analyzed_files']
        
        if high_complexity_files / total_files > 0.3:
            recommendations.append("High percentage of complex files. Consider refactoring critical areas.")
        
        # Maintainability recommendations
        poor_maintainability = analysis['quality_metrics']['maintainability_distribution']['poor']
        if poor_maintainability > total_files * 0.2:
            recommendations.append("Poor maintainability detected. Focus on improving code structure and documentation.")
        
        # Code smells recommendations
        total_smells = analysis['summary']['code_smells']['total']
        if total_smells > 50:
            recommendations.append(f"High number of code smells ({total_smells}). Prioritize refactoring.")
        
        # Specific smell recommendations
        smell_types = analysis['summary']['code_smells']['by_type']
        if 'long_method' in smell_types and smell_types['long_method'] > 10:
            recommendations.append("Many long methods detected. Apply Extract Method refactoring pattern.")
        
        if 'large_class' in smell_types and smell_types['large_class'] > 5:
            recommendations.append("Large classes detected. Apply Single Responsibility Principle.")
        
        if 'duplicate_code' in smell_types and smell_types['duplicate_code'] > 5:
            recommendations.append("Duplicate code detected. Extract common functionality.")
        
        # Technical debt recommendations
        tech_debt = analysis['quality_metrics']['technical_debt_estimate']
        if tech_debt > 100:
            recommendations.append(f"Estimated technical debt: {tech_debt} hours. Plan refactoring sprints.")
        
        # General recommendations
        recommendations.extend([
            "Implement code reviews to catch complexity issues early.",
            "Use static analysis tools in your CI/CD pipeline.",
            "Set complexity thresholds in your development process.",
            "Consider refactoring high-complexity hotspots first."
        ])
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()