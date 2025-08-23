#!/bin/bash

# CoderWiki 服务启动脚本

echo "🚀 启动 CoderWiki 服务..."

# 检查是否在正确的目录
if [ ! -f "backend/run.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 启动后端服务
start_backend() {
    echo "🔧 启动后端服务..."
    cd backend

    # 检查数据库
    if [ ! -f "coderwiki_dev.db" ]; then
        echo "🗄️  初始化数据库..."
        python init_db.py

        echo "👥 创建默认用户账户..."
        python create_default_user.py
    fi

    # 启动服务
    PORT=5001 python run.py &
    BACKEND_PID=$!
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID, 端口: 5001)"
    cd ..
}

# 启动前端开发服务器（如果需要）
start_frontend() {
    echo "🎨 前端使用静态文件服务，无需单独启动"
    echo "📱 前端页面可通过后端服务访问: http://localhost:5001"
}

# 主函数
main() {
    echo "=========================================="
    echo "    CoderWiki 服务启动脚本"
    echo "=========================================="

    # 检查端口
    if ! check_port 5001; then
        echo "❌ 请停止占用端口 5001 的服务后重试"
        exit 1
    fi

    # 启动服务
    start_backend
    start_frontend

    echo ""
    echo "🎉 服务启动完成！"
    echo ""
    echo "📋 服务信息:"
    echo "   🌐 后端 API: http://localhost:5001"
    echo "   🏠 主页: http://localhost:5001/"
    echo "   🔐 登录: http://localhost:5001/api/auth/login"
    echo "   📝 注册: http://localhost:5001/api/auth/register"
    echo "   📊 仪表板: http://localhost:5001/dashboard"
    echo ""
    echo "🔑 默认账户信息:"
    echo "   👑 管理员: admin / admin123"
    echo "   👤 演示用户: demo / demo123"
    echo "   🧪 测试用户: testuser / test123"
    echo ""
    echo "💡 提示:"
    echo "   - 按 Ctrl+C 停止服务"
    echo "   - 查看日志: tail -f backend/logs/app.log"
    echo "   - 数据库文件: backend/coderwiki_dev.db"
    echo "   - 建议首次登录后修改默认密码"
    echo ""

    # 等待用户中断
    wait $BACKEND_PID
}

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 后端服务已停止"
    fi
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 运行主函数
main
