#!/usr/bin/env python3
"""
Enhanced Claude Interactive Client with Robust Timeout and Retry Handling
Addresses QA Critical Concerns: Timeout Issues and Reliability
"""

import subprocess
import tempfile
import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

class ClaudeRobustClient:
    """Enhanced Claude client with robust timeout and retry mechanisms"""

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.max_retries = 3
        self.base_timeout = 120  # 2 minutes base timeout
        self.retry_delay = 5  # seconds between retries
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def send_interactive_message(self, message: str, timeout: Optional[int] = None, retry_count: int = 0) -> Dict[str, Any]:
        """
        Enhanced message sending with retry logic and progressive timeout
        
        Args:
            message: 要发送的消息
            timeout: 超时时间（秒）, None使用自适应超时
            retry_count: 当前重试次数
            
        Returns:
            响应结果
        """
        # 自适应超时：基础时间 + 重试递增时间 + 消息长度调整
        if timeout is None:
            message_length_factor = min(len(message) // 100, 60)  # 每100字符增加1秒，最多60秒
            retry_timeout_increase = retry_count * 30  # 每次重试增加30秒
            timeout = self.base_timeout + message_length_factor + retry_timeout_increase
        
        self.logger.info(f"🔄 尝试 {retry_count + 1}/{self.max_retries + 1}, 超时设置: {timeout}s")
        self.logger.info(f"📤 发送消息: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        # 创建输入脚本
        input_script = f"{message}\n/exit\n"
        
        # 创建临时输入文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(input_script)
            input_file = f.name

        try:
            # 创建干净的环境（移除 API Key）
            clean_env = os.environ.copy()
            for var in ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY']:
                if var in clean_env:
                    del clean_env[var]

            start_time = time.time()
            
            # 运行交互模式
            result = subprocess.run(
                ['claude'],
                stdin=open(input_file, 'r'),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace_path
            )
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"⏱️ Claude响应时间: {elapsed_time:.2f}s")

            if result.returncode == 0:
                response = result.stdout.strip()
                
                # 检查响应质量
                if self._is_valid_response(response):
                    self.logger.info("✅ Claude响应成功")
                    return {
                        'success': True,
                        'response': response,
                        'method': 'interactive_mode',
                        'elapsed_time': elapsed_time,
                        'retry_count': retry_count
                    }
                else:
                    error_msg = f"Invalid response: {response[:200]}..."
                    self.logger.warning(f"⚠️ 响应质量不佳: {error_msg}")
                    return self._handle_retry(message, timeout, retry_count, error_msg)
            else:
                error_msg = f"Command failed with code {result.returncode}"
                self.logger.error(f"❌ 命令执行失败: {error_msg}")
                self.logger.error(f"STDERR: {result.stderr}")
                
                return self._handle_retry(message, timeout, retry_count, error_msg, result.stderr)

        except subprocess.TimeoutExpired:
            error_msg = f"Timeout after {timeout}s"
            self.logger.warning(f"⏰ 超时: {error_msg}")
            return self._handle_retry(message, timeout, retry_count, error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"💥 意外错误: {error_msg}")
            return self._handle_retry(message, timeout, retry_count, error_msg)

        finally:
            # 清理临时文件
            try:
                os.unlink(input_file)
            except:
                pass

    def _is_valid_response(self, response: str) -> bool:
        """检查响应是否有效"""
        if not response:
            return False
        
        # 检查是否包含错误指示
        error_indicators = [
            "credit balance",
            "quota exceeded", 
            "rate limit",
            "authentication failed",
            "command not found"
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator in response_lower:
                return False
        
        # 检查响应长度是否合理（至少50个字符）
        return len(response.strip()) >= 50

    def _handle_retry(self, message: str, timeout: int, retry_count: int, error_msg: str, stderr: str = "") -> Dict[str, Any]:
        """处理重试逻辑"""
        if retry_count < self.max_retries:
            self.logger.info(f"🔄 准备重试 ({retry_count + 1}/{self.max_retries})...")
            time.sleep(self.retry_delay)
            return self.send_interactive_message(message, None, retry_count + 1)
        else:
            self.logger.error(f"❌ 所有重试已用完，最终失败")
            return {
                'success': False,
                'error': f"All retries exhausted. Last error: {error_msg}",
                'stderr': stderr,
                'retry_count': retry_count
            }

    def generate_project_analysis_robust(self, project_path: str) -> Dict[str, Any]:
        """
        生成项目分析文档 - 增强版，带完整错误处理
        
        Args:
            project_path: 项目路径
            
        Returns:
            分析结果
        """
        self.logger.info(f"📊 开始健壮性项目分析: {project_path}")
        
        # 验证项目路径
        if not os.path.exists(project_path):
            return {
                'success': False,
                'error': f"Project path does not exist: {project_path}"
            }

        # 分步骤进行分析，使用更简单的问题避免超时
        analysis_steps = [
            {
                'question': f'Please briefly analyze the project structure in {project_path}. What type of project is this?',
                'key': 'project_type',
                'description': 'Project Type Analysis'
            },
            {
                'question': f'What are the main technologies and frameworks used in {project_path}?',
                'key': 'tech_stack', 
                'description': 'Technology Stack Analysis'
            },
            {
                'question': f'What are the core features and functionality of the project in {project_path}?',
                'key': 'main_function',
                'description': 'Core Functionality Analysis'
            }
        ]

        results = {}
        successful_steps = 0

        for i, step in enumerate(analysis_steps, 1):
            self.logger.info(f"📝 步骤 {i}/3: {step['description']}")

            response = self.send_interactive_message(step['question'])

            if response['success']:
                results[step['key']] = {
                    'question': step['question'],
                    'answer': response['response'],
                    'success': True,
                    'elapsed_time': response.get('elapsed_time', 0),
                    'retry_count': response.get('retry_count', 0)
                }
                successful_steps += 1
                self.logger.info(f"✅ 步骤 {i} 完成 (用时: {response.get('elapsed_time', 0):.1f}s)")

                # 步骤间延迟，避免请求过快
                if i < len(analysis_steps):
                    time.sleep(3)
            else:
                results[step['key']] = {
                    'question': step['question'],
                    'error': response['error'],
                    'success': False,
                    'retry_count': response.get('retry_count', 0)
                }
                self.logger.error(f"❌ 步骤 {i} 失败: {response['error']}")

        # 生成综合分析
        if successful_steps > 0:
            self.logger.info("📋 生成综合分析报告...")

            summary_parts = []
            summary_parts.append(f"# {os.path.basename(project_path)} 项目分析报告")
            summary_parts.append(f"\n> 🤖 基于 Claude 交互模式自动生成")
            summary_parts.append(f"> 📅 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            summary_parts.append(f"> 📊 成功分析步骤: {successful_steps}/{len(analysis_steps)}")
            summary_parts.append(f"> 📁 项目路径: {project_path}")

            for key, result in results.items():
                if result['success']:
                    summary_parts.append(f"\n## {key.replace('_', ' ').title()}")
                    summary_parts.append(f"\n**分析问题**: {result['question']}")
                    summary_parts.append(f"\n**分析结果**:\n{result['answer']}")
                    summary_parts.append(f"\n**性能指标**: 用时 {result['elapsed_time']:.1f}s, 重试 {result['retry_count']} 次")
                    summary_parts.append("\n---")
                else:
                    summary_parts.append(f"\n## {key.replace('_', ' ').title()} ❌")
                    summary_parts.append(f"\n**错误**: {result['error']}")
                    summary_parts.append(f"\n**重试次数**: {result['retry_count']}")
                    summary_parts.append("\n---")

            summary_content = "\n".join(summary_parts)

            return {
                'success': True,
                'analysis': summary_content,
                'step_results': results,
                'method': 'robust_interactive_analysis',
                'successful_steps': successful_steps,
                'total_steps': len(analysis_steps),
                'success_rate': successful_steps / len(analysis_steps)
            }
        else:
            return {
                'success': False,
                'error': 'All analysis steps failed',
                'step_results': results,
                'successful_steps': 0,
                'total_steps': len(analysis_steps),
                'success_rate': 0.0
            }

    def quick_test(self) -> Dict[str, Any]:
        """快速测试Claude连接和响应能力"""
        self.logger.info("🧪 Quick Claude Connection Test")
        
        test_message = "Hello! Please respond with a brief confirmation that you can help with code analysis tasks."
        
        result = self.send_interactive_message(test_message, timeout=60)
        
        if result['success']:
            self.logger.info("✅ Claude连接测试成功")
        else:
            self.logger.error(f"❌ Claude连接测试失败: {result['error']}")
            
        return result


def main():
    """主测试函数 - 验证健壮性改进"""
    print("🧪 Claude健壮性客户端测试")
    print("=" * 60)
    
    client = ClaudeRobustClient()
    
    # 1. 快速连接测试
    print("\n💬 快速连接测试...")
    test_result = client.quick_test()
    
    if not test_result['success']:
        print("❌ 连接测试失败，请检查Claude CLI安装")
        return False
    
    # 2. 项目分析测试
    print("\n📊 健壮性项目分析测试...")
    project_path = "backend/repos/deepwiki-open"
    
    if os.path.exists(project_path):
        analysis_result = client.generate_project_analysis_robust(project_path)
        
        if analysis_result['success']:
            print("🎉 健壮性分析成功！")
            print(f"📊 成功率: {analysis_result['success_rate']:.1%}")
            
            # 保存分析结果
            output_file = "robust_deepwiki_analysis.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis_result['analysis'])
            
            print(f"📄 分析报告已保存: {output_file}")
            return True
        else:
            print("❌ 健壮性分析失败")
            print(f"📊 成功率: {analysis_result['success_rate']:.1%}")
            return False
    else:
        print(f"⚠️ 项目路径不存在: {project_path}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)