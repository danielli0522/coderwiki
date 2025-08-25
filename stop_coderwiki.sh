#!/bin/bash

# CoderWiki 停止脚本
# 使用方法: ./stop_coderwiki.sh [port]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
PORT=${1:-5001}

echo -e "${BLUE}🛑 CoderWiki 停止脚本${NC}"
echo "=================================="

# 检查是否有进程在运行
if ! lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口 $PORT 上没有运行中的进程${NC}"
    exit 0
fi

# 显示运行中的进程
echo -e "${YELLOW}📋 端口 $PORT 上运行中的进程:${NC}"
lsof -i :$PORT

# 询问是否停止
read -p "是否停止这些进程? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}🛑 停止端口 $PORT 上的进程...${NC}"
    lsof -ti :$PORT | xargs kill -9
    echo -e "${GREEN}✅ 进程已停止${NC}"
else
    echo -e "${YELLOW}操作取消${NC}"
fi
