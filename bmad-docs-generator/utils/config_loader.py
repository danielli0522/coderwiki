#!/usr/bin/env python3
"""
Config Loader - 配置加载器
负责加载和管理 BMAD 系统配置
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """配置加载器"""

    @staticmethod
    def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        if config_path and os.path.exists(config_path):
            return ConfigLoader._load_from_file(config_path)
        else:
            return ConfigLoader._load_default_config()

    @staticmethod
    def _load_from_file(config_path: str) -> Dict[str, Any]:
        """
        从文件加载配置

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        file_ext = Path(config_path).suffix.lower()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if file_ext in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif file_ext == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {file_ext}")
        except Exception as e:
            print(f"Failed to load config from {config_path}: {e}")
            return ConfigLoader._load_default_config()

    @staticmethod
    def _load_default_config() -> Dict[str, Any]:
        """
        加载默认配置

        Returns:
            默认配置字典
        """
        return {
            'agents': {
                'code-analyst': {
                    'name': 'Code Analyst (Alex)',
                    'capabilities': ['scan-codebase', 'validate-analysis']
                },
                'architecture-analyst': {
                    'name': 'Architecture Analyst',
                    'capabilities': ['create-architecture-views', 'generate-technical-overview']
                },
                'flow-analyst': {
                    'name': 'Flow Analyst (Jordan)',
                    'capabilities': ['analyze-complex-flows', 'validate-flow-analysis']
                },
                'problem-solver': {
                    'name': 'Problem Solver (Dr. Morgan)',
                    'capabilities': ['diagnose-potential-problems', 'validate-problem-diagnosis']
                },
                'doc-engineer': {
                    'name': 'Doc Engineer (Maya)',
                    'capabilities': ['generate-flow-analysis-doc', 'generate-problem-diagnosis-doc', 'final-quality-validation']
                }
            },
            'workflows': {
                'enhanced-docs-generation': {
                    'name': 'Enhanced Documentation Generation',
                    'description': 'Generate comprehensive technical documentation',
                    'phases': [
                        {
                            'name': 'initialization',
                            'description': 'Initialize project context',
                            'tasks': [
                                {
                                    'id': 'setup-context',
                                    'name': 'Setup Project Context',
                                    'agent': 'doc-engineer'
                                }
                            ]
                        },
                        {
                            'name': 'code-analysis',
                            'description': 'Analyze codebase structure',
                            'tasks': [
                                {
                                    'id': 'scan-codebase',
                                    'name': 'Scan Codebase',
                                    'agent': 'code-analyst'
                                },
                                {
                                    'id': 'validate-analysis',
                                    'name': 'Validate Analysis',
                                    'agent': 'code-analyst'
                                }
                            ]
                        },
                        {
                            'name': 'architecture-analysis',
                            'description': 'Analyze architecture patterns',
                            'tasks': [
                                {
                                    'id': 'create-architecture-views',
                                    'name': 'Create Architecture Views',
                                    'agent': 'architecture-analyst'
                                },
                                {
                                    'id': 'generate-technical-overview',
                                    'name': 'Generate Technical Overview',
                                    'agent': 'architecture-analyst'
                                }
                            ]
                        },
                        {
                            'name': 'flow-analysis',
                            'description': 'Analyze business flows',
                            'tasks': [
                                {
                                    'id': 'analyze-complex-flows',
                                    'name': 'Analyze Complex Flows',
                                    'agent': 'flow-analyst'
                                },
                                {
                                    'id': 'validate-flow-analysis',
                                    'name': 'Validate Flow Analysis',
                                    'agent': 'flow-analyst'
                                }
                            ]
                        },
                        {
                            'name': 'problem-diagnosis',
                            'description': 'Diagnose potential problems',
                            'tasks': [
                                {
                                    'id': 'diagnose-potential-problems',
                                    'name': 'Diagnose Potential Problems',
                                    'agent': 'problem-solver'
                                },
                                {
                                    'id': 'validate-problem-diagnosis',
                                    'name': 'Validate Problem Diagnosis',
                                    'agent': 'problem-solver'
                                }
                            ]
                        },
                        {
                            'name': 'documentation-generation',
                            'description': 'Generate final documentation',
                            'tasks': [
                                {
                                    'id': 'generate-flow-analysis-doc',
                                    'name': 'Generate Flow Analysis Doc',
                                    'agent': 'doc-engineer'
                                },
                                {
                                    'id': 'generate-problem-diagnosis-doc',
                                    'name': 'Generate Problem Diagnosis Doc',
                                    'agent': 'doc-engineer'
                                },
                                {
                                    'id': 'final-quality-validation',
                                    'name': 'Final Quality Validation',
                                    'agent': 'doc-engineer'
                                }
                            ]
                        }
                    ]
                }
            },
            'system': {
                'max_workers': 5,
                'timeout': 300,
                'log_level': 'INFO',
                'output_format': 'markdown'
            }
        }

