#!/usr/bin/env python3
"""
检查数据库中仓库的路径配置
"""
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'

try:
    # 导入应用
    from app import db
    from app.models.repository import Repository
    from config import DevelopmentConfig
    from flask import Flask

    # 创建应用
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # 初始化数据库
    db.init_app(app)

    with app.app_context():
        print("🔍 检查数据库中的仓库路径配置...")

        # 查找包含cc-sdk-demo的仓库
        repos = Repository.query.filter(
            Repository.local_path.contains('cc-sdk-demo')
        ).all()

        if not repos:
            print("⚠️  没有找到包含'cc-sdk-demo'的仓库")
            # 查看所有仓库
            all_repos = Repository.query.all()
            print(f"📊 数据库中共有 {len(all_repos)} 个仓库:")
            for repo in all_repos[:5]:  # 只显示前5个
                print(f"   - ID: {repo.id}, Name: {repo.name}")
                print(f"     URL: {repo.url}")
                print(f"     Local Path: {repo.local_path}")
                print(f"     Status: {repo.status}")
                print("     ---")
        else:
            print(f"✅ 找到 {len(repos)} 个包含'cc-sdk-demo'的仓库:")
            for repo in repos:
                print(f"   📁 仓库信息:")
                print(f"      - ID: {repo.id}")
                print(f"      - Name: {repo.name}")
                print(f"      - URL: {repo.url}")
                print(f"      - Local Path: {repo.local_path}")
                print(f"      - Status: {repo.status}")
                print(f"      - Clone Status: {repo.clone_status}")

                # 检查路径是否存在
                if repo.local_path and os.path.exists(repo.local_path):
                    print(f"      ✅ 本地路径存在: {repo.local_path}")

                    # 检查是否是目标目录
                    if 'cc-sdk-demo' in repo.local_path:
                        print(f"      🎯 这是目标仓库！")

                        # 列出目录内容
                        try:
                            files = os.listdir(repo.local_path)
                            print(f"      📂 目录包含 {len(files)} 个文件/目录")
                            print(f"      📄 主要文件: {[f for f in files if f.endswith(('.md', '.js', '.ts', '.json'))[:5]]}")
                        except Exception as e:
                            print(f"      ❌ 无法读取目录: {e}")
                else:
                    print(f"      ❌ 本地路径不存在: {repo.local_path}")

                print("      " + "="*50)

        # 检查/tmp/coderwiki_repos目录
        print("\n🔍 检查/tmp/coderwiki_repos目录...")
        tmp_dir = "/tmp/coderwiki_repos"
        if os.path.exists(tmp_dir):
            subdirs = [d for d in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, d))]
            print(f"   📂 找到 {len(subdirs)} 个子目录:")
            for subdir in subdirs:
                full_path = os.path.join(tmp_dir, subdir)
                print(f"      - {subdir}")
                if 'cc-sdk-demo' in subdir:
                    print(f"        🎯 这是目标目录: {full_path}")
        else:
            print(f"   ❌ 目录不存在: {tmp_dir}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
