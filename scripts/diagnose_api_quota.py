#!/usr/bin/env python3
"""
API配额诊断工具

用于诊断和解决LLM API配额相关问题。
"""

import os
import sys
import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 直接导入需要的模块，避免Flask应用初始化
try:
    from backend.app.utils.api_quota_manager import (
        APIQuotaManager,
        check_api_health,
        get_quota_optimization_tips
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("尝试直接实现诊断功能...")

    # 如果导入失败，提供基本的诊断功能
    class SimpleAPIQuotaManager:
        def __init__(self):
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            self.llm_api_key = os.getenv('LLM_API_KEY')

        def get_quota_recommendations(self):
            recommendations = []

            if not any([self.openai_api_key, self.anthropic_api_key, self.llm_api_key]):
                recommendations.append({
                    'priority': 'high',
                    'title': '配置API密钥',
                    'description': '未检测到任何LLM API密钥配置',
                    'action': '请设置OPENAI_API_KEY、ANTHROPIC_API_KEY或LLM_API_KEY环境变量'
                })

            return recommendations

    def check_api_health():
        manager = SimpleAPIQuotaManager()
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'openai_status': 'unknown',
            'anthropic_status': 'unknown',
            'recommendations': []
        }

        if manager.openai_api_key:
            try:
                headers = {'Authorization': f'Bearer {manager.openai_api_key}'}
                response = requests.get(
                    'https://api.openai.com/v1/models',
                    headers=headers,
                    timeout=5
                )
                health_status['openai_status'] = 'healthy' if response.status_code == 200 else 'error'
            except Exception as e:
                health_status['openai_status'] = 'error'
                health_status['recommendations'].append(f'OpenAI连接失败: {str(e)}')

        if manager.anthropic_api_key:
            try:
                headers = {
                    'x-api-key': manager.anthropic_api_key,
                    'anthropic-version': '2023-06-01'
                }
                response = requests.get(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    timeout=5
                )
                health_status['anthropic_status'] = 'healthy' if response.status_code in [200, 405] else 'error'
            except Exception as e:
                health_status['anthropic_status'] = 'error'
                health_status['recommendations'].append(f'Anthropic连接失败: {str(e)}')

        return health_status

    def get_quota_optimization_tips():
        return [
            "1. 使用更经济的模型（如gpt-3.5-turbo）",
            "2. 实现响应缓存机制",
            "3. 批量处理多个请求",
            "4. 设置合理的max_tokens限制",
            "5. 使用流式响应减少延迟",
            "6. 监控API使用情况",
            "7. 设置使用量告警",
            "8. 考虑使用本地模型作为备选"
        ]

def print_header(title: str):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """打印章节标题"""
    print(f"\n--- {title} ---")

def check_environment_variables():
    """检查环境变量配置"""
    print_section("环境变量检查")

    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'LLM_API_KEY': os.getenv('LLM_API_KEY'),
        'LLM_MODEL': os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
        'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'openai')
    }

    print("当前环境变量配置:")
    for var, value in env_vars.items():
        if value:
            # 隐藏API密钥的敏感信息
            if 'API_KEY' in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")

    # 检查是否有至少一个API密钥
    api_keys = [env_vars['OPENAI_API_KEY'], env_vars['ANTHROPIC_API_KEY'], env_vars['LLM_API_KEY']]
    if not any(api_keys):
        print("\n⚠️  警告: 未检测到任何API密钥配置!")
        print("   请设置以下环境变量之一:")
        print("   - OPENAI_API_KEY (OpenAI API)")
        print("   - ANTHROPIC_API_KEY (Anthropic API)")
        print("   - LLM_API_KEY (通用LLM API)")
        return False

    return True

def test_api_connections():
    """测试API连接"""
    print_section("API连接测试")

    health_status = check_api_health()

    print("API连接状态:")
    print(f"  OpenAI: {health_status['openai_status']}")
    print(f"  Anthropic: {health_status['anthropic_status']}")

    if health_status['recommendations']:
        print("\n连接问题建议:")
        for rec in health_status['recommendations']:
            print(f"  - {rec}")

    return health_status

def check_quota_status():
    """检查配额状态"""
    print_section("配额状态检查")

    try:
        manager = APIQuotaManager()
        quota_summary = manager.get_quota_status_summary()

        print("配额使用情况:")

        # OpenAI配额
        openai_info = quota_summary['providers']['openai']
        if openai_info:
            print(f"  OpenAI:")
            print(f"    状态: {openai_info['status']}")
            print(f"    模型: {openai_info['model']}")
            if openai_info['used_tokens'] > 0:
                print(f"    已用tokens: {openai_info['used_tokens']:,}")
            if openai_info['total_tokens'] > 0:
                print(f"    总tokens: {openai_info['total_tokens']:,}")
        else:
            print("  OpenAI: 无法获取配额信息")

        # Anthropic配额
        anthropic_info = quota_summary['providers']['anthropic']
        if anthropic_info:
            print(f"  Anthropic:")
            print(f"    状态: {anthropic_info['status']}")
            print(f"    模型: {anthropic_info['model']}")
        else:
            print("  Anthropic: 无法获取配额信息")

        return quota_summary
    except Exception as e:
        print(f"检查配额状态时出错: {str(e)}")
        return None

def show_recommendations():
    """显示优化建议"""
    print_section("优化建议")

    try:
        manager = APIQuotaManager()
        recommendations = manager.get_quota_recommendations()
    except:
        manager = SimpleAPIQuotaManager()
        recommendations = manager.get_quota_recommendations()

    print(f"发现 {len(recommendations)} 条优化建议:")

    for i, rec in enumerate(recommendations, 1):
        priority_icon = "🔴" if rec.get('priority') == 'high' else "🟡" if rec.get('priority') == 'medium' else "🟢"
        print(f"\n{priority_icon} 建议 {i}: {rec.get('title', 'Unknown')}")
        print(f"   描述: {rec.get('description', 'No description')}")
        print(f"   操作: {rec.get('action', 'No action specified')}")
        if rec.get('estimated_savings'):
            print(f"   预计节省: ${rec['estimated_savings']:.3f}/1000 tokens")

def show_optimization_tips():
    """显示优化提示"""
    print_section("配额优化提示")

    tips = get_quota_optimization_tips()
    for tip in tips:
        print(f"  {tip}")

def simulate_api_call():
    """模拟API调用测试"""
    print_section("API调用测试")

    try:
        # 简单的API调用测试
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')

        if openai_key:
            print("测试OpenAI API...")
            headers = {
                'Authorization': f'Bearer {openai_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': 'Hello'}],
                'max_tokens': 10
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                print("✅ OpenAI API调用成功!")
            elif response.status_code == 429:
                error_data = response.json()
                print(f"❌ OpenAI API配额不足: {error_data}")
            else:
                print(f"❌ OpenAI API调用失败: {response.status_code} - {response.text}")

        elif anthropic_key:
            print("测试Anthropic API...")
            headers = {
                'x-api-key': anthropic_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 10,
                'messages': [{'role': 'user', 'content': 'Hello'}]
            }

            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                print("✅ Anthropic API调用成功!")
            elif response.status_code == 429:
                error_data = response.json()
                print(f"❌ Anthropic API配额不足: {error_data}")
            else:
                print(f"❌ Anthropic API调用失败: {response.status_code} - {response.text}")
        else:
            print("❌ 未配置API密钥，无法进行测试")

    except Exception as e:
        print(f"❌ API调用异常: {str(e)}")

def main():
    """主函数"""
    print_header("API配额诊断工具")

    print("此工具将帮助您诊断和解决LLM API配额相关问题。")

    # 1. 检查环境变量
    env_ok = check_environment_variables()

    # 2. 测试API连接
    health_status = test_api_connections()

    # 3. 检查配额状态
    quota_summary = check_quota_status()

    # 4. 显示建议
    show_recommendations()

    # 5. 显示优化提示
    show_optimization_tips()

    # 6. 模拟API调用（如果环境变量配置正确）
    if env_ok:
        simulate_api_call()

    # 总结
    print_header("诊断总结")

    print("基于诊断结果，建议采取以下行动:")

    if not env_ok:
        print("1. 🔴 立即配置API密钥")
        print("   - 访问 https://platform.openai.com/api-keys (OpenAI)")
        print("   - 访问 https://console.anthropic.com/ (Anthropic)")
        print("   - 设置相应的环境变量")

    if health_status['openai_status'] == 'error' or health_status['anthropic_status'] == 'error':
        print("2. 🟡 检查API连接")
        print("   - 验证API密钥是否正确")
        print("   - 检查网络连接")
        print("   - 确认API服务状态")

    print("3. 🟢 实施优化建议")
    print("   - 使用更经济的模型")
    print("   - 实现缓存机制")
    print("   - 监控使用情况")

    print("\n如需更多帮助，请参考:")
    print("- OpenAI文档: https://platform.openai.com/docs")
    print("- Anthropic文档: https://docs.anthropic.com/")
    print("- 项目文档: docs/ARCHITECTURE.md")

if __name__ == "__main__":
    main()
