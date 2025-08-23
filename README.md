# CoderWiki - 智能代码文档生成与管理平台

## 项目简介

CoderWiki 是一个基于 Flask 的智能代码文档生成与管理平台，支持多种编程语言，提供自动化的代码分析和文档生成功能。

## 功能特性

- 🔐 用户认证与授权
- 📁 代码仓库管理
- 📚 自动文档生成
- 🤖 AI 驱动的代码分析
- 📊 项目仪表板
- 🔍 代码质量评估
- 📝 测试用例生成

## 技术栈

### 后端

- **框架**: Flask 2.3.3
- **数据库**: SQLite (开发) / MySQL (生产)
- **ORM**: SQLAlchemy
- **认证**: Flask-Login
- **AI**: OpenAI GPT / Anthropic Claude

### 前端

- **框架**: Bootstrap 5
- **图标**: Font Awesome
- **JavaScript**: 原生 JS + ES6+

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip
- Git

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd coderwiki

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 设置API密钥（可选，用于AI功能）
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# 设置Flask环境
export FLASK_ENV=development
export FLASK_DEBUG=True
```

### 4. 启动服务

#### 方法一：使用启动脚本（推荐）

```bash
# 在项目根目录运行
./start_services.sh
```

#### 方法二：手动启动

```bash
# 初始化数据库
cd backend
python init_db.py

# 创建默认用户
python create_default_user.py

# 启动后端服务
PORT=5001 python run.py
```

### 5. 访问应用

服务启动后，您可以通过以下地址访问：

- 🌐 **主页**: http://localhost:5001/
- 🔐 **登录**: http://localhost:5001/api/auth/login
- 📝 **注册**: http://localhost:5001/api/auth/register
- 📊 **仪表板**: http://localhost:5001/dashboard

### 6. 默认账户

系统会自动创建以下默认账户：

| 账户类型    | 用户名     | 密码       | 邮箱                | 权限     |
| ----------- | ---------- | ---------- | ------------------- | -------- |
| 👑 管理员   | `admin`    | `admin123` | admin@coderwiki.com | 管理员   |
| 👤 演示用户 | `demo`     | `demo123`  | demo@coderwiki.com  | 普通用户 |
| 🧪 测试用户 | `testuser` | `test123`  | test@example.com    | 普通用户 |

**⚠️ 安全提示**: 建议首次登录后立即修改默认密码！

## 项目结构

```
coderwiki/
├── backend/                 # 后端代码
│   ├── app/                # Flask应用
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   ├── utils/         # 工具函数
│   │   └── routes/        # 页面路由
│   ├── config.py          # 配置文件
│   ├── init_db.py         # 数据库初始化
│   ├── create_default_user.py  # 创建默认用户
│   ├── manage_users.py    # 用户管理工具
│   └── run.py             # 启动文件
├── frontend/               # 前端代码
│   ├── static/            # 静态资源
│   │   ├── css/          # 样式文件
│   │   ├── js/           # JavaScript文件
│   │   └── images/       # 图片资源
│   └── templates/         # HTML模板
├── docs/                  # 项目文档
├── scripts/               # 脚本文件
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## API 文档

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/status` - 获取登录状态

### 仓库管理

- `GET /api/repositories` - 获取仓库列表
- `POST /api/repositories` - 添加仓库
- `GET /api/repositories/{id}` - 获取仓库详情
- `DELETE /api/repositories/{id}` - 删除仓库

### 文档生成

- `POST /api/repositories/{id}/generate` - 生成文档
- `GET /api/repositories/{id}/documents` - 获取文档列表
- `GET /api/documents/{id}` - 获取文档详情

## 用户管理

### 查看用户列表

```bash
cd backend
python manage_users.py list
```

### 创建新用户

```bash
# 创建普通用户
python manage_users.py create john john@example.com password123

# 创建管理员用户
python manage_users.py create admin admin@example.com admin123 --admin
```

### 重置密码

```bash
python manage_users.py reset john newpassword123
```

### 删除用户

```bash
python manage_users.py delete john
```

## 开发指南

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型提示
- 编写单元测试
- 添加文档字符串

### 测试

```bash
# 运行单元测试
cd backend
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 运行端到端测试
python -m pytest tests/e2e/
```

### 数据库迁移

```bash
# 创建迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade
```

## 部署

### 开发环境

```bash
# 使用Flask开发服务器
python run.py
```

### 生产环境

```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# 使用uWSGI
uwsgi --ini uwsgi.ini
```

## 故障排除

### 常见问题

1. **端口被占用**

   ```bash
   # 检查端口占用
   lsof -i :5001

   # 使用不同端口
   PORT=5002 python run.py
   ```

2. **数据库错误**

   ```bash
   # 重新初始化数据库
   python init_db.py
   ```

3. **API 密钥问题**

   ```bash
   # 运行诊断工具
   python scripts/diagnose_api_quota.py
   ```

4. **用户账户问题**

   ```bash
   # 查看用户列表
   python manage_users.py list

   # 重置管理员密码
   python manage_users.py reset admin newpassword
   ```

### 日志查看

```bash
# 查看应用日志
tail -f backend/logs/app.log

# 查看错误日志
grep ERROR backend/logs/app.log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: [your-email@example.com]

## 更新日志

### v1.0.0 (2024-01-08)

- ✨ 初始版本发布
- 🔐 用户认证系统
- 📁 仓库管理功能
- 📚 文档生成功能
- 🤖 AI 代码分析
