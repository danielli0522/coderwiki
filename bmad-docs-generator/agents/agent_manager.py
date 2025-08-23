#!/usr/bin/env python3
"""
Agent Manager - 代理管理器
负责管理和实例化 BMAD 代理
"""

import os
import sys
import logging
import importlib
import inspect
from typing import Dict, Any, Optional, Type
from pathlib import Path
from abc import ABC, abstractmethod

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class BaseAgent(ABC):
    """代理基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化代理

        Args:
            config: 代理配置
        """
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.agent_id = config.get('id', self.__class__.__name__.lower())
        self.capabilities = config.get('capabilities', [])
        self.logger = logging.getLogger(f"agent.{self.agent_id}")

    @abstractmethod
    def execute_task(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task_name: 任务名称
            inputs: 输入参数

        Returns:
            执行结果
        """
        pass

    def get_capabilities(self) -> list:
        """获取代理能力列表"""
        return self.capabilities

    def can_execute_task(self, task_name: str) -> bool:
        """检查是否可以执行指定任务"""
        return task_name in self.capabilities


class CodeAnalystAgent(BaseAgent):
    """代码分析师代理"""

    def execute_task(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行代码分析任务"""
        if task_name == "Scan Codebase":
            return self._scan_codebase(inputs)
        elif task_name == "Validate Analysis":
            return self._validate_analysis(inputs)
        else:
            raise ValueError(f"Unknown task: {task_name}")

    def _scan_codebase(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """扫描代码库"""
        repo_path = inputs.get('repo_path', '')

        self.logger.info(f"Scanning codebase at: {repo_path}")

        # 模拟代码扫描结果
        result = {
            'codebase_structure': {
                'total_files': 150,
                'languages': ['Python', 'JavaScript', 'HTML', 'CSS'],
                'main_directories': ['src', 'tests', 'docs', 'config'],
                'complexity_score': 7.5
            },
            'dependencies': {
                'python': ['flask', 'sqlalchemy', 'requests'],
                'javascript': ['react', 'axios', 'lodash']
            },
            'code_quality': {
                'maintainability': 'Good',
                'test_coverage': '75%',
                'documentation': 'Partial'
            }
        }

        return result

    def _validate_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """验证分析结果"""
        analysis_data = inputs.get('analysis_data', {})

        self.logger.info("Validating analysis results")

        # 模拟验证结果
        validation_result = {
            'is_valid': True,
            'confidence_score': 0.85,
            'issues_found': [],
            'recommendations': [
                'Consider adding more unit tests',
                'Improve documentation coverage'
            ]
        }

        return validation_result


class ArchitectureAnalystAgent(BaseAgent):
    """架构分析师代理"""

    def execute_task(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行架构分析任务"""
        if task_name == "Create Architecture Views":
            return self._create_architecture_views(inputs)
        elif task_name == "Generate Technical Overview":
            return self._generate_technical_overview(inputs)
        else:
            raise ValueError(f"Unknown task: {task_name}")

    def _create_architecture_views(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """创建架构视图"""
        codebase_data = inputs.get('codebase_data', {})

        self.logger.info("Creating architecture views")

        # 模拟架构分析结果
        result = {
            'architecture_patterns': [
                'MVC Pattern',
                'Repository Pattern',
                'Factory Pattern'
            ],
            'component_diagram': {
                'components': [
                    {'name': 'Web Layer', 'type': 'Controller'},
                    {'name': 'Business Logic', 'type': 'Service'},
                    {'name': 'Data Access', 'type': 'Repository'}
                ],
                'relationships': [
                    {'from': 'Web Layer', 'to': 'Business Logic', 'type': 'uses'},
                    {'from': 'Business Logic', 'to': 'Data Access', 'type': 'uses'}
                ]
            },
            'deployment_architecture': {
                'tiers': ['Presentation', 'Application', 'Data'],
                'technologies': ['Nginx', 'Flask', 'MySQL']
            }
        }

        return result

    def _generate_technical_overview(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """生成技术概览"""
        architecture_data = inputs.get('architecture_data', {})

        self.logger.info("Generating technical overview")

        # 模拟技术概览
        overview = {
            'system_overview': 'A modern web application built with Flask and React',
            'key_technologies': ['Python', 'Flask', 'React', 'MySQL'],
            'architecture_style': 'Layered Architecture',
            'scalability_considerations': [
                'Horizontal scaling with load balancers',
                'Database sharding for large datasets',
                'Caching strategy with Redis'
            ]
        }

        return overview


class FlowAnalystAgent(BaseAgent):
    """流程分析师代理"""

    def execute_task(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行流程分析任务"""
        if task_name == "Analyze Complex Flows":
            return self._analyze_complex_flows(inputs)
        elif task_name == "Validate Flow Analysis":
            return self._validate_flow_analysis(inputs)
        else:
            raise ValueError(f"Unknown task: {task_name}")

    def _analyze_complex_flows(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """分析复杂流程"""
        codebase_data = inputs.get('codebase_data', {})

        self.logger.info("Analyzing complex flows")

        # 模拟流程分析结果
        result = {
            'business_flows': [
                {
                    'name': 'User Registration',
                    'steps': ['Input Validation', 'User Creation', 'Email Verification'],
                    'complexity': 'Medium'
                },
                {
                    'name': 'Document Generation',
                    'steps': ['Request Processing', 'Analysis', 'Document Creation'],
                    'complexity': 'High'
                }
            ],
            'data_flows': [
                {
                    'name': 'User Data Flow',
                    'source': 'Frontend',
                    'destination': 'Database',
                    'transformation': 'Validation and Encryption'
                }
            ],
            'sequence_diagrams': [
                {
                    'name': 'Document Generation Sequence',
                    'participants': ['User', 'API', 'Analysis Engine', 'Document Generator'],
                    'interactions': [
                        'User requests document',
                        'API validates request',
                        'Analysis Engine processes code',
                        'Document Generator creates output'
                    ]
                }
            ]
        }

        return result

    def _validate_flow_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """验证流程分析"""
        flow_data = inputs.get('flow_data', {})

        self.logger.info("Validating flow analysis")

        # 模拟验证结果
        validation = {
            'is_valid': True,
            'coverage_score': 0.9,
            'missing_flows': [],
            'improvements': [
                'Add error handling flows',
                'Include timeout scenarios'
            ]
        }

        return validation


class ProblemSolverAgent(BaseAgent):
    """问题解决专家代理"""

    def execute_task(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行问题诊断任务"""
        if task_name == "Diagnose Potential Problems":
            return self._diagnose_potential_problems(inputs)
        elif task_name == "Validate Problem Diagnosis":
            return self._validate_problem_diagnosis(inputs)
        else:
            raise ValueError(f"Unknown task: {task_name}")

    def _diagnose_potential_problems(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """诊断潜在问题"""
        analysis_data = inputs.get('analysis_data', {})

        self.logger.info("Diagnosing potential problems")

        # 模拟问题诊断结果
        result = {
            'identified_problems': [
                {
                    'category': 'Security',
                    'severity': 'High',
                    'description': 'Missing input validation in user registration',
                    'impact': 'Potential security vulnerabilities',
                    'recommendation': 'Implement comprehensive input validation'
                },
                {
                    'category': 'Performance',
                    'severity': 'Medium',
                    'description': 'No caching strategy for frequently accessed data',
                    'impact': 'Slower response times',
                    'recommendation': 'Implement Redis caching'
                }
            ],
            'risk_assessment': {
                'overall_risk': 'Medium',
                'security_risk': 'High',
                'performance_risk': 'Medium',
                'maintainability_risk': 'Low'
            }
        }

        return result

    def _validate_problem_diagnosis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """验证问题诊断"""
        problems_data = inputs.get('problems_data', {})

        self.logger.info("Validating problem diagnosis")

        # 模拟验证结果
        validation = {
            'is_accurate': True,
            'confidence_score': 0.8,
            'false_positives': 0,
            'missed_issues': 1,
            'priority_recommendations': [
                'Address security issues first',
                'Plan performance improvements'
            ]
        }

        return validation


class DocEngineerAgent(BaseAgent):
    """文档工程师代理"""

    def execute_task(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行文档生成任务"""
        if task_name == "Generate Flow Analysis Doc":
            return self._generate_flow_analysis_doc(inputs)
        elif task_name == "Generate Problem Diagnosis Doc":
            return self._generate_problem_diagnosis_doc(inputs)
        elif task_name == "Final Quality Validation":
            return self._final_quality_validation(inputs)
        elif task_name == "Setup Project Context":
            return self._setup_project_context(inputs)
        else:
            raise ValueError(f"Unknown task: {task_name}")

    def _generate_flow_analysis_doc(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """生成流程分析文档"""
        flow_data = inputs.get('flow_data', {})

        self.logger.info("Generating flow analysis documentation")

        # 模拟流程分析文档
        doc = {
            'title': 'Business Flow Analysis',
            'content': """
# Business Flow Analysis

## Overview
This document provides a comprehensive analysis of the business flows within the system.

## Key Flows

### User Registration Flow
1. User submits registration form
2. System validates input data
3. User account is created
4. Verification email is sent
5. User confirms email address

### Document Generation Flow
1. User requests document generation
2. System analyzes codebase
3. Multiple agents process different aspects
4. Results are aggregated
5. Final document is generated and delivered

## Data Flow Diagrams
[Detailed data flow information would be included here]

## Recommendations
- Implement comprehensive error handling
- Add monitoring and logging
- Consider performance optimization
            """,
            'sections': ['overview', 'flows', 'diagrams', 'recommendations']
        }

        return doc

    def _generate_problem_diagnosis_doc(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """生成问题诊断文档"""
        problems_data = inputs.get('problems_data', {})

        self.logger.info("Generating problem diagnosis documentation")

        # 模拟问题诊断文档
        doc = {
            'title': 'Problem Diagnosis Report',
            'content': """
# Problem Diagnosis Report

## Executive Summary
This report identifies potential issues and provides recommendations for improvement.

## Critical Issues

### Security Vulnerabilities
- **Issue**: Missing input validation
- **Severity**: High
- **Impact**: Potential security breaches
- **Recommendation**: Implement comprehensive validation

### Performance Concerns
- **Issue**: No caching strategy
- **Severity**: Medium
- **Impact**: Slower response times
- **Recommendation**: Implement Redis caching

## Risk Assessment
- Overall Risk: Medium
- Security Risk: High
- Performance Risk: Medium

## Action Plan
1. Address security issues immediately
2. Plan performance improvements
3. Implement monitoring solutions
            """,
            'sections': ['summary', 'issues', 'risks', 'actions']
        }

        return doc

    def _final_quality_validation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """最终质量验证"""
        all_docs = inputs.get('all_documents', {})

        self.logger.info("Performing final quality validation")

        # 模拟质量验证结果
        validation = {
            'quality_score': 0.85,
            'completeness': 0.9,
            'accuracy': 0.8,
            'readability': 0.9,
            'issues_found': [
                'Some technical terms need clarification',
                'Add more code examples'
            ],
            'recommendations': [
                'Include more visual diagrams',
                'Add troubleshooting section'
            ],
            'is_approved': True
        }

        return validation

    def _setup_project_context(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """设置项目上下文"""
        repo_path = inputs.get('repo_path', '')

        self.logger.info(f"Setting up project context for: {repo_path}")

        # 模拟项目上下文设置
        context = {
            'project_name': 'CoderWiki',
            'project_type': 'Web Application',
            'technology_stack': ['Python', 'Flask', 'React', 'MySQL'],
            'analysis_scope': 'Comprehensive',
            'output_format': 'Markdown'
        }

        return context


class AgentManager:
    """代理管理器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化代理管理器

        Args:
            config: 配置信息
        """
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger(__name__)

        # 注册默认代理
        self._register_default_agents()

    def _register_default_agents(self):
        """注册默认代理"""
        default_agents = {
            'code-analyst': CodeAnalystAgent,
            'architecture-analyst': ArchitectureAnalystAgent,
            'flow-analyst': FlowAnalystAgent,
            'problem-solver': ProblemSolverAgent,
            'doc-engineer': DocEngineerAgent
        }

        for agent_id, agent_class in default_agents.items():
            agent_config = self.config.get('agents', {}).get(agent_id, {})
            agent_config['id'] = agent_id

            try:
                agent = agent_class(agent_config)
                self.agents[agent_id] = agent
                self.logger.info(f"Registered agent: {agent_id}")
            except Exception as e:
                self.logger.error(f"Failed to register agent {agent_id}: {e}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        获取代理实例

        Args:
            agent_id: 代理ID

        Returns:
            代理实例
        """
        return self.agents.get(agent_id)

    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """
        获取所有代理

        Returns:
            代理字典
        """
        return self.agents.copy()

    def register_agent(self, agent_id: str, agent_class: Type[BaseAgent], config: Dict[str, Any]):
        """
        注册新代理

        Args:
            agent_id: 代理ID
            agent_class: 代理类
            config: 代理配置
        """
        try:
            agent = agent_class(config)
            self.agents[agent_id] = agent
            self.logger.info(f"Registered custom agent: {agent_id}")
        except Exception as e:
            self.logger.error(f"Failed to register custom agent {agent_id}: {e}")

    def list_agents(self) -> list:
        """
        列出所有代理

        Returns:
            代理列表
        """
        return [
            {
                'id': agent_id,
                'name': agent.name,
                'capabilities': agent.get_capabilities()
            }
            for agent_id, agent in self.agents.items()
        ]

    def get_agent_capabilities(self, agent_id: str) -> list:
        """
        获取代理能力

        Args:
            agent_id: 代理ID

        Returns:
            能力列表
        """
        agent = self.get_agent(agent_id)
        if agent:
            return agent.get_capabilities()
        return []

    def can_execute_task(self, agent_id: str, task_name: str) -> bool:
        """
        检查代理是否可以执行指定任务

        Args:
            agent_id: 代理ID
            task_name: 任务名称

        Returns:
            是否可以执行
        """
        agent = self.get_agent(agent_id)
        if agent:
            return agent.can_execute_task(task_name)
        return False


def main():
    """主函数 - 用于测试"""
    import json

    # 测试配置
    config = {
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
        }
    }

    # 创建代理管理器
    manager = AgentManager(config)

    # 列出所有代理
    agents = manager.list_agents()
    print("Registered Agents:")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['id']})")
        print(f"    Capabilities: {', '.join(agent['capabilities'])}")

    # 测试代理执行
    print("\nTesting Agent Execution:")

    # 测试代码分析师
    code_analyst = manager.get_agent('code-analyst')
    if code_analyst:
        result = code_analyst.execute_task('scan-codebase', {'repo_path': '/test/repo'})
        print(f"Code Analyst Result: {result}")


if __name__ == '__main__':
    main()
