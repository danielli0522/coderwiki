"""
Serena服务集成
用于在CoderWiki项目中集成Serena AI助手功能
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SerenaService:
    """Serena AI助手服务类"""

    def __init__(self, claude_api_key: str = None, workspace_id: str = None):
        """
        初始化Serena服务

        Args:
            claude_api_key: Claude API密钥
            workspace_id: Claude Code工作空间ID
        """
        self.claude_api_key = claude_api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.workspace_id = workspace_id or os.environ.get('CLAUDE_CODE_WORKSPACE_ID')
        self.serena_config = self._load_serena_config()

    def _load_serena_config(self) -> Dict[str, Any]:
        """加载Serena配置"""
        return {
            "name": "Serena",
            "role": "AI助手",
            "capabilities": [
                "代码优化建议",
                "文档生成协助",
                "技术架构分析",
                "问题诊断",
                "最佳实践推荐"
            ],
            "system_prompt": self._get_serena_system_prompt()
        }

    def _get_serena_system_prompt(self) -> str:
        """获取Serena的系统提示词"""
        return """
你是Serena，一个专业的AI助手，专门帮助开发者和技术团队：

## 你的核心能力
1. **代码分析与优化**：深入分析代码结构，提供优化建议
2. **文档生成**：协助生成高质量的技术文档
3. **架构设计**：帮助设计系统架构和解决方案
4. **问题诊断**：快速识别和解决技术问题
5. **最佳实践**：推荐行业最佳实践和标准

## 工作方式
- 始终保持专业、友好的态度
- 提供具体、可执行的建议
- 使用清晰的中文交流
- 结合项目实际情况给出建议
- 主动询问细节以确保建议的准确性

## 在CoderWiki项目中的角色
- 协助用户生成技术文档
- 优化代码质量和架构设计
- 提供开发建议和最佳实践
- 帮助解决技术难题

请告诉我你需要什么帮助？
"""

    async def get_serena_assistance(self,
                                  query: str,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取Serena的协助

        Args:
            query: 用户查询
            context: 上下文信息

        Returns:
            包含Serena建议的响应字典
        """
        try:
            # 构建完整的提示词
            full_prompt = self._build_assistance_prompt(query, context)

            # 这里应该调用Claude Code SDK
            # 由于环境限制，我们返回模拟响应
            response = await self._simulate_serena_response(query, context)

            return {
                'success': True,
                'assistant': 'Serena',
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'context': context
            }

        except Exception as e:
            logger.error(f"Serena协助失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'assistant': 'Serena'
            }

    def _build_assistance_prompt(self, query: str, context: Dict[str, Any] = None) -> str:
        """构建协助提示词"""
        prompt = self.serena_config['system_prompt']

        if context:
            prompt += f"\n\n## 项目上下文\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"

        prompt += f"\n\n## 用户查询\n{query}\n\n请提供专业的建议和解决方案。"

        return prompt

    async def _simulate_serena_response(self, query: str, context: Dict[str, Any] = None) -> str:
        """模拟Serena响应（在实际环境中应该调用Claude Code SDK）"""
        return f"""
你好！我是Serena，很高兴为你提供帮助。

关于你的问题："{query}"

## 我的建议

基于你的查询，我建议：

1. **深入分析**：首先需要了解你的具体需求和项目背景
2. **技术方案**：根据项目特点选择合适的技术方案
3. **最佳实践**：遵循行业标准和最佳实践
4. **持续优化**：定期评估和改进

## 下一步行动

为了更好地帮助你，请告诉我：
- 你的具体技术需求是什么？
- 项目当前面临的主要挑战？
- 你希望达到的目标？

我会根据你的回答提供更具体和针对性的建议。

期待与你进一步交流！
"""

    async def optimize_code_with_serena(self,
                                      code_content: str,
                                      language: str = "python") -> Dict[str, Any]:
        """
        使用Serena优化代码

        Args:
            code_content: 代码内容
            language: 编程语言

        Returns:
            优化建议字典
        """
        try:
            query = f"请帮我优化以下{language}代码：\n\n{code_content}"

            response = await self.get_serena_assistance(query, {
                'task_type': 'code_optimization',
                'language': language,
                'code_length': len(code_content)
            })

            return response

        except Exception as e:
            logger.error(f"代码优化失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_documentation_with_serena(self,
                                               project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用Serena生成文档

        Args:
            project_info: 项目信息

        Returns:
            文档生成结果
        """
        try:
            query = f"请帮我为这个项目生成技术文档：{project_info.get('description', '')}"

            response = await self.get_serena_assistance(query, {
                'task_type': 'documentation_generation',
                'project_info': project_info
            })

            return response

        except Exception as e:
            logger.error(f"文档生成失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_serena_status(self) -> Dict[str, Any]:
        """获取Serena服务状态"""
        return {
            'service_name': 'Serena',
            'status': 'available',
            'version': '1.0.0',
            'capabilities': self.serena_config['capabilities'],
            'last_updated': datetime.now().isoformat()
        }

