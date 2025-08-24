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
from config import Config, ProductionConfig, DevelopmentConfig

# 默认使用生产环境配置
config_class = ProductionConfig
if os.environ.get('FLASK_ENV') == 'development':
    config_class = DevelopmentConfig

# 创建Flask应用
app = create_app(config_class)

if __name__ == '__main__':
    # 生产环境运行 - 使用端口5001
    port = int(os.environ.get('PORT', 5001))
    flask_env = os.environ.get('FLASK_ENV', 'production')
    debug = flask_env == 'development'

    print(f"Starting CoderWiki application on port {port}")
    print(f"Environment: {flask_env}")
    print(f"Debug mode: {debug}")
    print(f"Using config: {config_class.__name__}")

    app.run(host='0.0.0.0', port=port, debug=debug)
