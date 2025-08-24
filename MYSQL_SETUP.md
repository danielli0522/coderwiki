# MySQL 数据库设置指导

当前生产环境已配置为默认使用MySQL数据库，但需要手动设置MySQL用户和数据库。

## 1. 手动创建MySQL数据库和用户

连接到MySQL并执行以下命令：

```sql
-- 连接MySQL (使用root用户)
mysql -u root -p

-- 创建数据库
CREATE DATABASE IF NOT EXISTS coderwiki CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER IF NOT EXISTS 'coderwiki_user'@'localhost' IDENTIFIED BY 'coderwiki_password';

-- 授权
GRANT ALL PRIVILEGES ON coderwiki.* TO 'coderwiki_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

## 2. 使用现有SQL脚本

或者直接执行项目中的SQL脚本：

```bash
mysql -u root -p < database/init_mysql.sql
```

## 3. 初始化应用数据库

设置完MySQL后，运行：

```bash
cd backend
python init_db.py
python create_default_user.py
```

## 4. 启动应用

```bash
PORT=5001 python run.py
```

## 当前配置

- 生产环境默认使用MySQL
- 数据库连接：`mysql+pymysql://coderwiki_user:coderwiki_password@localhost:3306/coderwiki`
- 如需修改，可在`.env`文件中设置`DATABASE_URL`

## 故障排除

如果遇到连接问题：

1. 确认MySQL服务正在运行
2. 验证用户名密码是否正确
3. 检查MySQL用户权限
4. 确认数据库已创建