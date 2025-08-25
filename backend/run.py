#!/usr/bin/env python3
"""
CoderWiki Application Entry Point
"""
import os
import sys
import signal
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        return False

    # 检查必要的目录
    required_dirs = ['logs', 'uploads', 'repos']
    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 目录检查: {dir_name}")

    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境: 已激活")
    else:
        print("⚠️  警告: 未检测到虚拟环境")

    return True

def signal_handler(signum, frame):
    """处理退出信号"""
    print(f"\n🛑 收到退出信号 {signum}，正在关闭服务...")
    sys.exit(0)

def main():
    """主启动函数"""
    print("🚀 启动 CoderWiki 应用...")
    print("=" * 50)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 检查环境
    if not check_environment():
        sys.exit(1)

    try:
        from app import create_app
        from config import DevelopmentConfig

        print("📦 导入应用模块...")

        # 创建Flask应用
        app = create_app(DevelopmentConfig)

        # 获取配置
        port = int(os.environ.get('PORT', 5001))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        host = os.environ.get('FLASK_HOST', '0.0.0.0')

        print(f"⚙️  配置信息:")
        print(f"   - 端口: {port}")
        print(f"   - 主机: {host}")
        print(f"   - 调试模式: {debug}")
        print(f"   - 环境: {os.environ.get('FLASK_ENV', 'development')}")

        # 显示访问地址
        print(f"\n🌐 服务地址:")
        print(f"   - 本地访问: http://localhost:{port}")
        print(f"   - 网络访问: http://10.11.75.81:{port}")
        print(f"   - 系统状态: http://{host}:{port}/system-status")

        print(f"\n🔑 默认用户:")
        print(f"   - admin (admin@coderwiki.com)")
        print(f"   - demo (demo@coderwiki.com)")
        print(f"   - testuser (test@example.com)")

        print(f"\n⏰ 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        # 启动应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # 避免重复启动
        )

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
