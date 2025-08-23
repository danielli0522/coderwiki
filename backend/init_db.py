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
from config import DevelopmentConfig

def init_database():
    """Initialize database tables"""
    app = create_app(DevelopmentConfig)

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
