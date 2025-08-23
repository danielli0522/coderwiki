#!/usr/bin/env python3
"""
MySQL数据库初始化脚本
"""

import os
import sys
import pymysql
from werkzeug.security import generate_password_hash

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'coderwiki_user',
    'password': 'coderwiki_password',
    'charset': 'utf8mb4'
}

def create_database():
    """创建数据库"""
    try:
        # 连接MySQL服务器
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )

        cursor = connection.cursor()

        # 创建数据库
        print("🔧 创建数据库...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS coderwiki CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("CREATE DATABASE IF NOT EXISTS coderwiki_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

        print("✅ 数据库创建成功")

        # 为两个数据库创建表
        databases = ['coderwiki', 'coderwiki_dev']

        for db_name in databases:
            print(f"🔧 为数据库 {db_name} 创建表...")
            cursor.execute(f"USE {db_name}")

            # 创建表

        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                last_login DATETIME NULL,
                INDEX idx_username (username),
                INDEX idx_email (email),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 仓库表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                git_url VARCHAR(500),
                local_path VARCHAR(500),
                user_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 文档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                file_path VARCHAR(500),
                repository_id INT,
                user_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_repository_id (repository_id),
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                repository_id INT,
                user_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                due_date DATETIME NULL,
                FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_repository_id (repository_id),
                INDEX idx_user_id (user_id),
                INDEX idx_status (status),
                INDEX idx_priority (priority),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        print("✅ 数据表创建成功")

        # 为两个数据库创建默认用户
        print("🔧 创建默认用户...")

        for db_name in databases:
            print(f"🔧 为数据库 {db_name} 创建用户...")
            cursor.execute(f"USE {db_name}")

            # 检查是否已存在用户
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            if user_count == 0:
                # 创建默认用户
                default_users = [
                    ('admin', 'admin@coderwiki.com', 'admin123', True),
                    ('demo', 'demo@coderwiki.com', 'demo123', False),
                    ('testuser', 'test@example.com', 'test123', False)
                ]

                for username, email, password, is_admin in default_users:
                    password_hash = generate_password_hash(password)
                    cursor.execute("""
                        INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                    """, (username, email, password_hash, True, is_admin))

                connection.commit()
                print(f"✅ 数据库 {db_name} 默认用户创建成功")
            else:
                print(f"⚠️  数据库 {db_name} 中已存在 {user_count} 个用户，跳过默认用户创建")

        # 显示表信息
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📋 数据库表列表:")
        for table in tables:
            print(f"  - {table[0]}")

        # 显示用户信息
        print(f"\n👥 用户列表:")
        for db_name in databases:
            print(f"\n📊 数据库 {db_name}:")
            cursor.execute(f"USE {db_name}")
            cursor.execute("SELECT id, username, email, is_admin, created_at FROM users")
            users = cursor.fetchall()
            for user in users:
                admin_status = "管理员" if user[3] else "普通用户"
                print(f"  - {user[1]} ({user[2]}) - {admin_status}")

        connection.close()
        print("\n🎉 MySQL数据库初始化完成！")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        return False

    return True

if __name__ == '__main__':
    print("🚀 开始初始化MySQL数据库...")
    success = create_database()
    if success:
        print("\n💡 提示:")
        print("  - 默认管理员账户: admin / admin123")
        print("  - 演示账户: demo / demo123")
        print("  - 测试账户: testuser / test123")
        print("  - 建议首次登录后修改默认密码")
    else:
        print("\n❌ 数据库初始化失败，请检查MySQL服务是否运行")
        sys.exit(1)
