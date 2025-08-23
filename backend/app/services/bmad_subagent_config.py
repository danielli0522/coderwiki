"""
BMAD Subagent Configuration for Claude Code Integration
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path

class BMADSubagentConfig:
    """BMAD子代理配置类"""

    def __init__(self, bmad_docs_path: str = None):
        """
        初始化BMAD子代理配置

        Args:
            bmad_docs_path: BMAD文档生成器路径
        """
        self.bmad_docs_path = bmad_docs_path or "../bmad-docs-generator/"
        self.config_file = os.path.join(self.bmad_docs_path, "config.yaml")
        self.workflows_dir = os.path.join(self.bmad_docs_path, "workflows/")
        self.agents_dir = os.path.join(self.bmad_docs_path, "agents/")
        self.teams_dir = os.path.join(self.bmad_docs_path, "agent-teams/")

        # 加载配置
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载BMAD配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading BMAD config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "bmad_docs_generator": {
                "version": "1.0.0",
                "name": "BMAD Documentation Generator",
                "description": "Advanced documentation generation using BMAD-Method framework",
                "settings": {
                    "default_analysis_depth": "detailed",
                    "enable_interactive_validation": True,
                    "enable_evidence_driven_analysis": True,
                    "enable_pattern_recognition": True
                },
                "paths": {
                    "agents_dir": "agents/",
                    "tasks_dir": "tasks/",
                    "workflows_dir": "workflows/",
                    "templates_dir": "templates/"
                },
                "output": {
                    "format": "markdown",
                    "include_diagrams": True,
                    "include_code_examples": True,
                    "include_troubleshooting": True
                },
                "quality": {
                    "min_complex_flows": 15,
                    "enable_quality_gates": True,
                    "validation_required": True
                }
            }
        }

    def get_subagent_teams(self) -> List[Dict[str, Any]]:
        """获取可用的子代理团队"""
        teams = []

        # 增强文档生成团队
        enhanced_team = {
            "id": "enhanced-docs-generation-team",
            "name": "Enhanced Documentation Generation Team",
            "description": "Advanced team for generating comprehensive technical documentation",
            "path": "bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml",
            "workflow": "enhanced-docs-generation",
            "agents": [
                "code-analyst",
                "tech-architect",
                "flow-analyst",
                "problem-solver",
                "doc-engineer"
            ]
        }
        teams.append(enhanced_team)

        # 基础文档生成团队
        basic_team = {
            "id": "docs-generation-team",
            "name": "Documentation Generation Team",
            "description": "Basic team for generating technical documentation",
            "path": "bmad-docs-generator/agent-teams/docs-generation-team.yaml",
            "workflow": "docs-generation-workflow",
            "agents": [
                "code-analyst",
                "tech-architect",
                "doc-engineer"
            ]
        }
        teams.append(basic_team)

        return teams

    def get_subagent_agents(self) -> List[Dict[str, Any]]:
        """获取可用的子代理"""
        agents = [
            {
                "id": "code-analyst",
                "name": "Code Analyst (Alex)",
                "role": "代码分析师",
                "path": "bmad-docs-generator/agents/code-analyst.md",
                "capabilities": [
                    "代码扫描",
                    "架构分析",
                    "模式识别",
                    "依赖分析",
                    "复杂度评估"
                ],
                "primary_tasks": [
                    "scan-codebase",
                    "analyze-dependencies",
                    "identify-patterns"
                ]
            },
            {
                "id": "tech-architect",
                "name": "Tech Architect (Sarah)",
                "role": "技术架构师",
                "path": "bmad-docs-generator/agents/tech-architect.md",
                "capabilities": [
                    "架构设计",
                    "技术选型",
                    "系统集成",
                    "性能优化"
                ],
                "primary_tasks": [
                    "create-architecture-views",
                    "generate-technical-overview",
                    "assess-tech-stack"
                ]
            },
            {
                "id": "flow-analyst",
                "name": "Flow Analyst (Jordan)",
                "role": "流程分析师",
                "path": "bmad-docs-generator/agents/flow-analyst.md",
                "capabilities": [
                    "流程分析",
                    "时序图生成",
                    "业务规则提取",
                    "性能影响评估"
                ],
                "primary_tasks": [
                    "analyze-complex-flows",
                    "generate-enhanced-sequence-diagrams",
                    "validate-flow-analysis"
                ]
            },
            {
                "id": "problem-solver",
                "name": "Problem Solver (Dr. Morgan)",
                "role": "问题诊断专家",
                "path": "bmad-docs-generator/agents/problem-solver.md",
                "capabilities": [
                    "问题诊断",
                    "风险评估",
                    "解决方案设计",
                    "监控策略"
                ],
                "primary_tasks": [
                    "diagnose-potential-problems",
                    "generate-arch-insights",
                    "validate-problem-diagnosis"
                ]
            },
            {
                "id": "doc-engineer",
                "name": "Doc Engineer (Maya)",
                "role": "文档工程师",
                "path": "bmad-docs-generator/agents/doc-engineer.md",
                "capabilities": [
                    "文档生成",
                    "模板管理",
                    "质量控制",
                    "格式转换"
                ],
                "primary_tasks": [
                    "generate-arch-documentation",
                    "assemble-final-documentation",
                    "final-quality-validation"
                ]
            }
        ]

        return agents

    def get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """获取工作流程配置"""
        workflow_file = os.path.join(self.workflows_dir, f"{workflow_name}.yaml")

        try:
            if os.path.exists(workflow_file):
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_workflow()
        except Exception as e:
            print(f"Error loading workflow {workflow_name}: {e}")
            return self._get_default_workflow()

    def _get_default_workflow(self) -> Dict[str, Any]:
        """获取默认工作流程"""
        return {
            "workflow": {
                "id": "enhanced-docs-generation",
                "name": "Enhanced Documentation Generation",
                "version": "2.0",
                "description": "Enhanced documentation generation workflow",
                "phases": [
                    {
                        "name": "initialization",
                        "tasks": ["setup-project-context"]
                    },
                    {
                        "name": "code-analysis",
                        "tasks": ["scan-codebase", "analyze-dependencies", "identify-patterns"]
                    },
                    {
                        "name": "architecture-analysis",
                        "tasks": ["analyze-architecture", "identify-arch-patterns", "assess-tech-stack"]
                    },
                    {
                        "name": "documentation-generation",
                        "tasks": ["generate-arch-documentation", "create-architecture-diagrams", "validate-documentation"]
                    }
                ]
            }
        }

    def get_subagent_call_instructions(self, team_id: str = "enhanced-docs-generation-team") -> str:
        """获取子代理调用指令"""
        teams = self.get_subagent_teams()
        team = next((t for t in teams if t["id"] == team_id), teams[0])

        instructions = f"""
**BMAD子代理调用指令**

1. **激活团队**: {team['path']}
   - 团队名称: {team['name']}
   - 描述: {team['description']}

2. **工作流程**: {team['workflow']}
   - 包含 {len(team['agents'])} 个专业代理
   - 支持多阶段文档生成

3. **可用代理**:
"""

        for agent_id in team['agents']:
            agents = self.get_subagent_agents()
            agent = next((a for a in agents if a["id"] == agent_id), None)
            if agent:
                instructions += f"   - {agent['name']} ({agent['role']}): {agent['path']}\n"

        instructions += """
4. **调用方式**:
   - 使用Task工具调用BMAD子代理
   - 指定代理路径和任务
   - 传递必要的参数和上下文

5. **输出格式**:
   - Markdown格式文档
   - 包含架构图和代码示例
   - 支持交互式验证
"""

        return instructions

    def validate_configuration(self) -> Dict[str, Any]:
        """验证配置完整性"""
        validation_result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "details": {}
        }

        # 检查路径
        if not os.path.exists(self.bmad_docs_path):
            validation_result["success"] = False
            validation_result["errors"].append(f"BMAD docs path not found: {self.bmad_docs_path}")

        # 检查关键目录
        key_dirs = ["agents", "tasks", "workflows", "templates"]
        for dir_name in key_dirs:
            dir_path = os.path.join(self.bmad_docs_path, dir_name)
            if not os.path.exists(dir_path):
                validation_result["warnings"].append(f"Directory not found: {dir_path}")

        # 检查配置文件
        if not os.path.exists(self.config_file):
            validation_result["warnings"].append(f"Config file not found: {self.config_file}")

        # 检查团队配置
        teams = self.get_subagent_teams()
        validation_result["details"]["teams_count"] = len(teams)

        # 检查代理配置
        agents = self.get_subagent_agents()
        validation_result["details"]["agents_count"] = len(agents)

        return validation_result
