#!/usr/bin/env python3
"""
Claude Code API 环境变量设置脚本
用于在 Python 中设置环境变量
"""

import os
import sys

def setup_claude_environment():
    """设置 Claude Code API 环境变量"""

    # Claude API Key
    api_key = "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"

    # 设置环境变量
    os.environ['ANTHROPIC_API_KEY'] = api_key
    os.environ['CLAUDE_API_KEY'] = api_key

    # 其他环境变量
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'

    print("✅ Claude Code API 环境变量已设置")
    print(f"📋 API Key: {api_key[:20]}...")
    print(f"🔧 Flask 环境: {os.environ.get('FLASK_ENV')}")
    print(f"🐛 调试模式: {os.environ.get('FLASK_DEBUG')}")

    return True

def verify_environment():
    """验证环境变量设置"""
    required_vars = ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY']

    print("\n🔍 验证环境变量设置:")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: 未设置")
            return False

    return True

if __name__ == "__main__":
    print("🚀 设置 Claude Code API 环境变量...")

    if setup_claude_environment():
        if verify_environment():
            print("\n✅ 环境变量设置完成！")
            print("\n📝 使用说明:")
            print("1. 在 Python 脚本中导入: from setup_claude_env import setup_claude_environment")
            print("2. 在代码开头调用: setup_claude_environment()")
            print("3. 或者运行: python setup_claude_env.py")
        else:
            print("\n❌ 环境变量验证失败")
            sys.exit(1)
    else:
        print("\n❌ 环境变量设置失败")
        sys.exit(1)
