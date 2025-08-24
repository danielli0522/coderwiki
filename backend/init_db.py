#!/usr/bin/env python3
"""
Initialize database tables
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from config import ProductionConfig, DevelopmentConfig
import os

def init_database():
    """Initialize database tables"""
    # 使用与run.py相同的配置逻辑
    config_class = ProductionConfig
    if os.environ.get('FLASK_ENV') == 'development':
        config_class = DevelopmentConfig
    
    print(f"Initializing database with {config_class.__name__}")
    app = create_app(config_class)

    with app.app_context():
        # 创建所有表
        db.create_all()
        print("Database tables created successfully!")

        # 显示创建的表
        from app.models.user import User
        from app.models.repository import Repository
        from app.models.document import Document
        from app.models.task import Task

        print("\nCreated tables:")
        print("- User")
        print("- Repository")
        print("- Document")
        print("- Task")

if __name__ == '__main__':
    init_database()
