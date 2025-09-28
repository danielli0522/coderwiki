#!/bin/bash

# 带检查的MySQL启动脚本
# 启动MySQL服务并等待其完全可用

echo "🚀 启动MySQL服务..."

# 启动MySQL服务
brew services start mysql

if [ $? -eq 0 ]; then
    echo "✅ MySQL服务启动命令执行成功"
    echo "⏳ 等待MySQL完全启动..."
    
    # 调用检查脚本
    ./scripts/mysql_startup_check.sh
    
    if [ $? -eq 0 ]; then
        echo "🎉 MySQL服务已完全启动并可以使用！"
        echo ""
        echo "数据库连接信息："
        echo "  主机: localhost"
        echo "  端口: 3306"
        echo "  用户: root"
        echo "  密码: 123456"
        echo ""
        echo "可用的数据库："
        mysql -u root -p123456 -h localhost -P 3306 -e "SHOW DATABASES;" 2>/dev/null | grep -v "mysql: \[Warning\]"
    else
        echo "❌ MySQL启动检查失败"
        exit 1
    fi
else
    echo "❌ MySQL服务启动失败"
    exit 1
fi