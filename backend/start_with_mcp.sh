#!/bin/bash

# CoderWiki with MCP Service Startup Script
# 此脚本帮助配置和启动支持MCP服务的CoderWiki后端

set -e

echo "🚀 CoderWiki MCP Service Startup Script"
echo "========================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env
    echo "⚠️  请编辑 .env 文件，配置必要的环境变量"
    echo "   特别是 MCP_SERVER_URL 和 MCP_SERVER_PORT"
fi

# 检查MCP服务配置
echo "🔍 检查MCP服务配置..."
MCP_ENABLED=${MCP_ENABLED:-true}
MCP_SERVER_URL=${MCP_SERVER_URL:-http://localhost}
MCP_SERVER_PORT=${MCP_SERVER_PORT:-3000}

echo "MCP_ENABLED: $MCP_ENABLED"
echo "MCP_SERVER_URL: $MCP_SERVER_URL"
echo "MCP_SERVER_PORT: $MCP_SERVER_PORT"

if [ "$MCP_ENABLED" = "true" ]; then
    echo "✅ MCP服务已启用"

    # 检查MCP服务是否运行
    echo "🔍 检查MCP服务状态..."
    if curl -s "$MCP_SERVER_URL:$MCP_SERVER_PORT/health" > /dev/null 2>&1; then
        echo "✅ MCP服务正在运行"
    else
        echo "⚠️  MCP服务未运行或无法访问"
        echo "   请确保doc-generator-tool的MCP服务正在运行在端口 $MCP_SERVER_PORT"
        echo "   或者设置 MCP_ENABLED=false 来禁用MCP服务"
    fi
else
    echo "ℹ️  MCP服务已禁用，将使用直接LLM API调用"
fi

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
flask db upgrade

# 启动应用
echo "🚀 启动CoderWiki后端服务..."
echo "   访问地址: http://localhost:5000"
echo "   API文档: http://localhost:5000/api"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 设置环境变量并启动Flask应用
export FLASK_APP=run.py
export FLASK_ENV=development

# 启动应用
python run.py
