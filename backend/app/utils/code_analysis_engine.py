"""
代码分析引擎主类
集成所有分析器，提供统一的代码分析接口
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict

from .structure_analyzer import StructureAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .complexity_analyzer import ComplexityAnalyzer
from .tech_stack_analyzer import TechStackAnalyzer
from .security_scanner import SecurityScanner
from .project_pattern_recognizer import ProjectPatternRecognizer
from .large_repository_optimizer import LargeRepositoryOptimizer

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """分析配置"""
    analysis_types: List[str]
    include_patterns: List[str]
    exclude_patterns: List[str]
    max_file_size: int
    timeout: int
    enable_cache: bool
    parallel_processing: bool

@dataclass
class AnalysisResult:
    """分析结果"""
    success: bool
    analysis_id: str
    repository_path: str
    analysis_type: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

class CodeAnalysisEngine:
    """代码分析引擎主类"""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """初始化分析引擎"""
        self.config = config or self._get_default_config()

        # 初始化各个分析器
        self.structure_analyzer = StructureAnalyzer
        self.dependency_analyzer = DependencyAnalyzer
        self.complexity_analyzer = ComplexityAnalyzer
        self.tech_stack_analyzer = TechStackAnalyzer
        self.security_scanner = SecurityScanner
        self.pattern_recognizer = ProjectPatternRecognizer
        self.repository_optimizer = LargeRepositoryOptimizer

        # 分析器映射
        self.analyzers = {
            'structure': self._analyze_structure,
            'dependencies': self._analyze_dependencies,
            'complexity': self._analyze_complexity,
            'tech_stack': self._analyze_tech_stack,
            'security': self._analyze_security,
            'patterns': self._analyze_patterns,
            'quality': self._analyze_quality
        }

        logger.info("Code analysis engine initialized")

    def _get_default_config(self) -> AnalysisConfig:
        """获取默认配置"""
        return AnalysisConfig(
            analysis_types=['structure', 'dependencies', 'complexity', 'tech_stack'],
            include_patterns=['*'],
            exclude_patterns=['*.log', '*.tmp', 'node_modules/', '.git/', '__pycache__/'],
            max_file_size=10 * 1024 * 1024,  # 10MB
            timeout=300,  # 5分钟
            enable_cache=True,
            parallel_processing=True
        )

    def analyze_repository(self, repository_path: str,
                         analysis_types: Optional[List[str]] = None,
                         config: Optional[AnalysisConfig] = None) -> AnalysisResult:
        """分析整个代码仓库"""
        start_time = time.time()
        analysis_id = f"analysis_{int(time.time())}"

        try:
            logger.info(f"Starting repository analysis: {repository_path}")

            # 验证仓库路径
            if not os.path.exists(repository_path):
                raise ValueError(f"Repository path does not exist: {repository_path}")

            # 使用提供的配置或默认配置
            analysis_config = config or self.config
            analysis_types = analysis_types or analysis_config.analysis_types

            # 验证分析类型
            valid_types = set(self.analyzers.keys())
            invalid_types = set(analysis_types) - valid_types
            if invalid_types:
                raise ValueError(f"Invalid analysis types: {invalid_types}")

            # 对于大型仓库，应用优化
            repo_size = self._get_repository_size(repository_path)
            if repo_size > analysis_config.max_file_size * 10:  # 如果仓库大小超过文件大小限制的10倍
                logger.info(f"Large repository detected ({repo_size} bytes), applying optimizations")
                optimizer = self.repository_optimizer(repository_path)
                repository_path = optimizer.optimize_for_analysis()

            # 执行分析
            results = {}
            metadata = {
                'repository_size': repo_size,
                'file_count': self._count_files(repository_path),
                'analysis_types': analysis_types,
                'config_used': asdict(analysis_config)
            }

            for analysis_type in analysis_types:
                if analysis_type in self.analyzers:
                    logger.info(f"Running {analysis_type} analysis")
                    try:
                        result = self.analyzers[analysis_type](repository_path, analysis_config)
                        results[analysis_type] = result
                        metadata[f'{analysis_type}_status'] = 'completed'
                    except Exception as e:
                        logger.error(f"Error in {analysis_type} analysis: {str(e)}")
                        results[analysis_type] = {'error': str(e)}
                        metadata[f'{analysis_type}_status'] = 'failed'

            # 计算执行时间
            execution_time = time.time() - start_time

            # 生成分析结果
            analysis_result = AnalysisResult(
                success=True,
                analysis_id=analysis_id,
                repository_path=repository_path,
                analysis_type=', '.join(analysis_types),
                results=results,
                metadata=metadata,
                execution_time=execution_time
            )

            logger.info(f"Repository analysis completed successfully in {execution_time:.2f}s")
            return analysis_result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Repository analysis failed: {str(e)}")

            return AnalysisResult(
                success=False,
                analysis_id=analysis_id,
                repository_path=repository_path,
                analysis_type=', '.join(analysis_types or []),
                results={},
                metadata={},
                execution_time=execution_time,
                error_message=str(e)
            )

    def analyze_file(self, file_path: str, analysis_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """分析单个文件"""
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")

        analysis_types = analysis_types or ['complexity', 'security']
        results = {}

        for analysis_type in analysis_types:
            if analysis_type in self.analyzers:
                try:
                    if analysis_type == 'complexity':
                        analyzer = self.complexity_analyzer(str(Path(file_path).parent))
                        result = analyzer.analyze_file(file_path)
                    elif analysis_type == 'security':
                        analyzer = self.security_scanner(str(Path(file_path).parent))
                        result = analyzer.scan_file(file_path)
                    else:
                        result = {'message': f'File-level analysis not supported for {analysis_type}'}

                    results[analysis_type] = result
                except Exception as e:
                    results[analysis_type] = {'error': str(e)}

        return results

    def get_supported_analysis_types(self) -> List[str]:
        """获取支持的分析类型"""
        return list(self.analyzers.keys())

    def get_analysis_capabilities(self) -> Dict[str, Any]:
        """获取分析能力描述"""
        return {
            'structure': {
                'description': '文件结构分析',
                'capabilities': ['目录树生成', '文件类型统计', '项目结构识别']
            },
            'dependencies': {
                'description': '依赖关系分析',
                'capabilities': ['包依赖解析', '依赖关系图', '版本冲突检测']
            },
            'complexity': {
                'description': '代码复杂度分析',
                'capabilities': ['圈复杂度计算', '代码质量指标', '代码异味检测']
            },
            'tech_stack': {
                'description': '技术栈分析',
                'capabilities': ['编程语言识别', '框架检测', '工具链分析']
            },
            'security': {
                'description': '安全扫描',
                'capabilities': ['漏洞检测', '敏感信息扫描', '安全模式识别']
            },
            'patterns': {
                'description': '项目模式识别',
                'capabilities': ['架构模式识别', '项目类型分类', '最佳实践检查']
            },
            'quality': {
                'description': '代码质量分析',
                'capabilities': ['代码规范检查', '重复代码检测', '可维护性评估']
            }
        }

    def validate_analysis_config(self, config: AnalysisConfig) -> List[str]:
        """验证分析配置"""
        errors = []

        # 验证分析类型
        valid_types = set(self.analyzers.keys())
        invalid_types = set(config.analysis_types) - valid_types
        if invalid_types:
            errors.append(f"Invalid analysis types: {invalid_types}")

        # 验证文件大小限制
        if config.max_file_size <= 0:
            errors.append("Max file size must be positive")

        # 验证超时设置
        if config.timeout <= 0:
            errors.append("Timeout must be positive")

        return errors

    def _analyze_structure(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析文件结构"""
        analyzer = self.structure_analyzer(repository_path)
        return analyzer.analyze_structure()

    def _analyze_dependencies(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析依赖关系"""
        analyzer = self.dependency_analyzer(repository_path)
        return analyzer.analyze_dependencies()

    def _analyze_complexity(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析代码复杂度"""
        analyzer = self.complexity_analyzer(repository_path)
        return analyzer.analyze_complexity()

    def _analyze_tech_stack(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析技术栈"""
        analyzer = self.tech_stack_analyzer(repository_path)
        return analyzer.analyze()

    def _analyze_security(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析安全性"""
        analyzer = self.security_scanner(repository_path)
        scan_result = analyzer.scan_repository()
        # 转换为字典格式以确保一致性
        return scan_result.to_dict() if hasattr(scan_result, 'to_dict') else scan_result.__dict__

    def _analyze_patterns(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析项目模式"""
        analyzer = self.pattern_recognizer(repository_path)
        return analyzer.analyze_patterns()

    def _analyze_quality(self, repository_path: str, config: AnalysisConfig) -> Dict[str, Any]:
        """分析代码质量"""
        # 综合多个分析器的结果来评估代码质量
        complexity_result = self._analyze_complexity(repository_path, config)
        structure_result = self._analyze_structure(repository_path, config)

        quality_metrics = {
            'complexity_score': complexity_result.get('overall_complexity', 0),
            'maintainability_index': self._calculate_maintainability(complexity_result),
            'code_duplication': self._calculate_duplication(structure_result),
            'documentation_coverage': self._calculate_documentation_coverage(structure_result),
            'test_coverage': self._calculate_test_coverage(structure_result),
            'overall_quality_score': 0
        }

        # 计算总体质量分数
        quality_metrics['overall_quality_score'] = self._calculate_overall_quality(quality_metrics)

        return quality_metrics

    def _calculate_maintainability(self, complexity_result: Dict[str, Any]) -> float:
        """计算可维护性指数"""
        overall_complexity = complexity_result.get('overall_complexity', 0)
        if overall_complexity <= 10:
            return 85.0
        elif overall_complexity <= 20:
            return 70.0
        elif overall_complexity <= 30:
            return 55.0
        else:
            return 40.0

    def _calculate_duplication(self, structure_result: Dict[str, Any]) -> float:
        """计算代码重复率（简化版本）"""
        # 这里可以集成更复杂的重复代码检测算法
        return 5.0  # 默认值

    def _calculate_documentation_coverage(self, structure_result: Dict[str, Any]) -> float:
        """计算文档覆盖率"""
        file_stats = structure_result.get('file_statistics', {})
        total_files = file_stats.get('total_files', 0)

        if total_files == 0:
            return 0.0

        # 简化的文档覆盖率计算
        documented_files = sum(1 for stats in file_stats.get('by_language', {}).values()
                            if isinstance(stats, dict) and stats.get('documented_files', 0))

        return (documented_files / total_files) * 100 if total_files > 0 else 0.0

    def _calculate_test_coverage(self, structure_result: Dict[str, Any]) -> float:
        """计算测试覆盖率"""
        file_stats = structure_result.get('file_statistics', {})
        test_files = file_stats.get('test_files', 0)
        total_files = file_stats.get('total_files', 0)

        if total_files == 0:
            return 0.0

        return (test_files / total_files) * 100

    def _calculate_overall_quality(self, quality_metrics: Dict[str, Any]) -> float:
        """计算总体质量分数"""
        weights = {
            'complexity_score': 0.3,
            'maintainability_index': 0.25,
            'code_duplication': 0.15,
            'documentation_coverage': 0.2,
            'test_coverage': 0.1
        }

        # 将各指标标准化到0-100范围
        normalized_metrics = {
            'complexity_score': max(0, 100 - quality_metrics['complexity_score'] * 2),
            'maintainability_index': quality_metrics['maintainability_index'],
            'code_duplication': max(0, 100 - quality_metrics['code_duplication']),
            'documentation_coverage': quality_metrics['documentation_coverage'],
            'test_coverage': quality_metrics['test_coverage']
        }

        overall_score = sum(
            normalized_metrics[key] * weights[key]
            for key in weights.keys()
        )

        return min(100, max(0, overall_score))

    def _get_repository_size(self, repository_path: str) -> int:
        """获取仓库大小"""
        total_size = 0
        for root, dirs, files in os.walk(repository_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
        return total_size

    def _count_files(self, repository_path: str) -> int:
        """统计文件数量"""
        count = 0
        for root, dirs, files in os.walk(repository_path):
            # 跳过隐藏目录和常见的忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
            count += len(files)
        return count

    def generate_summary_report(self, analysis_result: AnalysisResult) -> str:
        """生成分析摘要报告"""
        if not analysis_result.success:
            return f"Analysis failed: {analysis_result.error_message}"

        report = []
        report.append("=" * 60)
        report.append("代码分析报告摘要")
        report.append("=" * 60)
        report.append(f"分析ID: {analysis_result.analysis_id}")
        report.append(f"仓库路径: {analysis_result.repository_path}")
        report.append(f"分析类型: {analysis_result.analysis_type}")
        report.append(f"执行时间: {analysis_result.execution_time:.2f}s")
        report.append("")

        # 添加元数据
        metadata = analysis_result.metadata
        if 'repository_size' in metadata:
            size_mb = metadata['repository_size'] / (1024 * 1024)
            report.append(f"仓库大小: {size_mb:.2f} MB")

        if 'file_count' in metadata:
            report.append(f"文件数量: {metadata['file_count']}")

        report.append("")

        # 添加各类型分析结果摘要
        for analysis_type, result in analysis_result.results.items():
            if isinstance(result, dict) and 'error' not in result:
                report.append(f"=== {analysis_type.upper()} 分析结果 ===")

                if analysis_type == 'structure':
                    stats = result.get('file_statistics', {})
                    report.append(f"  总文件数: {stats.get('total_files', 0)}")
                    report.append(f"  主要语言: {list(stats.get('by_language', {}).keys())[:3]}")

                elif analysis_type == 'dependencies':
                    deps = result.get('dependencies', {})
                    report.append(f"  检测到 {len(deps)} 个依赖项")

                elif analysis_type == 'complexity':
                    report.append(f"  整体复杂度: {result.get('overall_complexity', 0)}")

                elif analysis_type == 'tech_stack':
                    languages = result.get('languages', [])
                    frameworks = result.get('frameworks', [])
                    report.append(f"  主要语言: {languages[:3] if languages else 'Unknown'}")
                    report.append(f"  主要框架: {frameworks[:3] if frameworks else 'None'}")

                elif analysis_type == 'security':
                    issues = result.get('security_issues', [])
                    report.append(f"  发现 {len(issues)} 个安全问题")

                elif analysis_type == 'quality':
                    report.append(f"  总体质量分数: {result.get('overall_quality_score', 0):.1f}/100")

                report.append("")

        return "\n".join(report)
