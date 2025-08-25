#!/bin/bash

# CoderWiki 状态检查脚本
# 使用方法: ./status_coderwiki.sh [port]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
PORT=${1:-5001}

echo -e "${BLUE}📊 CoderWiki 状态检查${NC}"
echo "=================================="

# 检查进程状态
echo -e "${YELLOW}🔍 检查进程状态...${NC}"
if lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 端口 $PORT 上有进程运行${NC}"
    echo -e "${BLUE}📋 进程详情:${NC}"
    lsof -i :$PORT
else
    echo -e "${RED}❌ 端口 $PORT 上没有进程运行${NC}"
fi

echo

# 检查服务响应
echo -e "${YELLOW}🌐 检查服务响应...${NC}"
if curl -s http://localhost:$PORT/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 本地服务响应正常${NC}"
else
    echo -e "${RED}❌ 本地服务无响应${NC}"
fi

if curl -s http://10.11.75.81:$PORT/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 网络服务响应正常${NC}"
else
    echo -e "${RED}❌ 网络服务无响应${NC}"
fi

echo

# 显示访问地址
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "  - 本地访问: http://localhost:$PORT"
echo "  - 网络访问: http://10.11.75.81:$PORT"
echo "  - 系统状态: http://localhost:$PORT/system-status"

echo

# 显示默认用户
echo -e "${BLUE}🔑 默认用户:${NC}"
echo "  - admin (admin@coderwiki.com)"
echo "  - demo (demo@coderwiki.com)"
echo "  - testuser (test@example.com)"
echo "  - test (test@test.com)"

echo "=================================="
