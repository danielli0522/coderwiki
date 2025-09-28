#!/bin/bash

# MySQL启动检查脚本
# 确保MySQL完全启动并可以接受连接

MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD="123456"
MAX_ATTEMPTS=30
ATTEMPT=0

echo "正在检查MySQL服务状态..."

# 检查MySQL服务是否运行
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "尝试连接MySQL (第 $ATTEMPT 次)..."
    
    # 尝试连接MySQL
    if mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ MySQL连接成功！"
        echo "MySQL服务已完全启动并可以接受连接。"
        exit 0
    else
        echo "❌ MySQL连接失败，等待2秒后重试..."
        sleep 2
    fi
done

echo "❌ MySQL启动超时，请检查服务状态。"
echo "可以尝试手动启动MySQL服务："
echo "brew services restart mysql"
exit 1