#!/bin/bash

# Claude Code API 环境变量设置脚本
# 使用方法: source setup_claude_env.sh

echo "设置 Claude Code API 环境变量..."

# 设置 Claude API Key
export ANTHROPIC_API_KEY="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"
export CLAUDE_API_KEY="$ANTHROPIC_API_KEY"

# 设置工作空间 ID（如果需要）
# export CLAUDE_WORKSPACE_ID="your-workspace-id-here"

# 设置其他环境变量
export FLASK_ENV="development"
export FLASK_DEBUG="True"

echo "环境变量已设置:"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:20}..."
echo "CLAUDE_API_KEY: ${CLAUDE_API_KEY:0:20}..."
echo "FLASK_ENV: $FLASK_ENV"
echo "FLASK_DEBUG: $FLASK_DEBUG"

echo ""
echo "使用方法:"
echo "1. 运行: source setup_claude_env.sh"
echo "2. 启动应用: python -m backend.app"
echo ""
echo "注意: 这些环境变量只在当前终端会话中有效"
echo "如需永久设置，请将 export 语句添加到 ~/.bashrc 或 ~/.zshrc"
