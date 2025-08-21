# CoderWiki - 代码文档自动生成系统

## 项目简介

CoderWiki是一个基于AI的代码文档自动生成系统，能够分析代码仓库结构并生成高质量的技术文档。

## 技术栈

- **后端**: Python 3.8+, Flask 2.3+, MySQL 8.0+
- **前端**: Bootstrap 5.3, jQuery 3.6+
- **数据库**: MySQL 8.0+
- **开发工具**: VS Code, Git, pytest

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.0+
- Git

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd coderwiki
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入实际配置
   ```

5. **初始化数据库**
   ```bash
   # 创建数据库
   mysql -u root -p -e "CREATE DATABASE coderwiki CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   
   # 运行迁移
   flask db upgrade
   ```

6. **启动应用**
   ```bash
   python run.py
   ```

访问 http://localhost:5000 查看应用。

## 项目结构

```
coderwiki/
├── backend/           # 后端应用
├── frontend/          # 前端资源
├── docs/              # 文档
├── requirements.txt   # 生产依赖
├── requirements-dev.txt # 开发依赖
├── .env.example      # 环境变量示例
├── .gitignore        # Git忽略文件
└── README.md         # 项目说明
```

## 开发指南

### 代码规范

- 遵循PEP 8规范
- 使用4个空格缩进
- 最大行长度120字符
- 使用UTF-8编码

### 提交规范

```
<类型>: <描述>

[可选的详细描述]

[可选的引用]
```

提交类型：
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式化
- **refactor**: 重构
- **test**: 测试相关
- **chore**: 构建或工具相关

### 测试

```bash
# 运行所有测试
pytest

# 运行覆盖率测试
pytest --cov=app

# 运行代码质量检查
flake8 app/
black app/
isort app/
```

## 部署

### 开发环境

```bash
# 启动开发服务器
python run.py
```

### 生产环境

```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建Issue或联系开发团队。