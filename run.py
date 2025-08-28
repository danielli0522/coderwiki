#!/usr/bin/env python3
"""
CoderWiki Application Entry Point
"""
import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 切换到backend目录
os.chdir(backend_dir)

from app import create_app
from config import Config

# 创建Flask应用
app, socketio = create_app(Config)

if __name__ == '__main__':
    # 开发环境运行 - 使用端口5001避免与AirPlay冲突
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Starting CoderWiki application on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")

    if socketio:
        socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
    else:
        app.run(host='0.0.0.0', port=port, debug=debug)
