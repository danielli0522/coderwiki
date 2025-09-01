#!/usr/bin/env python3
"""
使用特定BMAD子代理的示例脚本
演示如何固定使用某个特定的Claude Code子代理
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('FLASK_APP', 'run.py')

from app import create_app
from app.services.bmad_subagent_config import BMADSubagentConfig
from app.models.repository import Repository
from app.services.document_generator import DocumentGenerator
from app.utils.bmad_orchestrator import BMADOrchestrator
from app.utils.claude_client import ClaudeCodeClient


class SpecificAgentRunner:
    """特定子代理运行器"""
    
    def __init__(self, agent_id: str = None):
        """
        初始化特定代理运行器
        
        Args:
            agent_id: 指定的代理ID，如 'code-analyst', 'flow-analyst' 等
        """
        self.agent_id = agent_id
        self.config = BMADSubagentConfig()
        
        # 获取Flask应用上下文
        app_result = create_app()
        if isinstance(app_result, tuple):
            self.app, _ = app_result
        else:
            self.app = app_result
            
    def list_available_agents(self):
        """列出所有可用的子代理"""
        print("\n" + "="*60)
        print("可用的BMAD子代理列表")
        print("="*60)
        
        agents = self.config.get_subagent_agents()
        for i, agent in enumerate(agents, 1):
            print(f"\n{i}. {agent['name']} (ID: {agent['id']})")
            print(f"   角色: {agent['role']}")
            print(f"   能力: {', '.join(agent['capabilities'][:3])}...")
            print(f"   主要任务: {', '.join(agent['primary_tasks'])}")
            
        return agents
    
    def use_only_code_analyst(self, repository_path: str):
        """只使用Code Analyst (Alex)进行代码分析"""
        print("\n" + "="*60)
        print("使用Code Analyst (Alex)进行代码分析")
        print("="*60)
        
        with self.app.app_context():
            # 创建只包含code-analyst的配置
            single_agent_config = {
                'use_bmad': True,
                'agents': ['code-analyst'],  # 只使用这一个代理
                'analysis_depth': 'detailed',
                'tasks': [
                    'scan-codebase',
                    'analyze-dependencies',
                    'identify-patterns'
                ]
            }
            
            # 模拟执行
            result = self._execute_single_agent(
                agent_id='code-analyst',
                repository_path=repository_path,
                config=single_agent_config
            )
            
            return result
    
    def use_only_flow_analyst(self, repository_path: str):
        """只使用Flow Analyst (Jordan)进行流程分析"""
        print("\n" + "="*60)
        print("使用Flow Analyst (Jordan)进行流程分析")
        print("="*60)
        
        with self.app.app_context():
            single_agent_config = {
                'use_bmad': True,
                'agents': ['flow-analyst'],
                'analysis_depth': 'detailed',
                'tasks': [
                    'analyze-complex-flows',
                    'generate-enhanced-sequence-diagrams',
                    'validate-flow-analysis'
                ]
            }
            
            result = self._execute_single_agent(
                agent_id='flow-analyst',
                repository_path=repository_path,
                config=single_agent_config
            )
            
            return result
    
    def use_only_problem_solver(self, repository_path: str):
        """只使用Problem Solver (Dr. Morgan)进行问题诊断"""
        print("\n" + "="*60)
        print("使用Problem Solver (Dr. Morgan)进行问题诊断")
        print("="*60)
        
        with self.app.app_context():
            single_agent_config = {
                'use_bmad': True,
                'agents': ['problem-solver'],
                'analysis_depth': 'detailed',
                'tasks': [
                    'diagnose-potential-problems',
                    'generate-arch-insights',
                    'validate-problem-diagnosis'
                ]
            }
            
            result = self._execute_single_agent(
                agent_id='problem-solver',
                repository_path=repository_path,
                config=single_agent_config
            )
            
            return result
    
    def use_custom_agent_combination(self, repository_path: str, agent_ids: list):
        """使用自定义的代理组合"""
        print("\n" + "="*60)
        print(f"使用自定义代理组合: {', '.join(agent_ids)}")
        print("="*60)
        
        with self.app.app_context():
            results = {}
            
            for agent_id in agent_ids:
                print(f"\n执行代理: {agent_id}")
                config = {
                    'use_bmad': True,
                    'agents': [agent_id],
                    'analysis_depth': 'detailed'
                }
                
                result = self._execute_single_agent(
                    agent_id=agent_id,
                    repository_path=repository_path,
                    config=config
                )
                
                results[agent_id] = result
                
            return results
    
    def _execute_single_agent(self, agent_id: str, repository_path: str, config: dict):
        """
        执行单个代理
        
        Args:
            agent_id: 代理ID
            repository_path: 仓库路径
            config: 配置
        """
        # 获取代理信息
        agents = self.config.get_subagent_agents()
        agent_info = next((a for a in agents if a['id'] == agent_id), None)
        
        if not agent_info:
            print(f"错误: 未找到代理 {agent_id}")
            return None
        
        print(f"\n正在执行: {agent_info['name']} ({agent_info['role']})")
        print(f"任务: {config.get('tasks', agent_info['primary_tasks'])}")
        
        # 模拟执行结果（实际使用时需要调用真实的Claude API）
        result = {
            'agent_id': agent_id,
            'agent_name': agent_info['name'],
            'status': 'completed',
            'tasks_completed': config.get('tasks', agent_info['primary_tasks']),
            'output': f"{agent_info['name']}分析完成",
            'summary': f"使用{agent_info['role']}完成了指定任务"
        }
        
        print(f"✅ {agent_info['name']}执行完成")
        
        return result
    
    def demonstrate_all_modes(self, repository_path: str):
        """演示所有模式"""
        print("\n" + "="*60)
        print("BMAD子代理使用模式演示")
        print("="*60)
        
        # 1. 列出所有代理
        self.list_available_agents()
        
        # 2. 只使用Code Analyst
        print("\n\n### 模式1: 只使用Code Analyst ###")
        code_result = self.use_only_code_analyst(repository_path)
        print(f"结果: {json.dumps(code_result, ensure_ascii=False, indent=2)}")
        
        # 3. 只使用Flow Analyst
        print("\n\n### 模式2: 只使用Flow Analyst ###")
        flow_result = self.use_only_flow_analyst(repository_path)
        print(f"结果: {json.dumps(flow_result, ensure_ascii=False, indent=2)}")
        
        # 4. 只使用Problem Solver
        print("\n\n### 模式3: 只使用Problem Solver ###")
        problem_result = self.use_only_problem_solver(repository_path)
        print(f"结果: {json.dumps(problem_result, ensure_ascii=False, indent=2)}")
        
        # 5. 使用自定义组合（Code Analyst + Problem Solver）
        print("\n\n### 模式4: 自定义组合(Code Analyst + Problem Solver) ###")
        custom_result = self.use_custom_agent_combination(
            repository_path, 
            ['code-analyst', 'problem-solver']
        )
        print(f"结果: {json.dumps(custom_result, ensure_ascii=False, indent=2)}")


def main():
    """主函数"""
    # 设置测试仓库路径
    repository_path = "coderwiki-output-docs/repos/puppeteer-mcp-server_13"
    
    # 创建运行器
    runner = SpecificAgentRunner()
    
    # 运行演示
    runner.demonstrate_all_modes(repository_path)
    
    # 交互式选择模式
    print("\n\n" + "="*60)
    print("交互式代理选择")
    print("="*60)
    
    agents = runner.config.get_subagent_agents()
    
    print("\n请选择要使用的代理（输入数字）：")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent['name']} ({agent['id']})")
    
    try:
        choice = input("\n选择 (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(agents):
            selected_agent = agents[int(choice) - 1]
            print(f"\n您选择了: {selected_agent['name']}")
            
            # 执行选定的代理
            result = runner._execute_single_agent(
                agent_id=selected_agent['id'],
                repository_path=repository_path,
                config={
                    'use_bmad': True,
                    'agents': [selected_agent['id']],
                    'analysis_depth': 'detailed'
                }
            )
            
            print(f"\n执行结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
            
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    main()