#!/usr/bin/env python3
"""
Workflow Engine - 工作流引擎
负责管理和执行工作流定义
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化工作流引擎

        Args:
            config: 配置信息
        """
        self.config = config
        self.workflows = config.get('workflows', {})

    def load_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        加载工作流定义

        Args:
            workflow_name: 工作流名称

        Returns:
            工作流定义
        """
        return self.workflows.get(workflow_name)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        列出所有工作流

        Returns:
            工作流列表
        """
        return [
            {
                'name': name,
                'description': workflow.get('description', ''),
                'phases': len(workflow.get('phases', []))
            }
            for name, workflow in self.workflows.items()
        ]

    def validate_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        验证工作流定义

        Args:
            workflow_name: 工作流名称

        Returns:
            验证结果
        """
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return {'valid': False, 'error': f'Workflow "{workflow_name}" not found'}

        errors = []

        # 检查必需字段
        required_fields = ['name', 'phases']
        for field in required_fields:
            if field not in workflow:
                errors.append(f'Missing required field: {field}')

        # 检查阶段定义
        phases = workflow.get('phases', [])
        for i, phase in enumerate(phases):
            if 'name' not in phase:
                errors.append(f'Phase {i}: Missing name')
            if 'tasks' not in phase:
                errors.append(f'Phase {i}: Missing tasks')
            else:
                for j, task in enumerate(phase['tasks']):
                    if 'id' not in task:
                        errors.append(f'Phase {i}, Task {j}: Missing id')
                    if 'agent' not in task:
                        errors.append(f'Phase {i}, Task {j}: Missing agent')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }



