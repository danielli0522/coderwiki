#!/usr/bin/env python3
"""
BMAD Orchestrator - BMAD 代理编排器
负责协调和管理 BMAD 代理团队的工作流执行
"""

import os
import sys
import time
import logging
import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.agent_manager import AgentManager
from workflows.workflow_engine import WorkflowEngine
from utils.config_loader import ConfigLoader
from utils.result_aggregator import ResultAggregator


class WorkflowStatus(Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """代理任务定义"""
    agent_id: str
    agent_name: str
    task_name: str
    inputs: Dict[str, Any]
    expected_outputs: List[str]
    dependencies: List[str] = None
    timeout: int = 300
    priority: int = 1


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    status: WorkflowStatus
    start_time: float
    end_time: Optional[float] = None
    agent_results: Dict[str, Any] = None
    final_document: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class BMADOrchestrator:
    """BMAD 代理编排器"""

    def __init__(self, config_path: str = None):
        """
        初始化 BMAD 编排器

        Args:
            config_path: 配置文件路径
        """
        self.config = ConfigLoader.load_config(config_path)
        self.agent_manager = AgentManager(self.config)
        self.workflow_engine = WorkflowEngine(self.config)
        self.result_aggregator = ResultAggregator()

        # 工作流状态管理
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.workflow_history: List[WorkflowResult] = []

        # 执行器
        self.executor = ThreadPoolExecutor(max_workers=5)

        # 日志配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.logger.info("BMAD Orchestrator initialized successfully")

    def execute_workflow(self, workflow_name: str, inputs: Dict[str, Any]) -> WorkflowResult:
        """
        执行指定的工作流

        Args:
            workflow_name: 工作流名称
            inputs: 输入参数

        Returns:
            工作流执行结果
        """
        workflow_id = f"{workflow_name}_{int(time.time())}"

        self.logger.info(f"Starting workflow: {workflow_name} (ID: {workflow_id})")

        # 创建工作流结果对象
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            start_time=time.time(),
            agent_results={}
        )

        self.active_workflows[workflow_id] = workflow_result

        try:
            # 1. 加载工作流定义
            workflow_def = self.workflow_engine.load_workflow(workflow_name)
            if not workflow_def:
                raise ValueError(f"Workflow '{workflow_name}' not found")

            # 2. 验证输入参数
            self._validate_workflow_inputs(workflow_def, inputs)

            # 3. 更新状态为运行中
            workflow_result.status = WorkflowStatus.RUNNING

            # 4. 执行工作流阶段
            agent_results = self._execute_workflow_phases(workflow_def, inputs, workflow_id)

            # 5. 聚合结果
            final_document = self.result_aggregator.aggregate_results(agent_results, workflow_def)

            # 6. 完成工作流
            workflow_result.status = WorkflowStatus.COMPLETED
            workflow_result.end_time = time.time()
            workflow_result.execution_time = workflow_result.end_time - workflow_result.start_time
            workflow_result.agent_results = agent_results
            workflow_result.final_document = final_document

            self.logger.info(f"Workflow {workflow_id} completed successfully in {workflow_result.execution_time:.2f}s")

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            workflow_result.status = WorkflowStatus.FAILED
            workflow_result.end_time = time.time()
            workflow_result.error_message = str(e)

        finally:
            # 从活动工作流中移除
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

            # 添加到历史记录
            self.workflow_history.append(workflow_result)

        return workflow_result

    def _execute_workflow_phases(self, workflow_def: Dict, inputs: Dict, workflow_id: str) -> Dict[str, Any]:
        """
        执行工作流的各个阶段

        Args:
            workflow_def: 工作流定义
            inputs: 输入参数
            workflow_id: 工作流ID

        Returns:
            代理执行结果
        """
        agent_results = {}
        shared_context = inputs.copy()

        # 按阶段执行
        for phase in workflow_def.get('phases', []):
            phase_name = phase['name']
            self.logger.info(f"Executing phase: {phase_name}")

            # 执行阶段中的任务
            phase_results = self._execute_phase_tasks(phase, shared_context, workflow_id)
            agent_results.update(phase_results)

            # 更新共享上下文
            shared_context.update(phase_results)

        return agent_results

    def _execute_phase_tasks(self, phase: Dict, context: Dict, workflow_id: str) -> Dict[str, Any]:
        """
        执行阶段中的任务

        Args:
            phase: 阶段定义
            context: 执行上下文
            workflow_id: 工作流ID

        Returns:
            任务执行结果
        """
        tasks = phase.get('tasks', [])
        task_results = {}

        # 创建任务依赖图
        task_dependencies = self._build_task_dependencies(tasks)

        # 按依赖顺序执行任务
        executed_tasks = set()

        while len(executed_tasks) < len(tasks):
            # 找到可以执行的任务
            ready_tasks = [
                task for task in tasks
                if task['id'] not in executed_tasks and
                all(dep in executed_tasks for dep in task_dependencies.get(task['id'], []))
            ]

            if not ready_tasks:
                # 检测循环依赖
                raise ValueError(f"Circular dependency detected in phase {phase['name']}")

            # 并行执行就绪的任务
            futures = []
            for task in ready_tasks:
                future = self.executor.submit(
                    self._execute_agent_task,
                    task,
                    context,
                    workflow_id
                )
                futures.append((task['id'], future))

            # 等待任务完成
            for task_id, future in futures:
                try:
                    result = future.result(timeout=300)  # 5分钟超时
                    task_results[task_id] = result
                    executed_tasks.add(task_id)
                    self.logger.info(f"Task {task_id} completed successfully")
                except Exception as e:
                    self.logger.error(f"Task {task_id} failed: {str(e)}")
                    raise

        return task_results

    def _execute_agent_task(self, task: Dict, context: Dict, workflow_id: str) -> Dict[str, Any]:
        """
        执行单个代理任务

        Args:
            task: 任务定义
            context: 执行上下文
            workflow_id: 工作流ID

        Returns:
            任务执行结果
        """
        agent_id = task['agent']
        task_name = task['name']

        self.logger.info(f"Executing task: {task_name} with agent: {agent_id}")

        # 获取代理实例
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")

        # 准备任务输入
        task_inputs = self._prepare_task_inputs(task, context)

        # 执行代理任务
        start_time = time.time()
        try:
            result = agent.execute_task(task_name, task_inputs)
            execution_time = time.time() - start_time

            self.logger.info(f"Agent {agent_id} completed task {task_name} in {execution_time:.2f}s")

            return {
                'agent_id': agent_id,
                'task_name': task_name,
                'status': 'completed',
                'result': result,
                'execution_time': execution_time,
                'timestamp': time.time()
            }

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Agent {agent_id} failed task {task_name}: {str(e)}")

            return {
                'agent_id': agent_id,
                'task_name': task_name,
                'status': 'failed',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': time.time()
            }

    def _build_task_dependencies(self, tasks: List[Dict]) -> Dict[str, List[str]]:
        """
        构建任务依赖关系图

        Args:
            tasks: 任务列表

        Returns:
            依赖关系图
        """
        dependencies = {}

        for task in tasks:
            task_id = task['id']
            deps = task.get('dependencies', [])
            dependencies[task_id] = deps

        return dependencies

    def _prepare_task_inputs(self, task: Dict, context: Dict) -> Dict[str, Any]:
        """
        准备任务输入参数

        Args:
            task: 任务定义
            context: 执行上下文

        Returns:
            任务输入参数
        """
        inputs = task.get('inputs', {})
        prepared_inputs = {}

        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith('$'):
                # 从上下文中获取值
                context_key = value[1:]
                if context_key in context:
                    prepared_inputs[key] = context[context_key]
                else:
                    self.logger.warning(f"Context key '{context_key}' not found for task input '{key}'")
                    prepared_inputs[key] = None
            else:
                prepared_inputs[key] = value

        return prepared_inputs

    def _validate_workflow_inputs(self, workflow_def: Dict, inputs: Dict):
        """
        验证工作流输入参数

        Args:
            workflow_def: 工作流定义
            inputs: 输入参数
        """
        required_inputs = workflow_def.get('required_inputs', [])

        for required_input in required_inputs:
            if required_input not in inputs:
                raise ValueError(f"Required input '{required_input}' not provided")

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """
        获取工作流状态

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流结果
        """
        # 检查活动工作流
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]

        # 检查历史记录
        for result in self.workflow_history:
            if result.workflow_id == workflow_id:
                return result

        return None

    def get_active_workflows(self) -> List[WorkflowResult]:
        """
        获取所有活动工作流

        Returns:
            活动工作流列表
        """
        return list(self.active_workflows.values())

    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        取消工作流

        Args:
            workflow_id: 工作流ID

        Returns:
            是否成功取消
        """
        if workflow_id in self.active_workflows:
            workflow_result = self.active_workflows[workflow_id]
            workflow_result.status = WorkflowStatus.CANCELLED
            workflow_result.end_time = time.time()

            # 从活动工作流中移除
            del self.active_workflows[workflow_id]

            # 添加到历史记录
            self.workflow_history.append(workflow_result)

            self.logger.info(f"Workflow {workflow_id} cancelled")
            return True

        return False

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        获取工作流统计信息

        Returns:
            统计信息
        """
        total_workflows = len(self.workflow_history)
        completed_workflows = len([w for w in self.workflow_history if w.status == WorkflowStatus.COMPLETED])
        failed_workflows = len([w for w in self.workflow_history if w.status == WorkflowStatus.FAILED])
        active_workflows = len(self.active_workflows)

        avg_execution_time = 0
        if completed_workflows > 0:
            execution_times = [w.execution_time for w in self.workflow_history if w.execution_time]
            avg_execution_time = sum(execution_times) / len(execution_times)

        return {
            'total_workflows': total_workflows,
            'completed_workflows': completed_workflows,
            'failed_workflows': failed_workflows,
            'active_workflows': active_workflows,
            'success_rate': completed_workflows / total_workflows if total_workflows > 0 else 0,
            'average_execution_time': avg_execution_time
        }

    def shutdown(self):
        """关闭编排器"""
        self.logger.info("Shutting down BMAD Orchestrator")
        self.executor.shutdown(wait=True)
        self.logger.info("BMAD Orchestrator shutdown complete")


def main():
    """主函数 - 用于测试"""
    import argparse

    parser = argparse.ArgumentParser(description='BMAD Orchestrator')
    parser.add_argument('--workflow', '-w', required=True, help='Workflow name to execute')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--input', '-i', help='Input JSON file path')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    # 创建编排器
    orchestrator = BMADOrchestrator(args.config)

    try:
        # 加载输入参数
        inputs = {}
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                inputs = json.load(f)

        # 执行工作流
        result = orchestrator.execute_workflow(args.workflow, inputs)

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, default=str)
        else:
            print(json.dumps(asdict(result), indent=2, default=str))

        # 输出统计信息
        stats = orchestrator.get_workflow_statistics()
        print(f"\nWorkflow Statistics:")
        print(f"  Total: {stats['total_workflows']}")
        print(f"  Completed: {stats['completed_workflows']}")
        print(f"  Failed: {stats['failed_workflows']}")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        print(f"  Avg Execution Time: {stats['average_execution_time']:.2f}s")

    finally:
        orchestrator.shutdown()


if __name__ == '__main__':
    main()



