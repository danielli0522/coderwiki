#!/bin/bash

# 安装和启动puppeteer-mcp-server脚本

echo "🔧 安装和配置puppeteer-mcp-server"
echo "=================================="

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    echo "访问: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js已安装: $(node --version)"

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装"
    exit 1
fi

echo "✅ npm已安装: $(npm --version)"

# 检查是否已安装puppeteer-mcp-server
if npm list -g puppeteer-mcp-server &> /dev/null; then
    echo "✅ puppeteer-mcp-server已安装"
else
    echo "📦 安装puppeteer-mcp-server..."
    npm install -g puppeteer-mcp-server

    if [ $? -eq 0 ]; then
        echo "✅ puppeteer-mcp-server安装成功"
    else
        echo "❌ puppeteer-mcp-server安装失败"
        exit 1
    fi
fi

# 检查端口3001是否被占用
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ 端口3001已被占用，尝试停止现有进程..."
    lsof -ti:3001 | xargs kill -9
    sleep 2
fi

# 启动puppeteer-mcp-server
echo "🚀 启动puppeteer-mcp-server..."
echo "服务将在端口3001上运行"
echo "按Ctrl+C停止服务"

# 启动服务
puppeteer-mcp-server --port 3001
