#!/usr/bin/env python3
"""
简单检查数据库和路径配置
"""
import os
import pymysql

# MySQL连接配置
config = {
    'host': 'localhost',
    'user': 'coderwiki_user',
    'password': 'coderwiki_password',
    'database': 'coderwiki_dev',
    'charset': 'utf8mb4'
}

try:
    print("🔍 连接数据库...")
    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    # 检查repositories表结构
    print("\n📋 检查repositories表结构...")
    cursor.execute("DESCRIBE repositories")
    columns = cursor.fetchall()
    print("   表字段:")
    for column in columns:
        print(f"      - {column[0]} ({column[1]})")

    # 查看所有repository记录的local_path
    print("\n🔍 检查repositories表中的local_path...")
    cursor.execute("SELECT id, name, local_path, git_url FROM repositories")
    repos = cursor.fetchall()

    if not repos:
        print("   ⚠️  没有找到任何仓库记录")
    else:
        print(f"   📊 找到 {len(repos)} 个仓库:")
        for repo in repos:
            repo_id, name, local_path, git_url = repo
            print(f"      - ID: {repo_id}")
            print(f"        Name: {name}")
            print(f"        Local Path: {local_path}")
            print(f"        Git URL: {git_url}")

            # 检查是否是cc-sdk-demo
            if local_path and 'cc-sdk-demo' in local_path:
                print(f"        🎯 这是目标仓库！")

                # 检查路径是否存在
                if os.path.exists(local_path):
                    print(f"        ✅ 路径存在")
                    try:
                        files = os.listdir(local_path)
                        print(f"        📂 包含 {len(files)} 个文件/目录")
                        js_files = [f for f in files if f.endswith(('.js', '.ts'))]
                        md_files = [f for f in files if f.endswith('.md')]
                        print(f"        📄 JS/TS文件: {len(js_files)}")
                        print(f"        📄 MD文件: {len(md_files)}")
                    except Exception as e:
                        print(f"        ❌ 无法读取目录: {e}")
                else:
                    print(f"        ❌ 路径不存在")
            print("        " + "-"*30)

    cursor.close()
    conn.close()

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

                # 列出内容
                try:
                    files = os.listdir(full_path)
                    js_files = [f for f in files if f.endswith(('.js', '.ts'))]
                    md_files = [f for f in files if f.endswith('.md')]
                    print(f"        📂 包含 {len(files)} 个文件/目录")
                    print(f"        📄 JS/TS文件: {len(js_files)} 个")
                    print(f"        📄 MD文件: {len(md_files)} 个")

                    # 显示一些关键文件
                    key_files = [f for f in files if f in ['package.json', 'README.md', 'tsconfig.json']]
                    if key_files:
                        print(f"        🔑 关键文件: {key_files}")
                except Exception as e:
                    print(f"        ❌ 无法读取目录: {e}")
    else:
        print(f"   ❌ 目录不存在: {tmp_dir}")

    print("\n📋 总结:")
    print("   1. 检查数据库中是否有cc-sdk-demo仓库记录")
    print("   2. 检查该仓库的local_path字段")
    print("   3. 验证ClaudeCodeService是否能读取该路径")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
