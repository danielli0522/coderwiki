#!/usr/bin/env python3
"""
CoderWiki Application Entry Point
"""
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import create_app
from config import DevelopmentConfig

# 创建Flask应用
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    # 开发环境运行 - 使用端口5001避免与AirPlay冲突
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Starting CoderWiki application on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")

    app.run(host='0.0.0.0', port=port, debug=debug)
