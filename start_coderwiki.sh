#!/bin/bash

# CoderWiki 启动脚本
# 使用方法: ./start_coderwiki.sh [port]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${BLUE}🚀 CoderWiki 启动脚本${NC}"
echo "=================================="

# 检查参数
PORT=${1:-5001}
echo -e "${YELLOW}使用端口: $PORT${NC}"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Python3${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${RED}❌ 错误: 虚拟环境不存在${NC}"
    echo "请先运行: cd backend && python3 -m venv venv"
    exit 1
fi

# 检查是否已有进程在运行
if lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  警告: 端口 $PORT 已被占用${NC}"
    read -p "是否停止现有进程? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}停止端口 $PORT 上的进程...${NC}"
        lsof -ti :$PORT | xargs kill -9
        sleep 2
    else
        echo -e "${RED}启动取消${NC}"
        exit 1
    fi
fi

# 激活虚拟环境并启动
echo -e "${GREEN}📦 激活虚拟环境...${NC}"
cd "$BACKEND_DIR"

# 检查依赖
if [ ! -f "venv/bin/pip" ]; then
    echo -e "${RED}❌ 错误: 虚拟环境未正确安装${NC}"
    exit 1
fi

# 设置环境变量
export PORT=$PORT
export FLASK_ENV=development
export FLASK_DEBUG=True
export FLASK_HOST=0.0.0.0

echo -e "${GREEN}🔧 设置环境变量:${NC}"
echo "  - PORT=$PORT"
echo "  - FLASK_ENV=development"
echo "  - FLASK_DEBUG=True"
echo "  - FLASK_HOST=0.0.0.0"

echo -e "${GREEN}🚀 启动 CoderWiki 应用...${NC}"
echo "=================================="

# 启动应用
source venv/bin/activate
python run.py
