import os
import re
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path

class CodeAnalyzer:
    """代码分析工具"""
    
    def __init__(self):
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
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        if not os.path.exists(file_path):
            return {}
        
        file_ext = Path(file_path).suffix.lower()
        language = self.supported_languages.get(file_ext, 'unknown')
        
        analysis = {
            'file_path': file_path,
            'language': language,
            'size': os.path.getsize(file_path),
            'lines': 0,
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity_score': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis['lines'] = len(content.split('\n'))
            
            if language == 'python':
                analysis.update(self._analyze_python_code(content))
            elif language in ['javascript', 'typescript']:
                analysis.update(self._analyze_js_code(content))
            
            analysis['complexity_score'] = self._calculate_complexity(analysis)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """分析整个目录"""
        analysis = {
            'directory': directory,
            'total_files': 0,
            'total_lines': 0,
            'languages': {},
            'file_analysis': [],
            'complexity_summary': {
                'low': 0,
                'medium': 0,
                'high': 0
            }
        }
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if Path(file).suffix.lower() in self.supported_languages:
                    file_analysis = self.analyze_file(file_path)
                    if file_analysis:
                        analysis['file_analysis'].append(file_analysis)
                        analysis['total_files'] += 1
                        analysis['total_lines'] += file_analysis.get('lines', 0)
                        
                        # 统计语言
                        lang = file_analysis.get('language', 'unknown')
                        analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1
                        
                        # 统计复杂度
                        complexity = file_analysis.get('complexity_score', 0)
                        if complexity < 10:
                            analysis['complexity_summary']['low'] += 1
                        elif complexity < 20:
                            analysis['complexity_summary']['medium'] += 1
                        else:
                            analysis['complexity_summary']['high'] += 1
        
        return analysis
    
    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """分析Python代码"""
        result = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'docstring': ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    result['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': []
                    })
                    
                    # 获取类方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            result['classes'][-1]['methods'].append({
                                'name': item.name,
                                'line': item.lineno
                            })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result['imports'].append(node.module)
        
        except Exception as e:
            result['parse_error'] = str(e)
        
        return result
    
    def _analyze_js_code(self, content: str) -> Dict[str, Any]:
        """分析JavaScript代码"""
        result = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        # 简单的JavaScript函数和类匹配
        function_pattern = r'function\s+(\w+)\s*\('
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        
        result['functions'] = re.findall(function_pattern, content)
        result['classes'] = re.findall(class_pattern, content)
        result['imports'] = re.findall(import_pattern, content)
        
        return result
    
    def _calculate_complexity(self, analysis: Dict[str, Any]) -> int:
        """计算代码复杂度"""
        complexity = 0
        
        # 基于函数数量
        complexity += len(analysis.get('functions', [])) * 2
        
        # 基于类数量
        complexity += len(analysis.get('classes', [])) * 3
        
        # 基于代码行数
        lines = analysis.get('lines', 0)
        if lines > 100:
            complexity += 5
        elif lines > 500:
            complexity += 10
        
        # 基于导入数量
        complexity += len(analysis.get('imports', []))
        
        return complexity
    
    def get_code_quality_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """获取代码质量指标"""
        metrics = {
            'maintainability': 0,
            'complexity': 'low',
            'documentation': 0,
            'test_coverage': 0
        }
        
        # 计算可维护性（基于复杂度）
        complexity_score = analysis.get('complexity_score', 0)
        if complexity_score < 10:
            metrics['maintainability'] = 90
            metrics['complexity'] = 'low'
        elif complexity_score < 20:
            metrics['maintainability'] = 70
            metrics['complexity'] = 'medium'
        else:
            metrics['maintainability'] = 50
            metrics['complexity'] = 'high'
        
        # 计算文档覆盖率（基于docstring）
        functions = analysis.get('functions', [])
        if functions:
            documented = sum(1 for f in functions if f.get('docstring'))
            metrics['documentation'] = (documented / len(functions)) * 100
        
        return metrics
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """生成分析报告"""
        report = []
        report.append(f"代码分析报告")
        report.append("=" * 50)
        report.append(f"总文件数: {analysis.get('total_files', 0)}")
        report.append(f"总代码行数: {analysis.get('total_lines', 0)}")
        report.append(f"语言分布: {analysis.get('languages', {})}")
        report.append(f"复杂度分布: {analysis.get('complexity_summary', {})}")
        
        return "\n".join(report)