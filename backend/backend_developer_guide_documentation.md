# 开发者指南

## 项目概述

这是一个基于Flask的Web应用后端项目，使用Python开发。项目采用了现代化的Web开发架构，包含完整的用户认证、数据库管理、API接口等功能。

## 技术栈

- **后端框架**: Flask
- **数据库**: SQLAlchemy (支持MySQL、PostgreSQL、SQLite)
- **认证**: Flask-Login
- **API文档**: 自动生成
- **部署**: 支持Docker容器化部署

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── utils/             # 工具函数
├── config.py              # 配置文件
├── run.py                 # 启动脚本
└── requirements.txt       # 依赖包
```

## 核心功能

### 1. 用户管理
- 用户注册和登录
- 权限管理
- 会话管理

### 2. 文档生成
- 支持多种文档类型
- Claude Code集成
- MCP服务支持

### 3. API接口
- RESTful API设计
- 统一的响应格式
- 错误处理机制

### 4. 数据库管理
- 数据模型定义
- 数据库迁移
- 查询优化

## 部署说明

### 环境要求
- Python 3.8+
- 数据库 (MySQL/PostgreSQL/SQLite)
- 虚拟环境

### 安装步骤
1. 克隆项目
2. 创建虚拟环境
3. 安装依赖
4. 配置数据库
5. 运行迁移
6. 启动服务

## 开发指南

### 本地开发
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py
```

### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解
- 编写单元测试
- 文档字符串

## 工具调用记录

在文档生成过程中，系统使用了以下工具进行分析：



## 总结

本项目是一个功能完整的Flask后端应用，具有良好的架构设计和扩展性。通过集成Claude Code和MCP服务，提供了强大的文档生成能力。

---

*本文档由Claude Code SDK自动生成*
